import sys
import asyncio
import websockets
import json
import enum

from tajniacy_definitions import *
import tajniacy_network as tn


async def main():
	start_server = websockets.serve(tn.client_handler, "localhost", 8888)
	thing = await start_server
	print("server up")

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
