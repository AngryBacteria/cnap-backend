from helpers.DBHelper import DBHelper, SummonerFilter
from helpers.RiotHelper import RiotHelper
from models.SummonerDTODB import SummonerDTODB


class SummonerTasks:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()
        self.account_names = [
            {"name": "AngryBacteria", "tag": "cnap"},
            {"name": "BriBri", "tag": "0699"},
            {"name": "VerniHD", "tag": "EUW"},
            {"name": "Baywack", "tag": "CnAP"},
            {"name": "3 6 6 1", "tag": "#EUW"},
            {"name": "SignisAura", "tag": "CnAP"},
            {"name": "Alraune22", "tag": "CnAP"},
            {"name": "Aw3s0m3mag1c", "tag": "EUW"},
            {"name": "Gnerfedurf", "tag": "BCH"},
            {"name": "Gnoblin", "tag": "BCH"},
            {"name": "VredVampire", "tag": "2503"},
            {"name": "D3M0NK1LL3RG0D", "tag": "EUW"},
            {"name": "GLOMVE", "tag": "EUW"},
            {"name": "hide on büschli", "tag": "EUW"},
            {"name": "IBlueSnow", "tag": "EUW"},
            {"name": "Nayan Stocker", "tag": "EUW"},
            {"name": "Norina Michel", "tag": "EUW"},
            {"name": "pentaskill", "tag": "CnAP"},
            {"name": "Pollux", "tag": "2910"},
            {"name": "Polylinux", "tag": "EUW"},
            {"name": "Prequ", "tag": "EUW"},
            {"name": "Sausage Revolver", "tag": "EUW"},
            {"name": "swiss egirI", "tag": "EUW"},
            {"name": "TCT Tawan", "tag": "EUW"},
            {"name": "The 26th Bam", "tag": "EUW"},
            {"name": "Theera3rd", "tag": "EUW"},
            {"name": "Zinsstro", "tag": "EUW"},
            {"name": "WhatThePlay", "tag": "CnAP"},
            {"name": "pentaskill", "tag": "CnAP"},
            {"name": "Árexo", "tag": "CNAP"},
        ]

    async def fill_summoners(self):
        summoner_objects = []

        for account in self.account_names:
            summoner_data = await self.riot_helper.get_summoner_by_account_tag(
                account["name"], account["tag"]
            )
            if summoner_data is not None:
                summoner_objects.append(summoner_data)

        summoner_objects = [obj for obj in summoner_objects]
        await self.db_helper.generic_upsert(
            summoner_objects,
            "puuid",
            self.db_helper.summoner_collection,
            data_name="Summoner",
            validator=SummonerDTODB,
        )

    async def add_summoner(self, name: str, tag: str, puuid: str | None = None):
        if puuid is not None:
            summoner_data = await self.riot_helper.get_summoner_by_puuid_riot(puuid)
        else:
            summoner_data = await self.riot_helper.get_summoner_by_account_tag(
                name, tag
            )

        if summoner_data is not None:
            await self.db_helper.generic_upsert(
                [summoner_data],
                "puuid",
                self.db_helper.summoner_collection,
                data_name="Summoner",
                validator=SummonerDTODB,
            )
        else:
            raise ValueError("Summoner not found")

    async def update_summoner_data(self):
        existing_summoners = await self.db_helper.get_summoners(
            SummonerFilter(limit=1000)
        )
        if existing_summoners and len(existing_summoners) > 0:
            new_summoners = []
            for summoner in existing_summoners:
                summoner_riot = await self.riot_helper.get_summoner_by_puuid_riot(
                    summoner.puuid
                )
                if summoner_riot:
                    new_summoners.append(summoner_riot)

            await self.db_helper.generic_upsert(
                new_summoners,
                "puuid",
                self.db_helper.summoner_collection,
                "Summoner",
                SummonerDTODB,
            )
