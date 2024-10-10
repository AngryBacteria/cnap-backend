import asyncio
import os
from threading import Lock
from typing import List, Dict, Any, Union
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pydantic import BaseModel
from pymongo import UpdateOne

from interfaces.MatchV5DTO import MatchV5DTO
from interfaces.SummonerDTO import SummonerDTO


class MatchQueryFilter(BaseModel):
    # unique
    match_id: str = ""
    participant_puuids: List[str] = []
    # non unique
    queue: int = -1
    mode: str = ""
    match_type: str = ""
    game_version: str = ""
    offset: int = 0
    limit: int = 5


class SummonerHistoryFilter(BaseModel):
    # unique
    puuid: str = ""
    # non unique
    queue: int = -1
    mode: str = ""
    match_type: str = ""
    game_version: str = ""
    offset: int = 0
    limit: int = 20


def parse_filter_to_dict(
    filter_obj: Union[MatchQueryFilter, SummonerHistoryFilter]
) -> Dict[str, Any]:
    filter_dict: Dict[str, Any] = {}

    # Common fields for both filter types
    if hasattr(filter_obj, "queue") and filter_obj.queue != -1:
        filter_dict["info.queueId"] = filter_obj.queue
    if hasattr(filter_obj, "mode") and filter_obj.mode:
        filter_dict["info.gameMode"] = filter_obj.mode
    if hasattr(filter_obj, "match_type") and filter_obj.match_type:
        filter_dict["info.gameType"] = filter_obj.match_type
    if hasattr(filter_obj, "game_version") and filter_obj.game_version:
        filter_dict["info.gameVersion"] = filter_obj.game_version

    # Specific fields for MatchQueryFilter
    if isinstance(filter_obj, MatchQueryFilter):
        if filter_obj.match_id:
            filter_dict["metadata.matchId"] = filter_obj.match_id
        if filter_obj.participant_puuids:
            filter_dict["metadata.participants"] = {
                "$all": filter_obj.participant_puuids
            }

    # Specific fields for SummonerHistoryFilter
    elif isinstance(filter_obj, SummonerHistoryFilter):
        if filter_obj.puuid:
            filter_dict["metadata.participants"] = {"$all": [filter_obj.puuid]}

    return filter_dict


class DBHelper:
    _instance: Any = None
    _lock: Lock = Lock()

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
                    else:
                        raise ValueError(
                            "No MongoDB Connection String found in Environment"
                        )
        return cls._instance

    async def disconnect(self):
        self.mongo_client.close()
        print("Disconnected from MongoDB")

    async def init_indexes(self):
        try:
            await self.summoner_collection.create_index("puuid", unique=True)
            print("Created index on summoner.puuid")

            await self.match_collection.create_index("metadata.matchId", unique=True)
            print("Created index on match_v5.metadata.matchId")

            await self.match_collection.create_index("metadata.participants")
            print("Created index on match_v5.info.participants")

            print("All indexes created successfully")
        except Exception as error:
            print(f"Error creating indexes: {error}")

    async def get_non_existing_match_ids(self, ids: List[str]):
        try:
            if not ids:
                return []

            # Convert input ids to a set for faster lookup
            ids_set = set(ids)

            # Use distinct() to get only unique matchIds that exist in the database
            existing_ids = await self.match_collection.distinct(
                "metadata.matchId", {"metadata.matchId": {"$in": list(ids_set)}}
            )

            # Use set difference to find non-existing ids
            non_existing_ids = list(ids_set - set(existing_ids))

            print(
                f"{len(existing_ids)} of {len(ids)} Matches were already present in the database"
            )
            return non_existing_ids
        except Exception as error:
            print("Could not check for existing match ids: ", error)
            return []

    async def update_matches(self, matches: List[MatchV5DTO]):
        try:
            bulk_ops = [
                UpdateOne(
                    {"metadata.matchId": match["metadata"]["matchId"]},
                    {"$set": match},
                    upsert=True,
                )
                for match in matches
            ]
            result = await self.match_collection.bulk_write(bulk_ops)
            print(
                f"Upserted {result.upserted_count} and modified {result.modified_count} summoner data Inserted {result.inserted_count} Match data"
            )
            return True
        except Exception as error:
            print("Error uploading matches to MongoDB: ", error)
            return False

    async def get_matches_v5(self, match_filter: MatchQueryFilter) -> List[MatchV5DTO]:
        try:
            db_filter = parse_filter_to_dict(match_filter)
            print(f"Getting Match data from DB [{db_filter}]")

            cursor = (
                self.match_collection.find(db_filter, {"_id": 0})
                .skip(match_filter.offset)
                .limit(match_filter.limit)
            )
            return await cursor.to_list(length=None)
        except Exception as error:
            print("Error getting MatchArchive with MongoDB: ", error)
            return []

    async def get_summoner_match_history(
        self, history_filter: SummonerHistoryFilter
    ) -> List[Dict[str, Any]]:
        try:

            db_filter = parse_filter_to_dict(history_filter)
            print(f"Getting Summoner History data from DB [{db_filter}]")
            agg = [
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
                                    "$eq": ["$$participant.puuid", history_filter.puuid]
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
            print(
                f"Error getting MatchArchive for Summoner [{history_filter.puuid}] History with MongoDB: {error}"
            )
            return []

    async def get_summoners(
        self, name: str = "", puuid: str = "", skip: int = 0, limit: int = 25
    ) -> List[SummonerDTO]:
        try:
            db_filter: Dict[str, Any] = {}
            if name:
                db_filter["name"] = name
            if puuid:
                db_filter["puuid"] = puuid
            print(f"Getting Summoner data from DB")

            cursor = (
                self.summoner_collection.find(db_filter, {"_id": 0})
                .skip(skip)
                .limit(limit)
            )
            return await cursor.to_list(length=None)
        except Exception as error:
            print("Error getting Summoners with MongoDB: ", error)
            return []

    async def update_summoners(self, summoners: List[SummonerDTO]) -> bool:
        try:
            bulk_ops = [
                UpdateOne({"puuid": summoner["puuid"]}, {"$set": summoner}, upsert=True)
                for summoner in summoners
            ]

            result = await self.summoner_collection.bulk_write(bulk_ops)
            print(
                f"Upserted {result.upserted_count} modified {result.modified_count} Inserted {result.inserted_count} summoner data"
            )
            return True
        except Exception as error:
            print("Error uploading summoners to MongoDB: ", error)
            return False


async def main():
    dbh = DBHelper()
    await dbh.init_indexes()


if __name__ == "__main__":
    asyncio.run(main())
