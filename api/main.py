from fastapi import FastAPI, HTTPException

from helpers.DBHelper import DBHelper
from helpers.RiotHelper import RiotHelper

app = FastAPI()

dbh = DBHelper()
rh = RiotHelper()


@app.get("/match/{item_id}")
async def read_item(match_id: str):
    db_response = await dbh.get_matches_v5(match_id=match_id)
    db_match = db_response[0] if len(db_response) > 0 else None
    if db_match:
        return db_match
    else:
        riot_match = await rh.get_match(match_id)
        if riot_match:
            await dbh.save_match(riot_match)
            return riot_match
        else:
            raise HTTPException(status_code=404, detail="Match not found")
