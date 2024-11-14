from __future__ import annotations

from typing import Any, List, Optional

from pydantic import BaseModel


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


class SkinLine(BaseModel):
    id: int


class Description(BaseModel):
    region: str
    description: str


class Rarity(BaseModel):
    region: str
    rarity: int


class Chroma(BaseModel):
    id: int
    name: str
    chromaPath: str
    colors: List[str]
    descriptions: List[Description]
    rarities: List[Rarity]


class Skin(BaseModel):
    id: int
    isBase: bool
    name: str
    splashPath: str
    uncenteredSplashPath: str
    tilePath: str
    loadScreenPath: str
    skinType: str
    rarity: str
    isLegacy: bool
    splashVideoPath: Any
    collectionSplashVideoPath: Any
    collectionCardHoverVideoPath: Any
    featuresText: Any
    chromaPath: Optional[str]
    emblems: Any
    regionRarityId: int
    rarityGemPath: Any
    skinLines: Optional[List[SkinLine]]
    description: Optional[str]
    loadScreenVintagePath: Optional[str] = None
    chromas: Optional[List[Chroma]] = None


class Passive(BaseModel):
    name: str
    abilityIconPath: str
    abilityVideoPath: str
    abilityVideoImagePath: str
    description: str


class Coefficients(BaseModel):
    coefficient1: float
    coefficient2: float


class EffectAmounts(BaseModel):
    Effect1Amount: List[float]
    Effect2Amount: List[float]
    Effect3Amount: List[float]
    Effect4Amount: List[float]
    Effect5Amount: List[float]
    Effect6Amount: List[float]
    Effect7Amount: List[float]
    Effect8Amount: List[float]
    Effect9Amount: List[float]
    Effect10Amount: List[float]


class Ammo(BaseModel):
    ammoRechargeTime: List[float]
    maxAmmo: List[int]


class Spell(BaseModel):
    spellKey: str
    name: str
    abilityIconPath: str
    abilityVideoPath: str
    abilityVideoImagePath: str
    cost: str
    cooldown: str
    description: str
    dynamicDescription: str
    range: List[float]
    costCoefficients: List[float]
    cooldownCoefficients: List[float]
    coefficients: Coefficients
    effectAmounts: EffectAmounts
    ammo: Ammo
    maxLevel: int


class ChampionDataDTO(BaseModel):
    id: int
    name: str
    alias: str
    title: str
    shortBio: str
    tacticalInfo: TacticalInfo
    playstyleInfo: PlaystyleInfo
    squarePortraitPath: str
    stingerSfxPath: str
    chooseVoPath: str
    banVoPath: str
    roles: List[str]
    recommendedItemDefaults: List
    skins: List[Skin]
    passive: Passive
    spells: List[Spell]
