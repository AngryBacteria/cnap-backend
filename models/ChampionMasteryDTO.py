from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RequireGradeCounts(BaseModel):
    S_: Optional[int] = Field(None, alias="S-")
    C_: int = Field(..., alias="C-")
    B_: Optional[int] = Field(None, alias="B-")
    A_: Optional[int] = Field(None, alias="A-")


class RewardConfig(BaseModel):
    rewardValue: str
    rewardType: str
    maximumReward: int


class NextSeasonMilestone(BaseModel):
    requireGradeCounts: RequireGradeCounts
    rewardMarks: int
    bonus: bool
    rewardConfig: Optional[RewardConfig] = None
    totalGamesRequires: int


class ChampionMasteryDTO(BaseModel):
    puuid: str
    championId: int
    championLevel: int
    championPoints: int
    lastPlayTime: int
    championPointsSinceLastLevel: int
    championPointsUntilNextLevel: int
    markRequiredForNextLevel: int
    tokensEarned: int
    championSeasonMilestone: int
    milestoneGrades: Optional[List[str]] = None
    nextSeasonMilestone: NextSeasonMilestone
