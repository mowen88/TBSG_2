import pygame

FPS = 30
TILESIZE = 32
RES = WIDTH, HEIGHT = pygame.math.Vector2(640, 360)#(360, 202.5)#(480, 270)#(640, 360)#(960, 540) or... (512, 288)
HALF_WIDTH, HALF_HEIGHT = RES/2

FONT = '../fonts/Pokemon Classic.ttf'

# data that is dynamic and changes throughout play
TERRAIN_DATA = {
				'Nothing': 0,
				'City': 1, 
				'Bridge': 2,
				'Grass': 3,
				'Wood': 4,
				'Water': 5,
				'Mountain': 6,
				'Road': 7,
				'City': 8
				}

# key events
ACTIONS = {'escape': False, 'space': False, 'up': False, 'down': False, 'left': False,
			'right': False, 'return': False, 'backspace': False, 'left_click': False, 
			'right_click': False, 'scroll_up': False, 'scroll_down': False}

# game colours
BLACK = ((20, 14, 30))
GREY = ((91,83,145))
LIGHT_GREY = ((146, 143, 184))
WHITE = ((223, 234, 228)) 
BLUE = ((20, 68, 145))
LIGHT_BLUE = ((113, 181, 219))
RED = ((112, 21, 31))
ORANGE = ((227, 133, 36))
PINK = ((195, 67, 92))
GREEN = ((88, 179, 150))
LIGHT_GREEN = ((106, 226, 145))
PURPLE = ((66, 0, 78))
CYAN = ((0, 255, 255))
MAGENTA = ((153, 60, 139))
YELLOW = ((224, 225, 146))