import asyncio
from typing import List, Dict, Optional

from helpers.DBHelper import DBHelper
from helpers.RiotHelper import RiotHelper


class FillSummonersTask:
    def __init__(self):
        self.db_helper = DBHelper()
        self.riot_helper = RiotHelper()
        self.account_names = [
            {"name": "AngryBacteria", "tag": "cnap", "core": True},
            {"name": "BriBri", "tag": "0699", "core": True},
            {"name": "VerniHD", "tag": "EUW", "core": False},
            {"name": "Baywack", "tag": "CnAP", "core": True},
            {"name": "3 6 6 1", "tag": "#EUW", "core": False},
            {"name": "SignisAura", "tag": "CnAP", "core": True},
            {"name": "Alraune22", "tag": "CnAP", "core": True},
            {"name": "Aw3s0m3mag1c", "tag": "EUW", "core": False},
            {"name": "Gnerfedurf", "tag": "BCH", "core": True},
            {"name": "Gnoblin", "tag": "BCH", "core": True},
            {"name": "VredVampire", "tag": "2503", "core": False},
            {"name": "D3M0NK1LL3RG0D", "tag": "EUW", "core": True},
            {"name": "GLOMVE", "tag": "EUW", "core": False},
            {"name": "hide on büschli", "tag": "EUW", "core": True},
            {"name": "IBlueSnow", "tag": "EUW", "core": False},
            {"name": "Nayan Stocker", "tag": "EUW", "core": False},
            {"name": "Norina Michel", "tag": "EUW", "core": False},
            {"name": "pentaskill", "tag": "CnAP", "core": True},
            {"name": "Pollux", "tag": "2910", "core": True},
            {"name": "Polylinux", "tag": "EUW", "core": False},
            {"name": "Prequ", "tag": "EUW", "core": True},
            {"name": "Sausage Revolver", "tag": "EUW", "core": False},
            {"name": "swiss egirI", "tag": "EUW", "core": False},
            {"name": "TCT Tawan", "tag": "EUW", "core": False},
            {"name": "The 26th Bam", "tag": "EUW", "core": False},
            {"name": "Theera3rd", "tag": "EUW", "core": False},
            {"name": "Zinsstro", "tag": "EUW", "core": False},
            {"name": "WhatThePlay", "tag": "CnAP", "core": True},
            {"name": "pentaskill", "tag": "CnAP", "core": True},
            {"name": "Árexo", "tag": "CNAP", "core": True},
        ]

    async def fill_summoners(self, core_only=True):
        summoner_objects = []

        for account in self.account_names:
            if not account["core"] and core_only:
                continue
            summoner_data = await self.riot_helper.get_summoner_by_account_tag(
                account["name"], account["tag"]
            )
            if summoner_data is not None:
                summoner_objects.append(summoner_data)

        summoner_objects = [obj for obj in summoner_objects]
        await self.db_helper.update_summoners(summoner_objects)


async def main():
    task = FillSummonersTask()
    await task.fill_summoners()


if __name__ == "__main__":
    asyncio.run(main())
