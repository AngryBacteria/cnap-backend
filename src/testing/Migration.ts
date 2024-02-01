import DBHelper from "../helpers/DBHelper";

async function run() {
  const dbHelper = DBHelper.getInstance();
  await dbHelper.connect();
  await migrateArchive();
  await migrateSummoners();
  await dbHelper.disconnect();
}

async function migrateArchive() {
  const dbHelper = DBHelper.getInstance();
  console.log("getting match data");
  const { data, error } = await dbHelper.executeQuery("select * from match_archive limit 100");
  if (data && !error) {
    console.log("uploading to mongodb");
    const mappedArray = data.rows.map((item: { data: any }) => item.data);
    await dbHelper.mongoClient.db("cnap").collection("match_v5").insertMany(mappedArray);
  }
}

async function migrateSummoners() {
  const dbHelper = DBHelper.getInstance();
  console.log("getting summoners data");
  const { data, error } = await dbHelper.executeQuery("select * from summoners");
  if (data && !error) {
    console.log("uploading to mongodb");
    const mappedArray = data.rows.map((item: any) => item.data);
    await dbHelper.mongoClient.db("cnap").collection("summoner").insertMany(mappedArray);
  }
}

run().catch(console.dir);
