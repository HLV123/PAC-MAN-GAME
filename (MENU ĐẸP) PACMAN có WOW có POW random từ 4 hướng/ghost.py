import pygame
import math
from settings import *
import random

class Ghost:
    def __init__(self, start_pos, color=RED, personality='AGGRESSIVE'):
        self.start_tile_x = start_pos[0] // TILE_SIZE
        self.start_tile_y = start_pos[1] // TILE_SIZE
        
        self.tile_x = self.start_tile_x
        self.tile_y = self.start_tile_y
        
        self.x = self.tile_x * TILE_SIZE
        self.y = self.tile_y * TILE_SIZE
        
        self.speed = 1
        self.state = 'NORMAL'
        self.color = color
        self.original_color = color
        self.personality = personality
        self.scared_timer = 0
        self.scared_duration = 300
        self.direction = 'UP'
        
        self.target_tile_x = self.tile_x
        self.target_tile_y = self.tile_y
        self.move_progress = 0
        self.is_moving = False
        
        self.decision_timer = 0

    def set_speed(self, speed):
        self.speed = speed

    def move(self, pacman_pos, map_data, pacman_direction='STOP'):
        if self.state == 'SCARED':
            self.scared_timer -= 1
            if self.scared_timer <= 0:
                self.state = 'NORMAL'
                self.color = self.original_color
        
        self.decision_timer += 1
        
        if not self.is_moving:
            if self.decision_timer >= 20:
                self.decide_next_move(pacman_pos, map_data)
                self.decision_timer = 0
        
        if self.is_moving:
            self.update_movement()

    def decide_next_move(self, pacman_pos, map_data):
        pacman_tile_x = pacman_pos[0] // TILE_SIZE
        pacman_tile_y = pacman_pos[1] // TILE_SIZE
        
        possible_moves = self.get_valid_moves(map_data)
        
        if not possible_moves:
            return
        
        if self.state == 'SCARED':
            best_move = self.choose_flee_move(possible_moves, pacman_tile_x, pacman_tile_y)
        else:
            if self.personality == 'AGGRESSIVE':
                best_move = self.choose_aggressive_move(possible_moves, pacman_tile_x, pacman_tile_y)
            elif self.personality == 'AMBUSH':
                best_move = self.choose_ambush_move(possible_moves, pacman_tile_x, pacman_tile_y)
            elif self.personality == 'PATROL':
                best_move = self.choose_patrol_move(possible_moves, pacman_tile_x, pacman_tile_y)
            else:
                best_move = self.choose_random_move(possible_moves, pacman_tile_x, pacman_tile_y)
        
        if best_move:
            self.start_move_to(best_move[0], best_move[1], best_move[2])

    def get_valid_moves(self, map_data):
        moves = []
        directions = [
            (0, -1, 'UP'),
            (0, 1, 'DOWN'),
            (-1, 0, 'LEFT'),
            (1, 0, 'RIGHT')
        ]
        
        for dx, dy, direction in directions:
            new_tile_x = self.tile_x + dx
            new_tile_y = self.tile_y + dy
            
            if self.is_valid_tile(new_tile_x, new_tile_y, map_data):
                moves.append((new_tile_x, new_tile_y, direction))
        
        return moves

    def is_valid_tile(self, tile_x, tile_y, map_data):
        if tile_y < 0 or tile_y >= len(map_data):
            return False
        if tile_x < 0 or tile_x >= len(map_data[tile_y]):
            return False
        
        return map_data[tile_y][tile_x] != WALL

    def choose_aggressive_move(self, moves, pacman_tile_x, pacman_tile_y):
        best_move = None
        best_distance = float('inf')
        
        for tile_x, tile_y, direction in moves:
            distance = abs(tile_x - pacman_tile_x) + abs(tile_y - pacman_tile_y)
            if distance < best_distance:
                best_distance = distance
                best_move = (tile_x, tile_y, direction)
        
        return best_move

    def choose_ambush_move(self, moves, pacman_tile_x, pacman_tile_y):
        distance_to_pacman = abs(self.tile_x - pacman_tile_x) + abs(self.tile_y - pacman_tile_y)
        
        if distance_to_pacman < 8:
            return self.choose_aggressive_move(moves, pacman_tile_x, pacman_tile_y)
        else:
            target_x = pacman_tile_x + 3 if pacman_tile_x > self.tile_x else pacman_tile_x - 3
            target_y = pacman_tile_y + 3 if pacman_tile_y > self.tile_y else pacman_tile_y - 3
            
            best_move = None
            best_distance = float('inf')
            
            for tile_x, tile_y, direction in moves:
                distance = abs(tile_x - target_x) + abs(tile_y - target_y)
                if distance < best_distance:
                    best_distance = distance
                    best_move = (tile_x, tile_y, direction)
            
            return best_move

    def choose_patrol_move(self, moves, pacman_tile_x, pacman_tile_y):
        distance_to_pacman = abs(self.tile_x - pacman_tile_x) + abs(self.tile_y - pacman_tile_y)
        
        if distance_to_pacman < 10:
            return self.choose_aggressive_move(moves, pacman_tile_x, pacman_tile_y)
        else:
            patrol_points = [(10, 10), (30, 10), (30, 25), (10, 25)]
            closest_patrol = min(patrol_points, 
                key=lambda p: abs(p[0] - self.tile_x) + abs(p[1] - self.tile_y))
            
            best_move = None
            best_distance = float('inf')
            
            for tile_x, tile_y, direction in moves:
                distance = abs(tile_x - closest_patrol[0]) + abs(tile_y - closest_patrol[1])
                if distance < best_distance:
                    best_distance = distance
                    best_move = (tile_x, tile_y, direction)
            
            return best_move

    def choose_random_move(self, moves, pacman_tile_x, pacman_tile_y):
        if random.random() < 0.4:
            return self.choose_aggressive_move(moves, pacman_tile_x, pacman_tile_y)
        else:
            return random.choice(moves) if moves else None

    def choose_flee_move(self, moves, pacman_tile_x, pacman_tile_y):
        best_move = None
        best_distance = 0
        
        for tile_x, tile_y, direction in moves:
            distance = abs(tile_x - pacman_tile_x) + abs(tile_y - pacman_tile_y)
            if distance > best_distance:
                best_distance = distance
                best_move = (tile_x, tile_y, direction)
        
        return best_move

    def start_move_to(self, target_tile_x, target_tile_y, direction):
        self.target_tile_x = target_tile_x
        self.target_tile_y = target_tile_y
        self.direction = direction
        self.is_moving = True
        self.move_progress = 0

    def update_movement(self):
        self.move_progress += self.speed
        
        if self.move_progress >= TILE_SIZE:
            self.tile_x = self.target_tile_x
            self.tile_y = self.target_tile_y
            self.x = self.tile_x * TILE_SIZE
            self.y = self.tile_y * TILE_SIZE
            self.is_moving = False
            self.move_progress = 0
        else:
            progress_ratio = self.move_progress / TILE_SIZE
            
            start_x = self.tile_x * TILE_SIZE
            start_y = self.tile_y * TILE_SIZE
            target_x = self.target_tile_x * TILE_SIZE
            target_y = self.target_tile_y * TILE_SIZE
            
            self.x = start_x + (target_x - start_x) * progress_ratio
            self.y = start_y + (target_y - start_y) * progress_ratio

    def set_scared(self):
        self.state = 'SCARED'
        self.color = (0, 0, 255)
        self.scared_timer = self.scared_duration

    def check_pacman_collision(self, pacman_rect):
        ghost_rect = pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
        return ghost_rect.colliderect(pacman_rect)

    def draw(self, screen):
        color = self.color
        
        if self.state == 'SCARED':
            if self.scared_timer < 120 and self.scared_timer % 20 < 10:
                color = (255, 255, 255)
        
        body_rect = pygame.Rect(int(self.x), int(self.y), TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, color, body_rect)
        
        eye_size = 3
        left_eye_x = int(self.x) + 5
        left_eye_y = int(self.y) + 5
        right_eye_x = int(self.x) + TILE_SIZE - 5
        right_eye_y = int(self.y) + 5
        
        pygame.draw.circle(screen, WHITE, (left_eye_x, left_eye_y), eye_size)
        pygame.draw.circle(screen, WHITE, (right_eye_x, right_eye_y), eye_size)
        
        if self.state != 'SCARED':
            pupil_offset = 1
            pupil_x = pupil_y = 0
            
            if self.direction == 'RIGHT':
                pupil_x = pupil_offset
            elif self.direction == 'LEFT':
                pupil_x = -pupil_offset
            elif self.direction == 'UP':
                pupil_y = -pupil_offset
            elif self.direction == 'DOWN':
                pupil_y = pupil_offset
            
            pygame.draw.circle(screen, BLACK, (left_eye_x + pupil_x, left_eye_y + pupil_y), 1)
            pygame.draw.circle(screen, BLACK, (right_eye_x + pupil_x, right_eye_y + pupil_y), 1)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), TILE_SIZE, TILE_SIZE)