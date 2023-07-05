import pygame
from settings import *

class Camera(pygame.sprite.Group):
	def __init__(self, game, level):
		super().__init__()

		self.game = game
		self.level = level
		self.offset = pygame.math.Vector2()
		self.direction = pygame.math.Vector2()
		self.scroll_speed = 10

	def key_control(self):
		keys = pygame.key.get_pressed()
		if keys[pygame.K_LEFT]: self.direction.x = -1
		elif keys[pygame.K_RIGHT]: self.direction.x = +1
		else: self.direction.x = 0
		if keys[pygame.K_UP]: self.direction.y = -1
		elif keys[pygame.K_DOWN]: self.direction.y = +1
		else: self.direction.y = 0

	def dt_update(self, dt):
		if self.direction.magnitude() != 0: self.direction = self.direction.normalize() * self.scroll_speed * dt
		self.offset += self.direction

	def offset_draw(self, target):
		
		self.key_control()
		#self.offset += (target - RES/2 - self.offset)

		# limit offset to stop at edges
		if self.offset.x <= 0: self.offset.x = 0
		elif self.offset.x >= self.level.level_size[0] - WIDTH: self.offset.x = self.level.level_size[0] - WIDTH
		if self.offset.y <= 0: self.offset.y = 0
		elif self.offset.y >= self.level.level_size[1] - HEIGHT: self.offset.y = self.level.level_size[1] - HEIGHT
	
		for sprite in sorted(self.level.drawn_sprites, key = lambda sprite: sprite.rect.centery):
			offset = sprite.rect.topleft - self.offset
			self.game.screen.blit(sprite.image, offset)