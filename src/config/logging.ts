import winston, { createLogger, format } from "winston";

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
