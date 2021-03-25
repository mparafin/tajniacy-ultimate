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

# set of players connected to the server atm
PLAYERS = set()

# word matrix (5x5 array of str)
MATRIX = []
# affiliation matrix - which words are which team (5x5 array of Team)
SECRET = []
# which words' affiliations are visible to everyone (list of {"id":id, "team":Team})
UNCOVERED = dict()

# switch to alternate the beginning team during secret generation
PREV_BEGINNER = False
# whose turn is it
TURN = Team.SPEC
# how many clicks remaining for the current team
CLICKS_REMAINING = 0
