import asyncio
import os
from collections.abc import Sequence
from threading import Lock
from typing import Optional, Dict, TypeVar, Any, overload

import httpx
from asynciolimiter import Limiter
from dotenv import load_dotenv
from pydantic import BaseModel

from helpers.Logger import app_logger
from models.AccountDTO import AccountDTO
from models.ChampionDTO import ChampionDTO
from models.GameModeDTO import GameModeDTO
from models.GameTypeDTO import GameTypeDTO
from models.ItemDTO import ItemDTO
from models.MapDTO import MapDTO
from models.QueueDTO import QueueDTO
from models.SummonerDTO import SummonerDTO
from models.SummonerDTODB import SummonerDTODB


def map_asset_path(input_path: str | None, plugin: str = "rcp-be-lol-game-data") -> str:
    """
    Maps an asset path to the correct URL for the Community Dragon CDN.
    """
    prefix = "/lol-game-data/assets/"
    if input_path is None:
        return ""
    if not input_path.startswith(prefix):
        return input_path
    asset_path = input_path[len(prefix) :]
    mapped_path = f"https://raw.communitydragon.org/latest/plugins/{plugin}/global/default/{asset_path}".lower()

    return mapped_path


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

    async def test_connection(self) -> bool:
        """
        Test Riot API connection by attempting to fetch the lol status endpoint.
        Returns True if connection is successful, False otherwise.
        """
        try:
            await self._make_request(
                "https://euw1.api.riotgames.com/lol/status/v4/platform-data"
            )
            app_logger.info("Successfully tested Riot-API connection")
            return True
        except Exception as e:
            app_logger.error(
                f"Error while testing Riot-API connection. Check your API-Key: {e}"
            )
            return False

    GenericModel = TypeVar("GenericModel", bound=BaseModel)

    @overload
    async def _make_request(self, url: str) -> Any: ...

    @overload
    async def _make_request(self, url: str, *, use_limiter: bool) -> Any: ...

    @overload
    async def _make_request(
        self, url: str, model: type[GenericModel]
    ) -> GenericModel: ...

    async def _make_request(
        self,
        url: str,
        model: type[GenericModel] | None = None,
        use_limiter: bool = True,
    ) -> GenericModel | list[GenericModel] | Any:
        if use_limiter:
            await self.limiter.wait()
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json()
        if json_data is None:
            raise ValueError("No data returned")

        if model is not None:
            return model.model_validate(json_data)
        return json_data

    # TODO basic pydantic model for match
    async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a match from the Riot-API. No pydantic validation as data changes quite often.
        :param match_id: The match id of the match to fetch
        :return: Dict representation of the match
        """
        try:
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
            match = await self._make_request(url)
            app_logger.debug(f"Match [{match_id}] fetched with Riot-API")
            return match
        except Exception as e:
            app_logger.error(
                f"Error while fetching Match [{match_id}] with Riot-API: {e}"
            )
            return None

    # TODO basic pydantic model for timeline
    async def get_timeline(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a timeline from the Riot-API. No pydantic validation as data changes quite often.
        :param timeline_id: The id of the timeline to fetch
        :return: Dict representation of the timeline
        """
        try:
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{timeline_id}/timeline"
            timeline = await self._make_request(url)
            app_logger.debug(f"Timeline [{timeline_id}] fetched with Riot-API")
            return timeline
        except Exception as e:
            app_logger.error(
                f"Error while fetching Timeline [{timeline_id}] with Riot-API: {e}"
            )
            return None

    async def get_match_list(
        self, puuid: str, count: int = 95, offset: int = 0
    ) -> list[str]:
        """
        Fetch a matchlist from the Riot-API for a given puuid (summoner).
        :param puuid: The puuid of the summoner to fetch the matchlist for
        :param count: How many matches to parse (max 100)
        :param offset: The offset to start fetching matches
        :return: A list of match_ids (strings) for the given summoner
        """
        try:
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={offset}&count={count}"
            match_list = await self._make_request(url)
            app_logger.debug(
                f"Fetched Matchlist [count={count}, offset={offset}] [{puuid}] with Riot-API"
            )
            return match_list
        except Exception as e:
            app_logger.error(
                f"Error while fetching Matchlist [count={count}, offset={offset}] of Summoner [{puuid}] with Riot-API: {e}"
            )
            return []

    async def get_riot_account_by_tag(
        self, name: str, tag: str
    ) -> Optional[AccountDTO]:
        """
        Fetch an account from the Riot-API by name and tag.
        :param name: Name of the account
        :param tag: Tag of the account (4 characters)
        :return: AccountDTO object
        """
        try:
            tag = tag.replace("#", "")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            account = await self._make_request(url, AccountDTO)
            app_logger.debug(
                f"Fetched Account [{name} - {tag}] by name-tag with Riot-API"
            )
            return account

        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{name} - {tag}] with Riot-API: {e}"
            )
            return None

    async def get_riot_account_by_puuid(self, puuid: str) -> Optional[AccountDTO]:
        """
        Fetch an account from the Riot-API by puuid.
        :param puuid: The puuid of the account
        :return: AccountDTO object
        """
        try:
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
            account = await self._make_request(url, AccountDTO)
            app_logger.debug(f"Fetched Account [{puuid}] by puuid with Riot-API")
            return account

        except Exception as e:
            app_logger.error(
                f"Error while fetching Account [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_summoner_by_puuid_riot(
        self, puuid: str, account: Optional[AccountDTO] = None
    ) -> Optional[SummonerDTODB]:
        """
        Fetch a summoner from the Riot-API by puuid. Additionally, the account is also fetched to get the gameName and
        tagLine. The summoner and account data is then merged into a SummonerDTODB object.
        :param puuid: The puuid of the summoner to fetch
        :param account: Optionally provide the account directly doesn't need to be fetched again
        :return: SummonerDTODB object with the merged data
        """
        try:
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            summonerDTO = await self._make_request(url, SummonerDTO)
            app_logger.debug(f"Fetched Summoner [{puuid}] by puuid with Riot-API")
            # check if account provided
            if not account:
                account = await self.get_riot_account_by_puuid(summonerDTO.puuid)
            if account:
                dict_concat = summonerDTO.model_dump() | account.model_dump()
                return SummonerDTODB.model_validate(dict_concat)
            else:
                raise ValueError("Account not found")

        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{puuid}] with Riot-API: {e}"
            )
            return None

    async def get_summoner_by_account_tag(
        self, name: str, tag: str
    ) -> Optional[SummonerDTODB]:
        """
        Fetch a summoner from the Riot-API by name and tag. The account is fetched first and then the summoner is
        fetched by the puuid.
        :param name: Name of the account
        :param tag: Tag of the account (4 characters)
        :return: SummonerDTODB object
        """
        try:
            account = await self.get_riot_account_by_tag(name, tag)
            if account:
                return await self.get_summoner_by_puuid_riot(account.puuid, account)
            else:
                raise ValueError("Account not found")
        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{name} - {tag}] with Riot-API: {e}"
            )
            return None

    async def get_items(self) -> Sequence[ItemDTO]:
        raw_data = await self._make_request(
            "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/items.json",
            use_limiter=False,
        )
        output = []
        for item_raw in raw_data:
            item = ItemDTO.model_validate(item_raw)
            item.iconPath = map_asset_path(item.iconPath)
            output.append(item)

        app_logger.debug(f"Fetched {len(output)} Items with Riot-CDN")
        return output

    async def get_champions(
        self,
    ) -> Sequence[ChampionDTO]:
        try:
            output_data = []
            champions_summary = await self._make_request(
                "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-summary.json",
                use_limiter=False,
            )
            for champion_summary in champions_summary:
                champion_data_raw = await self._make_request(
                    f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champions/{champion_summary['id']}.json",
                    use_limiter=False,
                )
                if len(champion_data_raw["skins"]) > 0:
                    champion_data_raw["uncenteredSplashPath"] = champion_data_raw[
                        "skins"
                    ][0]["uncenteredSplashPath"]
                else:
                    champion_data_raw["uncenteredSplashPath"] = ""

                champion = ChampionDTO.model_validate(champion_data_raw)
                champion.squarePortraitPath = map_asset_path(
                    champion.squarePortraitPath
                )
                champion.stingerSfxPath = map_asset_path(champion.stingerSfxPath)
                champion.chooseVoPath = map_asset_path(champion.chooseVoPath)
                champion.banVoPath = map_asset_path(champion.banVoPath)
                champion.uncenteredSplashPath = map_asset_path(
                    champion.uncenteredSplashPath
                )

                for skin in champion.skins:
                    skin.splashPath = map_asset_path(skin.splashPath)
                    skin.uncenteredSplashPath = map_asset_path(
                        skin.uncenteredSplashPath
                    )
                    skin.tilePath = map_asset_path(skin.tilePath)
                    skin.loadScreenPath = map_asset_path(skin.loadScreenPath)

                champion.passive.abilityIconPath = map_asset_path(
                    champion.passive.abilityIconPath
                )
                champion.passive.abilityVideoPath = map_asset_path(
                    champion.passive.abilityVideoPath
                )
                champion.passive.abilityVideoImagePath = map_asset_path(
                    champion.passive.abilityVideoImagePath
                )

                for spell in champion.spells:
                    spell.abilityIconPath = map_asset_path(spell.abilityIconPath)
                    spell.abilityVideoPath = map_asset_path(spell.abilityVideoPath)
                    spell.abilityVideoImagePath = map_asset_path(
                        spell.abilityVideoImagePath
                    )

                output_data.append(champion)

            app_logger.debug(f"Fetched {len(output_data)} Champions with Riot-CDN")
            return output_data

        except Exception as e:
            app_logger.error(f"Error while fetching Champions with Riot-CDN: {e}")
            return []

    async def get_game_modes(self) -> Sequence[GameModeDTO]:
        try:
            raw_data = await self._make_request(
                "https://static.developer.riotgames.com/docs/lol/gameModes.json"
            )
            game_modes = [GameModeDTO.model_validate(data) for data in raw_data]
            app_logger.debug(f"Fetched {len(game_modes)} Game Modes with Riot-CDN")
            return [GameModeDTO.model_validate(data) for data in raw_data]
        except Exception as e:
            app_logger.error(f"Error while fetching Game Modes with Riot-CDN: {e}")
            return []

    async def get_game_types(self) -> Sequence[GameTypeDTO]:
        try:
            raw_data = await self._make_request(
                "https://static.developer.riotgames.com/docs/lol/gameTypes.json"
            )
            game_types = [GameTypeDTO.model_validate(data) for data in raw_data]
            app_logger.debug(f"Fetched {len(game_types)} Game Types with Riot-CDN")
            return [GameTypeDTO.model_validate(data) for data in raw_data]
        except Exception as e:
            app_logger.error(f"Error while fetching Game Types with Riot-CDN: {e}")
            return []

    async def get_maps(self) -> Sequence[MapDTO]:
        try:
            raw_data = await self._make_request(
                "https://static.developer.riotgames.com/docs/lol/maps.json"
            )
            maps = [MapDTO.model_validate(data) for data in raw_data]
            app_logger.debug(f"Fetched {len(maps)} Maps with Riot-CDN")
            return [MapDTO.model_validate(data) for data in raw_data]
        except Exception as e:
            app_logger.error(f"Error while fetching Maps with Riot-CDN: {e}")
            return []

    async def get_queues(self) -> Sequence[QueueDTO]:
        try:
            raw_data = await self._make_request(
                "https://static.developer.riotgames.com/docs/lol/queues.json"
            )
            queues = [QueueDTO.model_validate(data) for data in raw_data]
            app_logger.debug(f"Fetched {len(queues)} Queues with Riot-CDN")
            return [QueueDTO.model_validate(data) for data in raw_data]
        except Exception as e:
            app_logger.error(f"Error while fetching Queues with Riot-CDN: {e}")
            return []


async def main():
    rh = RiotHelper()
    await rh.get_items()
    await rh.get_champions()


if __name__ == "__main__":
    asyncio.run(main())
