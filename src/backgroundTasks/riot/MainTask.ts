import { logger } from "../../boot/config";
import axios from "axios";
import axiosRetry from "axios-retry";
import { Info, MatchDTO, Participant } from "../../interfaces/MatchInterfaces";
import { SummonerDB } from "../../interfaces/CustomInterfaces";
import differenceBy from "lodash/differenceBy";
import pgPromise from "pg-promise";
import DBHelper from "../../helpers/DBHelper";
import RiotHelper from "../../helpers/RiotHelper";

export default class MainTask {
  dbHelper: DBHelper;
  riotHelper: RiotHelper;

  constructor() {
    this.dbHelper = DBHelper.getInstance();
    this.riotHelper = RiotHelper.getInstance();
    axiosRetry(axios, {
      retries: 3, // number of retries
      retryDelay: (retryCount) => {
        logger.warn(`retry attempt: ${retryCount}`);
        return retryCount * 2000; // time interval between retries
      },
    });
  }

  //
  //DB Stuff
  //
  async prepareMatches(summoner: any, matchData: any[], archiveData: any[], count = 100, offset = 0) {
    const matchIds = await this.riotHelper.getMatchList(summoner, count, offset);
    for (const matchId of matchIds) {
      try {
        let match = await this.riotHelper.getMatch(matchId);
        archiveData.push({
          match_id: match.metadata.matchId,
          data: JSON.parse(JSON.stringify(match)),
        });

        let participantDto = this.getParticipantFromMatch(summoner.data.puuid, match);
        let match_id_puuid = match.metadata.matchId + "__" + summoner.data.puuid;
        matchData.push({
          match_id: match.metadata.matchId,
          match_id_puuid: match_id_puuid,
          summoner_id: summoner.id,
          puuid: summoner.data.puuid,
          data_participant: participantDto,
          data_match: this.createGameInfo(match),
        });
      } catch (e: any) {
        logger.error(`Request for summoner [${summoner.data.name}] failed with error, will continue the loop: ${e}`);
      }
    }
  }

  async updateMatchData(offset: number = 0, count: number = 6) {
    const { data, error } = await this.dbHelper.executeQuery("select * from summoners");
    if (error) {
      logger.error(`Error occurred while getting summoners: ${error}`);
    }
    if (data) {
      for (const summonerDB of data.rows as SummonerDB[]) {
        try {
          const matchData: any[] = [];
          const archiveData: any[] = [];
          await this.prepareMatches(summonerDB, matchData, archiveData, count, offset);

          const pgp = pgPromise({ pgFormatting: false, capSQL: true });
          const columsV5 = new pgp.helpers.ColumnSet(
            ["match_id", "match_id_puuid", "summoner_id", "puuid", "data_participant", "data_match"],
            { table: "match_v5" }
          );
          const queryV5 = pgp.helpers.insert(matchData, columsV5) + " ON CONFLICT (match_id_puuid) DO NOTHING";
          const columsArchive = new pgp.helpers.ColumnSet(["match_id", "data"], { table: "match_archive" });
          const queryArchive = pgp.helpers.insert(archiveData, columsArchive) + " ON CONFLICT (match_id) DO NOTHING";

          await this.dbHelper.executeQuery(queryV5);
          await this.dbHelper.executeQuery(queryArchive);
        } catch (e) {
          logger.error(e);
        }
      }
    }
  }

  async updateMatchDataForSummoner(puuid: string, offset: number = 0, count: number = 6) {
    const query = {
      text: "SELECT * FROM summoners WHERE puuid = $1",
      values: [puuid],
    };
    const { data, error } = await this.dbHelper.executeQuery(query);
    if (error) {
      logger.error(`Error occured while getting summoners: ${error}`);
    }

    if (data) {
      for (const summonerDB of data.rows as SummonerDB[]) {
        try {
          const matchData: any[] = [];
          const archiveData: any[] = [];
          await this.prepareMatches(summonerDB, matchData, archiveData, count, offset);

          const pgp = pgPromise({ pgFormatting: false, capSQL: true });
          const columsV5 = new pgp.helpers.ColumnSet(
            ["match_id", "match_id_puuid", "summoner_id", "puuid", "data_participant", "data_match"],
            { table: "match_v5" }
          );
          const queryV5 = pgp.helpers.insert(matchData, columsV5) + " ON CONFLICT (match_id_puuid) DO NOTHING";
          const columsArchive = new pgp.helpers.ColumnSet(["match_id", "data"], { table: "match_archive" });
          const queryArchive = pgp.helpers.insert(archiveData, columsArchive) + " ON CONFLICT (match_id) DO NOTHING";

          await this.dbHelper.executeQuery(queryV5);
          await this.dbHelper.executeQuery(queryArchive);
        } catch (e) {
          logger.error(e);
        }
      }
    }
  }

  async updateSummonerData() {
    const { data } = await this.dbHelper.executeQuery("select * from summoners");

    if (data) {
      for (const summonerDB of data.rows) {
        const summonerRiot = await this.riotHelper.getSummonerByPuuid(summonerDB.puuid);
        const query = {
          text: "UPDATE summoners SET data = $1 WHERE puuid = $2",
          values: [summonerRiot, summonerDB.data.puuid],
        };
        this.dbHelper.executeQuery(query);
      }
    }
  }

  async insertSummoner(name: string) {
    let summoner = await this.riotHelper.getSummonerByName(name);
    const query = {
      text: "INSERT INTO summoners(data, puuid) VALUES($1, $2)",
      values: [summoner, summoner.puuid],
    };
    const { error } = await this.dbHelper.executeQuery(query);
    if (error) {
      logger.error(`Error from inserting Summoner into the DB ${error.details}`);
    }
  }

  //
  //Helper Stuff
  //
  getParticipantFromMatch(puuid: string, match: MatchDTO): Participant {
    for (const participant of match.info.participants) {
      if (participant.puuid === puuid) {
        return participant;
      }
    }
    throw new Error(`No summoner found in Match [${match.metadata.matchId}] with PUUID [${puuid}]`);
  }

  createGameInfo(match: MatchDTO) {
    const optionalInfoDto: Partial<Info> = match.info;
    delete optionalInfoDto.participants;
    return { ...optionalInfoDto, ...match.metadata };
  }

  async getDifferencesInDB() {
    const { data } = await this.dbHelper.executeQuery("select match_id from match_v5");
    const { data: data2 } = await this.dbHelper.executeQuery("select match_id from match_archive");
    const diff1 = differenceBy(data.rows, data2.rows, "match_id");

    // @ts-ignore
    const diff2 = differenceBy(data2.rows, data.rows, "match_id");
    console.log(diff1);
    console.log(diff2);
  }

  async insertAllSummoners() {
    let summoners = [
      "Baywack",
      "AngryBacteria",
      "Lonely Toplaner",
      "GLOMVE",
      "HMS fangirl",
      "hide on büschli",
      "viranyx",
      "Hide in the Dark",
      "Prequ",
      "pentaskill",
      "WhatThePlay",
      "Alraune22",
      "Theera3rd",
      "tresserhorn",
      "Gnerfedurf",
      "nolsterpolster",
      "UnifixingGoblin5",
      "Árexo",
      "bruhthefighter",
      "PoIlux",
      "Prequ1",
      "Aw3s0m3mag1c",
    ];

    summoners.forEach((sum) => {
      this.insertSummoner(sum).then();
    });
  }

  async fillMatchData() {
    for (let i = 0; i < 2000; i = i + 95) {
      logger.info(`INSERTING WITH I = ${i}`);
      await this.updateMatchData(i, 95);
    }
  }

  async fillMatchDataForSummoner(puuid: string) {
    for (let i = 0; i < 2000; i = i + 95) {
      logger.info(`INSERTING WITH I = ${i}`);
      await this.updateMatchDataForSummoner(puuid, i, 95);
    }
  }

  async intervalUpdate(iteration: number, intervalTime: number) {
    logger.info(`DATA BEING UPDATED [${iteration}]: ${new Date().toUTCString()}`);
    iteration++;
    if (iteration === 10) {
      logger.info(`UPDATING SUMMONER DATA: ${new Date().toUTCString()}`);
      task.updateSummonerData();
      iteration = 0;
      logger.info(`UPDATED SUMMONER DATA: ${new Date().toUTCString()}`);
    }
    await this.updateMatchData(0, 10);
    logger.info(`DATA UPDATED [${iteration}]: ${new Date().toUTCString()}`);
    setTimeout(() => this.intervalUpdate(iteration, intervalTime), intervalTime);
  }
}

const task = new MainTask();
task.intervalUpdate(0, 1000 * 60 * 60 * 2).then(() => {
  console.log("first iteration done");
});
