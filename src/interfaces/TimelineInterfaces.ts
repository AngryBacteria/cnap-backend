export interface TimelineDTO {
  metadata: Metadata;
  info: Info;
}

export interface Info {
  frameInterval: number;
  frames: Frame[];
  gameId: number;
  participants: Participant[];
}

export interface Frame {
  events: Event[];
  participantFrames: { [key: string]: ParticipantFrame };
  timestamp: number;
}

export interface Event {
  realTimestamp: number;
  timestamp: number;
  type: string;
  itemId: number;
  participantId: number;
  levelUpType: string;
  skillSlot: number;
  creatorId: number;
  wardType: string;
  level: number;
  assistingParticipantIds: number[];
  bounty: number;
  killStreakLength: number;
  killerId: number;
  position: Position;
  victimDamageDealt: VictimDamage[];
  victimDamageReceived: VictimDamage[];
  victimId: number;
  killType: string;
  laneType: string;
  teamId: number;
  multiKillLength: number;
  killerTeamId: number;
  monsterType: string;
  monsterSubType: string;
  buildingType: string;
  towerType: string;
  afterId: number;
  beforeId: number;
  goldGain: number;
  gameId: number;
  winningTeam: number;
  transformType: string;
  name: string;
  shutdownBounty: number;
  actualStartTime: number;
}

export interface Position {
  x: number;
  y: number;
}

export interface VictimDamage {
  basic: boolean;
  magicDamage: number;
  name: string;
  participantId: number;
  physicalDamage: number;
  spellName: string;
  spellSlot: number;
  trueDamage: number;
  type: string;
}

export interface ParticipantFrame {
  championStats: { [key: string]: number };
  currentGold: number;
  damageStats: { [key: string]: number };
  goldPerSecond: number;
  jungleMinionsKilled: number;
  level: number;
  minionsKilled: number;
  participantId: number;
  position: Position;
  timeEnemySpentControlled: number;
  totalGold: number;
  xp: number;
}

export interface Participant {
  participantId: number;
  puuid: string;
}

export interface Metadata {
  dataVersion: string;
  matchId: string;
  participants: string[];
}
