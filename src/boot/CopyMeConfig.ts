import { createClient } from "@supabase/supabase-js";
import { createClient as createRedis } from "redis";
import express from "express";
import { Pool } from "pg";
import { RateLimiter } from "limiter";
import winston, { createLogger, format } from "winston";

const { combine, timestamp, label, printf } = format;

const supabaseUrl = "";
const supabaseAnonKey = "";

//supabase
export const supabase = createClient(supabaseUrl, supabaseAnonKey);

//lolapi
export const riotApiKey = "";

//express
export const expressInstance = express();
export const apiKey = "";

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
