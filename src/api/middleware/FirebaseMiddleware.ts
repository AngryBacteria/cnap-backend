import Express from "express";
import { getAuth } from "firebase-admin/auth";
import { firebaseApp } from "../../boot/firebase";
import { asyncWrap } from "../../helpers/GlobalFunctions";

export const checkClaim = (claim: string) => {
  return async (req: Express.Request, res: Express.Response, next: any) => {
    const bearerToken = req.headers.authorization?.replace("Bearer", "").trim();
    if (bearerToken) {
      const { data, error } = await asyncWrap(getAuth(firebaseApp).verifyIdToken(bearerToken));
      if (data && data[claim]) {
        console.log(data);
        next();
        return;
      }
    }
    res.status(401).send("You are not authorized to use this endpoint, please specify a valid bearer token");
  };
};
