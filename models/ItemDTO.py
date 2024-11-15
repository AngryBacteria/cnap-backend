from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from models.GlobalPydanticConfig import GLOBAL_PYDANTIC_CONFIG


# TODO expand
class ItemDTO(BaseModel):
    model_config = GLOBAL_PYDANTIC_CONFIG
    name: str
    id: int
    tier: int
    icon: str
