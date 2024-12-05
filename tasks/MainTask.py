import asyncio

from tasks.GameDataTask import GameDataTask
from tasks.MatchTasks import MatchTasks
from tasks.SummonerTasks import SummonerTasks

match_tasks = MatchTasks()
summoner_tasks = SummonerTasks()
game_data_task = GameDataTask()


async def interval_update(iteration, interval_time):
    if iteration % 10 == 0:
        await summoner_tasks.update_summoner_data()
        await game_data_task.update_items()
        await game_data_task.update_champions()
    await match_tasks.update_match_data(69, 0)
    await asyncio.sleep(interval_time)

    # next iteration
    iteration += 1
    await interval_update(iteration, interval_time)


if __name__ == "__main__":
    asyncio.run(interval_update(0, 60 * 60))
