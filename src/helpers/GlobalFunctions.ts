import Express from "express";

/**
 * Extracts typical query parameters from an Express Request object
 */
export function prepareQuery(req: Express.Request) {
  const queue = req.query.queue;
  const mode = req.query.mode;
  const type = req.query.type;
  const page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const limit = 25;
  const offset = (page - 1) * limit;
  return { limit, offset, queue, mode, type };
}
