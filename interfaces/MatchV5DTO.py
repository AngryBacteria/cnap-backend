from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Challenges(BaseModel):

    field_12AssistStreakCount: Optional[int] = Field(None, alias="12AssistStreakCount")
    HealFromMapSources: Optional[int] = None
    InfernalScalePickup: Optional[int] = None
    SWARM_DefeatAatrox: Optional[int] = None
    SWARM_DefeatBriar: Optional[int] = None
    SWARM_DefeatMiniBosses: Optional[int] = None
    SWARM_EvolveWeapon: Optional[int] = None
    SWARM_Have3Passives: Optional[int] = None
    SWARM_KillEnemy: Optional[int] = None
    SWARM_PickupGold: Optional[int] = None
    SWARM_ReachLevel50: Optional[int] = None
    SWARM_Survive15Min: Optional[int] = None
    SWARM_WinWith5EvolvedWeapons: Optional[int] = None
    abilityUses: Optional[int] = None
    acesBefore15Minutes: Optional[int] = None
    alliedJungleMonsterKills: Optional[int] = None
    baronTakedowns: Optional[int] = None
    blastConeOppositeOpponentCount: Optional[int] = None
    bountyGold: Optional[int] = None
    buffsStolen: Optional[int] = None
    completeSupportQuestInTime: Optional[int] = None
    controlWardsPlaced: Optional[int] = None
    damagePerMinute: Optional[float] = None
    damageTakenOnTeamPercentage: Optional[float] = None
    dancedWithRiftHerald: Optional[int] = None
    deathsByEnemyChamps: Optional[int] = None
    dodgeSkillShotsSmallWindow: Optional[int] = None
    doubleAces: Optional[int] = None
    dragonTakedowns: Optional[int] = None
    earlyLaningPhaseGoldExpAdvantage: Optional[int] = None
    effectiveHealAndShielding: Optional[float] = None
    elderDragonKillsWithOpposingSoul: Optional[int] = None
    elderDragonMultikills: Optional[int] = None
    enemyChampionImmobilizations: Optional[int] = None
    enemyJungleMonsterKills: Optional[int] = None
    epicMonsterKillsNearEnemyJungler: Optional[int] = None
    epicMonsterKillsWithin30SecondsOfSpawn: Optional[int] = None
    epicMonsterSteals: Optional[int] = None
    epicMonsterStolenWithoutSmite: Optional[int] = None
    firstTurretKilled: Optional[int] = None
    fistBumpParticipation: Optional[int] = None
    flawlessAces: Optional[int] = None
    fullTeamTakedown: Optional[int] = None
    gameLength: Optional[float] = None
    getTakedownsInAllLanesEarlyJungleAsLaner: Optional[int] = None
    goldPerMinute: Optional[float] = None
    hadOpenNexus: Optional[int] = None
    immobilizeAndKillWithAlly: Optional[int] = None
    initialBuffCount: Optional[int] = None
    initialCrabCount: Optional[int] = None
    jungleCsBefore10Minutes: Optional[float] = None
    junglerTakedownsNearDamagedEpicMonster: Optional[int] = None
    kTurretsDestroyedBeforePlatesFall: Optional[int] = None
    kda: Optional[float] = None
    killAfterHiddenWithAlly: Optional[int] = None
    killParticipation: Optional[float] = None
    killedChampTookFullTeamDamageSurvived: Optional[int] = None
    killingSprees: Optional[int] = None
    killsNearEnemyTurret: Optional[int] = None
    killsOnOtherLanesEarlyJungleAsLaner: Optional[int] = None
    killsOnRecentlyHealedByAramPack: Optional[int] = None
    killsUnderOwnTurret: Optional[int] = None
    killsWithHelpFromEpicMonster: Optional[int] = None
    knockEnemyIntoTeamAndKill: Optional[int] = None
    landSkillShotsEarlyGame: Optional[int] = None
    laneMinionsFirst10Minutes: Optional[int] = None
    laningPhaseGoldExpAdvantage: Optional[int] = None
    legendaryCount: Optional[int] = None
    legendaryItemUsed: Optional[List[int]] = None
    lostAnInhibitor: Optional[int] = None
    maxCsAdvantageOnLaneOpponent: Optional[float] = None
    maxKillDeficit: Optional[int] = None
    maxLevelLeadLaneOpponent: Optional[int] = None
    mejaisFullStackInTime: Optional[int] = None
    moreEnemyJungleThanOpponent: Optional[float] = None
    multiKillOneSpell: Optional[int] = None
    multiTurretRiftHeraldCount: Optional[int] = None
    multikills: Optional[int] = None
    multikillsAfterAggressiveFlash: Optional[int] = None
    outerTurretExecutesBefore10Minutes: Optional[int] = None
    outnumberedKills: Optional[int] = None
    outnumberedNexusKill: Optional[int] = None
    perfectDragonSoulsTaken: Optional[int] = None
    perfectGame: Optional[int] = None
    pickKillWithAlly: Optional[int] = None
    playedChampSelectPosition: Optional[int] = None
    poroExplosions: Optional[int] = None
    quickCleanse: Optional[int] = None
    quickFirstTurret: Optional[int] = None
    quickSoloKills: Optional[int] = None
    riftHeraldTakedowns: Optional[int] = None
    saveAllyFromDeath: Optional[int] = None
    scuttleCrabKills: Optional[int] = None
    skillshotsDodged: Optional[int] = None
    skillshotsHit: Optional[int] = None
    snowballsHit: Optional[int] = None
    soloBaronKills: Optional[int] = None
    soloKills: Optional[int] = None
    stealthWardsPlaced: Optional[int] = None
    survivedSingleDigitHpCount: Optional[int] = None
    survivedThreeImmobilizesInFight: Optional[int] = None
    takedownOnFirstTurret: Optional[int] = None
    takedowns: Optional[int] = None
    takedownsAfterGainingLevelAdvantage: Optional[int] = None
    takedownsBeforeJungleMinionSpawn: Optional[int] = None
    takedownsFirstXMinutes: Optional[int] = None
    takedownsInAlcove: Optional[int] = None
    takedownsInEnemyFountain: Optional[int] = None
    teamBaronKills: Optional[int] = None
    teamDamagePercentage: Optional[float] = None
    teamElderDragonKills: Optional[int] = None
    teamRiftHeraldKills: Optional[int] = None
    tookLargeDamageSurvived: Optional[int] = None
    turretPlatesTaken: Optional[int] = None
    turretTakedowns: Optional[int] = None
    turretsTakenWithRiftHerald: Optional[int] = None
    twentyMinionsIn3SecondsCount: Optional[int] = None
    twoWardsOneSweeperCount: Optional[int] = None
    unseenRecalls: Optional[int] = None
    visionScoreAdvantageLaneOpponent: Optional[float] = None
    visionScorePerMinute: Optional[float] = None
    voidMonsterKill: Optional[int] = None
    wardTakedowns: Optional[int] = None
    wardTakedownsBefore20M: Optional[int] = None
    wardsGuarded: Optional[int] = None
    earliestDragonTakedown: Optional[float] = None
    junglerKillsEarlyJungle: Optional[int] = None
    killsOnLanersEarlyJungleAsJungler: Optional[int] = None
    soloTurretsLategame: Optional[int] = None
    baronBuffGoldAdvantageOverThreshold: Optional[int] = None
    earliestBaron: Optional[float] = None
    firstTurretKilledTime: Optional[float] = None
    highestChampionDamage: Optional[int] = None
    shortestTimeToAceFromFirstTakedown: Optional[float] = None
    highestCrowdControlScore: Optional[int] = None
    highestWardKills: Optional[int] = None
    fasterSupportQuestCompletion: Optional[int] = None


class StatPerks(BaseModel):

    defense: Optional[int] = None
    flex: Optional[int] = None
    offense: Optional[int] = None


class Selection(BaseModel):

    perk: Optional[int] = None
    var1: Optional[int] = None
    var2: Optional[int] = None
    var3: Optional[int] = None


class Ban(BaseModel):

    championId: Optional[int] = None
    pickTurn: Optional[int] = None


class Baron(BaseModel):

    first: Optional[bool] = None
    kills: Optional[int] = None


class Metadata(BaseModel):

    dataVersion: Optional[int] = None
    matchId: Optional[str] = None
    participants: Optional[List[str]] = None


class Description(Enum):
    primaryStyle = "primaryStyle"
    subStyle = "subStyle"


class Style(BaseModel):

    description: Optional[Description] = None
    selections: Optional[List[Selection]] = None
    style: Optional[int] = None


class Objectives(BaseModel):

    baron: Optional[Baron] = None
    champion: Optional[Baron] = None
    dragon: Optional[Baron] = None
    horde: Optional[Baron] = None
    inhibitor: Optional[Baron] = None
    riftHerald: Optional[Baron] = None
    tower: Optional[Baron] = None


class Perks(BaseModel):

    statPerks: Optional[StatPerks] = None
    styles: Optional[List[Style]] = None


class Team(BaseModel):

    bans: Optional[List[Ban]] = None
    objectives: Optional[Objectives] = None
    teamId: Optional[int] = None
    win: Optional[bool] = None


class Participant(BaseModel):

    allInPings: Optional[int] = None
    assistMePings: Optional[int] = None
    assists: Optional[int] = None
    baronKills: Optional[int] = None
    basicPings: Optional[int] = None
    bountyLevel: Optional[int] = None
    challenges: Optional[Challenges] = None
    champExperience: Optional[int] = None
    champLevel: Optional[int] = None
    championId: Optional[int] = None
    championName: Optional[str] = None
    championTransform: Optional[int] = None
    commandPings: Optional[int] = None
    consumablesPurchased: Optional[int] = None
    damageDealtToBuildings: Optional[int] = None
    damageDealtToObjectives: Optional[int] = None
    damageDealtToTurrets: Optional[int] = None
    damageSelfMitigated: Optional[int] = None
    dangerPings: Optional[int] = None
    deaths: Optional[int] = None
    detectorWardsPlaced: Optional[int] = None
    doubleKills: Optional[int] = None
    dragonKills: Optional[int] = None
    eligibleForProgression: Optional[bool] = None
    enemyMissingPings: Optional[int] = None
    enemyVisionPings: Optional[int] = None
    firstBloodAssist: Optional[bool] = None
    firstBloodKill: Optional[bool] = None
    firstTowerAssist: Optional[bool] = None
    firstTowerKill: Optional[bool] = None
    gameEndedInEarlySurrender: Optional[bool] = None
    gameEndedInSurrender: Optional[bool] = None
    getBackPings: Optional[int] = None
    goldEarned: Optional[int] = None
    goldSpent: Optional[int] = None
    holdPings: Optional[int] = None
    individualPosition: Optional[str] = None
    inhibitorKills: Optional[int] = None
    inhibitorTakedowns: Optional[int] = None
    inhibitorsLost: Optional[int] = None
    item0: Optional[int] = None
    item1: Optional[int] = None
    item2: Optional[int] = None
    item3: Optional[int] = None
    item4: Optional[int] = None
    item5: Optional[int] = None
    item6: Optional[int] = None
    itemsPurchased: Optional[int] = None
    killingSprees: Optional[int] = None
    kills: Optional[int] = None
    lane: Optional[str] = None
    largestCriticalStrike: Optional[int] = None
    largestKillingSpree: Optional[int] = None
    largestMultiKill: Optional[int] = None
    longestTimeSpentLiving: Optional[int] = None
    magicDamageDealt: Optional[int] = None
    magicDamageDealtToChampions: Optional[int] = None
    magicDamageTaken: Optional[int] = None
    missions: Optional[Dict[str, int]] = None
    needVisionPings: Optional[int] = None
    neutralMinionsKilled: Optional[int] = None
    nexusKills: Optional[int] = None
    nexusLost: Optional[int] = None
    nexusTakedowns: Optional[int] = None
    objectivesStolen: Optional[int] = None
    objectivesStolenAssists: Optional[int] = None
    onMyWayPings: Optional[int] = None
    participantId: Optional[int] = None
    pentaKills: Optional[int] = None
    perks: Optional[Perks] = None
    physicalDamageDealt: Optional[int] = None
    physicalDamageDealtToChampions: Optional[int] = None
    physicalDamageTaken: Optional[int] = None
    placement: Optional[int] = None
    playerAugment1: Optional[int] = None
    playerAugment2: Optional[int] = None
    playerAugment3: Optional[int] = None
    playerAugment4: Optional[int] = None
    playerAugment5: Optional[int] = None
    playerAugment6: Optional[int] = None
    playerSubteamId: Optional[int] = None
    profileIcon: Optional[int] = None
    pushPings: Optional[int] = None
    puuid: Optional[str] = None
    quadraKills: Optional[int] = None
    riotIdGameName: Optional[str] = None
    riotIdTagline: Optional[str] = None
    role: Optional[str] = None
    sightWardsBoughtInGame: Optional[int] = None
    spell1Casts: Optional[int] = None
    spell2Casts: Optional[int] = None
    spell3Casts: Optional[int] = None
    spell4Casts: Optional[int] = None
    subteamPlacement: Optional[int] = None
    summoner1Casts: Optional[int] = None
    summoner1Id: Optional[int] = None
    summoner2Casts: Optional[int] = None
    summoner2Id: Optional[int] = None
    summonerId: Optional[str] = None
    summonerLevel: Optional[int] = None
    summonerName: Optional[str] = None
    teamEarlySurrendered: Optional[bool] = None
    teamId: Optional[int] = None
    teamPosition: Optional[str] = None
    timeCCingOthers: Optional[int] = None
    timePlayed: Optional[int] = None
    totalAllyJungleMinionsKilled: Optional[int] = None
    totalDamageDealt: Optional[int] = None
    totalDamageDealtToChampions: Optional[int] = None
    totalDamageShieldedOnTeammates: Optional[int] = None
    totalDamageTaken: Optional[int] = None
    totalEnemyJungleMinionsKilled: Optional[int] = None
    totalHeal: Optional[int] = None
    totalHealsOnTeammates: Optional[int] = None
    totalMinionsKilled: Optional[int] = None
    totalTimeCCDealt: Optional[int] = None
    totalTimeSpentDead: Optional[int] = None
    totalUnitsHealed: Optional[int] = None
    tripleKills: Optional[int] = None
    trueDamageDealt: Optional[int] = None
    trueDamageDealtToChampions: Optional[int] = None
    trueDamageTaken: Optional[int] = None
    turretKills: Optional[int] = None
    turretTakedowns: Optional[int] = None
    turretsLost: Optional[int] = None
    unrealKills: Optional[int] = None
    visionClearedPings: Optional[int] = None
    visionScore: Optional[int] = None
    visionWardsBoughtInGame: Optional[int] = None
    wardsKilled: Optional[int] = None
    wardsPlaced: Optional[int] = None
    win: Optional[bool] = None


class Info(BaseModel):

    endOfGameResult: Optional[str] = None
    gameCreation: Optional[int] = None
    gameDuration: Optional[int] = None
    gameEndTimestamp: Optional[int] = None
    gameId: Optional[int] = None
    gameMode: Optional[str] = None
    gameName: Optional[str] = None
    gameStartTimestamp: Optional[int] = None
    gameType: Optional[str] = None
    gameVersion: Optional[str] = None
    mapId: Optional[int] = None
    participants: Optional[List[Participant]] = None
    platformId: Optional[str] = None
    queueId: Optional[int] = None
    teams: Optional[List[Team]] = None
    tournamentCode: Optional[str] = None


class MatchV5DTO(BaseModel):

    metadata: Optional[Metadata] = None
    info: Optional[Info] = None
