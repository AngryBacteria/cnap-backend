from __future__ import annotations

from pydantic import BaseModel, Field

from models.GlobalPydanticConfig import GLOBAL_PYDANTIC_CONFIG


class AccountDTO(BaseModel):
    model_config = GLOBAL_PYDANTIC_CONFIG
    puuid: str = Field(
        description="Player Universally Unique Identifier. A unique identifier for the player across all Riot games.",
        examples=[
            "zk1tF-l0TT1SrT9SbUmofKLT4R2gLKxzhGSyNuuxTCbmjr6dOqTCw1GcYrHoRp5DV2f5M17GMLPEFw"
        ],
    )
    gameName: str = Field(
        description="The player's in-game name (IGN) shown in League of Legends.",
        examples=["AngryBacteria"],
    )
    tagLine: str = Field(
        description="The player's tag line (similar to Discord's discriminator) that appears after the # in their Riot ID.",
        examples=["CNAP"],
    )
