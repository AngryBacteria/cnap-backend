import asyncio
import os
from threading import Lock
from typing import List, Dict, Any, Union, Mapping, Sequence, Literal, Optional

from dotenv import load_dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pydantic import BaseModel
from pymongo import UpdateOne
from pymongo.results import BulkWriteResult

from helpers.Logger import app_logger
from models.ChampionDataDTO import ChampionDataDTO
from models.SummonerDTO import SummonerDTO


class BaseFilter(BaseModel):
    offset: Optional[int] = 0
    limit: Optional[int] = 20


class BaseMatchFilter(BaseFilter):
    participant_puuids: Optional[List[str]] = []
    match_ids: Optional[List[str]] = []
    queue: Optional[int] = -1
    mode: Optional[str] = ""
    match_type: Optional[str] = ""


class SummonerFilter(BaseFilter):
    puuid: Optional[str] = ""
    accountId: Optional[str] = ""
    summonerLevel: Optional[int] = -1


def parse_match_timeline_filter(filter_obj: BaseMatchFilter) -> Dict[str, Any]:
    filter_dict: Dict[str, Any] = {}

    if filter_obj.participant_puuids:
        filter_dict["metadata.participants"] = {"$all": filter_obj.participant_puuids}
    if len(filter_obj.match_ids):
        filter_dict["metadata.matchId"] = {"$in": filter_obj.match_ids}
    if filter_obj.queue != -1:
        filter_dict["info.queueId"] = filter_obj.queue
    if len(filter_obj.mode) > 0:
        filter_dict["info.gameMode"] = filter_obj.mode
    if len(filter_obj.match_type) > 0:
        filter_dict["info.gameType"] = filter_obj.match_type

    return filter_dict


class DBHelper:
    _instance: Any = None
    _lock: Lock = Lock()
    mongo_client: AsyncIOMotorClient[Mapping[str, Any]]
    database: AsyncIOMotorDatabase[Mapping[str, Any]]
    match_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    summoner_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    timeline_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    champion_collection: AsyncIOMotorCollection[Mapping[str, Any]]

    def __new__(cls) -> Any:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    load_dotenv()

                    # Initialize MongoDB Connection
                    mongodb_connection_string = os.getenv("MONGODB_CONNECTION_STRING")
                    if mongodb_connection_string:
                        cls._instance.mongo_client = AsyncIOMotorClient(
                            mongodb_connection_string
                        )
                        cls._instance.database = (
                            cls._instance.mongo_client.get_database("cnap")
                        )
                        cls._instance.match_collection = (
                            cls._instance.database.get_collection("match_v5")
                        )
                        cls._instance.summoner_collection = (
                            cls._instance.database.get_collection("summoner")
                        )
                        cls._instance.timeline_collection = (
                            cls._instance.database.get_collection("timeline_v5")
                        )
                        cls._instance.champion_collection = (
                            cls._instance.database.get_collection("champion")
                        )

                    else:
                        raise ValueError(
                            "No MongoDB Connection String found in Environment"
                        )
        return cls._instance

    async def disconnect(self):
        self.mongo_client.close()
        app_logger.debug("Disconnected from MongoDB")

    async def init_indexes(self):
        try:
            await self.summoner_collection.create_index("puuid", unique=True)
            app_logger.debug("Created index on summoner.puuid")

            await self.match_collection.create_index("metadata.matchId", unique=True)
            app_logger.debug("Created index on match_v5.metadata.matchId")

            await self.match_collection.create_index("info.gameCreation", unique=False)
            app_logger.debug("Created index on match_v5.info.gameCreation")

            app_logger.debug("All indexes created successfully")
        except Exception as error:
            app_logger.error(f"Error creating indexes: {error}")

    async def get_non_existing_ids(
        self,
        ids: List[str],
        entity_name: str = Literal["MatchV5", "TimelineV5"],
        id_field: str = "metadata.matchId",
    ) -> List[str]:
        try:
            if not ids:
                return []

            ids_set = set(ids)
            if entity_name == "MatchV5":
                existing_ids = await self.match_collection.distinct(
                    id_field, {id_field: {"$in": list(ids_set)}}
                )
            elif entity_name == "TimelineV5":
                existing_ids = await self.timeline_collection.distinct(
                    id_field, {id_field: {"$in": list(ids_set)}}
                )
            else:
                raise ValueError(f"Invalid entity name: {entity_name}")

            non_existing_ids = list(ids_set - set(existing_ids))
            app_logger.debug(
                f"{len(existing_ids)} of {len(ids_set)} {entity_name} were already present in the database"
            )
            return non_existing_ids

        except Exception as error:
            app_logger.error(
                f"Error while checking for existing {entity_name.lower()} ids: {error}"
            )
            return []

    async def update_match_timeline(
        self,
        documents: List[Dict],
        entity_name: str = Literal["MatchV5", "TimelineV5"],
        id_field: str = "metadata.matchId",
    ) -> bool:
        try:
            bulk_ops = [
                UpdateOne(
                    {id_field: doc["metadata"]["matchId"]}, {"$set": doc}, upsert=True
                )
                for doc in documents
            ]

            result: BulkWriteResult
            if entity_name == "MatchV5":
                result = await self.match_collection.bulk_write(bulk_ops)
            elif entity_name == "TimelineV5":
                result = await self.timeline_collection.bulk_write(bulk_ops)
            else:
                raise ValueError(f"Invalid entity name: {entity_name}")

            app_logger.debug(
                f"Upserted {result.upserted_count}, modified {result.modified_count} "
                f"and inserted {result.inserted_count} {entity_name} data"
            )
            return True

        except Exception as error:
            app_logger.error(f"Error uploading {entity_name} to MongoDB: {error}")
            return False

    async def get_matches_v5(self, match_filter: BaseMatchFilter) -> List[Dict]:
        try:
            db_filter = parse_match_timeline_filter(match_filter)
            app_logger.debug(f"Getting Match data from DB [{db_filter}]")

            cursor = (
                self.match_collection.find(db_filter, {"_id": 0})
                .sort("info.gameCreation", -1)
                .skip(match_filter.offset)
                .limit(match_filter.limit)
            )
            return await cursor.to_list(length=None)
        except Exception as error:
            app_logger.error("Error getting MatchArchive with MongoDB: ", error)
            return []

    async def get_summoner_match_history(
        self, history_filter: BaseMatchFilter
    ) -> List[Dict[str, Any]]:
        try:

            db_filter = parse_match_timeline_filter(history_filter)
            app_logger.debug(f"Getting Summoner History data from DB [{db_filter}]")
            agg: Sequence = [
                {"$match": db_filter},
                {"$sort": {"info.gameCreation": -1}},
                {"$skip": history_filter.offset},
                {"$limit": history_filter.limit},
                {
                    "$set": {
                        "info.participants": {
                            "$filter": {
                                "input": "$info.participants",
                                "as": "participant",
                                "cond": {
                                    "$all": [
                                        [
                                            "$$participant.puuid",
                                            history_filter.participant_puuids,
                                        ]
                                    ]
                                },
                            }
                        }
                    }
                },
                {"$project": {"_id": 0}},
            ]
            cursor = self.match_collection.aggregate(agg)
            return await cursor.to_list(length=None)
        except Exception as error:
            app_logger.error(
                f"Error getting MatchArchive for Summoner [{history_filter.participant_puuids}] History with MongoDB: {error}"
            )
            return []

    async def get_summoners(self, summoner_filter: SummonerFilter) -> List[SummonerDTO]:
        try:
            db_filter: Dict[str, Any] = {}

            if len(summoner_filter.puuid) > 0:
                db_filter["puuid"] = summoner_filter.puuid
            if len(summoner_filter.accountId) > 0:
                db_filter["accountId"] = summoner_filter.accountId
            if summoner_filter.summonerLevel != -1:
                db_filter["summonerLevel"] = summoner_filter.summonerLevel

            app_logger.debug("Getting Summoner data from DB")

            cursor = (
                self.summoner_collection.find(db_filter, {"_id": 0})
                .skip(summoner_filter.offset)
                .limit(summoner_filter.limit)
            )
            summoners_raw = await cursor.to_list(length=None)
            return [SummonerDTO.model_validate(summoner) for summoner in summoners_raw]
        except Exception as error:
            app_logger.error("Error getting Summoners with MongoDB: ", error)
            return []

    async def update_summoners(self, summoners: List[SummonerDTO]) -> bool:
        try:
            bulk_ops = [
                UpdateOne(
                    {"puuid": summoner.puuid},
                    {"$set": summoner.model_dump()},
                    upsert=True,
                )
                for summoner in summoners
            ]

            result = await self.summoner_collection.bulk_write(bulk_ops)
            app_logger.debug(
                f"Upserted {result.upserted_count} modified {result.modified_count} Inserted {result.inserted_count} summoner data"
            )
            return True
        except Exception as error:
            app_logger.error("Error uploading summoners to MongoDB: ", error)
            return False

    async def insert_champion_data(self, champions: List[ChampionDataDTO]) -> bool:
        try:
            bulk_ops = [
                UpdateOne(
                    {"id": champion.id}, {"$set": champion.model_dump()}, upsert=True
                )
                for champion in champions
            ]

            result = await self.champion_collection.bulk_write(bulk_ops)
            app_logger.debug(
                f"Upserted {result.upserted_count} modified {result.modified_count} Inserted {result.inserted_count} champion data"
            )
            return True
        except Exception as error:
            app_logger.error("Error uploading champions to MongoDB: ", error)
            return False


async def main():
    dbh = DBHelper()
    await dbh.init_indexes()


if __name__ == "__main__":
    asyncio.run(main())
