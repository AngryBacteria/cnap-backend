import express from "express";
import Express from "express";
import DBHelper from "../../../helpers/DBHelper";
import RiotHelper from "../../../helpers/RiotHelper";
import { asyncWrap } from "../../../helpers/GlobalFunctions";
import { logger } from "../../../boot/config";

const router = express.Router();
const baseUrl = "/match";
const dbHelper = DBHelper.getInstance();
const riotHelper = RiotHelper.getInstance();

//match_archive
/**
 * @swagger
 * /api/v1/match/archive:
 *   get:
 *     description: Endpoint for querying complete (All Participants) Match-V5 Objects
 *     responses:
 *       200:
 *         description: Array of a complete (All Participants) Match-V5 Objects
 *     parameters:
 *       - name: page
 *         in: query
 *         required: false
 *         type: string
 *         description: pagination (25 items per page)
 *       - name: queue
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot Queue ID (https://static.developer.riotgames.com/docs/lol/queues.json)
 *       - name: mode
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameMode ID (https://static.developer.riotgames.com/docs/lol/gameModes.json)
 *       - name: type
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameType ID (https://static.developer.riotgames.com/docs/lol/gameTypes.json)
 */
router.get(baseUrl + "/archive", async (req: Express.Request, res: Express.Response) => {
  //Query params
  const { limit, offset, queue, mode, type } = prepareQuery(req);

  //Query
  let query = "SELECT * FROM match_archive WHERE 1=1";
  if (queue) {
    query = query + ` AND data -> 'info' ->> 'queueId' = '${queue}'`;
  }
  if (mode) {
    query = query + ` AND data -> 'info'->> 'gameMode' = '${mode}'`;
  }
  if (type) {
    query = query + ` AND data -> 'info'->> 'gameType' = '${type}'`;
  }
  query = query + ` LIMIT ${limit} OFFSET ${offset}`;

  const { data, error } = await dbHelper.executeQuery(query);
  if (!error) {
    res.send(data.rows);
    logger.info(`Api-Request for Match Archive with Method: POSTGRES`);
  } else {
    res.status(500).send(error);
  }
});

/**
 * @swagger
 * /api/v1/match/archive/id/{id}:
 *   get:
 *     description: Endpoint for querying a complete (All Participants) Match-V5 Object by ID
 *     responses:
 *       200:
 *         description: complete (All Participants) Match-V5 Object
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         type: string
 *         description: ID of the Match (for example EUW1_5998862548)
 */
router.get(baseUrl + "/archive/id/:id", async (req: Express.Request, res: Express.Response) => {
  //redis
  const match_id = req.params.id;
  let match = await dbHelper.getObjectFromRedis(match_id);
  if (match) {
    res.send(match);
    logger.info(`Api-Request for Match [${match_id}] with Method: REDIS`);
    return;
  }

  //postgres
  const query = {
    name: "fetch_match_by_id",
    text: "SELECT * FROM match_archive WHERE match_id = $1",
    values: [match_id],
  };
  const { data } = await dbHelper.executeQuery(query);
  if (data?.rows.length) {
    res.send(data.rows[0]);
    logger.info(`Api-Request for Match [${match_id}] with Method: POSTGRES`);
    return;
  }

  //riot api
  const { data: riotData } = await asyncWrap(riotHelper.getMatch(match_id, false));
  if (riotData) {
    res.send(riotData);
    logger.info(`Api-Request for Match [${match_id}] with Method: RIOT-API`);
    return;
  }
  res.sendStatus(404);
});

//match_v5
/**
 * @swagger
 * /api/v1/match/participant/puuid/{puuid}:
 *   get:
 *     description: Endpoint for querying an incomplete (Only one Participant) Match-V5 Object by the puuid of a Summoner
 *     responses:
 *       200:
 *         description: incomplete (Only one Participant) Match-V5 Object
 *     parameters:
 *       - name: puuid
 *         in: path
 *         required: true
 *         type: string
 *         description: puuid of the Summoner. Only works with one Riot ApiKey
 *       - name: queue
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot Queue ID (https://static.developer.riotgames.com/docs/lol/queues.json)
 *       - name: mode
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameMode ID (https://static.developer.riotgames.com/docs/lol/gameModes.json)
 *       - name: type
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameType ID (https://static.developer.riotgames.com/docs/lol/gameTypes.json)
 */
router.get(baseUrl + "/participant/puuid/:puuid", async (req: Express.Request, res: Express.Response) => {
  //Query params
  const { limit, offset, queue, mode, type } = prepareQuery(req);
  const puuid = req.params.puuid;

  //Query
  let queryString = "SELECT * FROM match_v5 WHERE 1=1";
  if (queue) {
    queryString = queryString + ` AND data_match ->> 'queueId' = '${queue}'`;
  }
  if (mode) {
    queryString = queryString + ` AND data_match ->> 'gameMode' = '${mode}'`;
  }
  if (type) {
    queryString = queryString + ` AND data_match ->> 'gameType' = '${type}'`;
  }
  queryString = queryString + ` LIMIT ${limit} OFFSET ${offset}`;

  //postgres
  const { data, error } = await dbHelper.executeQuery(queryString);
  if (error) {
    res.status(500).send(error);
    return;
  }
  if (data?.rows.length) {
    res.send(data.rows[0]);
    logger.info(`Api-Request for Matches of Summoner [${puuid}] with Method: POSTGRES`);
    return;
  }
  res.sendStatus(404);
});

/**
 * @swagger
 * /api/v1/match/participant:
 *   get:
 *     description: Endpoint for querying incomplete (Only one Participant) Match-V5 Objects
 *     responses:
 *       200:
 *         description: Array of incomplete (Only one Participant) Match-V5 Objects
 *     parameters:
 *       - name: page
 *         in: query
 *         required: false
 *         type: string
 *         description: pagination (25 items per page)
 *       - name: queue
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot Queue ID (https://static.developer.riotgames.com/docs/lol/queues.json)
 *       - name: mode
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameMode ID (https://static.developer.riotgames.com/docs/lol/gameModes.json)
 *       - name: type
 *         in: query
 *         required: false
 *         type: string
 *         description: Riot GameType ID (https://static.developer.riotgames.com/docs/lol/gameTypes.json)
 */
router.get(baseUrl + "/participant", async (req: Express.Request, res: Express.Response) => {
  //Query params
  const { limit, offset } = prepareQuery(req);
  let queue = req.query.queue;
  let mode = req.query.mode;
  let type = req.query.type;

  //Query
  let query = "SELECT * FROM match_v5 WHERE 1=1";
  if (queue) {
    query = query + ` AND data_match ->> 'queueId' = '${queue}'`;
  }
  if (mode) {
    query = query + ` AND data_match ->> 'gameMode' = '${mode}'`;
  }
  if (type) {
    query = query + ` AND data_match ->> 'gameType' = '${type}'`;
  }
  query = query + ` LIMIT ${limit} OFFSET ${offset}`;

  const { data, error } = await dbHelper.executeQuery(query);
  if (!error) {
    res.send(data.rows);
    logger.info(`Api-Request for Match V5 with Method: POSTGRES`);
  } else {
    res.status(500).send(error);
  }
});

function prepareQuery(req: Express.Request) {
  let queue = req.query.queue;
  let mode = req.query.mode;
  let type = req.query.type;
  let page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const limit = 25;
  const offset = (page - 1) * limit;
  return { limit, offset, queue, mode, type };
}
export default router;
