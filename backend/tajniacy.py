import os
import asyncio
import websockets
import json
import enum
import random
import socket

import tajniacy_definitions as td
import tajniacy_network as tn

def reset_matrix():
	td.MATRIX.clear()

	words = set()
	filenames = os.listdir("./db")
	for file in filenames:
		path = "./db/"+file
		with open(path, encoding="utf-8") as f:
			for w in f:
				w = w.strip("\n,; ")
				w = w.upper()
				words.add(w)
	words = list(words)
	
	for i in range(5):
		td.MATRIX.append(list())
		for j in range(5):
			td.MATRIX[i].append(random.sample(words, 1)[0])
			words.remove(td.MATRIX[i][j])

def reset_secret():
	td.SECRET.clear()
	td.PREV_BEGINNER = True if td.PREV_BEGINNER == False else False

	tokens = list()
	for _ in range(8):
		tokens.append(td.Team.RED.name)
		tokens.append(td.Team.BLUE.name)
	# who's first?
	t = td.Team.RED if td.PREV_BEGINNER else td.Team.BLUE
	tokens.append(t.name)
	td.TURN = t
	# neutrals
	for _ in range(7):
		tokens.append(td.Team.SPEC.name)
	# BUKA
	tokens.append(td.Team.KILLER.name)
	
	for i in range(5):
		td.SECRET.append(list())
		for j in range(5):
			td.SECRET[i].append(random.sample(tokens, 1)[0])
			tokens.remove(td.SECRET[i][j])
	
async def main():
	td.init()
	reset_matrix()
	reset_secret()
	
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
