import { createClient as createRedis } from "redis";
import express from "express";
import { Pool } from "pg";
import { RateLimiter } from "limiter";
import winston, { createLogger, format } from "winston";
import ON_DEATH from "death";

const { combine, timestamp, label, printf } = format;

//lolapi
export const riotApiKey = "CHANGE_ME";

//express
export const expressInstance = express();
export const pathToEndpoints = "CHANGE_ME";

//postgres
export const pg = new Pool({
  user: "CHANGE_ME",
  password: "CHANGE_ME",
  host: "CHANGE_ME",
  database: "CHANGE_ME",
  port: -1,
  max: 20,
});

//redis
export const redisPassword = "CHANGE_ME";
export const cache = createRedis({
  url: `redis://:${redisPassword}@localhost:6379`,
});

cache
  .connect()
  .then(() => console.log("connected to cache"))
  .catch(() => console.log("redis connection error"));

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
    new winston.transports.File({
      level: "debug",
      filename: "combined.log",
      maxsize: 500 * 1024 * 1024, // 100MB
      maxFiles: 2,
    }),
  ],
});
