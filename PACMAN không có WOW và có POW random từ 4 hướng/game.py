from pacman import Pacman
from ghost import Ghost
from map import Map
from menu import MenuSystem
from levels import LEVELS
from settings import *
import pygame
import sys
import math
import random

class Game:
    def __init__(self):
        pygame.init()
        
        self.game_width = 800
        self.game_height = 660
        self.ui_width = 200
        self.total_width = self.game_width + self.ui_width
        
        self.screen = pygame.display.set_mode((self.total_width, self.game_height))
        pygame.display.set_caption("Pac-Man Game - Smart AI")
        self.clock = pygame.time.Clock()
        
        self.game_surface = pygame.Surface((self.game_width, self.game_height))
        self.ui_surface = pygame.Surface((self.ui_width, self.game_height))
        
        self.menu = MenuSystem(self.screen)
        self.current_state = 'MENU'
        self.selected_level = 1
        
        self.map = None
        self.pacman = None
        self.ghosts = []
        
        self.score = 0
        self.lives = 3
        self.level = 1
        self.high_score = self.load_high_score()
        self.power_pellet_timer = 0
        
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 24)
        
        self.pow_button_rect = pygame.Rect(10, 325, 180, 35)
        self.pow_cooldown = 0
        self.pow_max_cooldown = 300

    def initialize_level(self, level_num):
        self.selected_level = level_num
        self.level = level_num
        
        level_data = LEVELS[level_num]
        
        self.map = Map(level_data["map"])
        
        self.pacman = Pacman(self.map.pacman_start)
        self.pacman.speed = level_data["pacman_speed"]
        
        ghost_personalities = ['AGGRESSIVE', 'AMBUSH', 'PATROL', 'RANDOM']
        ghost_colors = [RED, PINK, CYAN, ORANGE]
        
        self.ghosts = []
        for i, pos in enumerate(self.map.ghost_starts):
            personality = ghost_personalities[i % len(ghost_personalities)]
            color = ghost_colors[i % len(ghost_colors)]
            ghost = Ghost(pos, color, personality)
            ghost.set_speed(level_data["ghost_speed"])
            self.ghosts.append(ghost)
        
        self.score = 0
        self.lives = 3
        self.power_pellet_timer = 0
        self.pow_cooldown = 0
        self.current_state = 'PLAYING'

    def find_safe_teleport_positions(self, pacman_pos):
        pacman_tile_x = int(pacman_pos[0] // TILE_SIZE)
        pacman_tile_y = int(pacman_pos[1] // TILE_SIZE)
        
        safe_positions = []
        
        directions = [
            (1, 0, "RIGHT"),   # Phải
            (-1, 0, "LEFT"),   # Trái  
            (0, 1, "DOWN"),    # Dưới
            (0, -1, "UP")      # Trên
        ]
        
        chosen_direction = random.choice(directions)
        dir_x, dir_y, dir_name = chosen_direction
        
        print(f"POW direction chosen: {dir_name}")
        
        min_distance = 4
        max_distance = 8
        
        for distance in range(min_distance, max_distance + 1):
            base_x = pacman_tile_x + (dir_x * distance)
            base_y = pacman_tile_y + (dir_y * distance)
            
            positions_to_check = [(base_x, base_y)]
            
            if dir_x != 0:
                positions_to_check.extend([
                    (base_x, base_y + 1),
                    (base_x, base_y - 1),
                    (base_x, base_y + 2),
                    (base_x, base_y - 2)
                ])
            else:
                positions_to_check.extend([
                    (base_x + 1, base_y),
                    (base_x - 1, base_y),
                    (base_x + 2, base_y),
                    (base_x - 2, base_y)
                ])
            
            for target_x, target_y in positions_to_check:
                if self.is_valid_teleport_position(target_x, target_y):
                    safe_positions.append((target_x * TILE_SIZE, target_y * TILE_SIZE))
        
        for _ in range(50):
            offset = random.randint(-3, 3)
            distance = random.randint(min_distance, max_distance)
            
            if dir_x != 0:
                target_x = int(pacman_tile_x + dir_x * distance)
                target_y = int(pacman_tile_y + offset)
            else:
                target_x = int(pacman_tile_x + offset)
                target_y = int(pacman_tile_y + dir_y * distance)
            
            if self.is_valid_teleport_position(target_x, target_y):
                pos = (target_x * TILE_SIZE, target_y * TILE_SIZE)
                if pos not in safe_positions:
                    safe_positions.append(pos)
        
        if len(safe_positions) < 4:
            print(f"Not enough positions in {dir_name} direction, adding more...")
            for y in range(1, len(self.map.map_data) - 1):
                for x in range(1, len(self.map.map_data[y]) - 1):
                    if self.is_basic_valid_position(x, y):
                        
                        is_in_direction = False
                        if dir_name == "RIGHT" and x > pacman_tile_x + 2:
                            is_in_direction = True
                        elif dir_name == "LEFT" and x < pacman_tile_x - 2:
                            is_in_direction = True
                        elif dir_name == "DOWN" and y > pacman_tile_y + 2:
                            is_in_direction = True
                        elif dir_name == "UP" and y < pacman_tile_y - 2:
                            is_in_direction = True
                        
                        if is_in_direction:
                            pos = (x * TILE_SIZE, y * TILE_SIZE)
                            if pos not in safe_positions:
                                safe_positions.append(pos)
                                if len(safe_positions) >= 8:
                                    break
                if len(safe_positions) >= 8:
                    break
        
        print(f"Final safe positions found: {len(safe_positions)} in {dir_name} direction")
        return safe_positions

    def is_valid_teleport_position(self, tile_x, tile_y):
        tile_x = int(tile_x)
        tile_y = int(tile_y)
        
        if tile_y <= 0 or tile_y >= len(self.map.map_data) - 1:
            return False
        if tile_x <= 0 or tile_x >= len(self.map.map_data[tile_y]) - 1:
            return False
        
        if self.map.map_data[tile_y][tile_x] == WALL:
            return False
        
        wall_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                check_x, check_y = int(tile_x + dx), int(tile_y + dy)
                if (check_y < 0 or check_y >= len(self.map.map_data) or
                    check_x < 0 or check_x >= len(self.map.map_data[check_y])):
                    wall_count += 1
                elif self.map.map_data[check_y][check_x] == WALL:
                    wall_count += 1
        
        return wall_count <= 6

    def is_basic_valid_position(self, tile_x, tile_y):
        tile_x = int(tile_x)
        tile_y = int(tile_y)
        
        if tile_y <= 0 or tile_y >= len(self.map.map_data) - 1:
            return False
        if tile_x <= 0 or tile_x >= len(self.map.map_data[tile_y]) - 1:
            return False
        
        return self.map.map_data[tile_y][tile_x] != WALL

    def activate_pow(self):
        if self.pow_cooldown > 0 or self.current_state != 'PLAYING':
            return
        
        print("POW activated!")
        
        safe_positions = self.find_safe_teleport_positions(self.pacman.pos)
        
        print(f"Found {len(safe_positions)} safe positions")
        
        if len(safe_positions) < 1:
            print("No safe positions found! Using fallback...")
            safe_positions = self.get_fallback_positions()
        
        if len(safe_positions) == 0:
            print("Even fallback failed!")
            return
        
        num_ghosts_to_move = min(len(self.ghosts), len(safe_positions))
        selected_positions = random.sample(safe_positions, num_ghosts_to_move)
        
        for i, ghost in enumerate(self.ghosts):
            if i < len(selected_positions):
                new_x, new_y = selected_positions[i]
                old_pos = (ghost.x, ghost.y)
                ghost.x = new_x
                ghost.y = new_y
                ghost.tile_x = new_x // TILE_SIZE
                ghost.tile_y = new_y // TILE_SIZE
                ghost.is_moving = False
                ghost.move_progress = 0
                print(f"Ghost {i+1} moved from {old_pos} to ({new_x}, {new_y})")
        
        self.pow_cooldown = self.pow_max_cooldown
        self.score += 100
        print("POW complete!")

    def get_fallback_positions(self):
        fallback_positions = []
        
        for y in range(2, len(self.map.map_data) - 2, 3):
            for x in range(2, len(self.map.map_data[y]) - 2, 3):
                if self.map.map_data[y][x] != WALL:
                    fallback_positions.append((x * TILE_SIZE, y * TILE_SIZE))
                    if len(fallback_positions) >= 8:
                        return fallback_positions
        
        return fallback_positions

    def load_high_score(self):
        try:
            with open('highscore.txt', 'r') as f:
                return int(f.read().strip())
        except:
            return 0

    def save_high_score(self):
        try:
            with open('highscore.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
                
            if self.current_state == 'MENU':
                result = self.menu.handle_events(event)
                if result == "quit":
                    return 'QUIT'
                elif isinstance(result, int):
                    self.initialize_level(result)
                    
            elif self.current_state == 'PLAYING':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.pacman.set_direction('UP')
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.pacman.set_direction('DOWN')
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.pacman.set_direction('LEFT')
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.pacman.set_direction('RIGHT')
                    elif event.key == pygame.K_SPACE:
                        self.current_state = 'PAUSED'
                    elif event.key == pygame.K_ESCAPE:
                        self.current_state = 'MENU'
                    elif event.key == pygame.K_p:
                        self.activate_pow()
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mouse_pos = event.pos
                        if mouse_pos[0] >= self.game_width:
                            adjusted_pos = (mouse_pos[0] - self.game_width, mouse_pos[1])
                            if self.pow_button_rect.collidepoint(adjusted_pos):
                                self.activate_pow()
                        
            elif self.current_state == 'PAUSED':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.current_state = 'PLAYING'
                    elif event.key == pygame.K_ESCAPE:
                        self.current_state = 'MENU'
                        
            elif self.current_state == 'GAME_OVER':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.initialize_level(self.selected_level)
                    elif event.key == pygame.K_m or event.key == pygame.K_ESCAPE:
                        self.current_state = 'MENU'
                    elif event.key == pygame.K_q:
                        return 'QUIT'
        
        return None

    def update(self):
        if self.current_state == 'MENU':
            self.menu.update()
        elif self.current_state == 'PLAYING':
            self.update_game()

    def update_game(self):
        if self.pow_cooldown > 0:
            self.pow_cooldown -= 1
            
        self.pacman.move(self.map.map_data)
        
        eaten_item = self.pacman.eat(self.map.map_data)
        if eaten_item == 'DOT':
            self.score += SCORE_DOT
        elif eaten_item == 'POWER_PELLET':
            self.score += SCORE_POWER_PELLET
            self.power_pellet_timer = POWER_PELLET_DURATION
            for ghost in self.ghosts:
                ghost.set_scared()

        if self.power_pellet_timer > 0:
            self.power_pellet_timer -= 1

        for ghost in self.ghosts:
            ghost.move(self.pacman.pos, self.map.map_data, self.pacman.direction)

            if ghost.check_pacman_collision(self.pacman.get_rect()):
                if ghost.state == 'NORMAL':
                    self.lives -= 1
                    self.reset_positions()
                    if self.lives <= 0:
                        self.current_state = 'GAME_OVER'
                        if self.score > self.high_score:
                            self.high_score = self.score
                            self.save_high_score()
                elif ghost.state == 'SCARED':
                    self.score += SCORE_GHOST
                    if self.map.ghost_starts:
                        ghost.x, ghost.y = self.map.ghost_starts[0]
                        ghost.tile_x = ghost.x // TILE_SIZE
                        ghost.tile_y = ghost.y // TILE_SIZE
                        ghost.state = 'NORMAL'
                        ghost.color = ghost.original_color

        if self.map.count_remaining_dots() == 0:
            next_level = self.level + 1
            if next_level in LEVELS:
                self.initialize_level(next_level)
            else:
                self.current_state = 'MENU'

        if self.score > 0 and self.score % SCORE_BONUS_LIFE == 0:
            self.lives += 1

    def reset_positions(self):
        if self.map and self.map.pacman_start:
            self.pacman.x, self.pacman.y = self.map.pacman_start
        self.pacman.direction = 'STOP'
        self.pacman.next_direction = 'STOP'
        
        for i, ghost in enumerate(self.ghosts):
            if i < len(self.map.ghost_starts):
                ghost.x, ghost.y = self.map.ghost_starts[i]
                ghost.tile_x = ghost.x // TILE_SIZE
                ghost.tile_y = ghost.y // TILE_SIZE
                ghost.state = 'NORMAL'
                ghost.color = ghost.original_color
                ghost.path = []
                ghost.path_index = 0

    def draw_game(self):
        self.game_surface.fill(BLACK)
        
        if self.map and self.pacman:
            self.map.draw(self.game_surface)
            self.pacman.draw(self.game_surface)
            for ghost in self.ghosts:
                ghost.draw(self.game_surface)
            
            if self.current_state == 'PAUSED':
                overlay = pygame.Surface((self.game_width, self.game_height))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                self.game_surface.blit(overlay, (0, 0))
                
                pause_text = self.font_large.render("PAUSED", True, WHITE)
                text_rect = pause_text.get_rect(center=(self.game_width//2, self.game_height//2))
                self.game_surface.blit(pause_text, text_rect)

    def draw_ui(self):
        self.ui_surface.fill((30, 30, 50))
        
        pygame.draw.line(self.ui_surface, WHITE, (0, 0), (0, self.game_height), 2)
        
        y_pos = 20
        
        title_text = self.font_large.render("SMART AI", True, YELLOW)
        self.ui_surface.blit(title_text, (10, y_pos))
        y_pos += 50
        
        if self.current_state in ['PLAYING', 'PAUSED', 'GAME_OVER']:
            level_name = LEVELS[self.selected_level]["name"]
            level_text = self.font_medium.render(f"Level {self.level}:", True, WHITE)
            self.ui_surface.blit(level_text, (10, y_pos))
            y_pos += 25
            
            name_text = self.font_small.render(level_name, True, CYAN)
            self.ui_surface.blit(name_text, (10, y_pos))
            y_pos += 40
        
        score_text = self.font_medium.render("SCORE", True, WHITE)
        self.ui_surface.blit(score_text, (10, y_pos))
        y_pos += 25
        
        score_value = self.font_medium.render(f"{self.score:,}", True, YELLOW)
        self.ui_surface.blit(score_value, (10, y_pos))
        y_pos += 40
        
        high_text = self.font_medium.render("HIGH SCORE", True, WHITE)
        self.ui_surface.blit(high_text, (10, y_pos))
        y_pos += 25
        
        high_value = self.font_medium.render(f"{self.high_score:,}", True, ORANGE)
        self.ui_surface.blit(high_value, (10, y_pos))
        y_pos += 40
        
        if self.current_state in ['PLAYING', 'PAUSED', 'GAME_OVER']:
            lives_text = self.font_medium.render("LIVES", True, WHITE)
            self.ui_surface.blit(lives_text, (10, y_pos))
            y_pos += 25
            
            for i in range(self.lives):
                icon_x = 10 + i * 25
                pygame.draw.circle(self.ui_surface, YELLOW, (icon_x + 10, y_pos + 10), 8)
            y_pos += 40
            
            if self.power_pellet_timer > 0:
                power_text = self.font_small.render("POWER MODE", True, WHITE)
                self.ui_surface.blit(power_text, (10, y_pos))
                y_pos += 20
                
                remaining_time = self.power_pellet_timer // 60 + 1
                time_text = self.font_small.render(f"{remaining_time}s", True, CYAN)
                self.ui_surface.blit(time_text, (10, y_pos))
                y_pos += 25
        
        button_color = (100, 50, 200) if self.pow_cooldown == 0 else (50, 50, 50)
        pygame.draw.rect(self.ui_surface, button_color, self.pow_button_rect)
        pygame.draw.rect(self.ui_surface, WHITE, self.pow_button_rect, 2)
        
        if self.pow_cooldown == 0:
            pow_text = self.font_medium.render("POW!", True, WHITE)
            text_rect = pow_text.get_rect(center=self.pow_button_rect.center)
            self.ui_surface.blit(pow_text, text_rect)
        else:
            cooldown_seconds = self.pow_cooldown // 60 + 1
            cooldown_text = self.font_small.render(f"Wait {cooldown_seconds}s", True, WHITE)
            text_rect = cooldown_text.get_rect(center=self.pow_button_rect.center)
            self.ui_surface.blit(cooldown_text, text_rect)
        
        y_pos += 50
        
        ai_info_text = self.font_small.render("AI STATUS", True, WHITE)
        self.ui_surface.blit(ai_info_text, (10, y_pos))
        y_pos += 20
        
        if self.ghosts:
            for i, ghost in enumerate(self.ghosts[:4]):
                danger_level = ghost.evaluate_danger_level(self.pacman.pos) if hasattr(ghost, 'evaluate_danger_level') else 'LOW'
                ai_text = f"G{i+1}: {ghost.personality[:3]} ({danger_level[:1]})"
                color = ghost.original_color if ghost.state == 'NORMAL' else (0, 0, 255)
                ai_surface = self.font_small.render(ai_text, True, color)
                self.ui_surface.blit(ai_surface, (10, y_pos))
                y_pos += 18
        
        y_pos = self.game_height - 120
        controls_title = self.font_medium.render("CONTROLS", True, WHITE)
        self.ui_surface.blit(controls_title, (10, y_pos))
        y_pos += 25
        
        controls = [
            "WASD: Move",
            "P/Click: POW",
            "SPACE: Pause",
            "ESC: Menu"
        ]
        
        for control in controls:
            control_text = self.font_small.render(control, True, (200, 200, 200))
            self.ui_surface.blit(control_text, (10, y_pos))
            y_pos += 18

    def draw_game_over(self):
        self.game_surface.fill(BLACK)
        
        game_over_text = self.font_large.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(self.game_width//2, self.game_height//2 - 60))
        self.game_surface.blit(game_over_text, text_rect)
        
        score_text = self.font_medium.render(f"Final Score: {self.score:,}", True, WHITE)
        text_rect = score_text.get_rect(center=(self.game_width//2, self.game_height//2 - 20))
        self.game_surface.blit(score_text, text_rect)
        
        if self.score == self.high_score and self.score > 0:
            new_high_text = self.font_medium.render("NEW HIGH SCORE!", True, YELLOW)
            text_rect = new_high_text.get_rect(center=(self.game_width//2, self.game_height//2 + 20))
            self.game_surface.blit(new_high_text, text_rect)
        
        restart_text = self.font_small.render("Press R to restart, M for menu, Q to quit", True, WHITE)
        text_rect = restart_text.get_rect(center=(self.game_width//2, self.game_height//2 + 80))
        self.game_surface.blit(restart_text, text_rect)

    def draw(self):
        self.screen.fill(BLACK)
        
        if self.current_state == 'MENU':
            self.menu.draw()
        else:
            if self.current_state == 'GAME_OVER':
                self.draw_game_over()
            else:
                self.draw_game()
            
            self.draw_ui()
            
            self.screen.blit(self.game_surface, (0, 0))
            self.screen.blit(self.ui_surface, (self.game_width, 0))
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            result = self.handle_events()
            if result == 'QUIT':
                running = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()