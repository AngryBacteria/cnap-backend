import asyncio
import sys
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

from models.GameModeDTO import GameModeDTO
from models.GameTypeDTO import GameTypeDTO
from models.GlobalPydanticConfig import BaseConfig
from models.ItemDTO import ItemDTO
from models.MapDTO import MapDTO
from models.QueueDTO import QueueDTO

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


@app.on_event("startup")
async def startup_event():
    """
    Verify all connections on startup.
    Exits the application if any connection fails.
    """
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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections"""
    await dbh.disconnect()
    await rh.client.aclose()
    app_logger.info("Connections closed.")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = perf_counter()
    response = await call_next(request)
    process_time = (perf_counter() - start_time) * 1000
    app_logger.debug(f"Request took {process_time:.2f}ms")
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


@app.get("/static/champions/{champion_key}")
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


class StaticDataResponse(BaseConfig):
    game_modes: list[GameModeDTO]
    game_types: list[GameTypeDTO]
    items: list[ItemDTO]
    maps: list[MapDTO]
    queues: list[QueueDTO]


@app.get("/static/data")
async def get_static_data() -> StaticDataResponse:
    # Run all queries concurrently
    game_modes, game_types, items, maps, queues = await asyncio.gather(
        dbh.generic_get(
            BasicFilter(limit=100000), dbh.game_mode_collection, GameModeDTO
        ),
        dbh.generic_get(
            BasicFilter(limit=100000), dbh.game_type_collection, GameTypeDTO
        ),
        dbh.generic_get(
            BasicFilter(
                limit=100000,
                project={
                    "_id": 0,
                    "name": 1,
                    "id": 1,
                    "icon": 1,
                    "simpleDescription": 1,
                },
            ),
            dbh.item_collection,
            ItemDTO
        ),
        dbh.generic_get(BasicFilter(limit=100000), dbh.map_collection, MapDTO),
        dbh.generic_get(BasicFilter(limit=100000), dbh.queue_collection, QueueDTO),
    )

    return StaticDataResponse(
        game_modes=game_modes,
        game_types=game_types,
        items=items,
        maps=maps,
        queues=queues,
    )


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
