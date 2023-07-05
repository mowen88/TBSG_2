import pygame
from settings import *

class Tile(pygame.sprite.Sprite):
	def __init__(self, game, level, groups, pos, surf = pygame.Surface((TILESIZE, TILESIZE))):
		super().__init__(groups)

		self.level = level
		self.image = surf
		self.rect = self.image.get_rect(topleft = pos)

class AnimatedTile(pygame.sprite.Sprite):
	def __init__(self, game, level, groups, pos, path):
		super().__init__(groups)

		self.game = game
		self.level = level
		self.frames = self.game.get_folder_images(path)
		self.frame_index = 0
		self.image = self.frames[self.frame_index]
		self.rect = self.image.get_rect(topleft = pos)

	def animate(self, animation_speed):
		self.frame_index += animation_speed
		self.frame_index = self.frame_index % len(self.frames)	
		self.image = self.frames[int(self.frame_index)]

	def update(self, dt):
		self.animate(0.2 * dt)


class Unit(pygame.sprite.Sprite):
	def __init__(self, game, level, groups, pos, surf, colour, name):
		super().__init__(groups)

		self.level = level
		self.image = surf
		self.name = name
		self.type = self.get_unit_type()
		self.mp_dict = {'Infantry': 4, 'Tank':7, 'Artillery':9, 'HQ':0}
		self.move_points = self.mp_dict[name]
		self.penalty = self.get_terrain_penalty(4)

		self.offset = self.level.drawn_sprites.offset
		self.rect = self.image.get_rect(topleft = pos)
		self.target_pos = pygame.math.Vector2()

		self.active = False

	def get_unit_type(self):
		types = {'Infantry': 'Foot', 'Tank':'Tracks', 'Artillery':'Wheels', 'HQ':'Static'}
		return types[self.name]

	def get_terrain_penalty(self, node):
		move_penalties = {
						'Nothing':{'Foot': 1, 'Tracks': 1, 'Wheels': 1, 'Static': 1},
						'City': {'Foot': 1, 'Tracks': 1, 'Wheels': 1, 'Static': 1},
						'Bridge': {'Foot': 1, 'Tracks': 2, 'Wheels': 4, 'Static': 1},
						'Grass': {'Foot': 1, 'Tracks': 1, 'Wheels': 2, 'Static': 1},
						'Wood': {'Foot': 2, 'Tracks': 3, 'Wheels': 3, 'Static': 1},
						'Water': {'Foot': 2, 'Tracks': 20, 'Wheels': 20, 'Static': 1},
						'Mountain': {'Foot': 2, 'Tracks': 20, 'Wheels': 20, 'Static': 1},
						'Road': {'Foot': 1, 'Tracks': 1, 'Wheels': 1, 'Static': 1},
						'City': {'Foot': 1, 'Tracks': 1, 'Wheels': 1, 'Static': 1}
						}
		for key, value in TERRAIN_DATA.items():
			if node == value:
				return move_penalties[key][self.type]

	


			

			

		