import asyncio
from datetime import datetime

from helpers.DBHelper import DBHelper
from helpers.RiotHelper import RiotHelper


class MainTask:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()

    async def update_match_data(self, offset=0, count=69):
        existing_summoners = await self.db_helper.get_summoners()
        if not existing_summoners:
            print(
                "No Summoner data available to update match history. Stopping the loop"
            )
            return

        for summoner in existing_summoners:
            print(f"Updating Match Data for Summoner [{summoner['puuid']}]")
            riot_match_ids = await self.riot_helper.get_match_list_riot(
                summoner, count, offset
            )
            filtered_ids = await self.db_helper.get_non_existing_match_ids(
                riot_match_ids
            )
            if len(filtered_ids) == 0:
                print(f"No new matches for summoner [{summoner['puuid']}]")
            else:
                match_data = []
                for match_id in filtered_ids:
                    match = await self.riot_helper.get_match_riot(match_id)
                    if match:
                        match_data.append(match)
                await self.db_helper.update_matches(match_data)

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
            print(f"INSERTING WITH I = {i}")
            await self.update_match_data(i, 95)

    async def interval_update(self, iteration, interval_time):
        print(f"UPDATING MATCH DATA [{iteration}]: {datetime.now().isoformat()}")
        iteration += 1
        if iteration == 10:
            print(f"UPDATING SUMMONER DATA: {datetime.now().isoformat()}")
            await self.update_summoner_data()
            iteration = 0
            print(f"UPDATED SUMMONER DATA: {datetime.now().isoformat()}")
        await self.update_match_data(0, 69)
        print(f"UPDATED MATCH DATA [{iteration}]: {datetime.now().isoformat()}")
        await asyncio.sleep(interval_time / 1000)  # Convert milliseconds to seconds
        await self.interval_update(iteration, interval_time)


async def main():
    task = MainTask()
    await task.update_match_data(0, 2)


if __name__ == "__main__":
    asyncio.run(main())
