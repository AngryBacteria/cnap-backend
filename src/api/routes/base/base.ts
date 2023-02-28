import express from "express";
import Express from "express";
import { pg } from "../../../boot/config";
import { checkClaim } from "../../middleware/FirebaseMiddleware";

const router = express.Router();

router.get('/hello' ,(req: Express.Request, res: Express.Response) => {
    if (req.query.id) {
        console.log('there is an id: ', req.query.id)
    }
    res.send('Hello World!')
})

router.get('/admin', checkClaim('admin'), (req: Express.Request, res: Express.Response) => {
    res.send('secured endpoint');
})

router.get('/now', async (req: Express.Request, res: Express.Response) => {
    const client = await pg.connect()
    const { rows } = await client.query('SELECT NOW()')
    res.send(rows)
    client.release(true)
})

export default router