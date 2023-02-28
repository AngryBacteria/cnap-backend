export interface SummonerDB {
    id: string,
    data: {
        name?: string,
        puuid: string,
        accountId?: string,
        revisionDate?: string,
        profileIconId?: string,
        summonerLevel?: string,
    },
}

export interface SummonerData {
    accountId:     string;
    profileIconId: number;
    revisionDate:  number;
    name:          string;
    id:            string;
    puuid:         string;
    summonerLevel: number;
}