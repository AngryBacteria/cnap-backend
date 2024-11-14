from __future__ import annotations

from pydantic import BaseModel


class AccountDTO(BaseModel):
    puuid: str
    gameName: str
    tagLine: str
