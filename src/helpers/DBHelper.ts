import { MongoClient, ServerApiVersion } from 'mongodb';
import { pgClient } from '../boot/config.js';
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
  public static getInstance(): DBHelper {
    if (!DBHelper.instance) {
      DBHelper.instance = new DBHelper();
    }
    return DBHelper.instance;
  }

  async connect() {
    this.mongoClient = await this.mongoClient.connect();
    logger.info('Connected to MongoDB');
  }

  async disconnect() {
    await this.mongoClient.close();
    logger.info('Disconnected from MongoDB');
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
    } catch (error) {
      logger.error('Error uploading matches to MongoDB: ', error);
    }
  }

  async getMatchesV5({
    id = '',
    queue = 0,
    mode = '',
    type = '',
    offset = 0,
    limit = 25,
  }): Promise<MatchV5DTO[]> {
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

      const results = await this.mongoClient
        .db('cnap')
        .collection<MatchV5DTO>('match_v5')
        .find(filter)
        .skip(offset)
        .limit(limit)
        .toArray();
      return results;
    } catch (error) {
      logger.error('Error getting MatchArchive with MongoDB: ', error);
      return [];
    }
  }

  /**
   * Fetches the match history of a summoner from the MongoDB collection `match_v5`.
   * @param puuid puuid of the summoner
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
      const result = await cursor.toArray();

      return result;
    } catch (error) {
      logger.error(
        `Error getting MatchArchive for Summoner [${puuid}] with MongoDB: ${error}`,
      );
      return [];
    }
  }

  async getSummoners({
    name = '',
    puuid = '',
    skip = 0,
    limit = 25,
  }): Promise<SummonerDTO[]> {
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

      const results = await this.mongoClient
        .db('cnap')
        .collection<SummonerDTO>('summoner')
        .find(filter)
        .skip(skip)
        .limit(limit)
        .toArray();
      return results;
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
    } catch (error) {
      logger.error('Error uploading summoners to MongoDB: ', error);
    }
  }

  /**
   * Function that executes a PostgreSQL query. It first fetches a client from the postgres pool.
   * If a client was able to be fetched it executes the query. If any errors occur it returns an error and no data.
   * If the query was successful it returns data and no error.
   * @param query SQL query that should be executed
   * @returns
   */
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async executeQuery(query: any) {
    const { data: client, error: clientError } = await this.asyncWrap(
      pgClient.connect(),
    );
    if (client) {
      const { data: data, error: queryError } = await this.asyncWrap(
        client.query(query),
      );
      client.release(true);
      if (queryError) {
        logger.error(
          `Inserting into Postgres failed with error: ${queryError}`,
        );
        return { data: null, error: queryError };
      }
      return { data: data, error: null };
    }
    logger.error(`Error creating pgClient client: ${clientError}`);
    return { data: null, error: clientError };
  }
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  async asyncWrap(promise: Promise<any>): Promise<{ data: any; error: any }> {
    try {
      const data = await promise;
      return { data: data, error: null };
    } catch (error) {
      return { data: null, error: error };
    }
  }
}
