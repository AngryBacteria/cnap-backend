import sys
from time import perf_counter
from typing import Dict, Any, Mapping, Sequence, Annotated

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from helpers.DBHelper import (
    DBHelper,
    BasicFilter,
    CollectionName,
)
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO, ChampionReducedDTO
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from models.GlobalPydanticConfig import BaseConfig
from models.MatchV5DTO import MatchV5SingleDTO
from models.QueueDTO import QueueDTO
from models.ItemDTO import ItemDTO
from models.SummonerSpellDTO import SummonerSpellDTO
from models.SummonerDBDTO import SummonerDBDTO


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


@app.get("/champions/reduced", response_model=list[ChampionReducedDTO])
async def get_champions_reduced() -> JSONResponse:
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
        return JSONResponse(content=champions)
    else:
        raise HTTPException(status_code=500, detail="No champion data available")


@app.get("/champion/{champion_alias}", response_model=ChampionDTO)
async def get_champions(champion_alias: str) -> JSONResponse:
    champions = await dbh.generic_get(
        BasicFilter(
            limit=100000,
            filter={"alias": {"$regex": f"^{champion_alias}$", "$options": "i"}},
        ),
        CollectionName.CHAMPION,
    )
    if len(champions) > 0:
        return JSONResponse(content=champions[0])
    else:
        raise HTTPException(status_code=404, detail="Champion not found")


class MatchesByChampionResponse(BaseConfig):
    page: int
    maxPage: int
    data: list[MatchV5SingleDTO]


@app.get(
    "/matches/champion/{champion_id}", response_model=list[MatchesByChampionResponse]
)
async def get_matches_by_champion(
    champion_id: int,
    queue_id: Annotated[int | None, Query()] = None,
    only_summoners_in_db: Annotated[bool, Query()] = True,
    page: int = 1,
) -> JSONResponse:
    # Pagination
    page_size = 10
    skip = (page - 1) * page_size

    # Init the pipeline
    pipeline: list[Mapping[str, Any]] = []

    # Filter by champion id
    pipeline.append({"$match": {"info.participants.championId": champion_id}})

    # Optionally Filter by summoner puuids
    if only_summoners_in_db:
        existingSummonerPuuids = await dbh.generic_get(
            BasicFilter(
                limit=100000,
                project={"puuid": 1},
            ),
            CollectionName.SUMMONER,
        )
        summonerPuuids = [summoner["puuid"] for summoner in existingSummonerPuuids]
        pipeline.append(
            {"$match": {"info.participants.puuid": {"$in": summonerPuuids}}}
        )

    # Filter by queue id
    if queue_id is not None:
        pipeline.append({"$match": {"info.queueId": queue_id}})

    # Unwind
    pipeline.append(
        {
            "$unwind": {
                "path": "$info.participants",
                "preserveNullAndEmptyArrays": True,
            }
        }
    )

    # Filter unwinded documents again by by champion_id
    pipeline.append({"$match": {"info.participants.championId": champion_id}})

    # Optionally filter unwinded documents again by summoner puuids
    if only_summoners_in_db:
        pipeline.append(
            {"$match": {"info.participants.puuid": {"$in": summonerPuuids}}}
        )

    # Sort and paginate
    pipeline.extend(
        [
            {"$sort": {"info.gameCreation": -1}},
            {
                "$facet": {
                    "metadata": [{"$count": "total"}],
                    "data": [
                        {"$skip": skip},
                        {"$limit": page_size},
                        {"$project": {"_id": 0}},
                    ],
                }
            },
        ]
    )

    cursor = dbh.get_collection(CollectionName.MATCH).aggregate(pipeline)
    result = await cursor.to_list(length=None)
    metadata = result[0].get("metadata", [])
    total = metadata[0]["total"] if metadata else 0

    max_page = (total + page_size - 1) // page_size
    data = result[0].get("data", [])

    return JSONResponse(content={"page": page, "maxPage": max_page, "data": data})


@app.get("/queues", response_model=list[QueueDTO])
async def get_queues() -> JSONResponse:
    queues = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.QUEUE,
    )
    if len(queues) > 0:
        return JSONResponse(content=queues)
    else:
        raise HTTPException(status_code=500, detail="No queue data available")


@app.get("/items", response_model=list[ItemDTO])
async def get_items() -> JSONResponse:
    items = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.ITEM,
    )
    if len(items) > 0:
        return JSONResponse(content=items)
    else:
        raise HTTPException(status_code=500, detail="No item data available")


@app.get("/summoner-spells", response_model=list[SummonerSpellDTO])
async def get_summoner_spells() -> JSONResponse:
    summoner_spells = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.SUMMONER_SPELL,
    )
    if len(summoner_spells) > 0:
        return JSONResponse(content=summoner_spells)
    else:
        raise HTTPException(status_code=500, detail="No summoner spell data available")


@app.get("/summoners", response_model=SummonerDBDTO)
async def get_summoners() -> JSONResponse:
    summoners = await dbh.generic_get(
        BasicFilter(
            limit=100000,
        ),
        CollectionName.SUMMONER,
    )
    if len(summoners) > 0:
        return JSONResponse(content=summoners)
    else:
        raise HTTPException(status_code=500, detail="No summoner data available")


@app.get("/")
async def read_main() -> Dict[str, str]:
    return {"msg": "Hello World"}
