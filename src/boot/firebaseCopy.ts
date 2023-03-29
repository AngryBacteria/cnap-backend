import { initializeApp } from "firebase-admin/app";
import { getFirestore } from "firebase-admin/firestore";
import { credential } from "firebase-admin";

const firebaseConfig = {
  apiKey: "",
  authDomain: "",
  projectId: "",
  storageBucket: "",
  messagingSenderId: "",
  appId: "",
  credential: credential.cert("/path/to/firebase/service/account/json"),
};
export const firebaseApp = initializeApp(firebaseConfig);
export const db = getFirestore(firebaseApp);
