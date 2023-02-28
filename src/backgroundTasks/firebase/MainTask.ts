import { getAuth, UserRecord } from "firebase-admin/auth";
import { firebaseApp } from "../../boot/firebase";

async function setClaims(claim: any, uid: string) {
  await getAuth(firebaseApp).setCustomUserClaims(uid, claim);
}

async function getUser(uid: string): Promise<UserRecord> {
    return await getAuth(firebaseApp).getUser(uid)
}

async function test() {
    const result = await getAuth(firebaseApp).verifyIdToken('eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJPbmxpbmUgSldUIEJ1aWxkZXIiLCJpYXQiOjE2NzcyNzUwODcsImV4cCI6MTcwODgxMTA4NywiYXVkIjoid3d3LmV4YW1wbGUuY29tIiwic3ViIjoianJvY2tldEBleGFtcGxlLmNvbSIsIkdpdmVuTmFtZSI6IkpvaG5ueSIsIlN1cm5hbWUiOiJSb2NrZXQiLCJFbWFpbCI6Impyb2NrZXRAZXhhbXBsZS5jb20iLCJSb2xlIjpbIk1hbmFnZXIiLCJQcm9qZWN0IEFkbWluaXN0cmF0b3IiXSwia2lkIjoidHJ1ZSJ9.SFOzbDReqLcg0pMW6waBHIkNSGD7mE-b92eYwVLp4Uo')
}

test().then()