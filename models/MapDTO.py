from __future__ import annotations
from pydantic import BaseModel


class MapDTO(BaseModel):
    mapId: int
    mapName: str
    notes: str
