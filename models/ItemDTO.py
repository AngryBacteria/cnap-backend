from __future__ import annotations

from pydantic import BaseModel

from models.GlobalPydanticConfig import GLOBAL_PYDANTIC_CONFIG


class ItemDTO(BaseModel):
    model_config = GLOBAL_PYDANTIC_CONFIG
    name: str
    id: int
    tier: int
    icon: str
