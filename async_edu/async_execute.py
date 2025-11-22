import asyncio
import random
import unittest
from typing import Callable, Tuple, Dict, Any
import time

from decorators.benchmarks import benchmark


async def async_execute(sync_func: Callable,
                        _arguments: Tuple[Tuple[Tuple[Any, ...], Dict[str, Any]], ...]) -> Tuple[Any, ...]:
    results = await asyncio.gather(
        *tuple(asyncio.to_thread(sync_func, *args, **kwargs) for args, kwargs in _arguments))
    return results


class TestAsyncExecute(unittest.TestCase):
    MAX_DELAY = 3
    COUNT = 10

    @staticmethod
    @benchmark('ASYNC_EXECUTE')
    def _async_execute_wrapper(_sync_func, _args):
        results = asyncio.run(async_execute(_sync_func, _args))
        print(f'\tResults: {results} ({len(results)} tasks)')
        return sum(results)

    @staticmethod
    def _test_func(_delay: int, _id: int, _name: str = 'task'):
        delay = random.randint(0, _delay)
        time.sleep(delay)
        print(f'\t\ttask#{_id} {_name} finished at {time.strftime("%X")} (delay={delay})')
        return delay

    def test_async_execute(self):
        arguments = (((self.MAX_DELAY, i), {'_name': f'TASK{i}'}) for i in range(self.COUNT))
        result = self._async_execute_wrapper(self._test_func, arguments)
        self.assertLessEqual(self.MAX_DELAY, result * 1.01)
        print(f'The total delay is {result}')


if __name__ == '__main__':
    unittest.main()
