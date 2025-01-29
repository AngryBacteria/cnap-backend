import asyncio
import os
from threading import Lock
from typing import Dict, Any, Mapping, Literal, Union, Type, TypeVar, overload, Sequence

from dotenv import load_dotenv
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
    AsyncIOMotorCollection,
)
from pydantic import BaseModel, Field
from pymongo import UpdateOne

from helpers.Logger import app_logger
from models.SummonerDTODB import SummonerDTODB


class BasicFilter(BaseModel):
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=5, ge=1, description="Maximum number of items to return")
    project: dict = Field(default={"_id": 0}, description="Fields to return")
    filter: dict = Field(default={}, description="Filter to apply")


class BasicMatchFilter(BaseModel):
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=5, ge=1, description="Maximum number of items to return")
    participant_puuids: list[str] = Field(
        default=[], description="List of participant PUUIDs to filter by"
    )
    match_ids: list[str] = Field(
        default=[], description="List of match IDs to filter by"
    )
    queue: int = Field(default=-1, description="Queue ID to filter by")
    mode: str = Field(default="", description="Game mode to filter by")
    match_type: str = Field(default="", description="Match type to filter by")
    timeline: bool = Field(default=False, description="Whether to fetch timeline data")


class SummonerFilter(BaseModel):
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=5, ge=1, description="Maximum number of items to return")
    puuid: str = Field(default="", description="Summoner PUUID to filter by")
    accountId: str = Field(default="", description="Account ID to filter by")
    summonerLevel: int = Field(default=-1, description="Summoner level to filter by")


def get_nested_value(item: Union[dict, BaseModel], nested_key: str) -> Any:
    """Helper function to get value from nested dictionary or Pydantic model using dot notation"""
    keys = nested_key.split(".")
    current: Union[Dict, BaseModel, Any] = item

    for key in keys:
        if isinstance(current, BaseModel):
            # Handle Pydantic models using getattr
            if not hasattr(current, key):
                raise ValueError(f"Invalid key {nested_key} for Pydantic model {item}")
            current = getattr(current, key)
        elif isinstance(current, dict):
            # Handle dictionaries using get
            current = current.get(key)
        else:
            raise ValueError(f"Invalid key {nested_key} for item {item}")

    if current is None:
        raise ValueError(f"Invalid key {nested_key} for item {item}")

    return current


# Make this shit more type safe
class DBHelper:
    _instance: Any = None
    _lock: Lock = Lock()
    mongo_client: AsyncIOMotorClient[Mapping[str, Any]]
    database: AsyncIOMotorDatabase[Mapping[str, Any]]
    # collections
    champion_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    game_mode_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    game_type_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    item_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    map_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    match_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    queue_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    summoner_collection: AsyncIOMotorCollection[Mapping[str, Any]]
    timeline_collection: AsyncIOMotorCollection[Mapping[str, Any]]

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
                        # collections
                        cls._instance.champion_collection = (
                            cls._instance.database.get_collection("champion")
                        )
                        cls._instance.game_mode_collection = (
                            cls._instance.database.get_collection("game_mode")
                        )
                        cls._instance.game_type_collection = (
                            cls._instance.database.get_collection("game_type")
                        )
                        cls._instance.item_collection = (
                            cls._instance.database.get_collection("item")
                        )
                        cls._instance.map_collection = (
                            cls._instance.database.get_collection("map")
                        )
                        cls._instance.match_collection = (
                            cls._instance.database.get_collection("match_v5")
                        )
                        cls._instance.queue_collection = (
                            cls._instance.database.get_collection("queue")
                        )
                        cls._instance.summoner_collection = (
                            cls._instance.database.get_collection("summoner")
                        )
                        cls._instance.timeline_collection = (
                            cls._instance.database.get_collection("timeline_v5")
                        )

                    else:
                        raise ValueError(
                            "No MongoDB Connection String found in Environment"
                        )
        return cls._instance

    async def disconnect(self):
        self.mongo_client.close()
        app_logger.debug("Disconnected from MongoDB")

    async def test_connection(self) -> bool:
        """
        Test MongoDB connection by attempting to execute a simple command.
        Returns True if connection is successful, False otherwise.
        """
        try:
            # Ping the database
            await self.database.command("ping")
            app_logger.info("Successfully connected to MongoDB")
            return True
        except Exception as error:
            app_logger.error(
                f"MongoDB connection test failed. Review your connection string and internet connection: {error}"
            )
            return False

    async def init_indexes(self):
        try:
            await self.summoner_collection.create_index("puuid", unique=True)
            app_logger.debug("Created summoner indexes")

            await self.match_collection.create_index("metadata.matchId", unique=True)
            await self.match_collection.create_index(
                "metadata.participants", unique=False
            )
            await self.match_collection.create_index("info.gameCreation", unique=False)
            await self.match_collection.create_index("info.queueId", unique=False)
            await self.match_collection.create_index("info.gameMode", unique=False)
            await self.match_collection.create_index("info.gameType", unique=False)
            app_logger.debug("Created match indexes")

            await self.timeline_collection.create_index("metadata.matchId", unique=True)
            await self.timeline_collection.create_index(
                "metadata.participants", unique=False
            )
            app_logger.debug("Created timeline indexes")

            await self.champion_collection.create_index("id", unique=True)
            await self.champion_collection.create_index("key", unique=True)
            await self.game_mode_collection.create_index("gameMode", unique=True)
            await self.game_type_collection.create_index("gametype", unique=True)
            await self.item_collection.create_index("id", unique=True)
            await self.map_collection.create_index("mapId", unique=True)
            await self.queue_collection.create_index("queueId", unique=True)
            app_logger.debug("Created static data indexes")

            app_logger.debug("All indexes created successfully")

            return True
        except Exception as error:
            app_logger.error(f"Error creating indexes: {error}")

    async def get_non_existing_match_ids(
        self,
        ids: list[str],
        entity_name: Literal["MatchV5", "TimelineV5"],
        id_field: str = "metadata.matchId",
    ) -> list[str]:
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

    async def get_matches(self, match_filter: BasicMatchFilter) -> list[Dict]:
        identifier = "Timeline" if match_filter.timeline else "Match"
        try:
            db_filter: Dict[str, Any] = {}
            if match_filter.participant_puuids:
                db_filter["metadata.participants"] = {
                    "$all": match_filter.participant_puuids
                }
            if len(match_filter.match_ids):
                db_filter["metadata.matchId"] = {"$in": match_filter.match_ids}
            if match_filter.queue != -1:
                db_filter["info.queueId"] = match_filter.queue
            if len(match_filter.mode) > 0:
                db_filter["info.gameMode"] = match_filter.mode
            if len(match_filter.match_type) > 0:
                db_filter["info.gameType"] = match_filter.match_type

            collection = (
                self.timeline_collection
                if match_filter.timeline
                else self.match_collection
            )
            cursor = (
                collection.find(db_filter, {"_id": 0})
                .sort("info.gameCreation", -1)
                .skip(match_filter.offset)
                .limit(match_filter.limit)
            )
            cursor_list = await cursor.to_list(length=None)
            app_logger.debug(f"Got {len(cursor_list)} {identifier} objects from DB")
            return cursor_list
        except Exception as error:
            app_logger.error(f"Error getting {identifier} with MongoDB: ", error)
            return []

    async def get_summoners(
        self, summoner_filter: SummonerFilter
    ) -> list[SummonerDTODB]:
        try:
            db_filter: Dict[str, Any] = {}

            if len(summoner_filter.puuid) > 0:
                db_filter["puuid"] = summoner_filter.puuid
            if len(summoner_filter.accountId) > 0:
                db_filter["accountId"] = summoner_filter.accountId
            if summoner_filter.summonerLevel != -1:
                db_filter["summonerLevel"] = summoner_filter.summonerLevel

            cursor = (
                self.summoner_collection.find(db_filter, {"_id": 0})
                .skip(summoner_filter.offset)
                .limit(summoner_filter.limit)
            )
            summoners_raw = await cursor.to_list(length=None)
            app_logger.debug(f"Got {len(summoners_raw)} Summoner objects from DB")
            return [
                SummonerDTODB.model_validate(summoner) for summoner in summoners_raw
            ]
        except Exception as error:
            app_logger.error("Error getting Summoners with MongoDB: ", error)
            return []

    GenericModel = TypeVar("GenericModel", bound=BaseModel)

    @overload
    async def generic_get(
        self, base_filter: BasicFilter, collection: AsyncIOMotorCollection
    ) -> list[dict]: ...

    @overload
    async def generic_get(
        self,
        base_filter: BasicFilter,
        collection: AsyncIOMotorCollection,
        validator: type[GenericModel],
    ) -> list[GenericModel]: ...

    async def generic_get(
        self,
        base_filter: BasicFilter,
        collection: AsyncIOMotorCollection,
        validator: type[GenericModel] | None = None,
    ) -> list[GenericModel] | list[Dict]:
        try:
            cursor = (
                collection.find(base_filter.filter, base_filter.project)
                .skip(base_filter.offset)
                .limit(base_filter.limit)
            )
            data_raw = await cursor.to_list(length=None)
            app_logger.debug(f"Got {len(data_raw)} objects from DB")

            if validator:
                return [validator.model_validate(data) for data in data_raw]
            else:
                return data_raw
        except Exception as error:
            app_logger.error("Error getting data with MongoDB: ", error)
            return []

    # TODO fix double validation
    async def generic_upsert(
        self,
        data: Union[Sequence[dict], Sequence[BaseModel]],
        key_field: str,
        collection: AsyncIOMotorCollection,
        data_name="Generic Data",
        validator: Type[BaseModel] | None = None,
    ) -> bool:
        try:
            if len(data) == 0:
                app_logger.debug(f"No {data_name} data to upsert")
                return False

            converted_data = [
                item.model_dump() if isinstance(item, BaseModel) else item
                for item in data
            ]

            if validator:
                [validator.model_validate(item) for item in converted_data]

            bulk_ops = [
                UpdateOne(
                    {key_field: get_nested_value(item, key_field)},
                    {"$set": item},
                    upsert=True,
                )
                for item in converted_data
            ]

            result = await collection.bulk_write(bulk_ops)
            app_logger.debug(
                f"Upserted {result.upserted_count} | Modified {result.modified_count} | Inserted {result.inserted_count} --> {data_name}"
            )
            return True
        except Exception as error:
            app_logger.error(f"Error uploading {data_name} to MongoDB: ", error)
            return False


async def main():
    dbh = DBHelper()
    await dbh.init_indexes()
    await dbh.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
