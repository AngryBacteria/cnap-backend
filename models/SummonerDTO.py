from __future__ import annotations

from pydantic import BaseModel


class SummonerDTO(BaseModel):
    id: str
    accountId: str
    puuid: str
    profileIconId: int
    revisionDate: int
    summonerLevel: int
