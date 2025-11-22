import asyncio
import time
from random import randint
import unittest

from decorators.benchmarks import async_benchmark
from ex_coros import random_wait


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


@async_benchmark('GATHER')
async def main_gather(count: int, max_delay: int = 2):
    results = await asyncio.gather(*tuple(random_wait(i, max_delay=max_delay) for i in range(count)))
    print('\t', results)
    return sum(results)


class TerminateTaskGroup(Exception):
    pass


async def terminate_task_group(delay: float):
    await asyncio.sleep(delay)
    raise TerminateTaskGroup


@async_benchmark('FORCE_TERMINATE')
async def main_tg_terminate(count: int, max_delay: int):
    try:
        async with asyncio.TaskGroup() as group:
            tasks = [group.create_task(random_wait(i, max_delay=max_delay)) for i in range(count)]
            tasks.append(group.create_task(terminate_task_group(max_delay / 2)))
    except* TerminateTaskGroup:
        print(f'\tgroup terminated at {time.strftime("%X")}')
    results = [task.result() for task in tasks[:-1] if not task.cancelled()]
    print(f'\tresults = {results}')
    return results


@async_benchmark('TIMEOUT')
async def main_timeout(count: int, max_delay: int):
    try:
        async with asyncio.timeout(max_delay / 2):
            tasks = [asyncio.create_task(random_wait(i, max_delay=max_delay)) for i in range(count)]
            for task in tasks:
                await task
    except* asyncio.TimeoutError:
        print(f'\ttimeout exceeded at {time.strftime("%X")}')
    return [t.result() for t in tasks if t.done() and not t.cancelled()]


class TestAsyncCoroutines(unittest.TestCase):
    MAX_DELAY = 4
    COUNT = 5
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

    def test_gather(self):
        start = time.time()
        delay = asyncio.run(main_gather(self.COUNT, max_delay=self.MAX_DELAY))
        duration = time.time() - start
        time.sleep(self.DELTA)
        self.assertLessEqual(duration, delay + self.DELTA)
        self.assertLessEqual(duration, self.MAX_DELAY + self.DELTA)

    def test_cancel_group(self):
        count = 10
        md = 9
        results = asyncio.run(main_tg_terminate(count, max_delay=md))
        self.assertLessEqual(max(results), md / 2)
        self.assertLessEqual(len(results), count)
        print(f'{len(results)} of {count} tasks done. Delay: sum={sum(results)}, max_done={max(results)}, max={md}')

    def test_timeout(self):
        asyncio.run(main_timeout(self.COUNT, max_delay=self.MAX_DELAY))

    def test_wait(self):
        @async_benchmark('WAIT')
        async def _test(count, max_delay):
            tasks = [asyncio.create_task(random_wait(i, max_delay=max_delay)) for i in range(count)]
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            done_results = [task.result() for task in done]
            print(f'\tfirst {len(done)} completed')
            await asyncio.sleep(1)
            _pending, _suspended = await asyncio.wait(pending, return_when=asyncio.ALL_COMPLETED)
            return done_results, [task.result() for task in _pending], len(_suspended)

        results_first, results_other, not_completed_count = asyncio.run(_test(self.COUNT, self.MAX_DELAY))
        print('\t', results_first, results_other, not_completed_count)
        self.assertGreater(len(results_first), 0, 'Some tasks must complete while 1st wait')
        self.assertEqual(not_completed_count, 0, 'no pending tasks expected')
        self.assertEqual(max(results_first), min(results_first), 'equal delays expected')
        if results_other:
            self.assertLess(max(results_first), min(results_other), 'first delays less than others expected')


if __name__ == '__main__':
    unittest.main(verbosity=2)
