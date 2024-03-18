import sys

from run import Run
from foo import *


def main_foo(x: int):
    y = 42
    print(x, y)
    raise ValueError("main_foo")


def main_bar():
    my_var = None
    raise AttributeError("main_bar")


def main_egg():
    assert False, "main_egg"


if __name__ == '__main__':
    if result := Run(func=main_foo).run(1):
        print(result.value)
    else:
        print(result.message)
        if 'AssertionError' in result.message:
            print("\t\t\tassertion - terminate")
    for f in (main_bar, main_egg, foo, bar, ham, egg):
        if result := Run(func=f).run():
            print(result.value)
        else:
            print(result.message)
            if 'AssertionError' in result.message:
                print("\t\t\tassertion - terminate")

    if r := Run().run():
        print(r.value)
        assert r.exception is None and r.message == ''
    else:
        assert False
