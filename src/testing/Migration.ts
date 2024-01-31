import { MongoClient, ServerApiVersion } from "mongodb";
import DBHelper from "../helpers/DBHelper";
import { mongoURL } from "../boot/config";
import MainTask from "../backgroundTasks/riot/MainTask";

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(mongoURL, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  },
});
async function run() {
  const task = new MainTask();
  await task.updateMatchData("", 300, 25)
}

async function migrateArchive() {
  try {
    await client.connect();
    const dbHelper = new DBHelper();
    console.log("getting match data");
    const { data, error } = await dbHelper.executeQuery("select * from match_archive limit 100");
    if (data && !error) {
      console.log("uploading to mongodb");
      const mappedArray = data.rows.map((item: { data: any }) => item.data);
      await client.db("cnap").collection("match_v5").insertMany(mappedArray);
    }
  } finally {
    await client.close();
    console.log("finished");
  }
}

async function migrateSummoners() {
  try {
    await client.connect();
    const dbHelper = new DBHelper();
    console.log("getting summoners data");
    const { data, error } = await dbHelper.executeQuery("select * from summoners");
    if (data && !error) {
      console.log("uploading to mongodb");
      const mappedArray = data.rows.map((item: any) => item.data);
      await client.db("cnap").collection("summoner").insertMany(mappedArray);
    }
  } finally {
    await client.close();
    console.log("finished");
  }
}

run().catch(console.dir);
