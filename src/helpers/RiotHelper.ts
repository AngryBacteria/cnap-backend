import { logger } from '../config/logging.js';
import axios from 'axios';
import axiosRetry from 'axios-retry';
import {
  AccountDto,
  ChampionMasteryDTO,
  MatchV5DTO,
  SummonerDTO,
} from '../interfaces/CustomInterfaces.js';
import { limiter } from '../config/limiting.js';
import { config } from 'dotenv';

export default class RiotHelper {
  private static instance: RiotHelper;
  private readonly riotApiKey: string;

  constructor() {
    axiosRetry(axios, {
      retries: 3,
      retryDelay: axiosRetry.exponentialDelay,
      onRetry: (retryCount) => {
        logger.warn(`Axios request failed. Retry attempt: ${retryCount}`);
      },
    });

    config();
    if (process.env.RIOT_API_KEY) {
      this.riotApiKey = process.env.RIOT_API_KEY;
    } else {
      throw new Error('No Riot API Key found in Environment');
    }
  }

  public static getInstance() {
    if (!RiotHelper.instance) {
      RiotHelper.instance = new RiotHelper();
    }
    return RiotHelper.instance;
  }

  /**
   * Function to fetch a specific match from the RiotAPI. If applicable it uses
   * the Redis Cache. Uses Rate Limiting and Axios Retries
   */
  async getMatchRiot(matchId: string) {
    return await limiter.schedule(async () => {
      try {
        logger.info(`Fetching Match [${matchId}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as MatchV5DTO;
      } catch (e) {
        logger.error(
          `Error while fetching Match [${matchId}] with Riot-API: ${e}`,
        );
        return undefined;
      }
    });
  }

  /**
   * Function to fetch a MatchList for a specific summoner from the RiotAPI.
   * Uses Rate Limiting and Axios Retries
   */
  async getMatchListRiot(summoner: SummonerDTO, count = 100, offset = 0) {
    return await limiter.schedule(async () => {
      try {
        logger.info(`Fetching Matchlist [${summoner.name}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/${summoner.puuid}/ids?start=${offset}&count=${count}&api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as string[];
      } catch (e) {
        logger.error(
          `Error while fetching Matchlist of Summoner [${summoner.name}] with Riot-API: ${e}`,
        );
        return [];
      }
    });
  }

  /**
   * Fetches a Summoner by PUUID from the RiotAPI
   */
  async getSummonerByPuuidRiot(puuid: string) {
    return await limiter.schedule(async () => {
      try {
        logger.info(`Fetching Summoner [${puuid}] with Riot-API`);
        const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as SummonerDTO;
      } catch (e) {
        logger.error(
          `Error while fetching Summoner [${puuid}] with Riot-API: ${e}`,
        );
        return undefined;
      }
    });
  }

  async getAccountByTag(name: string, tag: string) {
    try {
      tag = tag.replaceAll('#', '');
      return await limiter.schedule(async () => {
        logger.info(`Fetching Account [${name} - ${tag}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${name}/${tag}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as AccountDto;
      });
    } catch (error) {
      logger.error(
        `Error while fetching Account [${name} - ${tag}] with Riot-API: ${error}`,
      );
      return undefined;
    }
  }

  /**
   * New way of fetching a Summoner by AccountTag from the RiotAPI
   */
  async getSummonerByAccountTag(name: string, tag: string) {
    const account = await this.getAccountByTag(name, tag);
    if (account) {
      return await this.getSummonerByPuuidRiot(account.puuid);
    } else {
      return undefined;
    }
  }

  async getChampionMasteryByPuuidRiot(puuid: string) {
    return await limiter.schedule(async () => {
      try {
        logger.info(
          `Fetching Champion Mastery for Summoner [${puuid}] with Riot-API`,
        );
        const url = `https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/${puuid}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as ChampionMasteryDTO[];
      } catch (e) {
        logger.error(
          `Fetching Champion Mastery for Summoner [${puuid}] with Riot-API: ${e}`,
        );
        return undefined;
      }
    });
  }
}
