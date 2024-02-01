import { logger } from "../../config/logging";
import axios from "axios";
import axiosRetry from "axios-retry";
import DBHelper from "../../helpers/DBHelper";
import RiotHelper from "../../helpers/RiotHelper";
import { MatchV5DTO, SummonerDTO } from "../../interfaces/CustomInterfaces";

export default class MainTask {
  dbHelper: DBHelper;
  riotHelper: RiotHelper;

  constructor() {
    this.dbHelper = DBHelper.getInstance();
    this.riotHelper = RiotHelper.getInstance();
    axiosRetry(axios, {
      retries: 4, // number of retries
      retryDelay: (retryCount) => {
        logger.warn(`retry attempt: ${retryCount}`);
        return retryCount * 2000; // time interval between retries
      },
    });
  }

  //
  //DB Stuff
  //
  async connectToDb() {
    await this.dbHelper.connect();
  }
  /**
   * For all of a single summoner it inserts all new games into the database.
   * If the match already exists (recognized by match_id_puuid or match_id) it does not insert it
   * @param puuid puuid of the summoner. Leave empty to update all summoners
   * @param offset where to start
   * @param count amount of matches to fetch
   */
  async updateMatchData(puuid: string = "", offset: number = 0, count: number = 69) {
    const summonerQuery = puuid ? { puuid: puuid } : {};
    const existingSummoners = await this.dbHelper.getSummoners(summonerQuery);
    if (!existingSummoners || existingSummoners.length === 0) {
      const errorMessage = puuid
        ? `No Summoner [${puuid}] data available to update match history. Stopping the loop`
        : "No Summoner data available to update match history. Stopping the loop";
      logger.error(errorMessage);
      return;
    }
    if (existingSummoners) {
      for (const summoner of existingSummoners) {
        try {
          const riotMatchIds = await this.riotHelper.getMatchListRiot(summoner, count, offset);
          const filteredIds = await this.dbHelper.getNonExistingMatchIds(riotMatchIds);
          if (!filteredIds || filteredIds.length === 0) {
            logger.info(`No new matches for summoner [${summoner.name}]`);
          } else {
            const matchData: MatchV5DTO[] = [];
            for (const matchId of filteredIds) {
              try {
                const match = await this.riotHelper.getMatchRiot(matchId);
                matchData.push(match);
              } catch (e) {
                logger.error(`Request for summoner [${summoner.name}] failed with error, will continue the loop: ${e}`);
              }
            }
            await this.dbHelper.updateMatches(matchData);
          }
        } catch (e) {
          logger.error(e);
        }
      }
    }
  }

  /**
   * For each summoner in the database it updates the data by fetching new data from the riot api
   * and replacing the existing db data
   */
  async updateSummonerData() {
    const existingSummoners = await this.dbHelper.getSummoners({});
    if (existingSummoners) {
      const newSummoners: SummonerDTO[] = [];
      for (const summoner of existingSummoners) {
        try {
          const summonerRiot = await this.riotHelper.getSummonerByPuuidRiot(summoner.puuid);
          newSummoners.push(summonerRiot);
        } catch (error) {
          logger.error(`No Summoner [${summoner.name}] data available to update to insert. Continuing the loop`);
        }
      }
      this.dbHelper.updateSummoners(newSummoners);
    }
  }

  /**
   * Inserts a summoner into the database. First it searches the summoner in the riot api
   */
  async insertSummoner(name: string) {
    try {
      const riotSummoner = await this.riotHelper.getSummonerByNameRiot(name);
      this.dbHelper.updateSummoners([riotSummoner]);
    } catch (error) {
      logger.error(`No Summoner [${name}] data available to insert`);
    }
  }

  //
  //Helper Stuff
  //
  /**
   * Function to add all matches (max of 2000) of all summoners or a single summoner
   * @param puuid puuid of the summoner. Leave empty to update all summoners
   */
  async fillMatchData(puuid: string = "") {
    for (let i = 0; i < 2000; i = i + 95) {
      logger.info(`INSERTING WITH I = ${i}`);
      await this.updateMatchData(puuid, i, 95);
    }
  }

  /**
   * Function to update the data in a fixed interval
   * @param intervalTime Time in milliseconds to wait for the next iteration
   */
  async intervalUpdate(iteration: number, intervalTime: number) {
    logger.info(`UPDATING MATCH DATA [${iteration}]: ${new Date().toUTCString()}`);
    iteration++;
    // Update summoner data every 10 iterations
    if (iteration === 10) {
      logger.info(`UPDATING SUMMONER DATA: ${new Date().toUTCString()}`);
      await this.updateSummonerData();
      iteration = 0;
      logger.info(`UPDATED SUMMONER DATA: ${new Date().toUTCString()}`);
    }
    await this.updateMatchData("", 0, 50);
    logger.info(`UPDATED MATCH DATA [${iteration}]: ${new Date().toUTCString()}`);
    setTimeout(() => this.intervalUpdate(iteration, intervalTime), intervalTime);
  }
}
