from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class Position(BaseModel):

    x: Optional[int] = None
    y: Optional[int] = None


class ParticipantFrame(BaseModel):

    championStats: Optional[Dict[str, int]] = None
    currentGold: Optional[int] = None
    damageStats: Optional[Dict[str, int]] = None
    goldPerSecond: Optional[int] = None
    jungleMinionsKilled: Optional[int] = None
    level: Optional[int] = None
    minionsKilled: Optional[int] = None
    participantId: Optional[int] = None
    position: Optional[Position] = None
    timeEnemySpentControlled: Optional[int] = None
    totalGold: Optional[int] = None
    xp: Optional[int] = None


class Participant(BaseModel):

    participantId: Optional[int] = None
    puuid: Optional[str] = None


class Metadata(BaseModel):

    dataVersion: Optional[int] = None
    matchId: Optional[str] = None
    participants: Optional[List[str]] = None


class BuildingType(Enum):
    TOWER_BUILDING = "TOWER_BUILDING"
    INHIBITOR_BUILDING = "INHIBITOR_BUILDING"


class KillType(Enum):
    KILL_FIRST_BLOOD = "KILL_FIRST_BLOOD"
    KILL_MULTI = "KILL_MULTI"
    KILL_ACE = "KILL_ACE"


class LaneType(Enum):
    MID_LANE = "MID_LANE"
    BOT_LANE = "BOT_LANE"
    TOP_LANE = "TOP_LANE"


class LevelUpType(Enum):
    NORMAL = "NORMAL"


class MonsterType(Enum):
    HORDE = "HORDE"
    DRAGON = "DRAGON"
    BARON_NASHOR = "BARON_NASHOR"


class EventType(Enum):
    PAUSE_END = "PAUSE_END"
    LEVEL_UP = "LEVEL_UP"
    SKILL_LEVEL_UP = "SKILL_LEVEL_UP"
    ITEM_PURCHASED = "ITEM_PURCHASED"
    ITEM_UNDO = "ITEM_UNDO"
    WARD_PLACED = "WARD_PLACED"
    ITEM_DESTROYED = "ITEM_DESTROYED"
    CHAMPION_KILL = "CHAMPION_KILL"
    CHAMPION_SPECIAL_KILL = "CHAMPION_SPECIAL_KILL"
    ELITE_MONSTER_KILL = "ELITE_MONSTER_KILL"
    TURRET_PLATE_DESTROYED = "TURRET_PLATE_DESTROYED"
    ITEM_SOLD = "ITEM_SOLD"
    WARD_KILL = "WARD_KILL"
    BUILDING_KILL = "BUILDING_KILL"
    OBJECTIVE_BOUNTY_PRESTART = "OBJECTIVE_BOUNTY_PRESTART"
    DRAGON_SOUL_GIVEN = "DRAGON_SOUL_GIVEN"
    GAME_END = "GAME_END"


class Name(Enum):
    Garen = "Garen"
    Orianna = "Orianna"
    Darius = "Darius"
    TahmKench = "TahmKench"
    Caitlyn = "Caitlyn"
    Annie = "Annie"
    Alistar = "Alistar"
    Quinn = "Quinn"
    Vi = "Vi"
    Syndra = "Syndra"
    SRU_OrderMinionMelee = "SRU_OrderMinionMelee"
    SRU_OrderMinionRanged = "SRU_OrderMinionRanged"
    SRU_ChaosMinionRanged = "SRU_ChaosMinionRanged"
    Turret = "Turret"
    SRU_ChaosMinionMelee = "SRU_ChaosMinionMelee"
    SRU_OrderMinionSiege = "SRU_OrderMinionSiege"
    SRU_Dragon_Earth = "SRU_Dragon_Earth"
    SRU_ChaosMinionSiege = "SRU_ChaosMinionSiege"
    SRU_KrugMiniMini = "SRU_KrugMiniMini"
    SRU_Krug = "SRU_Krug"
    SRU_KrugMini = "SRU_KrugMini"
    SRU_RazorbeakMini = "SRU_RazorbeakMini"
    SRU_Razorbeak = "SRU_Razorbeak"


class VictimDamageDealtType(Enum):
    OTHER = "OTHER"
    MINION = "MINION"
    TOWER = "TOWER"
    MONSTER = "MONSTER"


class WardType(Enum):
    YELLOW_TRINKET = "YELLOW_TRINKET"
    UNDEFINED = "UNDEFINED"
    SIGHT_WARD = "SIGHT_WARD"


class VictimDamage(BaseModel):

    basic: Optional[bool] = None
    magicDamage: Optional[int] = None
    name: Optional[Name] = None
    participantId: Optional[int] = None
    physicalDamage: Optional[int] = None
    spellName: Optional[str] = None
    spellSlot: Optional[int] = None
    trueDamage: Optional[int] = None
    type: Optional[VictimDamageDealtType] = None


class Event(BaseModel):

    realTimestamp: Optional[int] = None
    timestamp: Optional[int] = None
    type: Optional[EventType] = None
    level: Optional[int] = None
    participantId: Optional[int] = None
    levelUpType: Optional[LevelUpType] = None
    skillSlot: Optional[int] = None
    itemId: Optional[int] = None
    afterId: Optional[int] = None
    beforeId: Optional[int] = None
    goldGain: Optional[int] = None
    creatorId: Optional[int] = None
    wardType: Optional[WardType] = None
    assistingParticipantIds: Optional[List[int]] = None
    bounty: Optional[int] = None
    killStreakLength: Optional[int] = None
    killerId: Optional[int] = None
    position: Optional[Position] = None
    shutdownBounty: Optional[int] = None
    victimDamageDealt: Optional[List[VictimDamage]] = None
    victimDamageReceived: Optional[List[VictimDamage]] = None
    victimId: Optional[int] = None
    killType: Optional[KillType] = None
    killerTeamId: Optional[int] = None
    monsterType: Optional[MonsterType] = None
    laneType: Optional[LaneType] = None
    teamId: Optional[int] = None
    monsterSubType: Optional[str] = None
    buildingType: Optional[BuildingType] = None
    towerType: Optional[str] = None
    multiKillLength: Optional[int] = None
    actualStartTime: Optional[int] = None
    name: Optional[str] = None
    gameId: Optional[int] = None
    winningTeam: Optional[int] = None


class Frame(BaseModel):

    events: Optional[List[Event]] = None
    participantFrames: Optional[Dict[str, ParticipantFrame]] = None
    timestamp: Optional[int] = None


class Info(BaseModel):

    endOfGameResult: Optional[str] = None
    frameInterval: Optional[int] = None
    frames: Optional[List[Frame]] = None
    gameId: Optional[int] = None
    participants: Optional[List[Participant]] = None


class TimelineDTO(BaseModel):

    metadata: Optional[Metadata] = None
    info: Optional[Info] = None
