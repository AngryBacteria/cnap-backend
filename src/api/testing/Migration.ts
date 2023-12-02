import { MongoClient, ServerApiVersion } from "mongodb";
import DBHelper from "../../helpers/DBHelper";
import { mongoURL } from "../../boot/config";

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(mongoURL, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  },
});
async function run() {
  try {
    await migrateArchive()
    await migrateMatches()
    await migrateSummoners();
  } finally {
  }
}

async function migrateArchive() {
  try {
    await client.connect();
    const dbHelper = new DBHelper();
    console.log("getting archive data");
    const { data, error } = await dbHelper.executeQuery("select * from match_archive");
    if (data && !error) {
      console.log("uploading to mongodb");
      const mappedArray = data.rows.map((item: { data: any }) => item.data);
      await client.db("cnap").collection("match_archive").insertMany(mappedArray);
    }
  } finally {
    await client.close();
    console.log("finished");
  }
}

async function migrateMatches() {
  try {
    await client.connect();
    const dbHelper = new DBHelper();
    console.log("getting matchv5 data");
    const { data, error } = await dbHelper.executeQuery("select * from match_v5 limit 20");
    if (data && !error) {
      console.log("uploading to mongodb");
      const mappedArray = data.rows.map((item: any) => ({
        match_id: item.match_id,
        puuid: item.puuid,
        match_id_puuid: item.match_id_puuid,
        data_participant: item.data_participant,
        data_match: item.data_match,
      }));
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
