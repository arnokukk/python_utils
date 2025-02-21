from typing import Any, Dict, Type
from unittest import main, TestCase


class Singleton:
    __instances: Dict[Type, Any] = {}

    def __init__(self):
        assert False, 'Cannot instantiate Singleton'

    @classmethod
    def init(cls, T: Type, *args, **kwargs) -> Any:
        if T in cls.__instances:
            raise TypeError(f'Singleton of {T} type was already created')
        cls.__instances[T] = T(*args, **kwargs)
        return cls.__instances[T]

    @classmethod
    def get(cls, T: Type) -> Any:
        return cls.__instances[T]


class SingletonTest(TestCase):
    class Ham:
        pass

    def test(self):
        self.assertRaises(AssertionError, Singleton)
        self.assertRaises(TypeError, Singleton, 1, a=2)
        self.assertRaises(KeyError, Singleton.get, int)
        Singleton.init(type(None))
        self.assertIsNone(Singleton.get(type(None)))
        self.assertRaises(KeyError, Singleton.get, self.Ham)
        Singleton.init(self.Ham)
        self.assertIsInstance(Singleton.get(self.Ham), self.Ham)
        self.assertEqual(Singleton.init(int, 42), 42)
        self.assertEqual(Singleton.init(dict, a=1, b=2), {'a': 1, 'b': 2})
        self.assertRaises(TypeError, Singleton.init, int)


if __name__ == '__main__':
    main()
