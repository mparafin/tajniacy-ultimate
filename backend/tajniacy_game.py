import os
import random
import tajniacy_definitions as td

def file_list():
	filenames = []
	for file in os.listdir(("./db")):
		filenames.append(os.path.splitext(file)[0])
	return filenames

def update_file_list(files):
	td.FILE_LIST.clear()
	for file in files:
		td.FILE_LIST.append(file)
	print("flhandler:")
	print(td.FILE_LIST)

def reset_matrix():
	td.MATRIX.clear()
	td.ENTRY = ""

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
	td.UNCOVERED.clear()
	td.CLICKS_REMAINING = -1
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


def change_name(player, newnick):
    print("Changing player name from " + player.nick + " to " + newnick)
    player.nick = newnick
    if player.nick == "":
    	player.team = td.Team.SPEC
    	player.capt = False

def click(player, x, y):
	id = str(x) + " " + str(y)
	
	if (player.team != td.TURN or
			td.CLICKS_REMAINING < 0 or
			id in td.UNCOVERED or
			player.capt):
		return False

	td.UNCOVERED[id] = td.SECRET[x][y]
	print("Clicked on card " + id + " (\"" + td.MATRIX[x][y] + "\")")
	td.CLICKS_REMAINING -= 1
	if player.team.name != td.SECRET[x][y] or td.CLICKS_REMAINING < 0:
		td.CLICKS_REMAINING = -1
		td.ENTRY = ""
		td.TURN = td.Team.RED if td.TURN == td.Team.BLUE else td.Team.BLUE
		return True
	return False

def change_team(player, team):
	if player.nick == "":
		return
	print("Changing team of player " + player.nick + " to " + team)
	player.team = {'red': td.Team.RED, 'blue': td.Team.BLUE, 'spec': td.Team.SPEC}[team]
	player.capt = False

def make_captain(player, team):
	if player.nick == "":
		return
	print("Making player " + player.nick + " a captain of team " + team)
	player.team = {'red': td.Team.RED, 'blue': td.Team.BLUE}[team]
	player.capt = True

def accept_entry(player, entry, number):
	if not player.capt or player.team != td.TURN:
		return False
	td.ENTRY = entry
	td.CLICKS_REMAINING = number
	if number == 0:
		td.CLICKS_REMAINING = 999
	return True