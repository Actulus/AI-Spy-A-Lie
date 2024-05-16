# client for the ai player
import asyncio
import socketio
import sys

socketio_client = socketio.AsyncClient()

@socketio_client.event
async def connect():
    print('AI connected')
    room = sys.argv[1]
    await socketio_client.emit('join', {'sid': f'ai_{room}'})

@socketio_client.event
async def disconnect():
    print('AI disconnected')

@socketio_client.event
async def join(data):
    print(f"Joined room: {data['sid']}")
    await socketio_client.emit('chat', {'sid': f'ai_{sys.argv[1]}', 'message': 'Hello! I am the AI.'})

@socketio_client.event
async def chat(data):
    print(f"Received message: {data['sid']}: {data['message']}")

async def main(room):
    await socketio_client.connect(f'http://localhost:8000/sockets?room={room}', socketio_path='sockets')
    await socketio_client.wait()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py <room>")
        sys.exit(1)
    
    room = sys.argv[1]
    asyncio.run(main(room))
