import asyncio

from helpers.DBHelper import DBHelper, SummonerFilter, CollectionName
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper


class MatchTasks:
    def __init__(self) -> None:
        self.db_helper = DBHelper.get_instance()
        self.riot_helper = RiotHelper.get_instance()

    async def update_match_data(
        self, count: int = 69, offset: int = 0, puuid: str = ""
    ) -> None:
        existing_summoners = await self.db_helper.get_summoners(
            SummonerFilter(limit=10000, puuid=puuid)
        )
        if not existing_summoners or len(existing_summoners) == 0:
            app_logger.debug(
                "No Summoner data available to update match history. Stopping the loop"
            )
            return

        for summoner in existing_summoners:
            riot_match_ids = await self.riot_helper.get_match_list(
                summoner.puuid, count, offset
            )
            filtered_match_ids = await self.db_helper.get_non_existing_match_ids(
                riot_match_ids, "MatchV5", "metadata.matchId"
            )
            filtered_timeline_ids = await self.db_helper.get_non_existing_match_ids(
                riot_match_ids, "TimelineV5", "metadata.matchId"
            )

            match_data = []
            for match_id in filtered_match_ids:
                match = await self.riot_helper.get_match(match_id)
                if match:
                    match_data.append(match)
            if match_data and len(match_data) > 0:
                await self.db_helper.generic_upsert(
                    match_data,
                    "metadata.matchId",
                    CollectionName.MATCH,
                    "Match",
                    None,
                )

            timeline_data = []
            for timeline_id in filtered_timeline_ids:
                timeline = await self.riot_helper.get_timeline(timeline_id)
                if timeline:
                    timeline_data.append(timeline)
            if timeline_data and len(timeline_data) > 0:
                await self.db_helper.generic_upsert(
                    timeline_data,
                    "metadata.matchId",
                    CollectionName.TIMELINE,
                    "Timeline",
                    None,
                )

    async def fill_match_data(self, puuid: str = "") -> None:
        for i in range(0, 2000, 95):
            app_logger.debug(f"INSERTING WITH I = {i}")
            await self.update_match_data(95, i, puuid)


async def main() -> None:
    match_tasks = MatchTasks()
    await match_tasks.fill_match_data(
        puuid="sUl1DJpnjR6C4eSv5O_r2tgnEfs_5o-5GSTG3Xs6v8mYFIIg-uC1CAZDYOP02xh6Yx9g5EE92KuuVA"
    )


if __name__ == "__main__":
    asyncio.run(main())
