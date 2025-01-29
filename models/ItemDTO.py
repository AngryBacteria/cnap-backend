from __future__ import annotations

from typing import List

from models.GlobalPydanticConfig import BaseConfig


# TODO verify model
class ItemDTO(BaseConfig):
    id: int
    name: str
    description: str
    categories: List[str]
    price: int
    priceTotal: int
    iconPath: str
