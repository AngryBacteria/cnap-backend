import { config } from 'dotenv';
import DBHelper from '../helpers/DBHelper.js';
import MainTask from './riot/MainTask.js';
import { logger } from '../config/logging.js';

async function run() {
  const dbh = DBHelper.getInstance();
  await dbh.connect();
  const task = new MainTask();
  config();
  const minutes = process.env.MINUTE_INTERVAL
    ? parseInt(process.env.MINUTE_INTERVAL)
    : 90;
  logger.info(`Starting interval update every ${minutes} minutes`);
  await task.intervalUpdate(0, 1000 * 60 * minutes);
  logger.info('First Interval update finished');
}
run().catch();
