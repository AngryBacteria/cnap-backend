import { getAuth, UserRecord } from "firebase-admin/auth";
import { firebaseApp } from "../../boot/firebase";

async function setClaims(claim: any, uid: string) {
  await getAuth(firebaseApp).setCustomUserClaims(uid, claim);
}

async function getUser(uid: string): Promise<UserRecord> {
    return await getAuth(firebaseApp).getUser(uid)
}

async function test() {
    await setClaims({swn: true}, '')
    // const user = await getUser('');
    // console.log(user.customClaims)
    
    // const testCollection = await db.collection('/test')
    // const documents = await testCollection.doc('').get()
    // console.log(documents)
}

test().then()