import asyncio

from tasks.MatchTasks import MatchTasks
from tasks.SummonerTasks import SummonerTasks

match_tasks = MatchTasks()
summoner_tasks = SummonerTasks()


async def interval_update(iteration, interval_time):
    if iteration % 10 == 0:
        await summoner_tasks.update_summoner_data()
    await match_tasks.update_match_data(69, 0)

    await asyncio.sleep(interval_time)
    # next iteration
    iteration += 1
    await interval_update(iteration, interval_time)


if __name__ == "__main__":
    asyncio.run(interval_update(0, 60 * 60))
