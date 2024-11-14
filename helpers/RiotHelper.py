import asyncio
import json
import os
from threading import Lock
from typing import List, Optional, Dict

import httpx
from asynciolimiter import Limiter
from dotenv import load_dotenv

from helpers.Logger import app_logger
from models.AccountDTO import AccountDTO
from models.ChampionDataDTO import ChampionDataDTO
from models.ChampionSummaryDTO import ChampionSummaryDTO
from models.SummonerDTO import SummonerDTO


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

    async def get_summoner_by_puuid_riot(self, puuid: str) -> Optional[SummonerDTO]:
        try:
            app_logger.debug(f"Fetching Summoner [{puuid}] with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            data = await self._make_request(url)
            # validate
            return SummonerDTO.model_validate(data)
        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_account_by_tag(self, name: str, tag: str) -> Optional[AccountDTO]:
        try:
            tag = tag.replace("#", "")
            app_logger.debug(f"Fetching Account [{name} - {tag}] with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            data = await self._make_request(url)
            return AccountDTO.model_validate(data)

        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{name} - {tag}] with Riot-API: {e}"
            )
            return None

    # TODO: re-add gameName and tagline
    async def get_summoner_by_account_tag(
        self, name: str, tag: str
    ) -> Optional[SummonerDTO]:
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

    async def get_lol_champions_summary(
        self, patch="latest", locale="default"
    ) -> list[ChampionSummaryDTO]:
        try:
            raw_champs = await self._make_request(
                f"{self.cdragon_url}/{patch}/plugins/rcp-be-lol-game-data/global/{locale}/v1/champion-summary.json"
            )

            champs = []
            for raw_champ in raw_champs:
                # fix asset paths
                keys_to_fix = ["squarePortraitPath"]
                for key in keys_to_fix:
                    raw_champ[key] = self.raw_to_cdragon_path(raw_champ[key])

                # validate
                champ = ChampionSummaryDTO.model_validate(raw_champ)
                champs.append(champ)

            return champs

        except Exception as e:
            app_logger.error(
                f"Error while fetching Champion Summary with Riot-API: {e}"
            )
            return []

    async def get_lol_champion(
        self, champion_id: str, patch="latest", locale="default"
    ) -> Optional[ChampionDataDTO]:
        try:
            raw_champ = await self._make_request(
                f"{self.cdragon_url}/{patch}/plugins/rcp-be-lol-game-data/global/{locale}/v1/champions/{champion_id}.json"
            )

            # fix asset paths
            keys_to_fix_root = [
                "squarePortraitPath",
                "stingerSfxPath",
                "chooseVoPath",
                "banVoPath",
            ]
            for key in keys_to_fix_root:
                raw_champ[key] = self.raw_to_cdragon_path(raw_champ[key])

            keys_to_fix_skins = [
                "splashPath",
                "uncenteredSplashPath",
                "tilePath",
                "loadScreenPath",
                "splashVideoPath",
                "collectionSplashVideoPath",
                "collectionCardHoverVideoPath",
                "chromaPath",
                "rarityGemPath",
            ]
            for skin in raw_champ["skins"]:
                for key in keys_to_fix_skins:
                    skin[key] = self.raw_to_cdragon_path(skin[key])

            keys_to_fix_passive = [
                "abilityIconPath",
                "abilityVideoPath",
                "abilityVideoImagePath",
            ]
            for key in keys_to_fix_passive:
                raw_champ["passive"][key] = self.raw_to_cdragon_path(
                    raw_champ["passive"][key]
                )

            keys_to_fix_spells = [
                "abilityIconPath",
                "abilityVideoPath",
                "abilityVideoImagePath",
            ]
            for ability in raw_champ["spells"]:
                for key in keys_to_fix_spells:
                    ability[key] = self.raw_to_cdragon_path(ability[key])

            # validate
            return ChampionDataDTO.model_validate(raw_champ)

        except Exception as e:
            app_logger.error(
                f"Error while fetching Champion [{champion_id}] with Riot-API: {e}"
            )
            return None

    def raw_to_cdragon_path(self, raw_path: str, patch="latest", locale="default"):
        if not raw_path:
            return raw_path

        if "/lol-game-data/assets/" in raw_path:
            raw_path = raw_path.split("/lol-game-data/assets/")[1]
            return f"{self.cdragon_url}/{patch}/plugins/rcp-be-lol-game-data/global/{locale}/{raw_path}".lower()

        if "champion-abilities" in raw_path:
            return f"https://d28xe8vt774jo5.cloudfront.net/{raw_path}"

        else:
            return raw_path


async def main():
    rh = RiotHelper()
    summoner = await rh.get_summoner_by_account_tag("AngryBacteria", "cnap")
    app_logger.debug(summoner)
    match_list = await rh.get_match_list_riot(summoner)
    app_logger.debug(match_list)
    champion_mastery = await rh.get_champion_mastery_by_puuid_riot(summoner.puuid)
    app_logger.debug(champion_mastery[0]["championPoints"])
    annie = await rh.get_lol_champion("1")
    print(json.dumps(annie.dict(), indent=4))


if __name__ == "__main__":
    asyncio.run(main())
