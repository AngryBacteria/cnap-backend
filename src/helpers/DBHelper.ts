import { cache, logger, pg } from "../boot/config";
import { asyncWrap } from "./GlobalFunctions";

export default class DBHelper {
  private static instance: DBHelper;

  constructor() {}

  public static getInstance(): DBHelper {
    if (!DBHelper.instance) {
      DBHelper.instance = new DBHelper();
    }
    return DBHelper.instance;
  }

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
