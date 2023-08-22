import asyncio
import os
import socket
from . import log

logger = log.get_logger(__name__)

async def run_exit_server(quit_app):
    sockfile = f'/tmp/{os.getpid()}.sock'
    # Make sure the socket does not already exist
    try:
        os.unlink(sockfile)
    except OSError:
        if os.path.exists(sockfile):
            raise
    server = None

    async def handle_exit(reader, writer):
        addr = writer.get_extra_info('sockname')
        print('connection from', addr)
        data = await reader.read(100)
        message = data.decode()
        print(f"received {message!r} from {addr!r}")
        if message == "":
            print("Socket closed from client")
            return
        writer.write(b'done')
        await writer.drain()

        quit_app()

        writer.close()

        server.close()
        await server.wait_closed()

    server = await asyncio.start_unix_server(handle_exit, sockfile)

    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()


def quit_app(pid):
    # Define the socket file
    sockfile = f'/tmp/{pid}.sock'
    if not os.path.exists(sockfile):
        logger.info('socket file not found: %s', sockfile)
        return
    # Create a Unix socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    try:
        sock.connect(sockfile)
        # Send data
        message = b'quit'
        print('sending {!r}'.format(message))
        sock.sendall(message)
        data = sock.recv(100)
        print('received {!r}'.format(data))
    except ConnectionRefusedError:
        logger.info('socket connection refused: %s', sockfile)
    finally:
        print('closing socket')
        sock.close()