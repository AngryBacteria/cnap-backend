from __future__ import annotations
from pydantic import BaseModel


class GameModeDTO(BaseModel):
    gameMode: str
    description: str
