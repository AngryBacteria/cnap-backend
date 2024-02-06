export interface SummonerDTO {
  id: string;
  accountId: string;
  puuid: string;
  name: string;
  profileIconId: number;
  revisionDate: number;
  summonerLevel: number;
}

export interface MatchV5DTO {
  info: Info;
  metadata: Metadata;
}

export interface Info {
  mapId: number;
  teams: Team[];
  gameId: number;
  queueId: number;
  gameMode: string;
  gameName: string;
  gameType: string;
  platformId: string;
  gameVersion: string;
  gameCreation: number;
  gameDuration: number;
  participants: Participant[];
  tournamentCode: string;
  gameEndTimestamp: number;
  gameStartTimestamp: number;
}

export interface Participant {
  win: boolean;
  lane: string;
  role: string;
  item0: number;
  item1: number;
  item2: number;
  item3: number;
  item4: number;
  item5: number;
  item6: number;
  kills: number;
  perks: Perks;
  puuid: string;
  deaths: number;
  teamId: number;
  assists: number;
  missions: { [key: string]: number };
  baitPings: number;
  goldSpent: number;
  holdPings: number;
  nexusLost: number;
  placement: number;
  pushPings: number;
  totalHeal: number;
  allInPings: number;
  baronKills: number;
  basicPings: number;
  challenges: { [key: string]: number };
  champLevel: number;
  championId: number;
  goldEarned: number;
  nexusKills: number;
  pentaKills: number;
  summonerId: string;
  timePlayed: number;
  bountyLevel: number;
  dangerPings: number;
  doubleKills: number;
  dragonKills: number;
  profileIcon: number;
  quadraKills: number;
  spell1Casts: number;
  spell2Casts: number;
  spell3Casts: number;
  spell4Casts: number;
  summoner1Id: number;
  summoner2Id: number;
  tripleKills: number;
  turretKills: number;
  turretsLost: number;
  unrealKills: number;
  visionScore: number;
  wardsKilled: number;
  wardsPlaced: number;
  championName: string;
  commandPings: number;
  getBackPings: number;
  onMyWayPings: number;
  playerScore0: number;
  playerScore1: number;
  playerScore2: number;
  playerScore3: number;
  playerScore4: number;
  playerScore5: number;
  playerScore6: number;
  playerScore7: number;
  playerScore8: number;
  playerScore9: number;
  summonerName: string;
  teamPosition: string;
  assistMePings: number;
  killingSprees: number;
  participantId: number;
  playerScore10: number;
  playerScore11: number;
  riotIdTagline: string;
  summonerLevel: number;
  firstBloodKill: boolean;
  firstTowerKill: boolean;
  inhibitorKills: number;
  inhibitorsLost: number;
  itemsPurchased: number;
  nexusTakedowns: number;
  playerAugment1: number;
  playerAugment2: number;
  playerAugment3: number;
  playerAugment4: number;
  riotIdGameName: string;
  summoner1Casts: number;
  summoner2Casts: number;
  champExperience: number;
  needVisionPings: number;
  playerSubteamId: number;
  timeCCingOthers: number;
  trueDamageDealt: number;
  trueDamageTaken: number;
  turretTakedowns: number;
  enemyVisionPings: number;
  firstBloodAssist: boolean;
  firstTowerAssist: boolean;
  largestMultiKill: number;
  magicDamageDealt: number;
  magicDamageTaken: number;
  objectivesStolen: number;
  subteamPlacement: number;
  totalDamageDealt: number;
  totalDamageTaken: number;
  totalTimeCCDealt: number;
  totalUnitsHealed: number;
  championTransform: number;
  enemyMissingPings: number;
  individualPosition: string;
  inhibitorTakedowns: number;
  totalMinionsKilled: number;
  totalTimeSpentDead: number;
  visionClearedPings: number;
  damageSelfMitigated: number;
  detectorWardsPlaced: number;
  largestKillingSpree: number;
  physicalDamageDealt: number;
  physicalDamageTaken: number;
  consumablesPurchased: number;
  damageDealtToTurrets: number;
  gameEndedInSurrender: boolean;
  neutralMinionsKilled: number;
  teamEarlySurrendered: boolean;
  largestCriticalStrike: number;
  totalHealsOnTeammates: number;
  damageDealtToBuildings: number;
  eligibleForProgression: boolean;
  longestTimeSpentLiving: number;
  sightWardsBoughtInGame: number;
  damageDealtToObjectives: number;
  objectivesStolenAssists: number;
  visionWardsBoughtInGame: number;
  gameEndedInEarlySurrender: boolean;
  trueDamageDealtToChampions: number;
  magicDamageDealtToChampions: number;
  totalDamageDealtToChampions: number;
  totalAllyJungleMinionsKilled: number;
  totalEnemyJungleMinionsKilled: number;
  physicalDamageDealtToChampions: number;
  totalDamageShieldedOnTeammates: number;
}

export interface Perks {
  styles: Style[];
  statPerks: StatPerks;
}

export interface StatPerks {
  flex: number;
  defense: number;
  offense: number;
}

export interface Style {
  style: number;
  selections: Selection[];
  description: Description;
}

export enum Description {
  PrimaryStyle = 'primaryStyle',
  SubStyle = 'subStyle',
}

export interface Selection {
  perk: number;
  var1: number;
  var2: number;
  var3: number;
}

export interface Team {
  win: boolean;
  bans: Ban[];
  teamId: number;
  objectives: Objectives;
}

export interface Ban {
  pickTurn: number;
  championId: number;
}

export interface Objectives {
  baron: Baron;
  horde: Baron;
  tower: Baron;
  dragon: Baron;
  champion: Baron;
  inhibitor: Baron;
  riftHerald: Baron;
}

export interface Baron {
  first: boolean;
  kills: number;
}

export interface Metadata {
  matchId: string;
  dataVersion: string;
  participants: string[];
}

export interface AccountDto {
  puuid: string;
  gameName: string;
  tagLine: string;
}
