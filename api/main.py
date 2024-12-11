from time import perf_counter
from typing import Dict

from fastapi import FastAPI, HTTPException, Request

from helpers.DBHelper import (
    DBHelper,
    BasicFilter,
)
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO
from fastapi.middleware.cors import CORSMiddleware

dbh = DBHelper()
rh = RiotHelper()
app = FastAPI()


origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    process_time = (perf_counter() - start_time) * 1000
    app_logger.debug(f"{process_time:.2f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response


@app.get("/static/champions/reduced")
async def get_champions_reduced() -> list[dict]:
    champions = await dbh.generic_get(
        BasicFilter(
            limit=100000,
            project={
                "_id": 0,
                "id": 1,
                "key": 1,
                "name": 1,
                "title": 1,
                "lore": 1,
                "skins.name": 1,
                "skins.lore": 1,
                "skins.splashPath": 1,
                "faction": 1,
            },
        ),
        dbh.champion_collection,
    )
    return champions


@app.get("/static/champion/{champion_key}")
async def get_champions(champion_key: str) -> ChampionDTO:
    champions = await dbh.generic_get(
        BasicFilter(limit=100000, filter={"key": champion_key}),
        dbh.champion_collection,
        ChampionDTO,
    )
    if len(champions) > 0:
        return champions[0]
    else:
        raise HTTPException(status_code=404, detail="Champion not found")


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
