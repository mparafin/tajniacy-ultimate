import os
import random
import re
import tajniacy_definitions as td

def file_list():
	filenames = []
	for file in os.listdir(("./db")):
		filenames.append(os.path.splitext(file)[0])
	return filenames

def save_file(filename, file):
	path = "./db/"+filename
	if os.path.exists(path):
		return "Taki plik już istnieje! Zmień nazwę pliku."

	bullshit = re.search(td.WORD_REGEX, file)
	if bullshit:
		return "wtf is this shit"

	with open(path, "w", encoding="utf-8",) as f:
		file = file.splitlines(keepends=False)
		for line in file:
			if len(line) > 20: continue
			line.encode()
			f.write(line+"\n")
	print("Zapisano plik: {}".format(path))
	

def update_file_choice(files):
	td.FILE_CHOICE.clear()
	for file in files:
		td.FILE_CHOICE.append(file)

def update_wordprefs(whitelist, blacklist):
	for word in whitelist:
		if word and not re.search(td.WORD_REGEX, word):
			td.WHITELIST.add(word)
	for word in blacklist:
		if word and not re.search(td.WORD_REGEX, word):
			td.BLACKLIST.add(word)
	

def reset_matrix():
	# create a list of words from whitelist and files
	words = set(td.WHITELIST)
	filenames = td.FILE_CHOICE
	for file in filenames:
		path = "./db/"+file+".txt"
		with open(path, encoding="utf-8") as f:
			for w in f:
				w = w.strip("\n,; ")
				w = w.upper()
				words.add(w)
	for word in td.WHITELIST:
		words.remove(word)
	for word in td.BLACKLIST:
		words.remove(word)

	# make sure that the whitelist words make it onto the matrix
	wordlist = list(words)
	random.shuffle(wordlist)
	words = list(td.WHITELIST)
	words.extend(wordlist[:25])
	if len(words) < 25:
		return "Zbyt mało słów! Wybierz więcej zbiorów lub rozszerz listę słów obowiązkowych."
	# shuffle the words once more so that whitelist words don't end up only at the beginning
	words = words[:25]
	random.shuffle(words)
	
	# clear the matrix and fill it with words
	td.MATRIX.clear()
	td.ENTRY = ""
	for i in range(5):
		td.MATRIX.append(list())
		for j in range(5):
			td.MATRIX[i].append(words.pop(0))
	return None

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
		return "Najpierw wpisz swój nick!"
	print("Changing team of player " + player.nick + " to " + team)
	player.team = {'red': td.Team.RED, 'blue': td.Team.BLUE, 'spec': td.Team.SPEC}[team]
	player.capt = False
	return None

def make_captain(player, team):
	if player.nick == "":
		return "Najpierw wpisz swój nick!"
	tdteam = {'red': td.Team.RED, 'blue': td.Team.BLUE}[team]
	for p in td.PLAYERS:
		if p.capt and p.team == tdteam:
			return "Może być tylko jeden kapitan drużyny!"
	print("Making player " + player.nick + " a captain of team " + team)
	player.team = tdteam
	player.capt = True
	return None

def randomize_teams():
	if td.ENTRY or len(td.UNCOVERED):
		return "No co Ty robisz, gra się zaczęła już"
	
	red = random.choice([True, False])
	random.shuffle(td.PLAYERS)
	for player in td.PLAYERS:
		player.team = td.Team.RED if red else td.Team.BLUE
		player.capt = False
		red = not red
	print("Teams randomized")

def accept_entry(player, entry, number):
	if not player.capt or player.team != td.TURN:
		return "Nie tak szybko, cwaniaku."
	td.ENTRY = entry
	td.ENTRY_NUMBER = number
	td.CLICKS_REMAINING = number
	if number == 0:
		td.CLICKS_REMAINING = 999
	return None
