import asyncio

from helpers.DBHelper import DBHelper
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper
from models.ChampionDTO import ChampionDTO
from models.ItemDTO import ItemDTO


class GameDataTask:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()

    async def update_items(self):
        items = await self.riot_helper.get_items()
        if len(items) <= 0:
            app_logger.error("No items found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                items,
                "id",
                self.db_helper.item_collection,
                data_name="Item",
                validator=ItemDTO,
            )
            app_logger.debug("Items updated")

    async def update_champions(self):
        champions = await self.riot_helper.get_champions()
        if len(champions) <= 0:
            app_logger.error("No champions found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                champions,
                "id",
                self.db_helper.champion_collection,
                data_name="champion",
                validator=ChampionDTO,
            )
            app_logger.debug("Champions updated")

    async def update_game_modes(self):
        game_modes = await self.riot_helper.get_game_modes()
        if len(game_modes) <= 0:
            app_logger.error("No game modes found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                game_modes,
                "gameMode",
                self.db_helper.game_modes_collection,
                data_name="game mode",
            )
            app_logger.debug("Game modes updated")

    async def update_game_types(self):
        game_types = await self.riot_helper.get_game_types()
        if len(game_types) <= 0:
            app_logger.error("No game types found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                game_types,
                "gametype",
                self.db_helper.game_types_collection,
                data_name="game type",
            )
            app_logger.debug("Game types updated")

    async def update_maps(self):
        maps = await self.riot_helper.get_maps()
        if len(maps) <= 0:
            app_logger.error("No maps found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                maps,
                "mapId",
                self.db_helper.maps_collection,
                data_name="map",
            )
            app_logger.debug("Maps updated")

    async def update_queues(self):
        queues = await self.riot_helper.get_queues()
        if len(queues) <= 0:
            app_logger.error("No queues found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                queues,
                "queueId",
                self.db_helper.queues_collection,
                data_name="queue",
            )
            app_logger.debug("Queues updated")


if __name__ == "__main__":

    async def main():
        game_data_task = GameDataTask()
        await game_data_task.update_items()
        await game_data_task.update_champions()
        await game_data_task.update_game_modes()
        await game_data_task.update_game_types()
        await game_data_task.update_maps()
        await game_data_task.update_queues()

    asyncio.run(main())
