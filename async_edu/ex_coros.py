import asyncio
import random
import time
import unittest


async def fixed_wait(_id: int, delay: float, *, start: bool = False, end: bool = True, fmt: str = '%X'):
    if start:
        print(f'wait #{_id} started ({delay}) at {time.strftime(fmt)}')
    await asyncio.sleep(delay)
    if end:
        print(f'wait #{_id} finished ({delay}) at {time.strftime(fmt)}')
    return delay


async def random_wait(_id: int, max_delay: float, *, start: bool = False, end: bool = True, fmt: str = '%X'):
    return await fixed_wait(_id, random.random() * max_delay, start=start, end=end, fmt=fmt)


class TestWait(unittest.TestCase):
    def test_fixed(self):
        asyncio.run(fixed_wait(0, 0.2))
        asyncio.run(fixed_wait(1, 0.2, start=True))
        asyncio.run(fixed_wait(2, 0.2, end=False))
        asyncio.run(fixed_wait(3, 0.2, start=True, end=False))
        asyncio.run(fixed_wait(4, 0.2, start=True, end=True, fmt="%M:%S"))
        time.sleep(0.2)

    def test_random(self):
        print(asyncio.run(random_wait(0, 2, start=True)))
        print(asyncio.run(random_wait(1, 1, start=True)))
        print(asyncio.run(random_wait(2, .5, start=True)))


if __name__ == '__main__':
    unittest.main(verbosity=2)
