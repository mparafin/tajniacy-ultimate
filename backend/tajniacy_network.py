import json
import asyncio

import tajniacy_definitions as td
import tajniacy_game as game

def player_list(player):
	result = {}
	result["type"] = "player_list"
	result["red"] = list()
	result["blue"] = list()
	result["spec"] = list()
	for p in td.PLAYERS:
		if p.nick == "" or p.nick == player.nick:
			continue
		{
			td.Team.RED: lambda p: result["red"].append({"nick":p.nick, "capt":p.capt}),
			td.Team.BLUE: lambda p: result["blue"].append({"nick":p.nick, "capt":p.capt}),
			td.Team.SPEC: lambda p: result["spec"].append({"nick":p.nick, "capt":p.capt}),
		}[p.team](p)
	result["player"] = {"nick":player.nick, "team":player.team.name, "capt":player.capt}
	if player.capt:
		result["secret"] = td.SECRET
	return json.dumps(result)

async def broadcast_player_list():
	await asyncio.gather(*[p.socket.send(player_list(p)) for p in td.PLAYERS])

async def broadcast(message):
	await asyncio.gather(*[p.socket.send(message) for p in td.PLAYERS])

async def name_handler(message, player):
	game.change_name(player, message["nick"])
	await broadcast_player_list()

async def click_handler(message, player):
	x, y = list(map(int, message["id"].split(" ")))
	change_turn = game.click(player, x, y)
	if change_turn:
		await broadcast(json.dumps({"type":"turn", "team":td.TURN.name}))
		await broadcast(json.dumps({"type":"entry", "entry":""}))
	await broadcast(json.dumps({"type":"uncovered", "uncovered":td.UNCOVERED}))
	
async def teamchange_handler(message, player):
	game.change_team(player, message["team"])
	await broadcast_player_list()

async def capt_handler(message, player):
	game.make_captain(player, message["team"])
	await broadcast_player_list()

async def entry_handler(message, player):
	game.accept_entry(player, message["entry"], int(message["entrynumber"]))
	await broadcast(json.dumps({"type":"entry", "entry":td.ENTRY, "number":td.CLICKS_REMAINING}))

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
	p = td.Player(websocket)
	td.PLAYERS.add(p)

	# send game state
	await websocket.send(player_list(p))
	await websocket.send(json.dumps({"type":"matrix", "matrix":td.MATRIX, "uncovered":td.UNCOVERED}))
	await websocket.send(json.dumps({"type":"turn", "team":td.TURN.name}))
	if td.CLICKS_REMAINING >= 0:
		await broadcast(json.dumps({"type":"entry", "entry":td.ENTRY, "number":td.CLICKS_REMAINING}))
	
	print("Entering echo mode")
	try:
		async for message in websocket:
			mes = json.loads(message)
			await message_handler(mes, p)			
			await websocket.send(json.dumps({"type":"echo", "data":mes}))
	finally:
		print("CLIENT DISCONNECTED")
		td.PLAYERS.remove(p)
		await broadcast_player_list()
