import asyncio
import sys
from time import perf_counter
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request

from helpers.DBHelper import (
    DBHelper,
    BasicFilter,
    CollectionName,
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

dbh = DBHelper.get_instance()
rh = RiotHelper.get_instance()
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
async def startup_event() -> None:
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
async def shutdown_event() -> None:
    """Cleanup connections"""
    await dbh.disconnect()
    await rh.client.aclose()
    app_logger.info("Connections closed.")


@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Any) -> Any:
    start_time = perf_counter()
    response = await call_next(request)
    process_time = (perf_counter() - start_time) * 1000
    app_logger.debug(f"Request took {process_time:.2f}ms")
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response


@app.get("/static/champions/reduced")
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


@app.get("/static/champions/{champion_id}")
async def get_champions(champion_id: int) -> ChampionDTO:
    champions = await dbh.generic_get(
        BasicFilter(limit=100000, filter={"id": champion_id}),
        CollectionName.CHAMPION,
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
            BasicFilter(limit=100000), CollectionName.GAME_MODE, GameModeDTO
        ),
        dbh.generic_get(
            BasicFilter(limit=100000), CollectionName.GAME_TYPE, GameTypeDTO
        ),
        dbh.generic_get(
            BasicFilter(
                limit=100000,
                project={
                    "_id": 0,
                    "id": 1,
                    "name": 1,
                    "description": 1,
                    "categories": 1,
                    "price": 1,
                    "priceTotal": 1,
                    "iconPath": 1,
                },
            ),
            CollectionName.ITEM,
            ItemDTO,
        ),
        dbh.generic_get(BasicFilter(limit=100000), CollectionName.MAP, MapDTO),
        dbh.generic_get(BasicFilter(limit=100000), CollectionName.QUEUE, QueueDTO),
    )

    if (
        len(game_modes) > 0
        and len(game_types) > 0
        and len(items) > 0
        and len(maps) > 0
        and len(queues) > 0
    ):
        return StaticDataResponse(
            game_modes=game_modes,
            game_types=game_types,
            items=items,
            maps=maps,
            queues=queues,
        )
    else:
        raise HTTPException(status_code=500, detail="Some static data is not available")


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
