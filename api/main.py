from time import perf_counter
from typing import Annotated, Dict

from fastapi import FastAPI, HTTPException, Query, Request

from helpers.DBHelper import (
    DBHelper,
    SummonerFilter,
    BaseMatchFilter,
    BaseFilter,
)
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO
from models.ItemDTO import ItemDTO
from models.SummonerDTODB import SummonerDTODB

dbh = DBHelper()
rh = RiotHelper()
app = FastAPI()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    process_time = (perf_counter() - start_time) * 1000
    app_logger.debug(f"{process_time:.2f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response


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


@app.get("/gamedata")
async def get_app_data():
    champions = await dbh.generic_get(
        BaseFilter(), dbh.champion_collection, ChampionDTO
    )
    items = await dbh.generic_get(BaseFilter(), dbh.item_collection, ItemDTO)
    game_modes = await dbh.generic_get(BaseFilter(), dbh.game_modes_collection)
    game_types = await dbh.generic_get(BaseFilter(), dbh.game_types_collection)
    maps = await dbh.generic_get(BaseFilter(), dbh.maps_collection)
    queues = await dbh.generic_get(BaseFilter(), dbh.queues_collection)

    return {
        "champions": champions,
        "items": items,
        "game_modes": game_modes,
        "game_types": game_types,
        "maps": maps,
        "queues": queues,
    }


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
