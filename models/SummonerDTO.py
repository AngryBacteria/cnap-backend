from __future__ import annotations

from pydantic import BaseModel, Field

from models.GlobalPydanticConfig import GLOBAL_PYDANTIC_CONFIG


class SummonerDTO(BaseModel):
    model_config = GLOBAL_PYDANTIC_CONFIG
    id: str = Field(
        description="Encrypted summoner ID. Used for looking up League-specific information.",
        examples=["OWjT1dt-lDb7Be0bSqcDJz3h9wdJEfkgf1OQjlKWKYmn138"],
    )
    accountId: str = Field(
        description="Encrypted account ID. Legacy identifier maintained for backwards compatibility.",
        examples=["EBBi1JBAgp-kqxQUnk04ZyCfehwDukJRD3OoNTWyDfkzFxk"],
    )
    puuid: str = Field(
        description="Player Universally Unique Identifier. A unique identifier for the player across all Riot games.",
        examples=[
            "zk1tF-l0TT1SrT9SbUmofKLT4R2gLKxzhGSyNuuxTCbmjr6dOqTCw1GcYrHoRp5DV2f5M17GMLPEFw"
        ],
    )
    profileIconId: int = Field(
        description="ID of the summoner icon associated with the player profile.",
        examples=[5294],
    )
    revisionDate: int = Field(
        description="Date when the summoner profile was last modified, in epoch milliseconds.",
        examples=[1731621546313],
    )
    summonerLevel: int = Field(
        description="Experience level of the summoner account.", examples=[367]
    )
