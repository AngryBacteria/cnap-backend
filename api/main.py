from typing import Annotated

from fastapi import FastAPI, HTTPException, Query

from helpers.DBHelper import DBHelper, MatchQueryFilter, SummonerHistoryFilter
from helpers.RiotHelper import RiotHelper

dbh = DBHelper()
rh = RiotHelper()
app = FastAPI()


@app.get("/match/{item_id}")
async def get_match_by_id(match_id: str):
    db_response = await dbh.get_matches_v5(MatchQueryFilter(match_id=match_id))
    db_match = db_response[0] if len(db_response) > 0 else None
    if db_match:
        return db_match
    else:
        riot_match = await rh.get_match_riot(match_id)
        if riot_match:
            return riot_match
        else:
            raise HTTPException(
                status_code=404, detail=f"Match with id [${match_id}] not found"
            )


@app.get("/matches")
async def get_matches(match_filter: Annotated[MatchQueryFilter, Query()]):
    db_response = await dbh.get_matches_v5(match_filter)
    db_matches = db_response if len(db_response) > 0 else None
    if db_matches:
        return db_matches
    else:
        raise HTTPException(
            status_code=404, detail="No matches found that match the filter"
        )


@app.get("/history")
async def get_matches(history_filter: Annotated[SummonerHistoryFilter, Query()]):
    db_response = await dbh.get_summoner_match_history(history_filter)
    db_matches = db_response if len(db_response) > 0 else None
    if db_matches:
        return db_matches
    else:
        raise HTTPException(
            status_code=404, detail="No summoner history found that match the filter"
        )
