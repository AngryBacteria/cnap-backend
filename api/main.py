from typing import Annotated, Dict

from fastapi import FastAPI, HTTPException, Query

from helpers.DBHelper import (
    DBHelper,
    SummonerFilter,
    BaseMatchFilter,
    BaseFilter,
)
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO
from models.ItemDTO import ItemDTO
from models.SummonerDTODB import SummonerDTODB

dbh = DBHelper()
rh = RiotHelper()
app = FastAPI()


@app.get("/match/{match_id}")
async def get_match_by_id(match_id: str):
    db_response = await dbh.get_matches(BaseMatchFilter(match_ids=[match_id]))
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
async def get_matches(match_filter: Annotated[BaseMatchFilter, Query()]):
    db_response = await dbh.get_matches(match_filter)
    db_matches = db_response if len(db_response) > 0 else None
    if db_matches:
        return db_matches
    else:
        raise HTTPException(
            status_code=404, detail="No matches found that match the filter"
        )


@app.get("/summoners")
async def get_summoners(
    summoner_filter: Annotated[SummonerFilter, Query()],
) -> list[SummonerDTODB]:
    db_response = await dbh.get_summoners(summoner_filter)
    if len(db_response) > 0:
        return db_response
    else:
        raise HTTPException(status_code=404, detail="No summoners found")


@app.get("/items")
async def get_items(base_filter: Annotated[BaseFilter, Query()]) -> list[ItemDTO]:
    db_response = await dbh.get_items(base_filter)
    db_items = db_response if len(db_response) > 0 else None
    if db_items:
        return db_items
    else:
        raise HTTPException(status_code=404, detail="No items found")


@app.get("/champions")
async def get_champions(
    base_filter: Annotated[BaseFilter, Query()],
) -> list[ChampionDTO]:
    db_response = await dbh.get_champions(base_filter)
    db_champions = db_response if len(db_response) > 0 else None
    if db_champions:
        return db_champions
    else:
        raise HTTPException(status_code=404, detail="No champions found")


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
