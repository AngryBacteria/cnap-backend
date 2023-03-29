import Express from "express";

export async function asyncWrap(promise: Promise<any>): Promise<{ data: any; error: any }> {
  try {
    const data = await promise;
    return { data: data, error: null };
  } catch (error) {
    return { data: null, error: error };
  }
}

export function prepareQuery(req: Express.Request) {
  let queue = req.query.queue;
  let mode = req.query.mode;
  let type = req.query.type;
  let page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const limit = 25;
  const offset = (page - 1) * limit;
  return { limit, offset, queue, mode, type };
}
