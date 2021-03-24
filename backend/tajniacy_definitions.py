import enum

class Team(enum.Enum):
	SPEC = 0
	RED = 1
	BLUE = 2

class Player:
	def __init__(self, websocket):
		self.socket = websocket
		self.nick = ""
		self.team = Team.SPEC
		self.capt = False

PLAYERS = set()