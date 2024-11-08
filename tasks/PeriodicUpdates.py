import asyncio
from datetime import datetime

from helpers.DBHelper import DBHelper
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper


class MainTask:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()

    async def update_match_data(self, count=69, offset=0):
        existing_summoners = await self.db_helper.get_summoners()
        if not existing_summoners or len(existing_summoners) == 0:
            app_logger.debug(
                "No Summoner data available to update match history. Stopping the loop"
            )
            return

        for summoner in existing_summoners:
            app_logger.debug(f"Updating Match Data for Summoner [{summoner['puuid']}]")
            riot_match_ids = await self.riot_helper.get_match_list_riot(
                summoner, count, offset
            )
            filtered_match_ids = await self.db_helper.get_non_existing_ids(
                riot_match_ids, "MatchV5", "metadata.matchId"
            )
            filtered_timeline_ids = await self.db_helper.get_non_existing_ids(
                riot_match_ids, "TimelineV5", "metadata.matchId"
            )

            if len(filtered_match_ids) == 0:
                app_logger.debug(f"No new matches for summoner [{summoner['puuid']}]")
            if len(filtered_timeline_ids) == 0:
                app_logger.debug(f"No new timelines for summoner [{summoner['puuid']}]")

            match_data = []
            for match_id in filtered_match_ids:
                match = await self.riot_helper.get_match_riot(match_id)
                if match:
                    match_data.append(match)
            if match_data and len(match_data) > 0:
                await self.db_helper.update_matches(
                    match_data, "MatchV5", "metadata.matchId"
                )

            timeline_data = []
            for timeline_id in filtered_timeline_ids:
                timeline = await self.riot_helper.get_timeline_riot(timeline_id)
                if timeline:
                    timeline_data.append(timeline)
            if timeline_data and len(timeline_data) > 0:
                await self.db_helper.update_matches(
                    timeline_data, "TimelineV5", "metadata.matchId"
                )

    async def update_summoner_data(self):
        existing_summoners = await self.db_helper.get_summoners()
        if existing_summoners:
            new_summoners = []
            for summoner in existing_summoners:
                summoner_riot = await self.riot_helper.get_summoner_by_puuid_riot(
                    summoner["puuid"]
                )
                if summoner_riot:
                    new_summoners.append(summoner_riot)
            await self.db_helper.update_summoners(new_summoners)

    async def fill_match_data(self):
        for i in range(0, 2000, 95):
            app_logger.debug(f"INSERTING WITH I = {i}")
            await self.update_match_data(95, i)

    async def interval_update(self, iteration, interval_time):
        app_logger.debug(
            f"UPDATING MATCH DATA [{iteration}]: {datetime.now().isoformat()}"
        )
        iteration += 1
        if iteration == 10:
            app_logger.debug(f"UPDATING SUMMONER DATA: {datetime.now().isoformat()}")
            await self.update_summoner_data()
            iteration = 0
            app_logger.debug(f"UPDATED SUMMONER DATA: {datetime.now().isoformat()}")
        await self.update_match_data(69, 0)
        app_logger.debug(
            f"UPDATED MATCH DATA [{iteration}]: {datetime.now().isoformat()}"
        )
        await asyncio.sleep(interval_time)
        await self.interval_update(iteration, interval_time)


async def main():
    task = MainTask()
    await task.interval_update(0, 60 * 60)


if __name__ == "__main__":
    asyncio.run(main())
