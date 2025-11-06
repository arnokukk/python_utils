import asyncio
import time
from random import randint

from decorators.benchmarks import async_benchmark


async def random_wait(_id: int, max_delay: int = 4):
    delay = randint(1, max_delay)
    await asyncio.sleep(delay)
    print(f'random_wait #{_id} finished ({delay}), time={time.strftime("%X")}')


@async_benchmark('TASK_LOOP')
async def main_tasks(count: int, *, max_delay: int = 4):
    tasks = []
    for i in range(count):
        tasks.append(asyncio.create_task(random_wait(i, max_delay=max_delay)))
    for task in tasks:
        await task


@async_benchmark('TASK_GROUP')
async def main_tg(count: int, *, max_delay: int = 5):
    async with asyncio.TaskGroup() as tg:
        for i in range(count):
            tg.create_task(random_wait(i, max_delay=max_delay))


if __name__ == '__main__':
    asyncio.run(main_tasks(5, max_delay=7))
    asyncio.run(main_tg(7, max_delay=5))
