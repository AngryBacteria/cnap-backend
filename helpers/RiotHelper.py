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
from models.ChampionMasteryDTO import ChampionMasteryDTO
from models.AccountDTO import AccountDTO
from models.ChampionDTO import ChampionDTO
from models.GameModeDTO import GameModeDTO
from models.GameTypeDTO import GameTypeDTO
from models.ItemDTO import ItemDTO
from models.MapDTO import MapDTO
from models.QueueDTO import QueueDTO
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

    GenericModel = TypeVar("GenericModel", bound=BaseModel)

    @overload
    async def _make_request(
        self, url: str, model: type[GenericModel]
    ) -> GenericModel: ...

    @overload
    async def _make_request(
        self, url: str, model: type[GenericModel], model_list: bool
    ) -> list[GenericModel]: ...

    @overload
    async def _make_request(self, url: str) -> Any: ...

    async def _make_request(
        self,
        url: str,
        model: type[GenericModel] | None = None,
        model_list: bool = False,
    ) -> GenericModel | list[GenericModel] | Any:
        await self.limiter.wait()
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json()
        if json_data is None:
            raise ValueError("No data returned")

        if model is not None:
            if isinstance(json_data, list) and model_list:
                return [model.model_validate(data) for data in json_data]
            else:
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
            app_logger.debug(f"Fetching Match [{match_id}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
            return await self._make_request(url)
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
            app_logger.debug(f"Fetching Timeline [{timeline_id}] with Riot-API")
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{timeline_id}/timeline"
            return await self._make_request(url)
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
            app_logger.debug(
                f"Fetching Matchlist [count={count}, offset={offset}] [{puuid}] with Riot-API"
            )
            url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start={offset}&count={count}"
            return await self._make_request(url)
        except Exception as e:
            app_logger.error(
                f"Error while fetching Matchlist [count={count}, offset={offset}] of Summoner [{puuid}] with Riot-API: {e}"
            )
            return []

    async def get_riot_account_by_tag(self, name: str, tag: str) -> Optional[AccountDTO]:
        """
        Fetch an account from the Riot-API by name and tag.
        :param name: Name of the account
        :param tag: Tag of the account (4 characters)
        :return: AccountDTO object
        """
        try:
            tag = tag.replace("#", "")
            app_logger.debug(
                f"Fetching Account [{name} - {tag}] by name-tag with Riot-API"
            )
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}"
            return await self._make_request(url, AccountDTO)

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
            app_logger.debug(f"Fetching Account [{puuid}] by puuid with Riot-API")
            url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
            return await self._make_request(url, AccountDTO)

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
            app_logger.debug(f"Fetching Summoner [{puuid}] by puuid with Riot-API")
            url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            summonerDTO = await self._make_request(url, SummonerDTO)
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

    async def get_items(self, patch="latest", locale="en-US") -> Sequence[ItemDTO]:
        raw_data = await self._make_request(
            f"https://cdn.merakianalytics.com/riot/lol/resources/{patch}/{locale}/items.json"
        )
        items = []
        for key, value in raw_data.items():
            item = ItemDTO.model_validate(value)
            items.append(item)
        return items

    async def get_champions(
        self, patch="latest", locale="en-US"
    ) -> Sequence[ChampionDTO]:
        raw_data = await self._make_request(
            f"https://cdn.merakianalytics.com/riot/lol/resources/{patch}/{locale}/champions.json"
        )
        champions = []
        for key, value in raw_data.items():
            item = ChampionDTO.model_validate(value)
            champions.append(item)
        return champions

    async def get_game_modes(self) -> Sequence[GameModeDTO]:
        raw_data = await self._make_request(
            "https://static.developer.riotgames.com/docs/lol/gameModes.json"
        )
        return [GameModeDTO.model_validate(data) for data in raw_data]

    async def get_game_types(self) -> Sequence[GameTypeDTO]:
        raw_data = await self._make_request(
            "https://static.developer.riotgames.com/docs/lol/gameTypes.json"
        )
        return [GameTypeDTO.model_validate(data) for data in raw_data]

    async def get_maps(self) -> Sequence[MapDTO]:
        raw_data = await self._make_request(
            "https://static.developer.riotgames.com/docs/lol/maps.json"
        )
        return [MapDTO.model_validate(data) for data in raw_data]

    async def get_queues(self) -> Sequence[QueueDTO]:
        raw_data = await self._make_request(
            "https://static.developer.riotgames.com/docs/lol/queues.json"
        )
        return [QueueDTO.model_validate(data) for data in raw_data]

    async def get_champion_mastery_by_puuid_riot(
        self, puuid: str
    ) -> Sequence[ChampionMasteryDTO]:
        """
        Fetch the Champion Mastery for all champions of a summoner by puuid.
        :param puuid: The puuid of the summoner
        :return: List of Champion Mastery objects
        """
        try:
            app_logger.debug(
                f"Fetching Champion Mastery for Summoner [{puuid}] with Riot-API"
            )
            url = f"https://euw1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
            return await self._make_request(url, ChampionMasteryDTO, True)
        except Exception as e:
            app_logger.error(
                f"Error while fetching Champion Mastery for Summoner [{puuid}] with Riot-API: {e}"
            )
            return []


async def main():
    rh = RiotHelper()
    # cdn
    champions = await rh.get_champions("champions")
    print(champions[0].name)


if __name__ == "__main__":
    asyncio.run(main())
