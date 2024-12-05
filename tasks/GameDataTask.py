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
        items = await self.riot_helper.get_cdn_resource("items")
        if len(items) <= 0:
            app_logger.error("No items found in CDN response")

        await self.db_helper.generic_upsert(
            items,
            "id",
            self.db_helper.item_collection,
            data_name="Item",
            validator=ItemDTO,
        )
        app_logger.debug("Items updated")

    async def update_champions(self):
        champions = await self.riot_helper.get_cdn_resource("champions")
        if len(champions) <= 0:
            app_logger.error("No champions found in CDN response")

        await self.db_helper.generic_upsert(
            champions,
            "id",
            self.db_helper.champion_collection,
            data_name="champion",
            validator=ChampionDTO,
        )
        app_logger.debug("Champions updated")


if __name__ == "__main__":

    async def main():
        game_data_task = GameDataTask()
        await game_data_task.update_items()
        await game_data_task.update_champions()

    asyncio.run(main())
