from __future__ import annotations

from models.GlobalPydanticConfig import BaseConfig


class MapDTO(BaseConfig):
    mapId: int
    mapName: str
    notes: str
