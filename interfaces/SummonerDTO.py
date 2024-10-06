from typing import Optional

from pydantic import BaseModel


class SummonerDTO(BaseModel):
    id: Optional[str] = None
    accountId: Optional[str] = None
    puuid: Optional[str] = None
    profileIconId: Optional[int] = None
    revisionDate: Optional[int] = None
    summonerLevel: Optional[int] = None
    gameName: Optional[str] = None
    tagLine: Optional[str] = None
