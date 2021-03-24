import os
import asyncio
import websockets
import json
import enum
import random

from tajniacy_definitions import *
import tajniacy_network as tn

def game_init():
	words = set()
	filenames = os.listdir("./db")
	for file in filenames:
		path = "./db/"+file
		with open(path) as f:
			for w in f:
				w = w.strip("\n,; ")
				w = w.upper()
				words.add(w)
	
	for i in range(5):
		MATRIX.append(list())
		for j in range(5):
			MATRIX[i].append(random.sample(words, 1)[0])
			words.remove(MATRIX[i][j])
	
async def main():
	start_server = websockets.serve(tn.client_handler, "localhost", 8888)
	thing = await start_server
	print("server up")
	game_init()
	await tn.broadcast(json.dumps(MATRIX))

asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
