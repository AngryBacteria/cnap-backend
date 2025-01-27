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
    account1 = await rh.get_riot_account_by_tag("AngryBacteria", "cnap")
    account2 = await rh.get_riot_account_by_puuid(angrybacteria_puuid)
    assert summoner1.puuid == angrybacteria_puuid
    assert summoner2.puuid == angrybacteria_puuid
    assert account1.puuid == angrybacteria_puuid
    assert account2.puuid == angrybacteria_puuid

    assert summoner1.gameName == angrybacteria_gameName
    assert summoner2.gameName == angrybacteria_gameName
    assert account1.gameName == angrybacteria_gameName
    assert account2.gameName == angrybacteria_gameName

    # match
    match = await rh.get_match(match1_id)
    assert match["metadata"]["matchId"] == match1_id
    match = await rh.get_match(match2_id)
    assert match["metadata"]["matchId"] == match2_id
    match = await rh.get_match("does-not-exist")
    assert match is None

    # timeline
    timeline = await rh.get_timeline(match1_id)
    assert timeline["metadata"]["matchId"] == match1_id
    assert timeline is not None
    timeline = await rh.get_timeline(match2_id)
    assert timeline["metadata"]["matchId"] == match2_id
    assert timeline is not None
    timeline = await rh.get_timeline("does-not-exist")
    assert timeline is None

    # matchlist
    matchlist = await rh.get_match_list(angrybacteria_puuid)
    assert len(matchlist) > 0
    assert matchlist is not None
    matchlist = await rh.get_match_list("does-not-exist")
    assert len(matchlist) == 0

    # CDN
    items = await rh.get_items()
    assert items is not None
    assert len(items) > 0

    champions = await rh.get_champions()
    assert champions is not None
    assert len(champions) > 0

    game_modes = await rh.get_game_modes()
    assert game_modes is not None
    assert len(game_modes) > 0

    game_types = await rh.get_game_types()
    assert game_types is not None
    assert len(game_types) > 0

    maps = await rh.get_maps()
    assert maps is not None
    assert len(maps) > 0

    queues = await rh.get_queues()
    assert queues is not None
    assert len(queues) > 0
