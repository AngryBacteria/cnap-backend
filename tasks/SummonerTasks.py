import asyncio
import os

from dotenv import load_dotenv

from helpers.DBHelper import DBHelper, SummonerFilter, CollectionName
from helpers.Logger import app_logger
from helpers.RiotHelper import RiotHelper


class SummonerTasks:
    def __init__(self) -> None:
        self.db_helper = DBHelper.get_instance()
        self.riot_helper = RiotHelper.get_instance()
        self.accounts_string = "AngryBacteria_cnap,BriBri_0699,VerniHD_EUW,Baywack_CnAP,3 6 6 1_#EUW,SignisAura_CnAP,Alraune22_CnAP,Aw3s0m3mag1c_EUW,Gnerfedurf_BCH,Gnoblin_BCH,VredVampire_2503,D3M0NK1LL3RG0D_EUW,GLOMVE_EUW,hide on büschli_EUW,IBlueSnow_EUW,Nayan Stocker_EUW,Norina Michel_EUW,pentaskill_CnAP,Pollux_2910,Polylinux_EUW,Prequ_EUW,Sausage Revolver_EUW,swiss egirI_EUW,TCT Tawan_EUW,The 26th Bam_EUW,Theera3rd_EUW,Zinsstro_EUW,WhatThePlay_CnAP,pentaskill_CnAP,Árexo_CNAP,Naaji_EUW,6c51o_6C51"

    # Fil the summoners collection with the accounts provided in the environment variable ACCOUNTS_STRING
    async def fill_summoners(self) -> None:
        load_dotenv()
        accounts_string = os.getenv("ACCOUNTS_STRING")
        if accounts_string is None:
            raise Exception("No ACCOUNTS_STRING string provided, aborting...")

        accounts_string_seperated = accounts_string.split(",")
        summoner_objects = []
        for account in accounts_string_seperated:
            if len(account.strip().split("_")) > 1:
                name = account.strip().split("_")[0]
                tag = account.strip().split("_")[1]
                summoner_data = await self.riot_helper.get_summoner_by_account_tag(
                    name, tag
                )
                if summoner_data is not None:
                    summoner_objects.append(summoner_data)
            else:
                app_logger.error(f"Account {account} is not valid, skipping it...")

        await self.db_helper.generic_upsert(
            summoner_objects,
            "puuid",
            CollectionName.SUMMONER,
            data_name="Summoner",
            validator=None,
        )

    # Add a single summoner to the summoners collection
    async def add_summoner(self, name: str, tag: str, puuid: str | None = None) -> None:
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
                CollectionName.SUMMONER,
                data_name="Summoner",
                validator=None,
            )
        else:
            raise ValueError("Summoner not found")

    # Update the summoner data of all summoners in the summoners collection
    async def update_summoner_data(self) -> None:
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
                CollectionName.SUMMONER,
                "Summoner",
                None,
            )


async def main() -> None:
    summoner_tasks = SummonerTasks()
    await summoner_tasks.fill_summoners()


if __name__ == "__main__":
    asyncio.run(main())
