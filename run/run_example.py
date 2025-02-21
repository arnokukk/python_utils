from logging import getLogger
from unittest import main, TestCase

from run import BaseRun, RunStatus


class RunExample(BaseRun):
    def __init__(self, value: int):
        super().__init__()
        self.value = value

    def _run(self, x: int, *, y: int = 0) -> RunStatus:
        self.calculate(x, y)
        return self.status

    def calculate(self, x, y):
        ret, value = _inner(x, y)
        self.value += value
        if not ret:
            self.status = RunStatus(False, f'Incorrect _inner({x}, {y}) result')


def _inner(x: int, y: int) -> (bool, int):
    if x % 2 == 0:
        return False, 0
    if y % 3 == 0:
        raise ValueError(f'y value = {y}')
    return True, x * y


class RunExampleTest(TestCase):
    _value = 42

    def _run(self, x: int, y: int) -> RunExample:
        r = RunExample(self._value).run(x, y=y)
        if not r.status:
            getLogger().error(f'*ERROR: {r.status} {r.status.message} ({r.value}) ERROR*')
        return r

    def test(self):
        res = RunExample(self._value)
        self.assertTrue(res.status)
        self.assertEqual(res.value, self._value)
        res = self._run(1, 1)
        self.assertTrue(res.status)
        self.assertEqual(res.value, self._value+1)
        res = self._run(2, 1)
        self.assertFalse(res.status)
        self.assertIs(res.status.exception_type, type(None))
        res = self._run(1, 3)
        self.assertFalse(res.status)
        self.assertIs(res.status.exception_type, ValueError)


if __name__ == '__main__':
    main(verbosity=1)
