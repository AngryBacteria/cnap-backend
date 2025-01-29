from __future__ import annotations

from typing import List

from pydantic import Field

from models.GlobalPydanticConfig import BaseConfig


class ChampionDTO(BaseConfig):
    id: int = Field(
        description="Unique identifier for the champion in the game system",
        examples=[1],
    )
    key: str = Field(
        description="Internal reference key used by the game, typically the champion's name in lowercase",
        examples=["annie"],
        min_length=1,
    )
    name: str = Field(
        description="Official display name of the champion",
        examples=["Annie"],
    )
    title: str = Field(
        description="Champion's epithet or title that reflects their character",
        examples=["The Dark Child"],
    )
    icon: str = Field(
        description="URL or path to the champion's primary icon image",
        examples=[
            "https://ddragon.leagueoflegends.com/cdn/14.20.1/img/champion/Aatrox.png"
        ],
    )
    resource: str = Field(
        description="Type of resource the champion uses for abilities (Mana, Energy, None, etc.)",
        examples=["Mana"],
    )
    attackType: str = Field(
        description="Primary attack classification of the champion (Melee or Ranged)",
        examples=["Ranged"],
    )
    adaptiveType: str = Field(
        description="The type of damage the champion primarily scales with for adaptive force",
        examples=["AP"],
    )
    positions: List[str] = Field(
        description="List of positions where the champion is commonly played",
        examples=["Mid", "Support"],
    )
    roles: List[str] = Field(
        description="List of primary combat roles the champion fulfills",
        examples=["Mage", "Support"],
    )
    releaseDate: str = Field(
        description="Date when the champion was first released", examples=["2009-02-21"]
    )
    releasePatch: str = Field(
        description="Game version patch when the champion was released",
        examples=["12.1"],
    )
    patchLastChanged: str = Field(
        description="Most recent patch version where the champion received changes",
        examples=["13.10.1"],
    )
    lore: str = Field(
        description="Official character backstory and narrative",
        examples=[
            "Dangerous, yet disarmingly precocious, Annie is a child mage with immense pyromantic power..."
        ],
    )
    faction: str = Field(
        description="The region or faction in Runeterra that the champion is affiliated with",
        examples=["Noxus"],
    )