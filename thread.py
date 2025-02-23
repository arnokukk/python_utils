from typing import Any, Callable, Dict, Tuple, Iterable
from threading import Thread as BaseThread, active_count
import uuid
from unittest import main, TestCase
from sys import stderr
from time import sleep
from datetime import datetime


class Arguments:
    def __init__(self, *args, **kwargs):
        self.args: Tuple[Any] = args
        self.kwargs: Dict[str, Any] = kwargs


class Thread(BaseThread):
    def __init__(self, target: Callable, arg: Arguments):
        super().__init__(group=None, target=target, name=str(uuid.uuid4()), args=arg.args, kwargs=arg.kwargs)
        self._target = target
        self._value: Any = None
        self._arg = arg

    def run(self) -> None:
        self._value = self._target(*self._arg.args, **self._arg.kwargs)

    @property
    def value(self):
        return self._value


def run_threads(target: Callable, args: Iterable[Arguments]) -> tuple:
    threads = tuple(Thread(target=target, arg=a) for a in args)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return tuple(thread.value for thread in threads)


class TestArgument(TestCase):
    a = Arguments(1, 2, 3, x=1, y=1, z=1)

    def test(self):
        self.assertIsInstance(self.a.args, tuple)
        self.assertIsInstance(self.a.kwargs, dict)
        self.assertIn(1, self.a.args)
        self.assertIn('x', self.a.kwargs)
        self.assertEqual(self.a.args, (1, 2, 3))
        self.assertEqual(self.a.kwargs, {'x': 1, 'y': 1, 'z': 1})

    def test_f(self):
        def func(a, b, c, *, x, y, z):
            return a, b, c, x, y, z

        self.assertEqual(func(*self.a.args, **self.a.kwargs), (1, 2, 3, 1, 1, 1))


class TestThread(TestCase):
    @staticmethod
    def function(x, y=1):
        sleep(.5)
        return x + y

    @staticmethod
    def run_thread(thread: Thread):
        print(f'\tThread "{thread.name}" run', file=stderr)
        thread.run()
        return thread.value

    def test_thread(self):
        self.assertEqual(self.run_thread(Thread(self.function, Arguments(1))), 2)
        self.assertEqual(self.run_thread(Thread(self.function, Arguments(1, y=0))), 1)
        self.assertRaises(TypeError, self.run_thread, Thread(self.function, Arguments(1, y=0, z=2)))
        self.assertRaises(TypeError, self.run_thread, Thread(self.function, Arguments(1, 2, y=0)))
        self.assertEqual(self.run_thread(Thread(self.function, Arguments(x=1, y=0))), 1)

    def test_run(self):
        start = datetime.now()
        self.assertEqual(run_threads(self.function, (Arguments(i, y=i) for i in range(5))),
                         tuple(i*2 for i in range(5)))
        delta = datetime.now() - start
        self.assertLess(delta.total_seconds(), 0.7, str(delta.total_seconds()))


if __name__ == '__main__':
    main(verbosity=2)
