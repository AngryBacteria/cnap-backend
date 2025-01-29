from __future__ import annotations

from models.GlobalPydanticConfig import BaseConfig


class ItemDTO(BaseConfig):
    name: str
    id: int
    icon: str
