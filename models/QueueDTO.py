from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class QueueDTO(BaseModel):
    queueId: int
    map: str
    description: Optional[str]
    notes: Optional[str]
