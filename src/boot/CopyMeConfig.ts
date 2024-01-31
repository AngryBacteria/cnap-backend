import express from "express";
import { RateLimiter } from "limiter";
import winston, { createLogger, format } from "winston";
import path from "path";
import ON_DEATH from "death";
import DBHelper from "../helpers/DBHelper";

//lolapi
export const riotApiKey = "RIOT-API-KEY-HERE";

//express
export const expressInstance = express();
export const pathToEndpoints = path.join("src", "api", "routes", "**", "*.ts");

//mongodb
export const mongoURL = process.env.MONGO_URL || "MONGODB_CONNECTION_STRING_HERE";
ON_DEATH(async () => {
  await DBHelper.getInstance().disconnect();
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
const { combine, timestamp, label, printf } = format;
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
