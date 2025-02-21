from typing import Any, Dict, List, Self
import unittest
import json

import yaml
from pathlib import Path


class DataStruct:
    def __init__(self, data: Dict[str, Any]):
        self.__names: List[str] = [k for k in data.keys()]
        for k, v in data.items():
            if isinstance(v, dict):
                self.__setattr__(k, DataStruct(v))
            else:
                self.__setattr__(k, v)

    def __contains__(self, key: str):
        return key in self.__names

    def __getitem__(self, key: str):
        return self.__getattribute__(key)

    def __str__(self):
        return '<' + ', '.join(f'{key}: {self[key]}' for key in self.__names) + '>'

    def __eq__(self, other: Self):
        return self.dict() == other.dict()

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(self.__names)

    def dict(self) -> Dict[str, Any]:
        data = {}
        for key in self.__names:
            data[key] = self[key].dict() if isinstance(self[key], DataStruct) else self[key]
        return data

    def dump_json(self, path: Path):
        with open(path, 'w') as file:
            json.dump(self.dict(), file)

    @classmethod
    def read_json(cls, path: Path) -> Self:
        with open(path) as file:
            return cls(json.load(file))

    def dump_yaml(self, path: Path):
        with open(path, 'w') as file:
            yaml.dump(self.dict(), file)

    @classmethod
    def read_yaml(cls, path: Path) -> Self:
        with open(path) as file:
            return cls(yaml.load(file, yaml.Loader))

    def __hash__(self):
        return hash(self.dict())


class DataStructTest(unittest.TestCase):
    _d = {'a': 1, 'b': {'a': 2, 'b': [1, 2, 3]}}
    ds = DataStruct(_d)

    def test_init(self):
        self.assertEqual(self.ds.names, ('a', 'b'))
        self.assertEqual(self.ds['b'].names, ('a', 'b'))

    def test_contains(self):
        self.assertTrue('a' in self.ds)
        self.assertFalse('c' in self.ds)
        self.assertTrue('a' in self.ds['b'])

    def test_attribute(self):
        self.assertEqual(self.ds.a, 1)
        self.assertRaises(AttributeError, lambda x: x.c, self.ds)
        self.assertRaises(AttributeError, lambda x, y: x[y], self.ds, 'c')

    def test_str(self):
        self.assertEqual(str(self.ds), "<a: 1, b: <a: 2, b: [1, 2, 3]>>")

    def test_dict(self):
        self.assertEqual(self.ds.dict(), self._d)

    def test_json(self):
        path = Path('test.json')
        self.ds.dump_json(path)
        ds = DataStruct.read_json(path)
        self.assertEqual(ds, self.ds)
        path.unlink()

    def test_yaml(self):
        path = Path('test.yaml')
        self.ds.dump_yaml(path)
        ds = DataStruct.read_yaml(path)
        self.assertEqual(ds, self.ds)
        path.unlink()

    def test_eq(self):
        self.assertTrue(DataStruct({}) == DataStruct({}))
        self.assertFalse(DataStruct({}) is DataStruct({}))
        self.assertTrue(DataStruct({}) != DataStruct({'a': 1}))
        self.assertTrue(DataStruct({'a': 1}) == DataStruct({'a': 1}))
        self.assertTrue(DataStruct({'a': 2}) != DataStruct({'a': 1}))


if __name__ == '__main__':
    unittest.main()
