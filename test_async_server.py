import asyncio
from argparse import ArgumentParser, Namespace
import math

from async_edu.stream import start_echo_server, tcp_echo_client


def parse_options() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('command', type=str, choices=('server', 'ping'))
    parser.add_argument('-H', '--host', type=str, default='localhost')
    parser.add_argument('-P', '--port', type=int, default=8888)
    parser.add_argument('-T', '--timeout', type=float, default=0)
    parser.add_argument('-N', '--count', type=int, default=0)
    return parser.parse_args()


async def server(_options: Namespace):
    await start_echo_server(_options.host, _options.port, timeout=None if _options.timeout == 0 else _options.timeout)


async def ping(_options: Namespace):
    count = math.inf if _options.count == 0 else _options.count
    n = 0
    while n < count:
        n += 1
        await tcp_echo_client(f'ping#{n}', host=_options.host, port=_options.port)
        await asyncio.sleep(_options.timeout)


if __name__ == '__main__':
    options = parse_options()
    if options.command == 'server':
        asyncio.run(server(options))
    elif options.command == 'ping':
        asyncio.run(ping(options))
