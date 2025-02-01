from typing import Any

import pytest

from helpers.DBHelper import (
    DBHelper,
    BasicFilter,
    SummonerFilter,
    BasicMatchFilter,
    CollectionName,
)
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
async def test_queries() -> None:
    dbh = DBHelper.get_instance()
    dbh2 = DBHelper.get_instance()
    assert dbh == dbh2

    with pytest.raises(Exception):
        DBHelper()

    is_connectable = await dbh.test_connection()
    assert is_connectable

    indexes_created = await dbh.init_indexes()
    assert indexes_created

    # test non-existing match ids
    do_exist = [match1_id, match2_id]
    do_not_exist = ["i do not exist", "euw_23432948723894722230848239047892"]

    db_response = await dbh.get_non_existing_match_ids(
        do_exist + do_not_exist, "MatchV5"
    )
    assert all(match_id not in db_response for match_id in do_exist)
    assert all(match_id in db_response for match_id in do_not_exist)

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
    matches = await dbh.get_matches(BasicMatchFilter())
    assert len(matches) > 0
    # single match id filtering
    matches = await dbh.get_matches(BasicMatchFilter(match_ids=[match1_id]))
    assert len(matches) == 1
    assert matches[0]["metadata"]["matchId"] == match1_id
    # non-existing match id filtering
    matches = await dbh.get_matches(
        BasicMatchFilter(match_ids=["this match id does not exist"])
    )
    assert len(matches) == 0
    # multiple match id filtering
    matches = await dbh.get_matches(BasicMatchFilter(match_ids=[match1_id, match2_id]))
    assert len(matches) == 2
    assert match1_id in [match["metadata"]["matchId"] for match in matches]
    assert match2_id in [match["metadata"]["matchId"] for match in matches]
    # filtering by mode
    matches = await dbh.get_matches(BasicMatchFilter(mode="CLASSIC"))
    assert all(match["info"]["gameMode"] == "CLASSIC" for match in matches)
    assert all(match["info"]["gameMode"] != "ULTBOOK" for match in matches)
    matches = await dbh.get_matches(BasicMatchFilter(mode="ULTBOOK"))
    assert all(match["info"]["gameMode"] == "ULTBOOK" for match in matches)
    assert all(match["info"]["gameMode"] != "CLASSIC" for match in matches)
    # filtering by participant
    matches = await dbh.get_matches(
        BasicMatchFilter(participant_puuids=[angrybacteria_puuid])
    )
    assert len(matches) > 0
    assert all(
        angrybacteria_puuid in match["metadata"]["participants"] for match in matches
    )
    matches = await dbh.get_matches(
        BasicMatchFilter(participant_puuids=["this puuid does not exist"])
    )
    assert len(matches) == 0
    # filtering by participants
    matches = await dbh.get_matches(
        BasicMatchFilter(
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
    matches = await dbh.get_matches(BasicMatchFilter(queue=400))
    assert all(match["info"]["queueId"] == 400 for match in matches)
    assert all(match["info"]["queueId"] != 1400 for match in matches)
    matches = await dbh.get_matches(BasicMatchFilter(queue=1400))
    assert all(match["info"]["queueId"] == 1400 for match in matches)
    assert all(match["info"]["queueId"] != 400 for match in matches)
    # filter by multiple filter options
    matches = await dbh.get_matches(
        BasicMatchFilter(
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
    static_type_map = {
        CollectionName.CHAMPION: ChampionDTO,
        CollectionName.GAME_MODE: GameModeDTO,
        CollectionName.GAME_TYPE: GameTypeDTO,
        CollectionName.ITEM: ItemDTO,
        CollectionName.MAP: MapDTO,
        CollectionName.QUEUE: QueueDTO,
    }
    for collection_type, dto_type in static_type_map.items():
        static_data: list[Any] = await dbh.generic_get(
            BasicFilter(), collection_type, dto_type
        )
        assert len(static_data) > 0
