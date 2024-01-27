import { createClient as createRedis } from "redis";
import express from "express";
import { Pool } from "pg";
import { RateLimiter } from "limiter";
import winston, { createLogger, format } from "winston";
import ON_DEATH from "death";

const { combine, timestamp, label, printf } = format;

//lolapi
export const riotApiKey = process.env.RIOT_KEY || "CHANGE";

//express
export const expressInstance = express();
export const pathToEndpoints = "src/api/routes/**/*.ts";

//postgres
export const pg = new Pool({
  user: process.env.POSTGRES_USER || "postgres",
  password: process.env.PASSWORD || "CHANGE",
  host: process.env.HOST || "CHANGE",
  database: process.env.POSTGRES_DB || "CHANGE",
  port: 5432,
  max: 20,
});
async function checkPostgres() {
  try {
    const client = await pg.connect();
    client.release(true);
    console.log("Connected to postgres")
  } catch (error) {
    console.log("Error connecting to postgres", error);
  }
}
checkPostgres();

//redis
const redisHost = process.env.REDIS_HOST || "CHANGE";
const redisPort = process.env.REDIS_PORT || "6379";
const redisPassword = process.env.REDIS_PASSWORD || "CHANGE";
export const cache = createRedis({
  url: `redis://:${redisPassword}@${redisHost}:${redisPort}`,
});

cache
  .connect()
  .then(() => console.log("connected to cache"))
  .catch((error) => console.log("redis connection error: ", error));

ON_DEATH(async () => {
  await cache.quit();
  console.log("disconnected from cache");
  process.exit();
});

//Rate limiters
//Background Task
export const backgroundLimiter1 = new RateLimiter({
  tokensPerInterval: 7,
  interval: "second",
});
export const backgroundLimiter2 = new RateLimiter({
  tokensPerInterval: 70,
  interval: 120000,
});

//Logging
const myFormat = printf(({ level, message, label, timestamp }) => {
  return `${timestamp} [${label}] ${level}: ${message}`;
});
export const logger = createLogger({
  format: combine(label({ label: "CAP Backend Service" }), timestamp(), myFormat),
  transports: [
    new winston.transports.Console({
      level: "debug",
    }),
  ],
});
