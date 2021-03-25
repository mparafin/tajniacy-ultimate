import os
import asyncio
import websockets
import json
import enum
import random
import socket

from tajniacy_definitions import *
import tajniacy_network as tn

def reset_matrix():
	MATRIX.clear()

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

def reset_secret():
	SECRET.clear()

	tokens = list()
	for _ in range(8):
		tokens.append(Team.RED)
		tokens.append(Team.BLUE)
	# who's first?
	t = Team.RED if PREV_BEGINNER else Team.BLUE
	tokens.append(t)
	TURN = t
	# neutrals
	for _ in range(7):
		tokens.append(Team.SPEC)
	# BUKA
	tokens.append(Team.KILLER)
	
	for i in range(5):
		SECRET.append(list())
		for j in range(5):
			SECRET[i].append(random.sample(tokens, 1)[0])
			tokens.remove(SECRET[i][j])
	
async def main():
	reset_matrix()
	reset_secret()
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	start_server = websockets.serve(tn.client_handler, s.getsockname()[0], 8888)
	# start_server = websockets.serve(tn.client_handler, '127.0.0.1', 8888)
	thing = await start_server
	s.close()
	print("server up")


asyncio.get_event_loop().run_until_complete(main())
asyncio.get_event_loop().run_forever()
