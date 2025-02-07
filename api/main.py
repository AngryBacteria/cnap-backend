import sys
from time import perf_counter
from typing import Dict, Any, Generator

from fastapi import FastAPI, HTTPException, Request
from starlette.staticfiles import StaticFiles

from helpers.DBHelper import (
    DBHelper,
    BasicFilter,
    CollectionName,
)
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.QueueDTO import QueueDTO
from models.ItemDTO import ItemDTO
from models.SummonerSpellDTO import SummonerSpellDTO
from models.SummonerDTODB import SummonerDTODB


dbh = DBHelper.get_instance()
rh = RiotHelper.get_instance()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    app_logger.info("Verifying connections...")
    # Check MongoDB connection
    if not await dbh.test_connection():
        app_logger.error("Failed to connect to MongoDB. Exiting application.")
        sys.exit(1)
    # Check Riot API connection
    if not await rh.test_connection():
        app_logger.error(
            "Failed to connect to Riot API or invalid API key. Exiting application."
        )
        sys.exit(1)
    app_logger.info("All connections verified successfully.")

    yield

    await dbh.disconnect()
    await rh.client.aclose()
    app_logger.info("Connections closed.")


app = FastAPI(lifespan=lifespan)

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

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    start_time = perf_counter()
    response = await call_next(request)
    process_time = (perf_counter() - start_time) * 1000
    app_logger.debug(f"Request took {process_time:.2f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response


@app.get("/champions/reduced")
async def get_champions_reduced() -> list[dict[str, Any]]:
    champions = await dbh.generic_get(
        BasicFilter(
            limit=100000,
            project={
                "_id": 0,
                "id": 1,
                "name": 1,
                "alias": 1,
                "title": 1,
                "shortBio": 1,
                "uncenteredSplashPath": 1,
            },
        ),
        CollectionName.CHAMPION,
    )
    if len(champions) > 0:
        return champions
    else:
        raise HTTPException(status_code=500, detail="No champion data available")


@app.get("/champions/{champion_alias}")
async def get_champions(champion_alias: str) -> ChampionDTO:
    champions = await dbh.generic_get(
        BasicFilter(
            limit=100000,
            filter={"alias": {"$regex": f"^{champion_alias}$", "$options": "i"}},
        ),
        CollectionName.CHAMPION,
        ChampionDTO,
    )
    if len(champions) > 0:
        return champions[0]
    else:
        raise HTTPException(status_code=404, detail="Champion not found")


@app.get("/queues")
async def get_queues() -> list[QueueDTO]:
    queues = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.QUEUE,
        QueueDTO,
    )
    if len(queues) > 0:
        return queues
    else:
        raise HTTPException(status_code=500, detail="No queue data available")


@app.get("/items")
async def get_items() -> list[ItemDTO]:
    items = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.ITEM,
        ItemDTO,
    )
    if len(items) > 0:
        return items
    else:
        raise HTTPException(status_code=500, detail="No item data available")


@app.get("/summoner-spells")
async def get_summoner_spells() -> list[SummonerSpellDTO]:
    summoner_spells = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.SUMMONER_SPELL,
        SummonerSpellDTO,
    )
    if len(summoner_spells) > 0:
        return summoner_spells
    else:
        raise HTTPException(status_code=500, detail="No summoner spell data available")


@app.get("/summoners")
async def get_summoners() -> list[SummonerDTODB]:
    summoners = await dbh.generic_get(
        BasicFilter(
            limit=100000,
            project={
                "_id": 0,
                "puuid": 1,
                "gameName": 1,
                "profileIconId": 1,
                "summonerLevel": 1,
                "tagLine": 1,
            },
        ),
        CollectionName.SUMMONER,
        SummonerDTODB,
    )
    if len(summoners) > 0:
        return summoners
    else:
        raise HTTPException(status_code=500, detail="No summoner data available")


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
