from models.GlobalPydanticConfig import BaseConfig


class TimelineMetadata(BaseConfig):
    data_version: str
    match_id: str
    participants: list[str]


class TimelineInfo(BaseConfig):
    frameInterval: int
    gameId: int


class TimelineDTO(BaseConfig):
    metadata: TimelineMetadata
