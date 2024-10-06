import asyncio
import os
from threading import Lock
from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pymongo import UpdateOne

from interfaces.MatchV5DTO import MatchV5DTO
from interfaces.SummonerDTO import SummonerDTO


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

    async def get_matches_v5(
        self,
        match_id: str = "",
        queue: int = 0,
        mode: str = "",
        match_type: str = "",
        game_version: str = "",
        participant_ids: List[str] = [],
        offset: int = 0,
        limit: int = 25,
    ) -> List[MatchV5DTO]:
        try:
            db_filter: Dict[str, Any] = {}
            if match_id:
                db_filter["metadata.matchId"] = match_id
            if queue:
                db_filter["info.queueId"] = queue
            if mode:
                db_filter["info.gameMode"] = mode
            if match_type:
                db_filter["info.gameType"] = match_type
            if game_version:
                db_filter["info.gameVersion"] = game_version
            if participant_ids and len(participant_ids) > 0:
                db_filter["metadata.participants"] = {"$in": [participant_ids]}
            print(f"Getting Match data from DB [{db_filter}]")

            cursor = self.match_collection.find(db_filter, {'_id': 0}).skip(offset).limit(limit)
            return await cursor.to_list(length=None)
        except Exception as error:
            print("Error getting MatchArchive with MongoDB: ", error)
            return []

    async def get_summoner_match_history(
        self, puuid: str, limit: int = 20, skip: int = 0
    ) -> List[Dict[str, Any]]:
        try:
            agg = [
                {"$match": {"metadata.participants": {"$all": [puuid]}}},
                {"$sort": {"info.gameCreation": -1}},
                {"$skip": skip},
                {"$limit": limit},
                {
                    "$set": {
                        "info.participants": {
                            "$filter": {
                                "input": "$info.participants",
                                "as": "participant",
                                "cond": {"$eq": ["$$participant.puuid", puuid]},
                            }
                        }
                    }
                },
            ]
            cursor = self.match_collection.aggregate(agg)
            return await cursor.to_list(length=None)
        except Exception as error:
            print(
                f"Error getting MatchArchive for Summoner [{puuid}] with MongoDB: {error}"
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

            cursor = self.summoner_collection.find(db_filter, {'_id': 0}).skip(skip).limit(limit)
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
