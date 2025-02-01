import asyncio

from helpers.DBHelper import DBHelper, CollectionName
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper


# TODO summoner spells, summoner icons


class GameDataTask:
    def __init__(self) -> None:
        self.db_helper = DBHelper.get_instance()
        self.riot_helper = RiotHelper.get_instance()

    async def update_champions(self) -> None:
        champions = await self.riot_helper.get_champions()
        if len(champions) <= 0:
            app_logger.error("No champions found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                champions,
                "id",
                CollectionName.CHAMPION,
                data_name="champion",
                validator=None,
            )
            app_logger.debug("Champions updated")

    async def update_game_modes(self) -> None:
        game_modes = await self.riot_helper.get_game_modes()
        if len(game_modes) <= 0:
            app_logger.error("No game modes found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                game_modes,
                "gameMode",
                CollectionName.GAME_MODE,
                data_name="game mode",
            )
            app_logger.debug("Game modes updated")

    async def update_game_types(self) -> None:
        game_types = await self.riot_helper.get_game_types()
        if len(game_types) <= 0:
            app_logger.error("No game types found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                game_types,
                "gametype",
                CollectionName.GAME_TYPE,
                data_name="game type",
            )
            app_logger.debug("Game types updated")

    async def update_items(self) -> None:
        items = await self.riot_helper.get_items()
        if len(items) <= 0:
            app_logger.error("No items found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                items,
                "id",
                CollectionName.ITEM,
                data_name="Item",
                validator=None,
            )
            app_logger.debug("Items updated")

    async def update_maps(self) -> None:
        maps = await self.riot_helper.get_maps()
        if len(maps) <= 0:
            app_logger.error("No maps found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                maps,
                "mapId",
                CollectionName.MAP,
                data_name="map",
            )
            app_logger.debug("Maps updated")

    async def update_queues(self) -> None:
        queues = await self.riot_helper.get_queues()
        if len(queues) <= 0:
            app_logger.error("No queues found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                queues,
                "queueId",
                CollectionName.QUEUE,
                data_name="queue",
            )
            app_logger.debug("Queues updated")

    async def update_summoner_icons(self) -> None:
        summoner_icons = await self.riot_helper.get_summoner_icons()
        if len(summoner_icons) <= 0:
            app_logger.error("No summoner icons found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                summoner_icons,
                "id",
                CollectionName.SUMMONER_ICON,
                data_name="summoner_icon",
            )
            app_logger.debug("Summoner icons updated")

    async def update_summoner_spells(self) -> None:
        summoner_spells = await self.riot_helper.get_summoner_spells()
        if len(summoner_spells) <= 0:
            app_logger.error("No summoner spells found in CDN response")

        else:
            await self.db_helper.generic_upsert(
                summoner_spells,
                "id",
                CollectionName.SUMMONER_SPELL,
                data_name="summoner_spell",
            )
            app_logger.debug("Summoner spells updated")

    async def update_everything(self) -> None:
        await self.update_champions()
        await self.update_game_modes()
        await self.update_game_types()
        await self.update_items()
        await self.update_maps()
        await self.update_queues()
        await self.update_summoner_icons()
        await self.update_summoner_spells()


if __name__ == "__main__":

    async def main() -> None:
        game_data_task = GameDataTask()
        await game_data_task.update_everything()

    asyncio.run(main())
