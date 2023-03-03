import express from "express";
import Express from "express";
import DBHelper from "../../../helpers/DBHelper";
import RiotHelper from "../../../helpers/RiotHelper";
import { asyncWrap } from "../../../helpers/GlobalFunctions";
import { apiLogger } from "../../../boot/config";

const router = express.Router();
const baseUrl = "/timeline";
const dbHelper = DBHelper.getInstance()
const riotHelper = RiotHelper.getInstance()

/**
 * @swagger
 * /api/v1/timeline/id/{id}:
 *   get:
 *     description: Endpoint for querying complete timeline objects from either the cache or Riot-API by their ID
 *     responses:
 *       200:
 *         description: Single timeline object
 *     parameters:
 *       - name: id
 *         in: path
 *         required: true
 *         type: string
 *         description: ID of a Riot-Match (for example EUW1_5998862548)
 */
router.get(baseUrl + '/id/:id', async (req: Express.Request, res: Express.Response) => {
    const matchId = req.params.id;
    const { data: timeline } = await asyncWrap(riotHelper.getTimeLine(matchId));
    if(timeline) {
        res.send(timeline)
        apiLogger.info(`Api-Request for Timeline [${matchId}]`);
        return;
    }
    res.sendStatus(404);
  });
  export default router;