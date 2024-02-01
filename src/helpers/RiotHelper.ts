import { logger } from "../config/logging";
import axios from "axios";
import axiosRetry from "axios-retry";
import { MatchV5DTO, SummonerDTO } from "../interfaces/CustomInterfaces";
import { backgroundLimiter1, backgroundLimiter2 } from "../config/limiting";
import { config } from "dotenv";

export default class RiotHelper {
  private static instance: RiotHelper;
  private riotApiKey: string;

  constructor() {
    axiosRetry(axios, {
      retries: 3, // number of retries
      retryDelay: (retryCount) => {
        logger.warn(`retry attempt: ${retryCount}`);
        return retryCount * 2000; // time interval between retries
      },
    });

    config();
    if (process.env.RIOT_API_KEY) {
      this.riotApiKey = process.env.RIOT_API_KEY;
    } else {
      throw new Error("No Riot API Key found in Environment");
    }
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
  async getMatchRiot(matchId: string): Promise<MatchV5DTO> {
    try {
      logger.info(`Fetching Match [${matchId}] with Riot-API`);
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const url = `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}?api_key=${this.riotApiKey}`;
      const axiosResponse = await axios.get(url);
      const match = axiosResponse.data;
      return match;
    } catch (e) {
      throw new Error(`Error while fetching Match [${matchId}] with Riot-API: ${e}`);
    }
  }

  /**
   * Function to fetch a MatchList for a specific summoner from the RiotAPI.
   * Uses Rate Limiting and Axios Retries
   */
  async getMatchListRiot(summoner: SummonerDTO, count = 100, offset = 0): Promise<string[]> {
    try {
      logger.info(`Fetching Matchlist [${summoner.name}] with Riot-API`);
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const url = `https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/${summoner.puuid}/ids?start=${offset}&count=${count}&api_key=${this.riotApiKey}`;
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e) {
      logger.error(`Error while fetching Matchlist of Summoner [${summoner.name}] with Riot-API: ${e}`);
    }
    return [];
  }

  /**
   * Fetches a Summoner by name from the RiotAPI
   */
  async getSummonerByNameRiot(name: string): Promise<SummonerDTO> {
    try {
      logger.info(`Fetching Summoner [${name}] with Riot-API`);
      const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/${name}?api_key=${this.riotApiKey}`;
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e) {
      throw new Error(`Error while fetching Summoner [${name}] with Riot-API: ${e}`);
    }
  }

  /**
   * Fetches a Summoner by PUUID from the RiotAPI
   */
  async getSummonerByPuuidRiot(puuid: string): Promise<SummonerDTO> {
    try {
      logger.info(`Fetching Summoner [${puuid}] with Riot-API`);
      const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}?api_key=${this.riotApiKey}`;
      await backgroundLimiter1.removeTokens(1);
      await backgroundLimiter2.removeTokens(1);
      const axiosResponse = await axios.get(url);
      return axiosResponse.data;
    } catch (e) {
      throw new Error(`Error while fetching Summoner [${puuid}] with Riot-API: ${e}`);
    }
  }
}
