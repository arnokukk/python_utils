import asyncio
import unittest

from decorators.benchmarks import async_benchmark


@async_benchmark('CLIENT')
async def tcp_echo_client(message: str, *, host: str, port: int):
    reader, writer = await asyncio.open_connection(host, port)
    writer.write(message.encode())
    await writer.drain()
    print(f'\tClient: {message!r} sent')
    data = await reader.read(100)
    print(f'\tClient: {data.decode()!r} received')
    print('\tClient: close connection')
    writer.close()
    await writer.wait_closed()


@async_benchmark('SERVER')
async def start_echo_server(host: str, port: int, *, timeout: float | None = None):
    async def _handle_echo(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        data = await reader.read(100)
        message = data.decode()
        address = writer.get_extra_info('peername')
        print(f'\tHandler: {message!r} from {address!r} received')

        print(f'\tHandler: {message!r} sent')
        writer.write(data)
        await writer.drain()

        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(_handle_echo, host, port)
    addresses = ', '.join(str(_socket.getsockname()) for _socket in server.sockets)
    print(f'\tServer: serving at {addresses}')
    try:
        async with asyncio.timeout(timeout):
            async with server:
                await server.serve_forever()
    except* TimeoutError:
        print('\tServer: timeout close')


class TestStream(unittest.TestCase):
    HOST = 'localhost'
    PORT = 8888

    def test_echo_client(self):
        async def _start_client(message):
            await asyncio.sleep(0.5)
            await tcp_echo_client(message, host=self.HOST, port=self.PORT)

        async def _start():
            server = asyncio.create_task(start_echo_server(self.HOST, self.PORT, timeout=3))
            await asyncio.sleep(0.5)
            client = asyncio.create_task(_start_client('client 0'))
            client1 = asyncio.create_task(_start_client('client 1'))
            await server
            await client
            await client1
            await asyncio.sleep(0.5)

        asyncio.run(_start())

    def test_echo_server(self):
        asyncio.run(start_echo_server(self.HOST, self.PORT, timeout=None))


if __name__ == '__main__':
    unittest.main(verbosity=2)
