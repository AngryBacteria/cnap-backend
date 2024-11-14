import asyncio

from helpers.DBHelper import DBHelper
from helpers.RiotHelper import RiotHelper


async def huh():
    rh = RiotHelper()
    dbh = DBHelper()
    champ = await rh.get_lol_champion("1")
    print(champ)


asyncio.run(huh())
