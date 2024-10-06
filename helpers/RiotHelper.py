import asyncio
import os
from threading import Lock
from typing import List, Optional

import httpx
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry

from interfaces.AccountDTO import AccountDTO
from interfaces.ChampionMasteryDTO import ChampionMasteryDTO
from interfaces.MatchV5DTO import MatchV5DTO
from interfaces.SummonerDTO import SummonerDTO


class RiotHelper:
    _instance = None
    _lock: Lock = Lock()

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

        return cls._instance

    @sleep_and_retry
    @limits(calls=20, period=1)
    @limits(calls=100, period=120)
    async def _make_request(self, url: str):
        response = await self.client.get(url)
        response.raise_for_status()
        return response.json()

    async def get_match_riot(self, match_id: str) -> Optional[MatchV5DTO]:
        try:
            print(f"Fetching Match [{match_id}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
            data = await self._make_request(url)
            return MatchV5DTO(**data)
        except Exception as e:
            print(f"Error while fetching Match [{match_id}] with Riot-API: {e}")
            return None

    async def get_match_list_riot(
        self, summoner: SummonerDTO, count: int = 100, offset: int = 0
    ) -> list[str]:
        try:
            print(f"Fetching Matchlist [{summoner.puuid}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{summoner.puuid}/ids?start={offset}&count={count}"
            return await self._make_request(url)
        except Exception as e:
            print(
                f"Error while fetching Matchlist of Summoner [{summoner.puuid}] with Riot-API: {e}"
            )
            return []

    async def get_summoner_by_puuid_riot(self, puuid: str) -> Optional[SummonerDTO]:
        try:
            print(f"Fetching Summoner [{puuid}] with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            data = await self._make_request(url)
            return SummonerDTO(**data)
        except Exception as e:
            print(f"Error while fetching Summoner [{puuid}] with Riot-API: {e}")
            return None

    async def get_account_by_tag(self, name: str, tag: str) -> Optional[AccountDTO]:
        try:
            tag = tag.replace("#", "")
            print(f"Fetching Account [{name} - {tag}] with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            data = await self._make_request(url)
            return AccountDTO(**data)
        except Exception as e:
            print(f"Error while fetching Account [{name} - {tag}] with Riot-API: {e}")
            return None

    async def get_summoner_by_account_tag(
        self, name: str, tag: str
    ) -> Optional[SummonerDTO]:
        account = await self.get_account_by_tag(name, tag)
        if account:
            summoner = await self.get_summoner_by_puuid_riot(account.puuid)
            if summoner:
                summoner.gameName = account.gameName
                summoner.tagLine = account.tagLine
                return summoner
        return None

    async def get_champion_mastery_by_puuid_riot(
        self, puuid: str
    ) -> List[ChampionMasteryDTO]:
        try:
            print(f"Fetching Champion Mastery for Summoner [{puuid}] with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
            data = await self._make_request(url)
            return [ChampionMasteryDTO(**champion) for champion in data]
        except Exception as e:
            print(
                f"Error while fetching Champion Mastery for Summoner [{puuid}] with Riot-API: {e}"
            )
            return []


async def main():
    rh = RiotHelper()
    summoner = await rh.get_summoner_by_account_tag("AngryBacteria", "cnap")
    print(summoner)
    match_list = await rh.get_match_list_riot(summoner)
    print(match_list)
    champion_mastery = await rh.get_champion_mastery_by_puuid_riot(summoner.puuid)
    print(champion_mastery[0].championPoints)


if __name__ == "__main__":
    asyncio.run(main())
