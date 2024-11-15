from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from models.GlobalPydanticConfig import GLOBAL_PYDANTIC_CONFIG


# TODO expand
class ChampionDTO(BaseModel):
    model_config = GLOBAL_PYDANTIC_CONFIG
    id: int = Field(
        description="Unique identifier for the champion in the game system", example=1
    )
    key: str = Field(
        description="Internal reference key used by the game, typically the champion's name in lowercase",
        example="annie",
        min_length=1,
    )
    name: str = Field(
        description="Official display name of the champion",
        example="Annie",
    )
    title: str = Field(
        description="Champion's epithet or title that reflects their character",
        example="The Dark Child",
    )
    icon: str = Field(
        description="URL or path to the champion's primary icon image",
        example="https://ddragon.leagueoflegends.com/cdn/14.20.1/img/champion/Aatrox.png",
    )
    resource: str = Field(
        description="Type of resource the champion uses for abilities (Mana, Energy, None, etc.)",
        example="Mana",
    )
    attackType: str = Field(
        description="Primary attack classification of the champion (Melee or Ranged)",
        example="Ranged",
    )
    adaptiveType: str = Field(
        description="The type of damage the champion primarily scales with for adaptive force",
        example="AP",
    )
    positions: List[str] = Field(
        description="List of positions where the champion is commonly played",
        example=["Mid", "Support"],
    )
    roles: List[str] = Field(
        description="List of primary combat roles the champion fulfills",
        example=["Mage", "Support"],
    )
    releaseDate: str = Field(
        description="Date when the champion was first released", example="2009-02-21"
    )
    releasePatch: str = Field(
        description="Game version patch when the champion was released",
        example="12.1",
    )
    patchLastChanged: str = Field(
        description="Most recent patch version where the champion received changes",
        example="13.10.1",
    )
    lore: str = Field(
        description="Official character backstory and narrative",
        example="Dangerous, yet disarmingly precocious, Annie is a child mage with immense pyromantic power...",
    )
    faction: str = Field(
        description="The region or faction in Runeterra that the champion is affiliated with",
        example="Noxus",
    )
