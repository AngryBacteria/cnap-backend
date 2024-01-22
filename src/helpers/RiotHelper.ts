import { MatchDTO } from "../interfaces/MatchInterfaces";
import { SummonerDB, SummonerData } from "../interfaces/CustomInterfaces";
import { backgroundLimiter1, backgroundLimiter2, logger, riotApiKey } from "../boot/config";
import axios from "axios";
import axiosRetry from "axios-retry";
import DBHelper from "./DBHelper";
import { TimelineDTO } from "../interfaces/TimelineInterfaces";

export default class RiotHelper {
  private static instance: RiotHelper;
  dbHelper: DBHelper;

  constructor() {
    this.dbHelper = DBHelper.getInstance();
    axiosRetry(axios, {
      retries: 3, // number of retries
      retryDelay: (retryCount) => {
        logger.warn(`retry attempt: ${retryCount}`);
        return retryCount * 2000; // time interval between retries
      },
    });
  }

  public static getInstance(): RiotHelper {
    if (!RiotHelper.instance) {
      RiotHelper.instance = new RiotHelper();
    }

    return RiotHelper.instance;
  }

  /**
   * Function to fetch a specific match from the RiotAPI. If applicable it uses
   * the Redis Cache. Uses Rate Limiting and Axios Retries
   */
  async getMatch(matchId: string, useCache = true): Promise<MatchDTO> {
    try {
      if (useCache) {
        const match = await this.dbHelper.getObjectFromRedis(matchId);
        if (match) {
          logger.info(`Match [${matchId}] found in cache`);
          return match;
        }
      }
      logger.info(`Fetching Match with Riot-API [${matchId}]`);
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const url = `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}?api_key=${riotApiKey}`;
      const axiosResponse = await axios.get(url);
      const match = axiosResponse.data;
      await this.dbHelper.setObjectInRedis(matchId, match);
      return match;
    } catch (e) {
      throw new Error(`Error while getting the data for match [${matchId}] because: + ${e}`);
    }
  }

  /**
   * Function to fetch a MatchList for a specific summoner from the RiotAPI.
   * Uses Rate Limiting and Axios Retries
   */
  async getMatchList(summoner: SummonerDB, count = 100, offset = 0): Promise<string[]> {
    try {
      logger.info(`Fetching Matchlist with Riot-API for [${summoner.data.name}]`);
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const url = `https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/${summoner.data.puuid}/ids?start=${offset}&count=${count}&api_key=${riotApiKey}`;
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e: any) {
      logger.error(`Request for summoner [${summoner.data.name}] failed with error: ${e}`);
    }
    return [];
  }

  /**
   * Function to fetch a TimeLine for a specific match from the RiotAPI. If applicable it uses
   * the Redis Cache. Uses Rate Limiting and Axios Retries
   */
  async getTimeLine(matchId: string, useCache = true): Promise<TimelineDTO> {
    try {
      if (useCache) {
        const timeline = await this.dbHelper.getObjectFromRedis("timeline_" + matchId);
        if (timeline) {
          logger.info(`Timeline [${matchId}] found in cache`);
          return timeline;
        }
      }

      logger.info(`Fetching Timeline with Riot-API for [${matchId}]`);
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const url = `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}/timeline?api_key=${riotApiKey}`;
      const axiosResponse = await axios.get(url);
      await this.dbHelper.setObjectInRedis("timeline_" + matchId, axiosResponse.data, 60 * 60);
      return axiosResponse.data;
    } catch (e: any) {
      throw new Error(`Request for TimeLine [${matchId}] failed with error: ${e}`);
    }
  }

  /**
   * Fetches a Summoner by name from the RiotAPI
   */
  async getSummonerByName(name: string): Promise<SummonerData> {
    try {
      logger.info(`Fetching Summoner with Riot-API by name [${name}]`);
      const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/${name}?api_key=${riotApiKey}`;
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e) {
      throw new Error(`Summoner with NAME [${name}] not found: ${e}`);
    }
  }

  /**
   * Fetches a Summoner by PUUID from the RiotAPI
   */
  async getSummonerByPuuid(puuid: string): Promise<SummonerData> {
    try {
      logger.info(`Fetching Summoner with Riot-API by puuid [${puuid}]`);
      const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}?api_key=${riotApiKey}`;
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e) {
      throw new Error(`Summoner with PUUID [${puuid}] not found: ${e}`);
    }
  }
}
