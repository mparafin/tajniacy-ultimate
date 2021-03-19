import sys
import asyncio
import websockets

wss = set()

async def hello(websocket, path):
	print("CONNECTION WITH CLIENT ESTABLISHED")
	wss.add(websocket)
	await websocket.send("What's your name?")
	name = await websocket.recv()
	print(f"< {name}")

	greeting = f"Hello {name}!"

	await websocket.send(greeting)
	print(f"> {greeting}")
	print("Entering echo mode")
	async for message in websocket:
		await websocket.send(f"OK... {message}")

async def main():
	start_server = websockets.serve(hello, "localhost", 8888)
	thing = await start_server
	print("server up")

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
