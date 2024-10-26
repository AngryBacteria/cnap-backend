import asyncio
import os
from threading import Lock
from typing import List, Optional, Dict

import httpx
from asynciolimiter import Limiter
from dotenv import load_dotenv

from helpers.Logger import app_logger


class RiotHelper:
    _instance = None
    _lock: Lock = Lock()
    riot_api_key: str
    client: httpx.AsyncClient
    limiter: Limiter

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

    async def get_match_list_riot(
        self, summoner: Dict, count: int = 95, offset: int = 0
    ) -> list[str]:
        try:
            app_logger.debug(f"Fetching Matchlist [count={count}, offset={offset}] [{summoner['puuid']}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner['puuid']}/ids?start={offset}&count={count}"
            return await self._make_request(url)
        except Exception as e:
            app_logger.error(
                f"Error while fetching Matchlist [count={count}, offset={offset}] of Summoner [{summoner['puuid']}] with Riot-API: {e}"
            )
            return []

    async def get_summoner_by_puuid_riot(self, puuid: str) -> Optional[Dict]:
        try:
            app_logger.debug(f"Fetching Summoner [{puuid}] with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            data = await self._make_request(url)
            return data
        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_account_by_tag(self, name: str, tag: str) -> Optional[Dict]:
        try:
            tag = tag.replace("#", "")
            app_logger.debug(f"Fetching Account [{name} - {tag}] with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            data = await self._make_request(url)
            return data
        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{name} - {tag}] with Riot-API: {e}"
            )
            return None

    async def get_summoner_by_account_tag(self, name: str, tag: str) -> Optional[Dict]:
        account = await self.get_account_by_tag(name, tag)
        if account:
            summoner = await self.get_summoner_by_puuid_riot(account["puuid"])
            if summoner:
                summoner["gameName"] = account["gameName"]
                summoner["tagLine"] = account["tagLine"]
                return summoner
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


async def main():
    rh = RiotHelper()
    summoner = await rh.get_summoner_by_account_tag("AngryBacteria", "cnap")
    app_logger.debug(summoner)
    match_list = await rh.get_match_list_riot(summoner)
    app_logger.debug(match_list)
    champion_mastery = await rh.get_champion_mastery_by_puuid_riot(summoner["puuid"])
    app_logger.debug(champion_mastery[0]["championPoints"])


if __name__ == "__main__":
    asyncio.run(main())
