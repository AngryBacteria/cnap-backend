import pytest

from helpers.DBHelper import DBHelper, BaseFilter, SummonerFilter, BaseMatchFilter
from models.ChampionDTO import ChampionDTO
from models.GameModeDTO import GameModeDTO
from models.GameTypeDTO import GameTypeDTO
from models.ItemDTO import ItemDTO
from models.MapDTO import MapDTO
from models.QueueDTO import QueueDTO

angrybacteria_puuid = (
    "zk1tF-l0TT1SrT9SbUmofKLT4R2gLKxzhGSyNuuxTCbmjr6dOqTCw1GcYrHoRp5DV2f5M17GMLPEFw"
)
bribri_puuid = (
    "Sbji7x0flde3VDc3n5u5UGrzG6pF_jqFQuNlgAig6JsTIhDnDRGBuN8I5O9ZBQIqoRsIm2esKq8UWg"
)

match1_id = "EUW1_7084514418"
match2_id = "EUW1_7075264366"


@pytest.mark.asyncio
async def test_queries():
    dbh = DBHelper()
    # summoner
    summoners = await dbh.get_summoners(SummonerFilter())
    assert len(summoners) > 0
    summoners = await dbh.get_summoners(SummonerFilter(puuid=angrybacteria_puuid))
    assert len(summoners) == 1
    assert summoners[0].gameName == "AngryBacteria"
    summoners = await dbh.get_summoners(
        SummonerFilter(puuid="this puuid does not exist")
    )
    assert len(summoners) == 0

    # match
    # no filtering
    matches = await dbh.get_matches(BaseMatchFilter())
    assert len(matches) > 0
    # single match id filtering
    matches = await dbh.get_matches(BaseMatchFilter(match_ids=[match1_id]))
    assert len(matches) == 1
    assert matches[0]["metadata"]["matchId"] == match1_id
    # non-existing match id filtering
    matches = await dbh.get_matches(
        BaseMatchFilter(match_ids=["this match id does not exist"])
    )
    assert len(matches) == 0
    # multiple match id filtering
    matches = await dbh.get_matches(BaseMatchFilter(match_ids=[match1_id, match2_id]))
    assert len(matches) == 2
    assert match1_id in [match["metadata"]["matchId"] for match in matches]
    assert match2_id in [match["metadata"]["matchId"] for match in matches]
    # filtering by mode
    matches = await dbh.get_matches(BaseMatchFilter(mode="CLASSIC"))
    assert all(match["info"]["gameMode"] == "CLASSIC" for match in matches)
    assert all(match["info"]["gameMode"] != "ULTBOOK" for match in matches)
    matches = await dbh.get_matches(BaseMatchFilter(mode="ULTBOOK"))
    assert all(match["info"]["gameMode"] == "ULTBOOK" for match in matches)
    assert all(match["info"]["gameMode"] != "CLASSIC" for match in matches)
    # filtering by participant
    matches = await dbh.get_matches(
        BaseMatchFilter(participant_puuids=[angrybacteria_puuid])
    )
    assert len(matches) > 0
    assert all(
        angrybacteria_puuid in match["metadata"]["participants"] for match in matches
    )
    matches = await dbh.get_matches(
        BaseMatchFilter(participant_puuids=["this puuid does not exist"])
    )
    assert len(matches) == 0
    # filtering by participants
    matches = await dbh.get_matches(
        BaseMatchFilter(
            participant_puuids=[
                angrybacteria_puuid,
                bribri_puuid,
            ]
        )
    )
    assert len(matches) > 0
    assert all(
        angrybacteria_puuid in match["metadata"]["participants"] for match in matches
    )
    assert all(bribri_puuid in match["metadata"]["participants"] for match in matches)
    # filtering by queue id
    matches = await dbh.get_matches(BaseMatchFilter(queue=400))
    assert all(match["info"]["queueId"] == 400 for match in matches)
    assert all(match["info"]["queueId"] != 1400 for match in matches)
    matches = await dbh.get_matches(BaseMatchFilter(queue=1400))
    assert all(match["info"]["queueId"] == 1400 for match in matches)
    assert all(match["info"]["queueId"] != 400 for match in matches)
    # filter by multiple filter options
    matches = await dbh.get_matches(
        BaseMatchFilter(
            mode="CLASSIC",
            queue=400,
            participant_puuids=[angrybacteria_puuid],
        )
    )
    assert all(match["info"]["gameMode"] == "CLASSIC" for match in matches)
    assert all(match["info"]["queueId"] == 400 for match in matches)
    assert all(
        angrybacteria_puuid in match["metadata"]["participants"] for match in matches
    )

    # static game data
    static_data = await dbh.generic_get(BaseFilter(), dbh.item_collection, ItemDTO)
    assert len(static_data) > 0

    static_data = await dbh.generic_get(
        BaseFilter(), dbh.champion_collection, ChampionDTO
    )
    assert len(static_data) > 0

    static_data = await dbh.generic_get(
        BaseFilter(), dbh.game_modes_collection, GameModeDTO
    )
    assert len(static_data) > 0

    static_data = await dbh.generic_get(
        BaseFilter(), dbh.game_types_collection, GameTypeDTO
    )
    assert len(static_data) > 0

    static_data = await dbh.generic_get(BaseFilter(), dbh.maps_collection, MapDTO)
    assert len(static_data) > 0

    static_data = await dbh.generic_get(BaseFilter(), dbh.queues_collection, QueueDTO)
    assert len(static_data) > 0
