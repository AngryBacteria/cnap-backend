import pytest

from helpers.RiotHelper import RiotHelper

angrybacteria_puuid = "zk1tF-l0TT1SrT9SbUmofKLT4R2gLKxzhGSyNuuxTCbmjr6dOqTCw1GcYrHoRp5DV2f5M17GMLPEFw"
angrybacteria_gameName = "AngryBacteria"

match1_id = "EUW1_7084514418"
match2_id = "EUW1_7075264366"

# TODO implement
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

    assert summoner1.tagLine.lower() == "cnap"
    assert summoner2.tagLine.lower() == "cnap"
    assert account1.tagLine.lower() == "cnap"
    assert account2.tagLine.lower() == "cnap"

    summoner = await rh.get_summoner_by_puuid_riot("does not exist")
    assert summoner is None
    summoner = await rh.get_summoner_by_account_tag("does not exist", "does not exist")
    assert summoner is None
    account = await rh.get_account_by_puuid("does not exist")
    assert account is None
    account = await rh.get_account_by_tag("does not exist", "does not exist")
    assert account is None


    # TODO Match
    # TODO Matchlist
    # TODO Match timeline
