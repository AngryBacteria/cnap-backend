import { createClient as createRedis } from "redis";
import express from "express";
import { Pool } from "pg";
import { RateLimiter } from "limiter";
import winston, { createLogger, format } from "winston";
import ON_DEATH from 'death';

const { combine, timestamp, label, printf } = format;

//lolapi
export const riotApiKey = "";

//express
export const expressInstance = express();
export const pathToEndpoints = 'src/api/routes/**/*.ts'

//postgres
export const pg = new Pool({
  user: "",
  password: "",
  host: "",
  database: "",
  port: 9999,
  max: 20,
});

//redis
export const redisPassword = "";
export const cache = createRedis({
  password: redisPassword,
});
cache.connect().then(() => console.log('connected to cache'))
ON_DEATH(async () => {
  await cache.quit()
  console.log('disconnected from cache')
  process.exit()
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
      filename: "combined.log",
      maxsize: 500 * 1024 * 1024, // 100MB
      maxFiles: 2,
    }),
  ],
});

export const apiLogger = createLogger({
  format: combine(label({ label: "CAP Backend Service" }), timestamp(), myFormat),
  transports: [
    new winston.transports.File({
      filename: "api.log",
      maxsize: 500 * 1024 * 1024, // 100MB
      maxFiles: 2,
    }),
  ],
});
