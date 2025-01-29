from __future__ import annotations

from models.GlobalPydanticConfig import BaseConfig


class GameTypeDTO(BaseConfig):
    gametype: str
    description: str
