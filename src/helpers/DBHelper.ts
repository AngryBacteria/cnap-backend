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

  async getObjectFromRedis(key: string): Promise<any> {
    try {
      await cache.connect();
      return await cache.get(key);
    } catch (e) {
      logger.error(`Error getting item [${key}] from cache: ${e}`);
      return null;
    } finally {
      await cache.disconnect();
    }
  }

  async setObjectInRedis(key: string, value: any) {
    try {
      await cache.connect();
      await cache.set(key, value);
    } catch (e) {
      logger.error(`Error setting item [${key}] from cache: ${e}`);
    } finally {
      await cache.disconnect();
    }
  }
}
