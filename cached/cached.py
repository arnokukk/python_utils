class Cached:
    _public: tuple[str, ...] = ()
    _cached: tuple[str, ...] = ()
    __slots__ = _public + _cached

    def __setattr__(self, key, value):
        if key in self._public:
            super().__setattr__(key, value)
        else:
            raise AttributeError(f'Attempt to set invalid attribute {key} in {self.__class__.__name__}')

    def _cache(self, name: str, value):
        if name in self._cached:
            print(f'Cashing {name}')
            super().__setattr__(name, value)
            return value
        else:
            raise AttributeError(f'Attempt to cache invalid attribute {name} in {self.__class__.__name__}')

    def invalidate_cache(self, *args):
        if args:
            for name in args:
                if name in self._cached and hasattr(self, name):
                    delattr(self, name)
        else:
            for name in self._cached:
                if hasattr(self, name):
                    delattr(self, name)


class Example(Cached):
    _public = ('value',)
    _cached = ('_v2', '_v3', '_vn')
    __slots__ = _public + _cached

    def __init__(self, value: int):
        self.value = value

    @property
    def v2(self) -> int:
        if hasattr(self, '_v2'):
            return self._v2
        return self._cache('_v2', self.value**2)

    @property
    def v3(self) -> int:
        if hasattr(self, '_v3'):
            return self._v3
        return self._cache('_v3', self.value**3)

    def vn(self, n=4):
        if hasattr(self, '_vn'):
            return self._vn
        return self._cache('_vn', self.value**n)


ham =  Example(0)
print(ham.value)
ham.value = 42
print(ham.value)
print(ham.v2, ham.v3)
print(ham.vn(-1))
ham.invalidate_cache('_vn')
print(ham.v2, ham.vn(0.5))
