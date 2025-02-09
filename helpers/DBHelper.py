import asyncio

from typing import Literal, Union, Type, TypeVar, overload, Sequence

from motor.motor_asyncio import (
    AsyncIOMotorCollection,
)

from pymongo import UpdateOne
from helpers.Logger import app_logger
from models.GlobalPydanticConfig import BaseConfig


import os
from enum import Enum
from threading import Lock
from typing import Optional, Mapping, Any

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field
from models.ItemDTO import ItemDTO


class CollectionName(str, Enum):
    CHAMPION = "champion"
    GAME_MODE = "game_mode"
    GAME_TYPE = "game_type"
    ITEM = "item"
    MAP = "map"
    MATCH = "match_v5"
    QUEUE = "queue"
    SUMMONER = "summoner"
    SUMMONER_ICON = "summoner_icon"
    SUMMONER_SPELL = "summoner_spell"
    TIMELINE = "timeline_v5"


class BasicFilter(BaseConfig):
    offset: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=5, ge=1, description="Maximum number of items to return")
    project: dict[str, int] = Field(default={"_id": 0}, description="Fields to return")
    filter: dict[str, Any] = Field(default={}, description="Filter to apply")


def get_nested_value(item: Union[dict[str, Any], BaseModel], nested_key: str) -> Any:
    """Helper function to get value from nested dictionary or Pydantic model using dot notation"""
    keys = nested_key.split(".")
    current: Union[dict[str, Any], BaseModel, Any] = item

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


class DBHelper:
    _instance: Optional["DBHelper"] = None
    _lock: Lock = Lock()
    _initialized: bool = False
    mongo_client: AsyncIOMotorClient[Mapping[str, Any]]
    database: AsyncIOMotorDatabase[Mapping[str, Any]]

    def __init__(self) -> None:
        raise RuntimeError("Call get_instance() instead")

    def __new__(cls) -> "DBHelper":
        raise RuntimeError("Call get_instance() instead")

    @classmethod
    def get_instance(cls) -> "DBHelper":
        # Double-checked locking pattern
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
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

                    else:
                        raise ValueError(
                            "No MongoDB Connection String found in Environment"
                        )
        return cls._instance

    def get_collection(
        self, name: CollectionName
    ) -> AsyncIOMotorCollection[Mapping[str, Any]]:
        return self.database.get_collection(name.value)

    async def disconnect(self) -> None:
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

    async def init_indexes(self) -> bool:
        try:
            await self.get_collection(CollectionName.SUMMONER).create_index(
                "puuid", unique=True
            )
            app_logger.debug("Created summoner indexes")

            await self.get_collection(CollectionName.MATCH).create_index(
                "metadata.matchId", unique=True
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "metadata.participants", unique=False
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "info.gameCreation", unique=False
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "info.queueId", unique=False
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "info.gameMode", unique=False
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "info.gameType", unique=False
            )
            await self.get_collection(CollectionName.MATCH).create_index(
                "info.participants.championId", unique=False
            )
            app_logger.debug("Created match indexes")

            await self.get_collection(CollectionName.TIMELINE).create_index(
                "metadata.matchId", unique=True
            )
            await self.get_collection(CollectionName.TIMELINE).create_index(
                "metadata.participants", unique=False
            )
            app_logger.debug("Created timeline indexes")

            await self.get_collection(CollectionName.CHAMPION).create_index(
                "id", unique=True
            )
            await self.get_collection(CollectionName.GAME_MODE).create_index(
                "gameMode", unique=True
            )
            await self.get_collection(CollectionName.GAME_TYPE).create_index(
                "gametype", unique=True
            )
            await self.get_collection(CollectionName.ITEM).create_index(
                "id", unique=True
            )
            await self.get_collection(CollectionName.MAP).create_index(
                "mapId", unique=True
            )
            await self.get_collection(CollectionName.QUEUE).create_index(
                "queueId", unique=True
            )
            app_logger.debug("Created static data indexes")

            app_logger.debug("All indexes created successfully")
            return True

        except Exception as error:
            app_logger.error(f"Error creating indexes: {error}")
            return False

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
                existing_ids = await self.get_collection(CollectionName.MATCH).distinct(
                    id_field, {id_field: {"$in": list(ids_set)}}
                )
            elif entity_name == "TimelineV5":
                existing_ids = await self.get_collection(
                    CollectionName.TIMELINE
                ).distinct(id_field, {id_field: {"$in": list(ids_set)}})
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

    GenericModel = TypeVar("GenericModel", bound=BaseModel)

    @overload
    async def generic_get(
        self, base_filter: BasicFilter, collection_name: CollectionName
    ) -> list[dict[str, Any]]: ...

    @overload
    async def generic_get(
        self,
        base_filter: BasicFilter,
        collection_name: CollectionName,
        validator: type[GenericModel],
    ) -> list[GenericModel]: ...

    async def generic_get(
        self,
        base_filter: BasicFilter,
        collection_name: CollectionName,
        validator: type[GenericModel] | None = None,
    ) -> list[GenericModel] | list[dict[str, Any]]:
        try:
            cursor = (
                self.get_collection(collection_name)
                .find(base_filter.filter, base_filter.project)
                .skip(base_filter.offset)
                .limit(base_filter.limit)
            )
            data_raw = await cursor.to_list(length=None)
            app_logger.debug(
                f"Got {len(data_raw)} {collection_name.value} objects from DB"
            )

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
        data: Union[Sequence[dict[str, Any]], Sequence[BaseModel]],
        key_field: str,
        collection_name: CollectionName,
        data_name: str = "Generic Data",
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

            result = await self.get_collection(collection_name).bulk_write(bulk_ops)
            app_logger.debug(
                f"Upserted {result.upserted_count} | Modified {result.modified_count} | Inserted {result.inserted_count} --> {data_name}"
            )
            return True
        except Exception as error:
            app_logger.error(f"Error uploading {data_name} to MongoDB: ", error)
            return False


async def main() -> None:
    dbh = DBHelper.get_instance()
    items = await dbh.generic_get(
        BasicFilter(limit=100000), CollectionName.ITEM, validator=ItemDTO
    )
    print(items)


if __name__ == "__main__":
    asyncio.run(main())
