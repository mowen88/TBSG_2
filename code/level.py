import pygame, csv
from os import walk
from settings import *
from pytmx.util_pygame import load_pygame
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from state import State
from camera import Camera
from sprites import Tile, Unit

class Level(State):
    def __init__(self, game):
        State.__init__(self, game)

        self.game = game

        self.turn = 'allied'
        self.turn_count = 0
        self.day = 1

        self.updated_sprites = pygame.sprite.Group()
        self.drawn_sprites = Camera(self.game, self)
        self.offset = self.drawn_sprites.offset

        self.terrain_sprites = pygame.sprite.Group()
        self.player_units = pygame.sprite.Group()
        self.allied_units = pygame.sprite.Group()
        self.axis_units = pygame.sprite.Group()
        self.used_units = pygame.sprite.Group()

        self.selected_unit = None

        self.create_level()

        self.matrix = self.get_matrix(f'../maps/map_1/map_1.csv')
        self.level_size = self.get_level_size(f'../maps/map_1/map_1.csv')

        self.active_sprite = None
        self.move_destination = None
        self.center_screen = [100, 100]

        self.shortest_path = []
        self.potential_moves = {}
        self.selected = False
        self.select_box = pygame.image.load('../assets/select_box.png').convert_alpha()
        self.populate_player_units()

    def get_matrix(self, filename):
        matrix = []
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                matrix.append([int(value) for value in row])
            return matrix

    def get_level_size(self, filename):
        with open(filename, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for row in reader:
                rows = (sum (1 for row in reader) + 1)
                cols = len(row)
        return (cols * TILESIZE, rows * TILESIZE)

    # def get_potential_moves(self):
        # for unit in self.player_units:
        #     unit.calculate_moves(self.matrix)
    # Function to find the shortest path using BFS
    def find_shortest_path(self, start, end):
        queue = deque([(start, [])])
        visited = set([start])
        costs = {start: 0}

        while queue:
            current, path = queue.popleft()

            if current == end:
                return path

            neighbors = get_neighbors(current)
            neighbors.sort(key=lambda n: grid[n[1]][n[0]])

            for neighbor in neighbors:
                neighbor_cost = costs[current] + grid[neighbor[1]][neighbor[0]]
                if neighbor not in visited or neighbor_cost < costs[neighbor]:
                    queue.append((neighbor, path + [neighbor]))
                    visited.add(neighbor)
                    costs[neighbor] = neighbor_cost

        return None

    def get_neighbors(self, node):
        x, y = node
        neighbors = []

        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.level.level_size[0] - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.level.level_size[1] - 1:
            neighbors.append((x, y + 1))

        return neighbors

    def calculate_moves(self, grid):
        possible_moves = []
        visited_tiles = set()
        move_points = self.move_points

        def dfs(row, column, move_points, distance):

            if move_points < 0 or distance > self.move_points or (row, column) in visited_tiles:
                return

            visited_tiles.add((row, column))
            possible_moves.append((row, column))

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                new_row = row + dy
                new_column = column + dx

                if 0 <= new_row < self.level.level_size[1] and 0 <= new_column < self.level.level_size[0]:
                    tile_penalty = grid[new_row][new_column]
                    new_move_points = move_points - tile_penalty
                    dfs(new_row, new_column, new_move_points, distance + 1)

        sprite_row = self.rect.y // TILESIZE
        sprite_column = self.rect.x // TILESIZE
        dfs(sprite_row, sprite_column, move_points, 0)

        self.potential_moves = possible_moves

    def get_potential_moves(self, selected_unit):
	    # Create a new matrix with the same values as the original matrix
	    # but with a move penalty of 50 for occupied tiles
	    penalty_matrix = [[self.matrix[row][col] for col in range(len(self.matrix[0]))] for row in range(len(self.matrix))]
	    
	    # Assign a move penalty of 50 to tiles occupied by units in any group
	    if selected_unit in self.allied_units:
		    for unit in self.axis_units:
		        row, col = unit.rect.center[1] // TILESIZE, unit.rect.center[0] // TILESIZE
		        penalty_matrix[row][col] = 50
	    else:
	    	for unit in self.allied_units:
		        row, col = unit.rect.center[1] // TILESIZE, unit.rect.center[0] // TILESIZE
		        penalty_matrix[row][col] = 50

	    # # # Update the potential moves for each unit using the new penalty matrix
	    # for unit in self.player_units:
	    #     unit.calculate_moves(self.matrix)

    def swap_teams(self):
    	if ACTIONS['right_click']:
	    	if self.turn == 'allied':
	    		self.turn = 'axis'
	    	else:
	    		self.turn = 'allied'
	    	self.populate_player_units()
	    	self.turn_count += 1
	    	if self.turn_count % 2 == 0:
	    		self.day += 1
	    	ACTIONS['right_click'] = False

    def populate_player_units(self):
    	self.used_units.empty()
    	self.player_units.empty()
    	if self.turn == 'allied':
	    	for unit in self.allied_units:
	    		unit.add(self.player_units)		
    	else:
	    	for unit in self.axis_units:
	    		unit.add(self.player_units)

    def activate(self):
        if ACTIONS['left_click']:
            mouse_pos = pygame.mouse.get_pos() + self.offset
            clicked_tile_row = mouse_pos[1] // TILESIZE
            clicked_tile_column = mouse_pos[0] // TILESIZE

            clicked_unit = None

            for unit in self.player_units:
                if unit.rect.collidepoint(mouse_pos):
                    self.selected = True
                    clicked_unit = unit
                    break

            if clicked_unit is not None:
                if unit not in self.used_units and unit in self.player_units:
                    if self.active_sprite != clicked_unit:
                        self.active_sprite = clicked_unit
                        self.active_sprite.active = True
                        self.get_potential_moves(unit)

            elif hasattr(self.active_sprite, 'potential_moves'):
                if (clicked_tile_row, clicked_tile_column) in self.active_sprite.potential_moves:
                    self.active_sprite.rect.topleft = clicked_tile_column * TILESIZE, clicked_tile_row * TILESIZE
                    self.used_units.add(self.active_sprite)
                    self.active_sprite = None
                    self.selected = False
                else:
                    self.active_sprite = None
          

            self.move_destination = None

            # ACTIONS['left_click'] = False

    def create_level(self):
    	tmx_data = load_pygame(f'../maps/map_1/map_1.tmx')

    	for x, y, surf in tmx_data.get_layer_by_name('tiles').tiles():
    		Tile(self.game, self, [self.terrain_sprites, self.drawn_sprites], (x * TILESIZE, y * TILESIZE), surf)

    	for obj in tmx_data.get_layer_by_name('reds'):
    		for name in ['Infantry','Tank','Artillery','HQ']:
    			if obj.name == name: Unit(self.game, self, [self.allied_units, self.updated_sprites, self.drawn_sprites], (obj.x, obj.y), pygame.image.load(f'../assets/red_units/{obj.name}.png').convert_alpha(), RED, obj.name)

    	for obj in tmx_data.get_layer_by_name('blues'):
    		for name in ['Infantry','Tank','Artillery','HQ']:
    			if obj.name == name: Unit(self.game, self, [self.axis_units, self.updated_sprites, self.drawn_sprites], (obj.x, obj.y), pygame.image.load(f'../assets/blue_units/{obj.name}.png').convert_alpha(), RED, obj.name)

    def show_potential_moves(self, screen):
        # Draw the grid with numbers and highlight tiles within the move point range
        mouse_pos = pygame.mouse.get_pos() + self.offset
        for unit in self.player_units:
            if unit == self.active_sprite:
                for y in range(self.level_size[1]//TILESIZE):
                    for x in range(self.level_size[0]//TILESIZE):
                        rect = pygame.Rect(x, y, TILESIZE, TILESIZE)
                        value = str(self.matrix[y][x])
                        
                        # Check if the mouse is over a highlighted tile
                        mouse_pos = pygame.mouse.get_pos()
                        if rect.collidepoint(mouse_pos):
                            # Find the shortest path between the sprite and the highlighted tile
                            start = (self.active_sprite.rect.topleft)
                            end = (x, y)
                            shortest_path = self.find_shortest_path(start, end)

                # Check if the potential move tiles dictionary needs to be updated
                if self.shortest_path:
                    last_path_node = self.shortest_path[-1]
                    if last_path_node not in self.potential_moves:
                        self.potential_moves.clear()

                        # Find all potential move-to tiles in blue
                        for y in range(self.level_size[1]//TILESIZE):
                            for x in range(self.level_size[0]//TILESIZE):
                                # Find the path between the sprite and the current tile
                                start = (self.active_sprite.rect.x, self.active_sprite.rect.y)
                                end = (x, y)
                                path = self.find_shortest_path(start, end)

                                if path:
                                    accumulated_value = sum(self.matrix[node[1]][node[0]] for node in path)
                                    if accumulated_value <= self.active_sprite.move_points:
                                        self.potential_moves[(x, y)] = path

                
                # Draw the potential move tiles in blue and potential attackable tiles in red
                for move_tile, path in self.potential_moves.items():
                    attackable_tiles = self.get_neighbors(path[-1])
                    for path_node in path:
                        path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILESIZE, TILESIZE, TILESIZE)
                        pygame.draw.rect(screen, BLUE, path_rect)
            #             for tile_node in attackable_tiles:
            #                 if tile_node not in potential_moves and tile_node != unit2.rect.topleft:
            #                     attackable_rect = pygame.Rect(tile_node[0] * TILE_SIZE, tile_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            #                     pygame.draw.rect(screen, CYAN, attackable_rect)

            #             # Draw the tile value on top of the blue tile
            #             tile_value = str(grid[path_node[1]][path_node[0]])
            #             font = pygame.font.Font(None, 24)
            #             text = font.render(tile_value, True, WHITE)
            #             text_rect = text.get_rect(center=path_rect.center)
            #             screen.blit(text, text_rect)

            #     # Draw the shortest path and their values
            #     accumulated_value = 0
            #     for path_node in shortest_path:
            #         path_rect = pygame.Rect(path_node[0] * TILE_SIZE, path_node[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            #         node_value = grid[path_node[1]][path_node[0]]
            #         accumulated_value += node_value
                
    def draw_cursor(self, screen):
        mouse_pos = pygame.mouse.get_pos() + self.offset
        snapped_pos = [(mouse_pos[0] // TILESIZE) * TILESIZE,(mouse_pos[1] // TILESIZE) * TILESIZE]
        screen.blit(self.select_box, (snapped_pos[0] - self.offset.x, snapped_pos[1] - self.offset.y))

    def update(self, dt):
        self.activate()
        self.swap_teams()

        if ACTIONS['return']: 
            self.exit_state()
            self.game.reset_keys()

        self.updated_sprites.update(dt)
        self.drawn_sprites.dt_update(dt)

    def draw(self, screen):
        screen.fill(GREEN)
        self.drawn_sprites.offset_draw(self.center_screen)
        self.game.render_text(self.active_sprite, PINK, self.game.big_font, RES/2)
        self.show_potential_moves(screen)
        self.draw_cursor(screen)

		

		




		
