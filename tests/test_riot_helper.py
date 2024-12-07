from typing import Literal

import pytest

from helpers.RiotHelper import RiotHelper

angrybacteria_puuid = (
    "zk1tF-l0TT1SrT9SbUmofKLT4R2gLKxzhGSyNuuxTCbmjr6dOqTCw1GcYrHoRp5DV2f5M17GMLPEFw"
)
angrybacteria_gameName = "AngryBacteria"

match1_id = "EUW1_7084514418"
match2_id = "EUW1_7075264366"


@pytest.mark.asyncio
async def test_queries():
    rh = RiotHelper()
    # summoner / account
    summoner1 = await rh.get_summoner_by_account_tag("AngryBacteria", "cnap")
    summoner2 = await rh.get_summoner_by_puuid_riot(angrybacteria_puuid)
    account1 = await rh.get_account_by_tag("AngryBacteria", "cnap")
    account2 = await rh.get_account_by_puuid(angrybacteria_puuid)
    assert summoner1.puuid == angrybacteria_puuid
    assert summoner2.puuid == angrybacteria_puuid
    assert account1.puuid == angrybacteria_puuid
    assert account2.puuid == angrybacteria_puuid

    assert summoner1.gameName == angrybacteria_gameName
    assert summoner2.gameName == angrybacteria_gameName
    assert account1.gameName == angrybacteria_gameName
    assert account2.gameName == angrybacteria_gameName

    # match
    match = await rh.get_match_riot(match1_id)
    assert match["metadata"]["matchId"] == match1_id
    match = await rh.get_match_riot(match2_id)
    assert match["metadata"]["matchId"] == match2_id
    match = await rh.get_match_riot("does not exist")
    assert match is None

    # timeline
    timeline = await rh.get_timeline_riot(match1_id)
    assert timeline["metadata"]["matchId"] == match1_id
    assert timeline is not None
    timeline = await rh.get_timeline_riot(match2_id)
    assert timeline["metadata"]["matchId"] == match2_id
    assert timeline is not None
    timeline = await rh.get_timeline_riot("does not exist")
    assert timeline is None

    # matchlist
    matchlist = await rh.get_match_list_riot(angrybacteria_puuid)
    assert len(matchlist) > 0
    assert matchlist is not None
    matchlist = await rh.get_match_list_riot("does not exist")
    assert len(matchlist) == 0

    # cdn
    resource_types: list[
        Literal["items", "champions", "gameModes", "gameTypes", "maps", "queues"]
    ] = ["items", "champions", "gameModes", "gameTypes", "maps", "queues"]
    for resource_type in resource_types:
        resources = await rh.get_cdn_resource(resource_type)
        assert resources is not None
        assert len(resources) > 0

    # mastery
    mastery = await rh.get_mastery_riot(angrybacteria_puuid)
    assert mastery is not None
    assert len(mastery) > 0
    mastery = await rh.get_mastery_riot("does not exist")
    assert len(mastery) == 0
