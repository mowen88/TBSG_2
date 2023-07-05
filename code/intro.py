from state import State
from level import Level
from settings import *

class Intro(State):
	def __init__(self, game):
		State.__init__(self, game)

	def update(self, dt):
		if ACTIONS['return']: Level(self.game).enter_state()
		self.game.reset_keys()

	def draw(self, screen):
		screen.fill(GREY)

