from typing import Optional

from pydantic import BaseModel


class AccountDTO(BaseModel):
    puuid: Optional[str] = None
    gameName: Optional[str] = None
    tagLine: Optional[str] = None
