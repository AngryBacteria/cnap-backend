from models.GlobalPydanticConfig import BaseConfig


# TODO way more
class MatchInfo(BaseConfig):
    gameId: int
    gameMode: str
    gameType: str
    mapId: int
    queueId: int


class MatchMetadata(BaseConfig):
    data_version: str
    match_id: str
    participants: list[str]


class MatchV5DTO(BaseConfig):
    metadata: MatchMetadata
    info: MatchInfo
