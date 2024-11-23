from helpers.DBHelper import DBHelper, SummonerFilter
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper


# TODO add champion / item / new summoners updates
class MatchTasks:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()

    async def update_match_data(self, count=69, offset=0, puuid=""):
        existing_summoners = await self.db_helper.get_summoners(
            SummonerFilter(limit=10000, puuid=puuid)
        )
        if not existing_summoners or len(existing_summoners) == 0:
            app_logger.debug(
                "No Summoner data available to update match history. Stopping the loop"
            )
            return

        for summoner in existing_summoners:
            riot_match_ids = await self.riot_helper.get_match_list_riot(
                summoner.puuid, count, offset
            )
            filtered_match_ids = await self.db_helper.get_non_existing_ids(
                riot_match_ids, "MatchV5", "metadata.matchId"
            )
            filtered_timeline_ids = await self.db_helper.get_non_existing_ids(
                riot_match_ids, "TimelineV5", "metadata.matchId"
            )

            match_data = []
            for match_id in filtered_match_ids:
                match = await self.riot_helper.get_match_riot(match_id)
                if match:
                    match_data.append(match)
            if match_data and len(match_data) > 0:
                await self.db_helper.generic_upsert(
                    match_data,
                    "metadata.matchId",
                    self.db_helper.match_collection,
                    "Match",
                    None,
                )

            timeline_data = []
            for timeline_id in filtered_timeline_ids:
                timeline = await self.riot_helper.get_timeline_riot(timeline_id)
                if timeline:
                    timeline_data.append(timeline)
            if timeline_data and len(timeline_data) > 0:
                await self.db_helper.generic_upsert(
                    timeline_data,
                    "metadata.matchId",
                    self.db_helper.timeline_collection,
                    "Timeline",
                    None,
                )

    async def fill_match_data(self):
        for i in range(0, 2000, 95):
            app_logger.debug(f"INSERTING WITH I = {i}")
            await self.update_match_data(95, i)
