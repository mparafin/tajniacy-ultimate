import json
import asyncio

import tajniacy_definitions as td
import tajniacy_game as game

def protocol(key):
	return {
	"matrix":json.dumps({
		"type":"matrix",
		"matrix":td.MATRIX,
		"uncovered":td.UNCOVERED
	}),
	"uncovered":json.dumps({
		"type":"uncovered",
		"uncovered":td.UNCOVERED
	}),
	"entry":json.dumps({
		"type":"entry",
		"entry":td.ENTRY,
		"number":td.ENTRY_NUMBER,
		"turn":td.TURN.name
	}),
	"secret":json.dumps({
		"type":"secret",
		"secret":td.SECRET
	}),
	"file_list":json.dumps({
		"type":"file_list",
		"files":game.file_list()
	}),
	"file_choice":json.dumps({
		"type":"file_choice",
		"files":td.FILE_CHOICE
	})
	}[key]

def player_list(player):
	result = {}
	result["type"] = "player_list"
	result["red"] = list()
	result["blue"] = list()
	result["spec"] = list()
	for p in td.PLAYERS:
		if p == player:
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

async def broadcast(message):
	await asyncio.gather(*[p.socket.send(message) for p in td.PLAYERS])

async def broadcast_player_list():
	await asyncio.gather(*[p.socket.send(player_list(p)) for p in td.PLAYERS])
	await broadcast(protocol("uncovered"))

async def name_handler(message, player):
	game.change_name(player, message["nick"])
	await broadcast_player_list()

async def click_handler(message, player):
	x, y = list(map(int, message["id"].split(" ")))
	change_turn = game.click(player, x, y)
	if change_turn:
		await broadcast(protocol("entry"))
	await broadcast(protocol("uncovered"))

async def pass_handler(message, player):
	if player.team != td.TURN or td.TURN == td.Team.SPEC:
		return
	td.TURN = td.Team.RED if td.TURN == td.Team.BLUE else td.Team.BLUE
	td.ENTRY = ""
	td.CLICKS_REMAINING = -1
	await broadcast(protocol("entry"))
	
async def teamchange_handler(message, player):
	game.change_team(player, message["team"])
	await broadcast_player_list()

async def capt_handler(message, player):
	game.make_captain(player, message["team"])
	await player.socket.send(protocol("secret"))
	await broadcast_player_list()

async def entry_handler(message, player):
	ok = game.accept_entry(player, message["entry"], int(message["entrynumber"]))
	if ok:
		await broadcast(protocol("entry"))

async def reset_game_handler(message, player):
	game.reset_matrix()
	game.reset_secret()
	print("Game reset")
	await broadcast(protocol("matrix"))
	await broadcast(protocol("entry"))
	for p in td.PLAYERS:
		if p.capt:
			await p.socket.send(protocol("secret"))


async def reset_secret_handler(message, player):
	game.reset_secret()
	print("Secret reset")
	await broadcast(protocol("uncovered"))
	for p in td.PLAYERS:
		if p.capt:
			await p.socket.send(protocol("secret"))

async def file_choice_handler(message, player):
	game.update_file_choice(message["files"])
	print("File choice updated to: ")
	print(td.FILE_CHOICE)
	await broadcast(protocol("file_choice"))
	

async def message_handler(message, player):
	await {
		'nick': name_handler,
		'click': click_handler,
		'pass': pass_handler,
		'teamchange': teamchange_handler,
		'capt': capt_handler,
		'entry': entry_handler,
		'resetgame': reset_game_handler,
		'resetsecret': reset_secret_handler,
		'file_choice': file_choice_handler,
	}[message["type"]](message, player)

async def client_handler(websocket, path):
	print("CONNECTION WITH CLIENT ESTABLISHED")
	p = td.Player(websocket)
	td.PLAYERS.add(p)

	# send game state
	# (the order of the first three is significant)
	await websocket.send(protocol("entry"))
	await websocket.send(player_list(p))
	await websocket.send(protocol("matrix"))
	await websocket.send(protocol("file_list"))
	await websocket.send(protocol("file_choice"))

	
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
