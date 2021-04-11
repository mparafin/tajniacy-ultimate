import enum

class Team(enum.Enum):
	SPEC = 0
	RED = 1
	BLUE = 2
	KILLER = 3

class Player:
	def __init__(self, websocket):
		self.socket = websocket
		self.nick = ""
		self.team = Team.SPEC
		self.capt = False

def init():

	# set of players connected to the server atm
	global PLAYERS
	PLAYERS = set()

	# word matrix (5x5 array of str)
	global MATRIX
	MATRIX  = []
	# affiliation matrix - which words are which team (5x5 array of Team)
	global SECRET
	SECRET = []
	# which words' affiliations are visible to everyone (list of {"id":id, "team":Team})
	global UNCOVERED
	UNCOVERED = dict()

	# switch to alternate the beginning team during secret generation
	global PREV_BEGINNER
	PREV_BEGINNER = False
	# whose turn is it
	global TURN
	TURN = Team.SPEC
	# current entry (word from captain)
	global ENTRY
	ENTRY = ""
	# current entry number (number from captain)
	global ENTRY_NUMBER
	ENTRY_NUMBER = -1
	# how many clicks remaining for the current team
	global CLICKS_REMAINING
	CLICKS_REMAINING = -1

	# which files to take words from
	global FILE_CHOICE
	FILE_CHOICE = []
