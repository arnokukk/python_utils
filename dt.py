from contextlib import contextmanager
import datetime as dt
import dateutil.tz as dtz
from typing import Dict


class Now:
    @staticmethod
    def local() -> dt.datetime:
        return dt.datetime.now().astimezone()

    @staticmethod
    def utc() -> dt.datetime:
        return dt.datetime.now(tz=dt.timezone.utc)

    @staticmethod
    def tz(name: str) -> dt.datetime:
        return dt.datetime.now(dtz.gettz(name))


class TZ:
    local: dt.tzinfo = Now.local().tzinfo
    utc: dt.tzinfo = Now.utc().tzinfo

    @staticmethod
    def by_name(name: str) -> dt.tzinfo:
        return dtz.gettz(name)


class Duration:
    """
    Usage:
    def heavy_function():
        duration = Duration.start()  # or just Duration()
        do_heavy_staff()
        Logger.info(f"heavy_function completed, duration = {duration.seconds} seconds")
    """
    def __init__(self, start: dt.datetime | None = None):
        self._start = dt.datetime.now() if start is None else start

    @property
    def delta(self) -> dt.timedelta:
        return dt.datetime.now() - self._start

    @property
    def seconds(self) -> float:
        return self.delta.total_seconds()

    @classmethod
    def start(cls):
        return cls()


class Timer:
    """
    Purpose:
        measure time spent on some heavy actions
    Usage:
    timer = Timer()
    with timer.measure('action 1'):
        do_action_1()
    with timer.measure('action 2'):
        do_action_2()
    with timer.measure('action 1'):  # if action 1 should perform more than once
        do_action_1()
    Logger.info(f"Action 1 duration {timer.seconds('action 1')} seconds")
    Logger.info(f"Action 2 duration {timer.seconds('action 2')} seconds")

    No special initialization needed.
    """
    class _T:
        def __init__(self, now: dt.datetime):
            self.start: dt.datetime = now
            self.duration: dt.timedelta = dt.timedelta()

    def __init__(self):
        self._timers: Dict[str, Timer._T] = {}

    @contextmanager
    def measure(self, name: str):
        try:
            self._start(name)
            yield self._timers[name]
        finally:
            self._stop(name)

    def _start(self, name: str) -> None:
        if name in self._timers:
            self._timers[name].start = Now.utc()
        else:
            self._timers[name] = Timer._T(Now.utc())

    def _stop(self, name: str) -> None:
        assert name in self._timers
        self._timers[name].duration += Now.utc() - self._timers[name].start

    def duration(self, name: str) -> dt.timedelta:
        assert name in self._timers
        return self._timers[name].duration

    def seconds(self, name: str) -> float:
        return self.duration(name).total_seconds()

    def __contains__(self, name: str) -> bool:
        return name in self._timers

    @property
    def names(self):
        return self._timers.keys()

    def to_string(self, sep: str = ', '):
        return sep.join([f'{n}: {self.seconds(n)} sec.' for n in self.names])


class Timeout:
    """
    Purpose:
        do not perform some action if previous one was performed too recently.
        Only class methods provided. Do not create aa instance.
    Usage:
    if condition_for_action(action_name) and Timeout.expired(action_name):
        perform_action(action_name)

    default timeout is 1 second.
    To change: Timeout.set_timeout(minutes=1, seconds=30)
    """
    _timer: Dict[str, dt.datetime] = {}
    _timeout: dt.timedelta = dt.timedelta(seconds=1)

    @classmethod
    def expired(cls, name: str) -> bool:
        now = Now.utc()
        if name not in cls._timer or now - cls._timer[name] > cls._timeout:
            cls._timer[name] = now
            return True
        return False

    @classmethod
    def set_timeout(cls, *, seconds: float = 0, minutes: float = 0):
        cls._timeout = dt.timedelta(minutes=minutes, seconds=seconds)

    @classmethod
    def reset(cls, name: str):
        cls._timer[name] = Now.utc()

    @classmethod
    def clear(cls):
        cls._timer.clear()

    @classmethod
    def contains(cls, name: str) -> bool:
        return name in cls._timer


def _test_timeout():
    from logging import getLogger
    from time import sleep
    d = Duration.start()
    assert Timeout.expired('test')
    assert Timeout.contains('test')
    assert not Timeout.contains('name')
    assert not Timeout.expired('test')
    assert Timeout.expired('name')
    sleep(1.1)
    assert Timeout.expired('test')
    Timeout.set_timeout(seconds=2)
    assert not Timeout.expired('name')
    sleep(1)
    assert Timeout.expired('name')
    Timeout.clear()
    assert Timeout.expired('test')
    assert Timeout.expired('name')
    getLogger().critical(f'TEST TIMEOUT: PASSED, duration = {d.seconds:.1f}')


def _test_timer():
    from random import random
    from time import sleep
    from logging import getLogger

    timer = Timer()
    d = Duration()
    with timer.measure('a'):
        sleep(random())
    with timer.measure('b'):
        sleep(random())
    with timer.measure('a'):
        sleep(random())
    assert 'a' in timer and 'b' in timer
    try:
        _ = timer.duration('c')
    except AssertionError:
        getLogger().critical(f'TEST TIMER: PASSED, duration: {d.seconds},'
                             f' measured: {timer.to_string()}')
        return
    assert False


if __name__ == '__main__':
    _test_timeout()
    _test_timer()
