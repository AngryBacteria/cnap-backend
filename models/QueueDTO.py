from __future__ import annotations

from typing import Optional

from models.GlobalPydanticConfig import BaseConfig


class QueueDTO(BaseConfig):
    queueId: int
    map: str
    description: Optional[str]
    notes: Optional[str]
