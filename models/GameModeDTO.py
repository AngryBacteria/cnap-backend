from __future__ import annotations

from models.GlobalPydanticConfig import BaseConfig


class GameModeDTO(BaseConfig):
    gameMode: str
    description: str
