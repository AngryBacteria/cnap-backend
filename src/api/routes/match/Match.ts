import express from "express";
import Express from "express";
import DBHelper from "../../../helpers/DBHelper";
import RiotHelper from "../../../helpers/RiotHelper";
import { logger } from "../../../config/logging";

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
  const result = await dbHelper.getMatchesV5({
    limit: limit,
    offset: offset,
    queue: Number(queue as string),
    mode: mode as string,
    type: type as string,
  });
  logger.info(`Api-Request for Archive-Matches with Method: MongoDB`);
  if (result.length >= 1) {
    return res.send(result);
  } else {
    res.sendStatus(404);
  }
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
  const results = await dbHelper.getMatchesV5({
    id: match_id,
  });
  if (results.length >= 1 && results[0]) {
    logger.info(`Api-Request for Match [${match_id}] with Method: MongoDB`);
    res.send(results[0]);
    return;
  }

  //riot api
  try {
    const riotMatch = await riotHelper.getMatchRiot(match_id);
    if (riotMatch) {
      res.send(riotMatch);
      logger.info(`Api-Request for Match [${match_id}] with Method: RIOT-API`);
      return;
    }
  } catch (error) {
    res.sendStatus(404);
  }
});

function prepareQuery(req: Express.Request) {
  const queue = req.query.queue;
  const mode = req.query.mode;
  const type = req.query.type;
  const page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const limit = 25;
  const offset = (page - 1) * limit;
  return { limit, offset, queue, mode, type };
}
export default router;
