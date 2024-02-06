import express from 'express';
import Express from 'express';

const router = express.Router();

router.get('/hello', (req: Express.Request, res: Express.Response) => {
  if (req.query.id) {
    console.log('there is an id: ', req.query.id);
  }
  res.send('Hello World!');
});

export default router;
