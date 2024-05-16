import asyncio

import socketio

socketio_client = socketio.AsyncClient()


@socketio_client.event
async def connect():
    print('I\'m connected')


@socketio_client.event
async def disconnect():
    print('I\'m disconnected')


async def main():
    await socketio_client.connect(url='http://localhost:8000', socketio_path='sockets')
    await socketio_client.disconnect()

asyncio.run(main())