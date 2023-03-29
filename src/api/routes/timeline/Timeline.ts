import express from "express";
import Express from "express";
import RiotHelper from "../../../helpers/RiotHelper";
import { asyncWrap } from "../../../helpers/GlobalFunctions";

const router = express.Router();
const baseUrl = "/timeline";
const riotHelper = RiotHelper.getInstance();

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
router.get(baseUrl + "/id/:id", async (req: Express.Request, res: Express.Response) => {
  const matchId = req.params.id;
  const { data: timeline } = await asyncWrap(riotHelper.getTimeLine(matchId));
  if (timeline) {
    res.send(timeline);
    return;
  }
  res.sendStatus(404);
});
export default router;
