import { MongoClient, ServerApiVersion } from "mongodb";
import { cache, logger, mongoURL, pg } from "../boot/config";
import { asyncWrap } from "./GlobalFunctions";
import { MatchArchiveDB, MatchV5DB, SummonerDB } from "../interfaces/DBInterfaces";

export default class DBHelper {
  private static instance: DBHelper;

  public mongoClient: MongoClient;

  constructor() {
    this.mongoClient = new MongoClient(mongoURL, {
      serverApi: {
        version: ServerApiVersion.v1,
        strict: true,
        deprecationErrors: true,
      },
    });
  }

  //TODO implement sorting!!
  public static getInstance(): DBHelper {
    if (!DBHelper.instance) {
      DBHelper.instance = new DBHelper();
    }
    return DBHelper.instance;
  }

  async getMatchArchive({
    id = "",
    queue = 0,
    mode = "",
    type = "",
    offset = 0,
    limit = 25,
  }): Promise<MatchArchiveDB[]> {
    try {
      await this.mongoClient.connect();
      logger.info("Getting MatchArchive with MongoDB");
      let filter: any = {};
      if (id) {
        filter["metadata.matchId"] = id;
      }
      if (queue) {
        filter["info.queueId"] = queue;
      }
      if (mode) {
        filter["info.gameMode"] = mode;
      }
      if (type) {
        filter["info.gameType"] = type;
      }

      const results = await this.mongoClient
        .db("cnap")
        .collection<MatchArchiveDB>("match_archive")
        .find(filter)
        .skip(offset)
        .limit(limit)
        .toArray();
      return results;
    } finally {
      await this.mongoClient.close();
    }
  }

  async getMatchesV5({ puuid = "", queue = 0, mode = "", type = "", offset = 0, limit = 25 }): Promise<MatchV5DB[]> {
    try {
      await this.mongoClient.connect();
      logger.info("Getting MatchesV5 with MongoDB");
      let filter: any = {};
      if (puuid) {
        filter["data_participant.puuid"] = puuid;
      }
      if (queue) {
        filter["data_match.queueId"] = queue;
      }
      if (mode) {
        filter["data_match.gameMode"] = mode;
      }
      if (type) {
        filter["data_match.gameType"] = type;
      }

      const results = await this.mongoClient
        .db("cnap")
        .collection<MatchV5DB>("match_v5")
        .find(filter)
        .skip(offset)
        .limit(limit)
        .toArray();
      return results;
    } finally {
      await this.mongoClient.close();
    }
  }

  async getSummoners({ name = "", puuid = "", skip = 0, limit = 25 }): Promise<SummonerDB[]> {
    try {
      await this.mongoClient.connect();
      logger.info("Getting Summoners with MongoDB");
      let filter: any = {};
      if (name) {
        filter["name"] = name;
      }
      if (puuid) {
        filter["puuid"] = puuid;
      }

      const results = await this.mongoClient
        .db("cnap")
        .collection<SummonerDB>("summoner")
        .find(filter)
        .skip(skip)
        .limit(limit)
        .toArray();
      return results;
    } finally {
      await this.mongoClient.close();
    }
  }

  /**
   * Function that executes a PostgreSQL query. It first fetches a client from the postgres pool.
   * If a client was able to be fetched it executes the query. If any errors occur it returns an error and no data.
   * If the query was successful it returns data and no error.
   * @param query SQL query that should be executed
   * @returns
   */
  async executeQuery(query: any) {
    const { data: client, error: clientError } = await asyncWrap(pg.connect());
    if (client) {
      const { data: data, error: queryError } = await asyncWrap(client.query(query));
      client.release(true);
      if (queryError) {
        logger.error(`Inserting into Postgres failed with error: ${queryError}`);
        return { data: null, error: queryError };
      }
      return { data: data, error: null };
    }
    logger.error(`Error creating pg client: ${clientError}`);
    return { data: null, error: clientError };
  }

  /**
   * Gets a Javascript Object from the redis database and parses it with JSON.parse()
   * @param key Unique Key for the redis database
   * @returns Response from redis. Either null or the Object
   */
  async getObjectFromRedis(key: string): Promise<any> {
    try {
      const obj = await cache.get(key);
      if (obj) {
        return JSON.parse(obj);
      } else return null;
    } catch (e) {
      logger.error(`Error getting item [${key}] from cache: ${e}`);
      return null;
    }
  }

  /**
   * Method to set an Object in the Redis Database. The object gets turned into a string with JSON.stringify
   * @param key  Unique Key for the redis database
   * @param value Javascript Object
   * @param expiry Number of seconds the value should stay in the database. Standard expiry is infinite
   */
  async setObjectInRedis(key: string, value: any, expiry: number = -1) {
    try {
      expiry === -1
        ? await cache.set(key, JSON.stringify(value))
        : await cache.set(key, JSON.stringify(value), { EX: expiry });
    } catch (e) {
      logger.error(`Error setting item [${key}] from cache: ${e}`);
    }
  }

  /**
   * Gets an element from the redis database
   * @param key Unique Key for the redis database
   * @returns Response from redis. Either null or the data
   */
  async getElementFromRedis(key: string) {
    try {
      return await cache.get(key);
    } catch (e) {
      logger.error(`Error getting item [${key}] from cache: ${e}`);
      return null;
    }
  }

  /**
   * Method to set an item in the Redis Database
   * @param key  Unique Key for the redis database
   * @param value Item to be saved in the database
   * @param expiry Number of seconds the value should stay in the database. Standard expiry is infinite
   */
  async setElementInRedis(key: string, value: any, expiry: number = -1) {
    try {
      expiry === -1 ? await cache.set(key, value) : await cache.set(key, value, { EX: expiry });
    } catch (e) {
      logger.error(`Error setting item [${key}] from cache: ${e}`);
    }
  }
}
