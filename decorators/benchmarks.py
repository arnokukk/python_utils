import time


def _time_str() -> str:
    return time.strftime('%X')


def benchmark(name: str):
    def _benchmark(func):
        def wrapper(*args, **kwargs):
            print(f'<== {name} started at {_time_str()}')
            start = time.time()
            rv = func(*args, **kwargs)
            print(f'==> {name} finished at {_time_str()}, duration: {time.time() - start:.1f} sec')
            return rv
        return wrapper
    return _benchmark


def async_benchmark(name: str):
    def _benchmark(async_func):
        async def wrapper(*args, **kwargs):
            print(f'<== {name} started at {_time_str()}')
            start = time.time()
            rv = await async_func(*args, **kwargs)
            print(f'==> {name} finished at {_time_str()}, duration: {time.time() - start:.1f} sec')
            return rv
        return wrapper
    return _benchmark


if __name__ == '__main__':
    @benchmark('SYNC FUNC')
    def foo():
        time.sleep(2)

    @async_benchmark('ASYNC FUNC')
    async def bar():
        await asyncio.sleep(2)

    import asyncio
    foo()
    asyncio.run(bar())
