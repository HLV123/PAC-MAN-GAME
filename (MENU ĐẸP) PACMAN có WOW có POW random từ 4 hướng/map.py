import pygame
import math
from settings import *

class Map:
    def __init__(self, map_source):
        if isinstance(map_source, str):
            self.map_data = self.load_map(map_source)
        else:
            self.map_data = map_source.copy()
            
        self.pacman_start = None
        self.ghost_starts = []
        self.total_dots = 0
        self.parse_map()
        
        self.wall_surface = None
        self.create_wall_surface()

    def load_map(self, filename):
        try:
            with open(filename, 'r') as file:
                return [line.rstrip() for line in file.readlines()]
        except FileNotFoundError:
            return self.create_default_map()

    def create_default_map(self):
        return [
            "####################################",
            "#..................#.................#",
            "#.####.#######.####.#.####.#######.####.#",
            "#o#  #.#     #.#  #.#.#  #.#     #.#  #o#",
            "#.####.#######.####.#.####.#######.####.#",
            "#..................................#",
            "#.####.##.############.##.####.#",
            "#......##......##......##......#",
            "######.#######.##.#######.######",
            "     #.#     #....#     #.#     ",
            "     #.# ###.####.### #.#     ",
            "     #...#..........#...#     ",
            "     #.# ############.#.#     ",
            "######.#              #.######",
            "#......   G  G  G  G   ......#",
            "######.# ############.#######",
            "     #.#              #.#     ",
            "     #.# ############.#.#     ",
            "     #...#..........#...#     ",
            "     #.# ###.####.### #.#     ",
            "     #.#     #....#     #.#     ",
            "######.#######.##.#######.######",
            "#......##......##......##......#",
            "#.####.##.############.##.####.#",
            "#o..##................##..o#",
            "###.##.##.########.##.##.###",
            "#......##....##....##......#",
            "#.##########.##.##########.#",
            "#..........................#",
            "#.####.######.######.####.#",
            "#......#    #.#    #......#",
            "#######.####.P.####.#######",
            "####################################"
        ]

    def parse_map(self):
        for y, row in enumerate(self.map_data):
            new_row = ""
            for x, tile in enumerate(row):
                if tile == PACMAN_START:
                    self.pacman_start = (x * TILE_SIZE, y * TILE_SIZE)
                    new_row += EMPTY
                elif tile == GHOST_START:
                    self.ghost_starts.append((x * TILE_SIZE, y * TILE_SIZE))
                    new_row += EMPTY
                elif tile == DOT:
                    self.total_dots += 1
                    new_row += tile
                else:
                    new_row += tile
            self.map_data[y] = new_row
        
        if self.pacman_start is None:
            self.pacman_start = self.find_safe_start_position()
        
        if not self.ghost_starts:
            center_x = len(self.map_data[0]) // 2 if self.map_data else 10
            center_y = len(self.map_data) // 2 if self.map_data else 10
            for i in range(4):
                ghost_x = (center_x + i) * TILE_SIZE
                ghost_y = center_y * TILE_SIZE
                self.ghost_starts.append((ghost_x, ghost_y))

    def find_safe_start_position(self):
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile == EMPTY or tile == DOT:
                    return (x * TILE_SIZE, y * TILE_SIZE)
        return (TILE_SIZE, TILE_SIZE)

    def create_wall_surface(self):
        if len(self.map_data) == 0:
            return
            
        self.wall_surface = pygame.Surface((len(self.map_data[0]) * TILE_SIZE, 
                                          len(self.map_data) * TILE_SIZE))
        self.wall_surface.fill(BLACK)
        
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                if tile == WALL:
                    wall_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    
                    pygame.draw.rect(self.wall_surface, WALL_COLOR, wall_rect)
                    
                    pygame.draw.line(self.wall_surface, WALL_HIGHLIGHT, 
                                   (wall_rect.left, wall_rect.top), 
                                   (wall_rect.right-1, wall_rect.top), 2)
                    pygame.draw.line(self.wall_surface, WALL_HIGHLIGHT, 
                                   (wall_rect.left, wall_rect.top), 
                                   (wall_rect.left, wall_rect.bottom-1), 2)
                    
                    pygame.draw.line(self.wall_surface, WALL_SHADOW, 
                                   (wall_rect.left+1, wall_rect.bottom-1), 
                                   (wall_rect.right-1, wall_rect.bottom-1), 2)
                    pygame.draw.line(self.wall_surface, WALL_SHADOW, 
                                   (wall_rect.right-1, wall_rect.top+1), 
                                   (wall_rect.right-1, wall_rect.bottom-1), 2)

    def draw(self, screen):
        if self.wall_surface:
            screen.blit(self.wall_surface, (0, 0))
        
        for y, row in enumerate(self.map_data):
            for x, tile in enumerate(row):
                center_x = x * TILE_SIZE + TILE_SIZE // 2
                center_y = y * TILE_SIZE + TILE_SIZE // 2
                
                if tile == DOT:
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), 2)
                    pygame.draw.circle(screen, (255, 255, 100), (center_x, center_y), 1)
                    
                elif tile == POWER_PELLET:
                    pulse = abs(math.sin(pygame.time.get_ticks() * 0.01)) * 2 + 4
                    pygame.draw.circle(screen, WHITE, (center_x, center_y), int(pulse))
                    pygame.draw.circle(screen, YELLOW, (center_x, center_y), int(pulse - 1))

    def is_valid_position(self, x, y):
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if (map_y < 0 or map_y >= len(self.map_data) or 
            map_x < 0 or len(self.map_data) == 0 or
            map_x >= len(self.map_data[map_y if map_y < len(self.map_data) else 0])):
            return False
            
        return self.map_data[map_y][map_x] != WALL

    def get_tile_at(self, x, y):
        map_x = int(x // TILE_SIZE)
        map_y = int(y // TILE_SIZE)
        
        if (map_y < 0 or map_y >= len(self.map_data) or 
            map_x < 0 or len(self.map_data) == 0 or
            map_x >= len(self.map_data[map_y if map_y < len(self.map_data) else 0])):
            return WALL
            
        return self.map_data[map_y][map_x]

    def count_remaining_dots(self):
        count = 0
        for row in self.map_data:
            count += row.count(DOT)
        return count