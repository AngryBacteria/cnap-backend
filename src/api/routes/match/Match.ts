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
 *     tags:
 *      - match
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
  const result = await dbHelper.getMatchArchive({
    limit: limit,
    offset: offset,
    queue: Number(queue as string),
    mode: mode as string,
    type: type as string,
  });
  logger.info(`Api-Request for Archive-Matches with Method: MongoDB`);
  return res.send(result);
});

/**
 * @swagger
 * /api/v1/match/archive/id/{id}:
 *   get:
 *     description: Endpoint for querying a complete (All Participants) Match-V5 Object by ID
 *     tags:
 *      - match
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
  const match_id = req.params.id;
  //DB
  const results = await dbHelper.getMatchArchive({
    id: match_id,
  });
  if (results.length >= 1 && results[0]) {
    logger.info(`Api-Request for Match [${match_id}] with Method: MongoDB`);
    res.send(results[0]);
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
 *     tags:
 *      - match
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

  const results = await dbHelper.getMatchesV5({
    puuid: puuid,
    limit: limit,
    offset: offset,
    queue: Number(queue),
    mode: mode as string,
    type: type as string,
  });

  if (results.length >= 1 && results[0]) {
    logger.info(`Api-Request for Matches of Summoner [${puuid}] with Method: MongoDB`);
    res.send(results[0]);
    return;
  }
  res.sendStatus(404);
});

/**
 * @swagger
 * /api/v1/match/participant:
 *   get:
 *     description: Endpoint for querying incomplete (Only one Participant) Match-V5 Objects
 *     tags:
 *      - match
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
  const { limit, offset, queue, mode, type } = prepareQuery(req);

  const results = await dbHelper.getMatchesV5({
    limit: limit,
    offset: offset,
    queue: Number(queue),
    mode: mode as string,
    type: type as string,
  });

  if (results.length >= 1) {
    logger.info(`Api-Request for Participant-Matches with Method: MongoDB`);
    res.send(results);
    return;
  }
  res.sendStatus(404);
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
