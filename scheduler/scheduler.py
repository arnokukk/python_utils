from datetime import datetime
from time import sleep
from typing import Tuple, Callable


_all_hours: Tuple[int, ...] = tuple(h for h in range(24))


def _hour() -> int:
    return datetime.now().astimezone().hour


class Scheduler:
    def __init__(self, hours: Tuple[int, ...] = _all_hours, timeout: float = 60):
        self._hours = hours
        self._timeout = timeout

    def run_once(self, function: Callable, *args, **kwargs):
        if _hour() in self._hours:
            return function(*args, **kwargs)
        sleep(self._timeout)

    def run(self, function: Callable, *args, **kwargs):
        while True:
            print(self.run_once(function, *args, **kwargs))


if __name__ == '__main__':
    pass
