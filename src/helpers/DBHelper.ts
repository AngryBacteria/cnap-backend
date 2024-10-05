import { MongoClient, ServerApiVersion } from 'mongodb';
import { logger } from '../config/logging.js';
import { MatchV5DTO, SummonerDTO } from '../interfaces/CustomInterfaces.js';
import { config } from 'dotenv';

//TODO: implement on death disconnect

interface DynamicFilter {
  [key: string]: string | number;
}

export default class DBHelper {
  private static instance: DBHelper;

  public mongoClient: MongoClient;

  constructor() {
    config();
    if (process.env.MONGODB_CONNECTION_STRING) {
      this.mongoClient = new MongoClient(
        process.env.MONGODB_CONNECTION_STRING,
        {
          serverApi: {
            version: ServerApiVersion.v1,
            strict: true,
            deprecationErrors: true,
          },
        },
      );
    } else {
      throw new Error('No MongoDB Connection String found in Environment');
    }
  }

  //TODO implement sorting!!
  //TODO: implement error handling
  //TODO implement more env variables via docker
  //TODO: implement on death disconnect
  //TODO: better logging
  public static getInstance() {
    if (!DBHelper.instance) {
      DBHelper.instance = new DBHelper();
    }
    return DBHelper.instance;
  }

  async connect() {
    this.mongoClient = await this.mongoClient.connect();
    logger.info('Connected to MongoDB');
    return true;
  }

  async disconnect() {
    await this.mongoClient.close();
    logger.info('Disconnected from MongoDB');
    return true;
  }

  /**
   * Retrieves the IDs that do not exist in the MongoDB collection `match_v5` from a given array of IDs.
   *
   * @param ids - An array of match_v5 IDs to check against the database.
   * @returns A promise that resolves to an array of non-existing match IDs.
   */
  async getNonExistingMatchIds(ids: string[]) {
    try {
      if (ids.length === 0) {
        return [];
      }
      const db = this.mongoClient.db('cnap');
      const collection = db.collection<MatchV5DTO>('match_v5');

      const existingIds = await collection
        .find(
          { 'metadata.matchId': { $in: ids } },
          { projection: { 'metadata.matchId': 1 } },
        )
        .toArray();

      const existingIdsSet = new Set(
        existingIds.map((match) => match.metadata.matchId),
      );
      const nonExistingIds = ids.filter((id) => !existingIdsSet.has(id));
      logger.info(
        `${ids.length - nonExistingIds.length} of ${
          ids.length
        } Matches were already present in the database`,
      );
      return nonExistingIds;
    } catch (error) {
      logger.log('Could not check for existing match ids: ', error);
      throw new Error('Could not check for existing match ids');
    }
  }

  /**
   * Updates or inserts match data in the MongoDB collection `match_v5`.
   * Utilizes bulk write operations for efficiency.
   *
   * @param matches - An array of match data transfer objects to be upserted.
   * @returns A promise that resolves when the operation is complete.
   */
  async updateMatches(matches: MatchV5DTO[]) {
    try {
      const db = this.mongoClient.db('cnap');
      const collection = db.collection<MatchV5DTO>('match_v5');
      const bulkOps = matches.map((match) => ({
        updateOne: {
          filter: { 'metadata.matchId': match.metadata.matchId },
          update: { $set: match },
          upsert: true,
        },
      }));
      const result = await collection.bulkWrite(bulkOps);
      logger.info(`Updated ${result.upsertedCount} Match data`);
      return true;
    } catch (error) {
      logger.error('Error uploading matches to MongoDB: ', error);
      return false;
    }
  }

  async getMatchesV5({
    id = '',
    queue = 0,
    mode = '',
    type = '',
    offset = 0,
    limit = 25,
  }) {
    try {
      const filter: DynamicFilter = {};
      if (id) {
        filter['metadata.matchId'] = id;
      }
      if (queue) {
        filter['info.queueId'] = queue;
      }
      if (mode) {
        filter['info.gameMode'] = mode;
      }
      if (type) {
        filter['info.gameType'] = type;
      }
      logger.info(`Getting Match data from DB [${filter}]`);

      return await this.mongoClient
        .db('cnap')
        .collection<MatchV5DTO>('match_v5')
        .find(filter)
        .skip(offset)
        .limit(limit)
        .toArray();
    } catch (error) {
      logger.error('Error getting MatchArchive with MongoDB: ', error);
      return [];
    }
  }

  /**
   * Fetches the match history of a summoner from the MongoDB collection `match_v5`.
   * @param puuid puuid of the summoner
   * @param limit number of matches to fetch
   * @param skip number of matches to skip
   * @returns A promise that resolves to an array of reduced match data objects. They only include
   * the summoner data and the metadata of the match.
   */
  async getSummonerMatchHistory(
    puuid: string,
    limit: number = 20,
    skip: number = 0,
  ) {
    try {
      const agg = [
        {
          $match: {
            'metadata.participants': {
              $all: [puuid],
            },
          },
        },
        {
          $sort: {
            'info.gameCreation': -1,
          },
        },
        {
          $skip: skip,
        },
        {
          $limit: limit,
        },
        {
          $set: {
            'info.participants': {
              $filter: {
                input: '$info.participants',
                as: 'participant',
                cond: {
                  $eq: ['$$participant.puuid', puuid],
                },
              },
            },
          },
        },
      ];
      const coll = this.mongoClient
        .db('cnap')
        .collection<MatchV5DTO>('match_v5');
      const cursor = coll.aggregate(agg);
      return await cursor.toArray();
    } catch (error) {
      logger.error(
        `Error getting MatchArchive for Summoner [${puuid}] with MongoDB: ${error}`,
      );
      return [];
    }
  }

  async getSummoners({ name = '', puuid = '', skip = 0, limit = 25 }) {
    try {
      const filter: DynamicFilter = {};
      if (name) {
        filter['name'] = name;
      }
      if (puuid) {
        filter['puuid'] = puuid;
      }
      logger.info(
        `Getting Summoner data from DB [${filter?.puuid}, ${filter?.name}]`,
      );

      return await this.mongoClient
        .db('cnap')
        .collection<SummonerDTO>('summoner')
        .find(filter)
        .skip(skip)
        .limit(limit)
        .toArray();
    } catch (error) {
      logger.error('Error getting Summoners with MongoDB');
      return [];
    }
  }

  /**
   * Updates or inserts summoner data in the MongoDB collection `summoner`.
   * Utilizes bulk write operations for efficiency.
   *
   * @param summoners - An array of summoner data transfer objects to be upserted.
   * @returns A promise that resolves when the operation is complete.
   */
  async updateSummoners(summoners: SummonerDTO[]) {
    try {
      const db = this.mongoClient.db('cnap');
      const collection = db.collection<SummonerDTO>('summoner');

      const bulkOps = summoners.map((summoner) => ({
        updateOne: {
          filter: { puuid: summoner.puuid },
          update: { $set: summoner },
          upsert: true,
        },
      }));

      const result = await collection.bulkWrite(bulkOps);
      logger.info(`Updated ${result.upsertedCount} summoner data`);
      return true;
    } catch (error) {
      logger.error('Error uploading summoners to MongoDB: ', error);
      return false;
    }
  }
}
