import pygame, csv
from settings import *
from pathfinding.core.grid import Grid
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.finder.a_star import AStarFinder

class Pathfinder:
    def __init__(self, game, level, matrix):

        self.game = game
        self.level = level
        self.matrix = matrix
        self.grid = Grid(matrix = self.matrix)
        self.select_box = pygame.image.load('../assets/select_box.png').convert_alpha()
        self.select_box_rect = self.select_box.get_rect()
        self.move_tile_list = []

        # print(self.get_optimum_path_nodes((0,0),(20,11)))
        # for node in self.matrix:
        #     print(node)

    def draw_cell_rect(self, screen):
        mouse = pygame.mouse.get_pos()
        row = int(mouse[1] + self.level.drawn_sprites.offset.y)//TILESIZE
        col = int(mouse[0] + self.level.drawn_sprites.offset.x)//TILESIZE
        current_cell_value = self.matrix[row][col]
        if current_cell_value == 3:
            self.select_box_rect = pygame.Rect((col * TILESIZE, row * TILESIZE) - self.level.drawn_sprites.offset, (TILESIZE, TILESIZE))
            screen.blit(self.select_box, self.select_box_rect)

    def highlight_unit(self, screen):
        for unit in self.level.red_sprites:
            x, y = unit.rect.x + 36 - self.level.drawn_sprites.offset.x, unit.rect.y - 40 - self.level.drawn_sprites.offset.y
            w, h = 62, 40
            if unit.rect.collidepoint(pygame.mouse.get_pos() + self.level.drawn_sprites.offset):
                pygame.draw.rect(screen, MAGENTA, (x, y, w, h), border_radius=3)
                self.game.render_text(unit.name, WHITE, self.game.small_font, (x + w/2, y + h/2))
                
                if ACTIONS['left_click']:
                    current_cell_value = self.matrix[unit.rect.x//TILESIZE][unit.rect.y//TILESIZE]
                    self.level.selected_unit = unit

    def potential_moves(self, screen):
        if self.level.selected_unit != None:
            origin_x, origin_y = self.level.selected_unit.rect.x//TILESIZE, self.level.selected_unit.rect.y//TILESIZE
            for x in range(self.level.level_size[0]//TILESIZE):
                for y in range(self.level.level_size[1]//TILESIZE):
                    tile_distance = abs(x - origin_x) + abs(y - origin_y)
                    if tile_distance <= self.level.selected_unit.mp:
                        self.move_tile_list.append(pygame.Rect(((x * TILESIZE) - self.level.drawn_sprites.offset.x, (y * TILESIZE) - self.level.drawn_sprites.offset.y, TILESIZE, TILESIZE)))
                        pygame.draw.rect(screen, WHITE, ((x * TILESIZE) - self.level.drawn_sprites.offset.x + 4, (y * TILESIZE) - self.level.drawn_sprites.offset.y + 4, TILESIZE -8, TILESIZE -8),2, border_radius=2)


    def get_optimum_path_nodes(self, start_point, end_point):
        start = self.grid.node(start_point[0], start_point[1])
        end = self.grid.node(end_point[0], end_point[1])
        path, runs = AStarFinder(diagonal_movement = DiagonalMovement.always).find_path(start, end, self.grid)
        return path

    def draw(self, screen):
        self.potential_moves(screen)
        self.draw_cell_rect(screen)
        self.highlight_unit(screen)

        if self.level.selected_unit != None:
          
            pygame.draw.line(screen, LIGHT_BLUE, (self.select_box_rect.center), (self.level.selected_unit.rect.center), 3)
        

            
                

        
