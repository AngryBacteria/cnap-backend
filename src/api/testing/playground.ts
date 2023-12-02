import DBHelper from "../../helpers/DBHelper";

async function run() {
  const dbHelper = new DBHelper();

  console.log(
    await dbHelper.getMatchesV5({
      limit: 1,
    })
  );
}

run().catch();
