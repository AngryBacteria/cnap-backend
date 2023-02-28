import express from "express";
import Express from "express";
import DBHelper from "../../../helpers/DBHelper";
import RiotHelper from "../../../helpers/RiotHelper";
import { asyncWrap } from "../../../helpers/GlobalFunctions";
import { apiLogger } from "../../../boot/config";

const router = express.Router();
const baseUrl = "/summoner";
const dbHelper = DBHelper.getInstance()
const riotHelper = RiotHelper.getInstance()

/**
 * Endpoint to get all available summoners. Limits to 25 at a time. Supports pagination with the query parameter "?page"
 */
router.get(baseUrl, async (req: Express.Request, res: Express.Response) => {
  console.time();
  const limit = 25;
  let page = isNaN(Number(req.query.page)) ? 1 : Number(req.query.page);
  const offset = (page - 1) * limit;
  const { data, error } = await dbHelper.executeQuery(`SELECT * FROM summoners LIMIT ${limit} OFFSET ${offset}`);
  if (!error) {
    res.send(data.rows);
  } else {
    res.status(500).send(error);
  }
  console.timeEnd();
});

/**
 * Endpoint to get a specific summoner by its puuid. If present in postgres it fetches it that way.
 * Else it uses the Riot-Api directly
 */
router.get(baseUrl + "/puuid/:puuid", async (req: Express.Request, res: Express.Response) => {
  console.time();
  const puuid = req.params.puuid;

  //postgres
  const query = {
    name: "fetch_summoner_by_puuid",
    text: "SELECT * FROM summoners WHERE puuid = $1",
    values: [puuid],
  };
  const { data } = await dbHelper.executeQuery(query);
  if (data?.rows.length) {
    res.send(data.rows[0]);
    apiLogger.info(`Api-Request for Summoner [${puuid}] with Method: POSTGRES`);
    console.timeEnd();
    return;
  }

  //riot api
  const { data: riotData } = await asyncWrap(riotHelper.getSummonerByPuuid(puuid));
  if (riotData) {
    res.send(riotData);
    apiLogger.info(`Api-Request for Summoner [${puuid}] with Method: RIOT-API`);
    console.timeEnd();
    return;
  }
  res.status(404).send(`No summoner found with puuid [${puuid}]`);
  console.timeEnd();
});

/**
 * Endpoint to get a specific summoner by its name. If present in postgres it fetches it that way.
 * Else it uses the Riot-Api directly
 */
router.get(baseUrl + "/name/:name", async (req: Express.Request, res: Express.Response) => {
  console.time();
  const name = req.params.name;

  //postgres
  const query = {
    name: "fetch_summoner_by_name",
    text: "SELECT * FROM summoners WHERE data ->> 'name' = $1",
    values: [name],
  };
  const { data } = await dbHelper.executeQuery(query);
  if (data?.rows.length) {
    res.send(data.rows[0]);
    apiLogger.info(`Api-Request for Summoner [${name}] with Method: POSTGRES`);
    console.timeEnd();
    return;
  }

  //riot api
  const { data: riotData } = await asyncWrap(riotHelper.getSummonerByName(name));
  if (riotData) {
    res.send(riotData);
    apiLogger.info(`Api-Request for Summoner [${name}] with Method: RIOT-API`);
    console.timeEnd();
    return;
  }
  res.status(404).send(`No summoner found with name [${name}]`);
  console.timeEnd();
});

export default router;
