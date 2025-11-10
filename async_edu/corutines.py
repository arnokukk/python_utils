import asyncio
import time
from random import randint
import unittest

from decorators.benchmarks import async_benchmark


async def random_wait(_id: int, max_delay: int = 4) -> int:
    delay = randint(1, max_delay)
    await asyncio.sleep(delay)
    print(f'random_wait #{_id} finished ({delay}), time={time.strftime("%X")}')
    return delay


@async_benchmark('TASK_LOOP')
async def main_tasks(count: int, *, max_delay: int = 4):
    tasks = [asyncio.create_task(random_wait(i, max_delay=max_delay)) for i in range(count)]
    total_delay = sum([await task for task in tasks])
    print(f'\tTL: total delay = {total_delay}')
    return total_delay


@async_benchmark('TASK_GROUP')
async def main_tg(count: int, *, max_delay: int = 5) -> int:
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(random_wait(i, max_delay=max_delay)) for i in range(count)]
    total_delay = sum(t.result() for t in tasks)
    print(f'\tTG: total delay = {total_delay}')
    return total_delay


@async_benchmark('CALLBACK')
async def main_callback(max_delay: int = 5) -> int:
    def _callback(t: asyncio.Task):
        print(f'\t\tcallback from {t.get_name()}')
    task = asyncio.create_task(random_wait(0, max_delay=max_delay))
    print(f'\ttask {task.get_name()} created')
    task.add_done_callback(_callback)
    print(f'\tcallback added to task {task.get_name()}')
    delay = await task
    print(f'\ttask {task.get_name()} done')
    return delay


class TestAsyncCoroutines(unittest.TestCase):
    MAX_DELAY = 3
    COUNT = 3
    DELTA = 0.1

    def test_task_list(self):
        start = time.time()
        delay = asyncio.run(main_tasks(self.COUNT, max_delay=self.MAX_DELAY))
        duration = time.time() - start
        time.sleep(self.DELTA)
        self.assertLessEqual(duration, delay + self.DELTA, f'{duration} > {delay}')
        self.assertLessEqual(duration, self.MAX_DELAY + self.DELTA)

    def test_task_group(self):
        start = time.time()
        delay = asyncio.run(main_tg(self.COUNT, max_delay=self.MAX_DELAY))
        duration = time.time() - start
        time.sleep(self.DELTA)
        self.assertLessEqual(duration, delay + self.DELTA, f'{duration} > {delay}')
        self.assertLessEqual(duration, self.MAX_DELAY + self.DELTA)

    def test_callback(self):
        asyncio.run(main_callback(max_delay=self.MAX_DELAY))


if __name__ == '__main__':
    unittest.main(verbosity=2)
