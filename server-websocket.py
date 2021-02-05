#! /usr/bin/env python3

import asyncio
import websockets

async def hello(websocket, path):
    while True:
        # content = await websocket.recv()
        # print(content)
        message = input('my message')
        await websocket.send(message)

start_server = websockets.serve(hello, "192.168.100.131", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

