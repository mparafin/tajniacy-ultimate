import json
import asyncio

from tajniacy_definitions import *

def player_list(player):
	result = {}
	result["type"] = "player_list"
	result["red"] = list()
	result["blue"] = list()
	result["spec"] = list()
	for p in PLAYERS:
		if p.nick == "" or p.nick == player.nick:
			continue
		{
			Team.RED: lambda p: result["red"].append(p.nick),
			Team.BLUE: lambda p: result["blue"].append(p.nick),
			Team.SPEC: lambda p: result["spec"].append(p.nick),
		}[p.team](p)
	result["player"] = {"nick":player.nick, "team":player.team.name}
	return json.dumps(result)

async def broadcast_player_list():
	await asyncio.gather(*[p.socket.send(player_list(p)) for p in PLAYERS])

async def broadcast(message):
	await asyncio.gather(*[p.socket.send(message) for p in PLAYERS])

async def name_handler(message, player):
	print("Changing player name from " + player.nick + " to " + message["nick"])
	player.nick = message["nick"]
	await broadcast_player_list()

async def click_handler(message, player):
	print("click_handler")
	if message["id"] == "0 0":
		await broadcast("woof!")

async def teamchange_handler(message, player):
	print("Changing team of player " + player.nick + " to " + message["team"])
	player.team = {'red': Team.RED, 'blue': Team.BLUE, 'spec': Team.SPEC}[message["team"]]
	await broadcast_player_list()

async def message_handler(message, player):
	await {
		'nick': name_handler,
		'click': click_handler,
		'teamchange': teamchange_handler,
	}[message["type"]](message, player)

async def client_handler(websocket, path):
	print("CONNECTION WITH CLIENT ESTABLISHED")
	p = Player(websocket)
	PLAYERS.add(p)
	await websocket.send(player_list(p))
	await websocket.send(json.dumps({"type":"matrix", "matrix":json.dumps(MATRIX)}))
	
	print("Entering echo mode")
	try:
		async for message in websocket:
			mes = json.loads(message)
			await message_handler(mes, p)			
			await websocket.send(json.dumps({"type":"misc", "data":json.dumps(mes)}))
	finally:
		print("CLIENT DISCONNECTED")
		PLAYERS.remove(p)
		await broadcast_player_list()