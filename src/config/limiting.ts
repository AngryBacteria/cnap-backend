import { RateLimiter } from "limiter";

export const backgroundLimiter1 = new RateLimiter({
  tokensPerInterval: 7,
  interval: "second",
});
export const backgroundLimiter2 = new RateLimiter({
  tokensPerInterval: 70,
  interval: 120000,
});
