from __future__ import annotations

from pydantic import Field

from models.SummonerDTO import SummonerDTO


class SummonerDBDTO(SummonerDTO):
    gameName: str = Field(
        description="The player's in-game name (IGN) shown in League of Legends.",
        examples=["AngryBacteria"],
    )
    tagLine: str = Field(
        description="The player's tag line (similar to Discord's discriminator) that appears after the # in their Riot ID.",
        examples=["CNAP"],
    )
