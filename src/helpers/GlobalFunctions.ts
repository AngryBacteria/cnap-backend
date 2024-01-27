import Express from "express";
import { logger } from "../boot/config";

/**
 * Wrapper function for any sort of async promise. Works by executing the promise
 * and then either returning data and no error or no data and an error.
 * Makes the code far more readable as no try / catch blocks are needed anymore
 */
export async function asyncWrap(promise: Promise<any>): Promise<{ data: any; error: any }> {
  try {
    const data = await promise;
    return { data: data, error: null };
  } catch (error) {
    logger.error("error in asyncwrap: ", error);
    return { data: null, error: error };
  }
}

export function prepareQuery(req: Express.Request) {
  const queue = req.query.queue;
  const mode = req.query.mode;
  const type = req.query.type;
  const page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const limit = 25;
  const offset = (page - 1) * limit;
  return { limit, offset, queue, mode, type };
}
