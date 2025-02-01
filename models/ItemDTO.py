from __future__ import annotations

from typing import List

from models.GlobalPydanticConfig import BaseConfig


class ItemDTO(BaseConfig):
    id: int
    name: str
    description: str
    active: bool
    inStore: bool
    categories: List[str]
    maxStacks: int
    requiredChampion: str
    requiredAlly: str
    requiredBuffCurrencyName: str
    requiredBuffCurrencyCost: int
    specialRecipe: int
    isEnchantment: bool
    price: int
    priceTotal: int
    iconPath: str
    displayInItemSets: bool
