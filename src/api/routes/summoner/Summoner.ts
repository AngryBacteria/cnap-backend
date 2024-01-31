import express from "express";
import Express from "express";
import DBHelper from "../../../helpers/DBHelper";
import RiotHelper from "../../../helpers/RiotHelper";
import { logger } from "../../../boot/config";

const router = express.Router();
const baseUrl = "/summoner";
const dbHelper = DBHelper.getInstance();
const riotHelper = RiotHelper.getInstance();

/**
 * @swagger
 * /api/v1/summoner:
 *   get:
 *     description: Endpoint to get all available summoners. Limits to 25 at a time. Supports pagination with the query parameter "?page"
 *     tags:
 *      - summoner
 *     responses:
 *       200:
 *         description: All available summoners
 *     parameters:
 *       - name: page
 *         in: query
 *         required: false
 *         type: string
 *         description: page
 */
router.get(baseUrl, async (req: Express.Request, res: Express.Response) => {
  const limit = 25;
  const page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const offset = (page - 1) * limit;

  const results = await dbHelper.getSummoners({
    limit: limit,
    skip: offset,
  });
  if (results.length >= 1) {
    res.send(results);
  } else {
    res.send(404);
  }
});

/**
 * @swagger
 * /api/v1/summoner/puuid/{puuid}:
 *   get:
 *     description: Endpoint to get a specific summoner by its puuid. If present in postgres it fetches it that way. Else it uses the Riot-Api directly
 *     tags:
 *      - summoner
 *     responses:
 *       200:
 *         description: Summoner Object
 *     parameters:
 *       - name: puuid
 *         in: path
 *         required: true
 *         type: string
 *         description: puuid of a summoner
 */
router.get(baseUrl + "/puuid/:puuid", async (req: Express.Request, res: Express.Response) => {
  const puuid = req.params.puuid;

  //mongodb
  const results = await dbHelper.getSummoners({
    puuid: puuid,
  });

  if (results.length >= 1) {
    res.send(results[0]);
    logger.info(`Api-Request for Summoner [${puuid}] with Method: MongoDB`);
    return;
  }

  //riot api
  try {
    const riotSummoner = await riotHelper.getSummonerByPuuidRiot(puuid);
    if (riotSummoner) {
      res.send(riotSummoner);
      logger.info(`Api-Request for Summoner [${puuid}] with Method: RIOT-API`);
    }
  } catch (error) {
    res.status(404).send(`No summoner found with puuid [${puuid}]`);
  }
});

/**
 * @swagger
 * /api/v1/summoner/name/{name}:
 *   get:
 *     description: Endpoint to get a specific summoner by its name. If present in postgres it fetches it that way. Else it uses the Riot-Api directly
 *     tags:
 *      - summoner
 *     responses:
 *       200:
 *         description: Summoner Object
 *     parameters:
 *       - name: name
 *         in: path
 *         required: true
 *         type: string
 *         description: name of a summoner
 */
router.get(baseUrl + "/name/:name", async (req: Express.Request, res: Express.Response) => {
  const name = req.params.name;

  //mongodb
  const results = await dbHelper.getSummoners({
    name: name,
  });

  if (results.length >= 1) {
    res.send(results[0]);
    logger.info(`Api-Request for Summoner [${name}] with Method: MongoDB`);
    return;
  }

  //riot api
  try {
    const riotSummoner = await riotHelper.getSummonerByNameRiot(name);
    if (riotSummoner) {
      res.send(riotSummoner);
      logger.info(`Api-Request for Summoner [${name}] with Method: RIOT-API`);
    }
  } catch (error) {
    res.status(404).send(`No summoner found with name [${name}]`);
  }
});

export default router;
