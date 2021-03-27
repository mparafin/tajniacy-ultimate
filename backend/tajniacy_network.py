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
			Team.RED: lambda p: result["red"].append({"nick":p.nick, "capt":p.capt}),
			Team.BLUE: lambda p: result["blue"].append({"nick":p.nick, "capt":p.capt}),
			Team.SPEC: lambda p: result["spec"].append({"nick":p.nick, "capt":p.capt}),
		}[p.team](p)
	result["player"] = {"nick":player.nick, "team":player.team.name, "capt":player.capt}
	if player.capt:
		result["secret"] = SECRET
	return json.dumps(result)

async def broadcast_player_list():
	await asyncio.gather(*[p.socket.send(player_list(p)) for p in PLAYERS])

async def broadcast(message):
	await asyncio.gather(*[p.socket.send(message) for p in PLAYERS])

async def name_handler(message, player):
	print("Changing player name from " + player.nick + " to " + message["nick"])
	player.nick = message["nick"]
	if player.nick == "":
		player.team = Team.SPEC
		player.capt = False
	await broadcast_player_list()

async def click_handler(message, player):
	global CLICKS_REMAINING
	if player.team == Team.SPEC:
		return
	if player.capt:
		return
	if CLICKS_REMAINING < 0:
		return
	CLICKS_REMAINING -= 1

	x, y = message["id"].split(" ")
	UNCOVERED[message["id"]] = SECRET[int(x)][int(y)]
	print("Clicked on card " + message["id"] + " (\"" + MATRIX[int(x)][int(y)] + "\")")
	await broadcast(json.dumps({"type":"uncovered", "uncovered":UNCOVERED}))
	
async def teamchange_handler(message, player):
	if player.nick == "":
		return
	print("Changing team of player " + player.nick + " to " + message["team"])
	player.team = {'red': Team.RED, 'blue': Team.BLUE, 'spec': Team.SPEC}[message["team"]]
	player.capt = False
	await broadcast_player_list()

async def capt_handler(message, player):
	if player.nick == "":
		return
	print("Making player " + player.nick + " a captain of team " + message["team"])
	player.team = {'red': Team.RED, 'blue': Team.BLUE}[message["team"]]
	player.capt = True
	await broadcast_player_list()

async def entry_handler(message, player):
	global CLICKS_REMAINING
	CLICKS_REMAINING = int(message["entrynumber"])
	await broadcast(json.dumps({"type":"entry", "entry":message["entry"], "number":message["entrynumber"]}))

async def message_handler(message, player):
	await {
		'nick': name_handler,
		'click': click_handler,
		'teamchange': teamchange_handler,
		'capt': capt_handler,
		'entry': entry_handler,
	}[message["type"]](message, player)

async def client_handler(websocket, path):
	print("CONNECTION WITH CLIENT ESTABLISHED")
	p = Player(websocket)
	PLAYERS.add(p)
	await websocket.send(player_list(p))
	await websocket.send(json.dumps({"type":"matrix", "matrix":MATRIX, "uncovered":UNCOVERED}))
	
	print("Entering echo mode")
	try:
		async for message in websocket:
			mes = json.loads(message)
			await message_handler(mes, p)			
			await websocket.send(json.dumps({"type":"echo", "data":mes}))
	finally:
		print("CLIENT DISCONNECTED")
		PLAYERS.remove(p)
		await broadcast_player_list()
