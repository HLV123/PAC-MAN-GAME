import pygame
import math
from settings import *

class Pacman:
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.direction = 'STOP'
        self.next_direction = 'STOP'
        self.speed = 2
        self.animation_frame = 0
        self.animation_speed = 0.2
        self.mouth_angle = 0
        self.power_mode = False  # Track if Pacman is in power mode
        
        # For smooth movement
        self.target_x = self.x
        self.target_y = self.y

    def set_power_mode(self, power_mode):
        """Set Pacman's power mode state"""
        self.power_mode = power_mode

    def move(self, map_data):
        # Try to change direction if a new direction was requested
        if self.next_direction != 'STOP':
            new_x, new_y = self.x, self.y
            if self.next_direction == 'UP':
                new_y -= self.speed
            elif self.next_direction == 'DOWN':
                new_y += self.speed
            elif self.next_direction == 'LEFT':
                new_x -= self.speed
            elif self.next_direction == 'RIGHT':
                new_x += self.speed
            
            # Check if we can move in the new direction
            if not self.is_collision(new_x, new_y, map_data):
                self.direction = self.next_direction
                self.next_direction = 'STOP'

        # Move in current direction
        new_x, new_y = self.x, self.y
        if self.direction == 'UP':
            new_y -= self.speed
        elif self.direction == 'DOWN':
            new_y += self.speed
        elif self.direction == 'LEFT':
            new_x -= self.speed
        elif self.direction == 'RIGHT':
            new_x += self.speed

        # Check for collision with walls and ensure we stay within bounds
        if not self.is_collision(new_x, new_y, map_data):
            # Additional safety check to ensure we don't go off screen
            new_x = max(0, min(new_x, SCREEN_WIDTH - TILE_SIZE))
            new_y = max(0, min(new_y, SCREEN_HEIGHT - TILE_SIZE))
            self.x, self.y = new_x, new_y
        else:
            self.direction = 'STOP'  # Stop if hitting a wall

        # Update animation
        if self.direction != 'STOP':
            self.animation_frame += self.animation_speed
            if self.animation_frame >= 2 * math.pi:
                self.animation_frame = 0

    def is_collision(self, x, y, map_data):
        # Check collision with map bounds first
        if x < 0 or y < 0:
            return True
        
        # Convert pixel position to tile index
        # Check all corners of Pacman's bounding box
        tile_positions = [
            (int(x // TILE_SIZE), int(y // TILE_SIZE)),  # Top-left
            (int((x + TILE_SIZE - 1) // TILE_SIZE), int(y // TILE_SIZE)),  # Top-right
            (int(x // TILE_SIZE), int((y + TILE_SIZE - 1) // TILE_SIZE)),  # Bottom-left
            (int((x + TILE_SIZE - 1) // TILE_SIZE), int((y + TILE_SIZE - 1) // TILE_SIZE))  # Bottom-right
        ]
        
        for map_x, map_y in tile_positions:
            # Check bounds more carefully
            if (map_y >= len(map_data) or 
                map_y < 0 or 
                map_x < 0 or 
                len(map_data) == 0 or
                map_x >= len(map_data[map_y]) or
                len(map_data[map_y]) == 0):
                return True
                
            # Check if any corner is in a wall
            if map_data[map_y][map_x] == WALL:
                return True
                
        return False

    def eat(self, map_data):
        # Check if Pacman is on a dot or power pellet
        map_x = int((self.x + TILE_SIZE//2) // TILE_SIZE)
        map_y = int((self.y + TILE_SIZE//2) // TILE_SIZE)
        
        if (0 <= map_y < len(map_data) and 
            0 <= map_x < len(map_data[map_y]) and 
            len(map_data[map_y]) > 0):
            
            if map_data[map_y][map_x] == DOT:
                # Create new row with the dot removed
                row = map_data[map_y]
                new_row = row[:map_x] + EMPTY + row[map_x+1:]
                map_data[map_y] = new_row
                return 'DOT'
            elif map_data[map_y][map_x] == POWER_PELLET:
                # Create new row with the power pellet removed
                row = map_data[map_y]
                new_row = row[:map_x] + EMPTY + row[map_x+1:]
                map_data[map_y] = new_row
                return 'POWER_PELLET'
        return None

    def set_direction(self, direction):
        """Set the next direction for Pacman"""
        self.next_direction = direction

    def draw(self, screen):
        center_x = self.x + TILE_SIZE // 2
        center_y = self.y + TILE_SIZE // 2
        radius = TILE_SIZE // 2 - 1
        
        # Calculate mouth opening angle based on animation
        mouth_opening = abs(math.sin(self.animation_frame)) * 0.8 + 0.2
        
        # Determine facing direction for mouth
        start_angle = 0
        end_angle = 2 * math.pi
        
        if self.direction == 'RIGHT':
            start_angle = mouth_opening
            end_angle = 2 * math.pi - mouth_opening
        elif self.direction == 'LEFT':
            start_angle = math.pi - mouth_opening
            end_angle = math.pi + mouth_opening
        elif self.direction == 'UP':
            start_angle = 3 * math.pi / 2 - mouth_opening
            end_angle = 3 * math.pi / 2 + mouth_opening
        elif self.direction == 'DOWN':
            start_angle = math.pi / 2 - mouth_opening
            end_angle = math.pi / 2 + mouth_opening
        
        # Choose color based on power mode
        if self.power_mode:
            # Power mode: Make Pacman glow with alternating colors
            time_factor = pygame.time.get_ticks() * 0.01
            glow_intensity = abs(math.sin(time_factor)) * 0.5 + 0.5
            pacman_color = (
                int(255 * glow_intensity),
                int(255 * glow_intensity),
                int(100 + 155 * glow_intensity)
            )
            
            # Draw a larger glowing outline
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), radius + 3)
        else:
            pacman_color = YELLOW
        
        if self.direction != 'STOP':
            # Draw Pacman with mouth animation
            points = [(center_x, center_y)]
            
            # Create arc points
            for angle in range(int(math.degrees(end_angle)), int(math.degrees(start_angle + 2 * math.pi)), 5):
                if angle > 360:
                    angle -= 360
                rad_angle = math.radians(angle)
                point_x = center_x + radius * math.cos(rad_angle)
                point_y = center_y + radius * math.sin(rad_angle)
                points.append((point_x, point_y))
            
            points.append((center_x, center_y))
            
            if len(points) > 2:
                pygame.draw.polygon(screen, pacman_color, points)
        else:
            # Draw full circle when stopped
            pygame.draw.circle(screen, pacman_color, (center_x, center_y), radius)
        
        # Draw eye
        eye_x = center_x
        eye_y = center_y - 3
        if self.direction == 'RIGHT':
            eye_x += 2
        elif self.direction == 'LEFT':
            eye_x -= 2
        elif self.direction == 'UP':
            eye_y -= 2
        elif self.direction == 'DOWN':
            eye_y += 2
        
        # In power mode, make eyes glow red
        eye_color = (255, 0, 0) if self.power_mode else BLACK
        pygame.draw.circle(screen, eye_color, (int(eye_x), int(eye_y)), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, TILE_SIZE, TILE_SIZE)
    
    @property
    def pos(self):
        return (self.x, self.y)