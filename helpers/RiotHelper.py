import asyncio
import os
from collections.abc import Sequence
from threading import Lock
from typing import Optional, Dict, Literal, TypeVar, Any

import httpx
from asynciolimiter import Limiter
from dotenv import load_dotenv
from pydantic import BaseModel

from helpers.Logger import app_logger
from models.ChampionMasteryDTO import ChampionMasteryDTO
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

    GenericModel = TypeVar("GenericModel", bound=BaseModel)

    async def _make_request(
        self, url: str, model: Optional[type[GenericModel]] = None
    ) -> GenericModel | Any:
        """
        Make a request to the given URL and return the response. If a pydantic model is provided, validate the
        response with the model for better type safety.
        :param url: The url to make the request to
        :param model: The pydantic model to validate the response with
        :return: Parsed JSON data or the validated pydantic model
        """
        await self.limiter.wait()
        response = await self.client.get(url)
        response.raise_for_status()
        json_data = response.json()
        if json_data is None:
            raise ValueError("No data returned")

        if model:
            return model.model_validate(json_data)
        else:
            return json_data

    # TODO basic pydantic model for match
    async def get_match_riot(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a match from the Riot-API. No pydantic validation as data changes quite often.
        :param match_id: The match id of the match to fetch
        :return: Dict representation of the match
        """
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

    # TODO basic pydantic model for timeline
    async def get_timeline_riot(self, timeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a timeline from the Riot-API. No pydantic validation as data changes quite often.
        :param timeline_id: The id of the timeline to fetch
        :return: Dict representation of the timeline
        """
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

    async def get_account_by_tag(self, name: str, tag: str) -> Optional[AccountDTO]:
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

    async def get_account_by_puuid(self, puuid: str) -> Optional[AccountDTO]:
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
                account = await self.get_account_by_puuid(summonerDTO.puuid)
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
            account = await self.get_account_by_tag(name, tag)
            if account:
                return await self.get_summoner_by_puuid_riot(account.puuid, account)
            else:
                raise ValueError("Account not found")
        except Exception as e:
            app_logger.error(
                f"Error while fetching Summoner [{name} - {tag}] with Riot-API: {e}"
            )
            return None

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
            data = await self._make_request(url)
            return [ChampionMasteryDTO.model_validate(mastery) for mastery in data]
        except Exception as e:
            app_logger.error(
                f"Error while fetching Champion Mastery for Summoner [{puuid}] with Riot-API: {e}"
            )
            return []

    async def get_cdn_resource(
        self,
        resource_type: Literal["items", "champions"],
        patch="latest",
        locale="en-US",
    ) -> Sequence[ItemDTO] | Sequence[ChampionDTO]:
        """
        Fetch a resource from the Meraki-CDN. The resource can be either items or champions.
        :param resource_type: Can be either "items" or "champions"
        :param patch: The Game Patch to fetch the resource for. Default is "latest"
        :param locale: The locale to fetch the resource for. Default is "en-US"
        :return: CDN resource as a list of pydantic models
        """
        app_logger.debug(f"Fetching {resource_type} with Meraki-CDN")
        raw_data = await self._make_request(
            f"https://cdn.merakianalytics.com/riot/lol/resources/{patch}/{locale}/{resource_type}.json"
        )
        if resource_type == "champions":
            champions = []
            for key, value in raw_data.items():
                champion = ChampionDTO.model_validate(value)
                champions.append(champion)

            return champions
        else:
            items = []
            for key, value in raw_data.items():
                item = ItemDTO.model_validate(value)
                items.append(item)

            return items


async def main():
    rh = RiotHelper()
    # cdn
    champions = await rh.get_cdn_resource("champions")
    print(champions[0].name)
    items = await rh.get_cdn_resource("items")
    print(items[0].name)
    # account
    account = await rh.get_account_by_tag("AngryBacteria", "cnap")
    summoner = await rh.get_summoner_by_account_tag("AngryBacteria", "cnap")
    summoner2 = await rh.get_summoner_by_puuid_riot(account.puuid)
    print(account.gameName)
    print(summoner.gameName)
    print(summoner2.gameName)
    # matchlist
    matchlist = await rh.get_match_list_riot(summoner.puuid)
    print(matchlist)
    # match
    match = await rh.get_match_riot(matchlist[0])
    print(match)
    # Mastery
    mastery = await rh.get_champion_mastery_by_puuid_riot(summoner.puuid)
    print(mastery[0])


if __name__ == "__main__":
    asyncio.run(main())
