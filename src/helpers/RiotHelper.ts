import { logger } from '../config/logging.js';
import axios from 'axios';
import axiosRetry from 'axios-retry';
import {
  AccountDto,
  MatchV5DTO,
  SummonerDTO,
} from '../interfaces/CustomInterfaces.js';
import { limiter } from '../config/limiting.js';
import { config } from 'dotenv';

export default class RiotHelper {
  private static instance: RiotHelper;
  private riotApiKey: string;

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
  async getMatchRiot(matchId: string): Promise<MatchV5DTO | undefined> {
    return limiter.schedule(async () => {
      try {
        logger.info(`Fetching Match [${matchId}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/lol/match/v5/matches/${matchId}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        const match = axiosResponse.data;
        return match;
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
  async getMatchListRiot(
    summoner: SummonerDTO,
    count = 100,
    offset = 0,
  ): Promise<string[]> {
    return limiter.schedule(async () => {
      try {
        logger.info(`Fetching Matchlist [${summoner.name}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/${summoner.puuid}/ids?start=${offset}&count=${count}&api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data;
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
  async getSummonerByPuuidRiot(
    puuid: string,
  ): Promise<SummonerDTO | undefined> {
    return limiter.schedule(async () => {
      try {
        logger.info(`Fetching Summoner [${puuid}] with Riot-API`);
        const url = `https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/${puuid}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data;
      } catch (e) {
        logger.error(
          `Error while fetching Summoner [${puuid}] with Riot-API: ${e}`,
        );
        return undefined;
      }
    });
  }

  async getAccountByTag(
    name: string,
    tag: string,
  ): Promise<AccountDto | undefined> {
    try {
      tag = tag.replaceAll('#', '');
      const account: AccountDto = await limiter.schedule(async () => {
        logger.info(`Fetching Account [${name} - ${tag}] with Riot-API`);
        const url = `https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/${name}/${tag}?api_key=${this.riotApiKey}`;
        const axiosResponse = await axios.get(url);
        return axiosResponse.data as AccountDto;
      });
      return account;
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
  async getSummonerByAccountTag(
    name: string,
    tag: string,
  ): Promise<SummonerDTO | undefined> {
    const account = await this.getAccountByTag(name, tag);
    const summoner = await this.getSummonerByPuuidRiot(account.puuid);
    return summoner;
  }
}
