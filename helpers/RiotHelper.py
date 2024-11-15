import asyncio
import os
from threading import Lock
from typing import List, Optional, Dict

import httpx
from asynciolimiter import Limiter
from dotenv import load_dotenv

from helpers.Logger import app_logger
from models.AccountDTO import AccountDTO
from models.ChampionDTO import ChampionDTO
from models.ItemDTO import ItemDTO
from models.SummonerDTO import SummonerDTO
from models.SummonerDTODB import SummonerDTODB


class RiotHelper:
    _instance = None
    _lock: Lock = Lock()
    riot_api_key: str
    client: httpx.AsyncClient
    limiter: Limiter
    cdragon_url: str = "https://raw.communitydragon.org"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    load_dotenv()

                    # Initialize Riot API Key
                    cls._instance.riot_api_key = os.getenv("RIOT_API_KEY")
                    if not cls._instance.riot_api_key:
                        raise ValueError("No Riot API Key found in Environment")

                    # Initialize HTTP Client
                    cls._instance.client = httpx.AsyncClient()
                    cls._instance.client.headers.update(
                        {"X-Riot-Token": cls._instance.riot_api_key}
                    )
                    cls._instance.limiter = Limiter(80 / 120)

        return cls._instance

    async def _make_request(self, url: str):
        await self.limiter.wait()
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_match_riot(self, match_id: str) -> Optional[Dict]:
        try:
            app_logger.debug(f"Fetching Match [{match_id}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
            data = await self._make_request(url)
            return data
        except Exception as e:
            app_logger.error(
                f"Error while fetching Match [{match_id}] with Riot-API: {e}"
            )
            return None

    async def get_timeline_riot(self, timeline_id: str) -> Optional[Dict]:
        try:
            app_logger.debug(f"Fetching Timeline [{timeline_id}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{timeline_id}/timeline"
            data = await self._make_request(url)
            return data
        except Exception as e:
            app_logger.error(
                f"Error while fetching Timeline [{timeline_id}] with Riot-API: {e}"
            )
            return None

    async def get_match_list_riot(
        self, summoner: SummonerDTO, count: int = 95, offset: int = 0
    ) -> list[str]:
        try:
            app_logger.debug(
                f"Fetching Matchlist [count={count}, offset={offset}] [{summoner.puuid}] with Riot-API"
            )
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner.puuid}/ids?start={offset}&count={count}"
            return await self._make_request(url)
        except Exception as e:
            app_logger.error(
                f"Error while fetching Matchlist [count={count}, offset={offset}] of Summoner [{summoner.puuid}] with Riot-API: {e}"
            )
            return []

    async def get_summoner_by_puuid_riot(self, puuid: str):
        try:
            app_logger.debug(f"Fetching Summoner [{puuid}] with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            data = await self._make_request(url)
            # validate
            summonerDTO = SummonerDTO.model_validate(data)
            account = await self.get_account_by_puuid(summonerDTO.puuid)
            if account:
                dict_concat = summonerDTO.model_dump() | account.model_dump()
                summonerDTODB = SummonerDTODB.model_validate(dict_concat)
                return summonerDTODB

        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_account_by_tag(self, name: str, tag: str):
        try:
            tag = tag.replace("#", "")
            app_logger.debug(f"Fetching Account [{name} - {tag}] with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            data = await self._make_request(url)
            # validate
            return AccountDTO.model_validate(data)

        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{name} - {tag}] with Riot-API: {e}"
            )
            return None

    async def get_account_by_puuid(self, puuid: str):
        try:
            app_logger.debug(f"Fetching Account [{puuid}] with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
            data = await self._make_request(url)
            # validate
            return AccountDTO.model_validate(data)

        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_summoner_by_account_tag(self, name: str, tag: str):
        account = await self.get_account_by_tag(name, tag)
        if account:
            return await self.get_summoner_by_puuid_riot(account.puuid)
        return None

    async def get_champion_mastery_by_puuid_riot(self, puuid: str) -> List[Dict]:
        try:
            app_logger.debug(
                f"Fetching Champion Mastery for Summoner [{puuid}] with Riot-API"
            )
            url = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
            data = await self._make_request(url)
            return [champion for champion in data]
        except Exception as e:
            app_logger.error(
                f"Error while fetching Champion Mastery for Summoner [{puuid}] with Riot-API: {e}"
            )
            return []

    async def get_champions(self, patch="latest", locale="en-US"):
        try:
            raw_champions = await self._make_request(
                f"https://cdn.merakianalytics.com/riot/lol/resources/{patch}/{locale}/champions.json"
            )

            # validate and parse
            champions = []
            for key, value in raw_champions.items():
                champion = ChampionDTO.model_validate(value)
                champions.append(champion)
            return champions
        except Exception as e:
            app_logger.error(f"Error while fetching Champions with Meraki-CDN: {e}")
            return []

    async def get_items(self, patch="latest", locale="en-US"):
        try:
            raw_items = await self._make_request(
                f"https://cdn.merakianalytics.com/riot/lol/resources/{patch}/{locale}/items.json"
            )

            # Validate and return
            items = []
            for key, value in raw_items.items():
                item = ItemDTO.model_validate(value)
                items.append(item)
            return items
        except Exception as e:
            app_logger.error(f"Error while fetching Items with Meraki-CDN: {e}")
            return []


async def main():
    rh = RiotHelper()
    items = await rh.get_items()
    print(items[0].name)
    champions = await rh.get_champions()
    print(champions[0].name)


if __name__ == "__main__":
    asyncio.run(main())
