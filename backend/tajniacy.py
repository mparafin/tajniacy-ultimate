import os
import asyncio
import websockets
import json
import enum
import random
import socket

import tajniacy_definitions as td
import tajniacy_game as game
import tajniacy_network as tn

	
async def main():
	td.init()
	game.reset_matrix()
	game.reset_secret()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	ip = s.getsockname()[0]
	start_server = websockets.serve(tn.client_handler, ip, 8888)
	# start_server = websockets.serve(tn.client_handler, '127.0.0.1', 8888)
	thing = await start_server
	s.close()
	print("server up on address " + ip)


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
