from typing import Optional

from models.GlobalPydanticConfig import BaseConfig


class Description(BaseConfig):
    region: str
    description: str


class Rarity(BaseConfig):
    region: str
    rarity: int


class SummonerIconDTO(BaseConfig):
    id: int
    contentId: str
    title: str
    yearReleased: int
    isLegacy: bool
    imagePath: Optional[str] = None
    descriptions: list[Description]
    rarities: list[Rarity]
    disabledRegions: list[str]
    esportsTeam: Optional[str] = None
    esportsRegion: Optional[str] = None
    esportsEvent: Optional[str] = None
