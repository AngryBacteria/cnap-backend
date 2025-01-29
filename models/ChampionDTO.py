from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

from models.GlobalPydanticConfig import BaseConfig


# TODO verify model
class TacticalInfo(BaseModel):
    style: int
    difficulty: int
    damageType: str


class PlaystyleInfo(BaseModel):
    damage: int
    durability: int
    crowdControl: int
    mobility: int
    utility: int


class Skin(BaseModel):
    id: int
    name: str
    splashPath: str
    uncenteredSplashPath: str
    tilePath: str
    loadScreenPath: str
    rarity: Optional[str]
    isLegacy: Optional[bool]
    description: Optional[str]


class Passive(BaseModel):
    name: str
    abilityIconPath: str
    abilityVideoPath: Optional[str]
    abilityVideoImagePath: Optional[str]
    description: str


class Spell(BaseModel):
    spellKey: Optional[str]
    name: str
    abilityIconPath: str
    abilityVideoPath: Optional[str]
    abilityVideoImagePath: Optional[str]
    cost: str
    cooldown: str
    description: str
    dynamicDescription: str
    range: List[float]
    costCoefficients: Optional[List[float]]
    cooldownCoefficients: Optional[List[float]]


class ChampionDTO(BaseConfig):
    id: int
    name: str
    alias: str
    title: str
    shortBio: str
    tacticalInfo: TacticalInfo
    playstyleInfo: PlaystyleInfo
    squarePortraitPath: str
    stingerSfxPath: Optional[str]
    chooseVoPath: Optional[str]
    banVoPath: Optional[str]
    roles: List[str]
    skins: List[Skin]
    passive: Passive
    spells: List[Spell]
    uncenteredSplashPath: str
