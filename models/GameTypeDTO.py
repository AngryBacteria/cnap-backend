from __future__ import annotations

from pydantic import BaseModel


class GameTypeDTO(BaseModel):
    gametype: str
    description: str
