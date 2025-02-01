from typing import Optional, List

from models.GlobalPydanticConfig import BaseConfig


class LolV1ChampionTacticalInfo(BaseConfig):
    style: int
    difficulty: int
    damageType: str


class LolV1ChampionPlaystyleInfo(BaseConfig):
    damage: int
    durability: int
    crowdControl: int
    mobility: int
    utility: int


class LolV1ChampionSkinLine(BaseConfig):
    id: int


class LolV1ChampionSkinChromaDescription(BaseConfig):
    region: str
    description: str


class LolV1ChampionSkinChromaRarity(BaseConfig):
    region: str
    rarity: int


class LolV1ChampionSkinChroma(BaseConfig):
    id: int
    name: str
    chromaPath: str
    colors: List[str]
    descriptions: List[LolV1ChampionSkinChromaDescription]
    rarities: List[LolV1ChampionSkinChromaRarity]


class LolV1ChampionSkin(BaseConfig):
    id: int
    isBase: bool
    name: str
    splashPath: str
    uncenteredSplashPath: str
    tilePath: str
    loadScreenPath: str
    loadScreenVintagePath: Optional[str] = None
    skinType: str
    rarity: str
    isLegacy: bool
    splashVideoPath: Optional[str]
    collectionSplashVideoPath: Optional[str]
    collectionCardHoverVideoPath: Optional[str]
    featuresText: Optional[str]
    chromaPath: Optional[str] = None
    emblems: Optional[str]
    regionRarityId: int
    rarityGemPath: Optional[str]
    skinLines: Optional[List[LolV1ChampionSkinLine]]
    description: Optional[str]
    chromas: Optional[List[LolV1ChampionSkinChroma]] = None


class LolV1ChampionPassive(BaseConfig):
    name: str
    abilityIconPath: str
    abilityVideoPath: str
    abilityVideoImagePath: str
    description: str


class LolV1ChampionSpellCoefficients(BaseConfig):
    coefficient1: float
    coefficient2: float


class LolV1ChampionSpellEffectAmounts(BaseConfig):
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


class LolV1ChampionSpellAmmo(BaseConfig):
    ammoRechargeTime: List[float]
    maxAmmo: List[int]


class LolV1ChampionSpell(BaseConfig):
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
    coefficients: LolV1ChampionSpellCoefficients
    effectAmounts: LolV1ChampionSpellEffectAmounts
    ammo: LolV1ChampionSpellAmmo
    maxLevel: int


class ChampionDTO(BaseConfig):
    id: int
    name: str
    alias: str
    title: str
    shortBio: str
    tacticalInfo: LolV1ChampionTacticalInfo
    playstyleInfo: LolV1ChampionPlaystyleInfo
    squarePortraitPath: str
    stingerSfxPath: str
    chooseVoPath: str
    banVoPath: str
    roles: List[str]
    recommendedItemDefaults: List[int]
    skins: List[LolV1ChampionSkin]
    passive: LolV1ChampionPassive
    spells: List[LolV1ChampionSpell]
    uncenteredSplashPath: str
