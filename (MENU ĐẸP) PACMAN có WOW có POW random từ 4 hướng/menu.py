import pygame
import math
import random
from settings import *
from levels import LEVELS

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.selected_level = 1
        self.max_level = len(LEVELS)
        
        # Animation variables
        self.time = 0
        self.pulse_offset = 0
        self.floating_dots = []
        self.ghost_animation_time = 0
        
        # Particle system
        self.particles = []
        
        # Initialize floating dots
        for i in range(20):
            self.floating_dots.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'speed': random.uniform(0.5, 2.0),
                'size': random.randint(2, 6),
                'color': random.choice([YELLOW, WHITE, CYAN, PINK])
            })
        
        # Initialize particles
        for i in range(50):
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'life': random.uniform(0.5, 1.0),
                'max_life': random.uniform(0.5, 1.0),
                'size': random.randint(1, 3)
            })

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_level = max(1, self.selected_level - 1)
                self.create_selection_particles()
            elif event.key == pygame.K_DOWN:
                self.selected_level = min(self.max_level, self.selected_level + 1)
                self.create_selection_particles()
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self.create_start_particles()
                return self.selected_level
            elif event.key == pygame.K_ESCAPE:
                return "quit"
        return None

    def create_selection_particles(self):
        """Create particles when selection changes"""
        for i in range(10):
            self.particles.append({
                'x': SCREEN_WIDTH // 2 + random.randint(-100, 100),
                'y': 220 + (self.selected_level - 1) * 80 + random.randint(-20, 20),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 1.0,
                'max_life': 1.0,
                'size': random.randint(2, 5)
            })

    def create_start_particles(self):
        """Create explosion particles when starting game"""
        for i in range(30):
            angle = (i / 30) * 2 * math.pi
            speed = random.uniform(3, 8)
            self.particles.append({
                'x': SCREEN_WIDTH // 2,
                'y': 220 + (self.selected_level - 1) * 80,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.5,
                'max_life': 1.5,
                'size': random.randint(3, 8)
            })

    def update(self):
        self.time += 0.05
        self.ghost_animation_time += 1
        
        # Update floating dots
        for dot in self.floating_dots:
            dot['y'] += dot['speed']
            if dot['y'] > SCREEN_HEIGHT + 10:
                dot['y'] = -10
                dot['x'] = random.randint(0, SCREEN_WIDTH)
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 0.02
            particle['vy'] += 0.1  # Gravity
            
            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_background_effects(self):
        """Draw animated background effects"""
        # Draw floating dots
        for dot in self.floating_dots:
            alpha = int(128 + 127 * math.sin(self.time + dot['x'] * 0.01))
            color = (*dot['color'][:3], alpha) if len(dot['color']) == 3 else dot['color']
            
            # Create surface for alpha blending
            dot_surface = pygame.Surface((dot['size'] * 2, dot['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surface, color, (dot['size'], dot['size']), dot['size'])
            self.screen.blit(dot_surface, (dot['x'] - dot['size'], dot['y'] - dot['size']))
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * (particle['life'] / particle['max_life']))
                size = int(particle['size'] * (particle['life'] / particle['max_life']))
                
                if size > 0:
                    particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                    color = YELLOW  # Remove alpha channel for pygame.draw.circle
                    pygame.draw.circle(particle_surface, color, (size, size), size)
                    particle_surface.set_alpha(alpha)  # Set alpha for entire surface
                    self.screen.blit(particle_surface, (particle['x'] - size, particle['y'] - size))

    def draw_animated_ghosts(self):
        """Draw animated ghosts around the screen"""
        ghost_colors = [RED, PINK, CYAN, ORANGE]
        
        for i, color in enumerate(ghost_colors):
            # Calculate position in circular motion
            angle = (self.ghost_animation_time * 0.02) + (i * math.pi / 2)
            radius = 150
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            # Draw ghost body
            ghost_size = 30
            body_rect = pygame.Rect(int(x - ghost_size/2), int(y - ghost_size/2), ghost_size, ghost_size)
            
            # Add glow effect
            glow_surface = pygame.Surface((ghost_size + 20, ghost_size + 20), pygame.SRCALPHA)
            glow_color = (*color[:3], 50)
            pygame.draw.circle(glow_surface, glow_color, (ghost_size//2 + 10, ghost_size//2 + 10), ghost_size//2 + 10)
            self.screen.blit(glow_surface, (x - ghost_size/2 - 10, y - ghost_size/2 - 10))
            
            # Draw main ghost body
            pygame.draw.rect(self.screen, color, body_rect)
            
            # Draw eyes
            eye_size = 4
            left_eye_x = int(x - 8)
            left_eye_y = int(y - 5)
            right_eye_x = int(x + 8)
            right_eye_y = int(y - 5)
            
            pygame.draw.circle(self.screen, WHITE, (left_eye_x, left_eye_y), eye_size)
            pygame.draw.circle(self.screen, WHITE, (right_eye_x, right_eye_y), eye_size)
            pygame.draw.circle(self.screen, BLACK, (left_eye_x, left_eye_y), 2)
            pygame.draw.circle(self.screen, BLACK, (right_eye_x, right_eye_y), 2)

    def draw_pacman_animation(self):
        """Draw animated Pacman at the top"""
        # Pacman position (moving across top)
        pacman_x = (self.time * 100) % (SCREEN_WIDTH + 100) - 50
        pacman_y = 50
        
        # Only draw if on screen
        if -50 < pacman_x < SCREEN_WIDTH + 50:
            radius = 25
            
            # Calculate mouth opening
            mouth_opening = abs(math.sin(self.time * 5)) * 0.8 + 0.2
            
            # Draw Pacman body with glow
            glow_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            glow_color = (*YELLOW[:3], 100)
            pygame.draw.circle(glow_surface, glow_color, (radius * 2, radius * 2), radius + 10)
            self.screen.blit(glow_surface, (pacman_x - radius * 2, pacman_y - radius * 2))
            
            # Draw Pacman with mouth animation
            start_angle = mouth_opening
            end_angle = 2 * math.pi - mouth_opening
            
            # Create points for the pac-man shape
            points = [(pacman_x, pacman_y)]
            
            # Add arc points
            for angle in range(int(math.degrees(end_angle)), int(math.degrees(start_angle + 2 * math.pi)), 5):
                if angle > 360:
                    angle -= 360
                rad_angle = math.radians(angle)
                point_x = pacman_x + radius * math.cos(rad_angle)
                point_y = pacman_y + radius * math.sin(rad_angle)
                points.append((point_x, point_y))
            
            if len(points) > 2:
                pygame.draw.polygon(self.screen, YELLOW, points)
            
            # Draw eye
            eye_x = pacman_x
            eye_y = pacman_y - 8
            pygame.draw.circle(self.screen, BLACK, (int(eye_x), int(eye_y)), 3)

    def draw_glowing_text(self, text, font, x, y, base_color, glow_color=None):
        """Draw text with a glowing effect"""
        if glow_color is None:
            glow_color = base_color
        
        # Create glow effect
        for offset in range(5, 0, -1):
            alpha = 50 - (offset * 8)
            if alpha > 0:
                glow_surface = font.render(text, True, glow_color)
                glow_surface.set_alpha(alpha)
                
                # Draw glow in multiple directions
                for dx in [-offset, 0, offset]:
                    for dy in [-offset, 0, offset]:
                        if dx != 0 or dy != 0:
                            self.screen.blit(glow_surface, (x + dx, y + dy))
        
        # Draw main text
        text_surface = font.render(text, True, base_color)
        self.screen.blit(text_surface, (x, y))
        
        return text_surface.get_rect(topleft=(x, y))

    def draw(self):
        # Create gradient background
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(10 + (30 - 10) * color_ratio)
            g = int(10 + (20 - 10) * color_ratio)
            b = int(50 + (80 - 50) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw background effects
        self.draw_background_effects()
        
        # Draw animated elements
        self.draw_pacman_animation()
        self.draw_animated_ghosts()
        
        # Draw title with pulsing effect
        pulse = abs(math.sin(self.time)) * 0.3 + 0.7
        title_color = (int(255 * pulse), int(255 * pulse), 0)
        
        title_text = "PAC-MAN"
        title_width = self.font_title.size(title_text)[0]
        title_x = (SCREEN_WIDTH - title_width) // 2
        title_y = 120
        
        # Draw title with rainbow effect
        for i, char in enumerate(title_text):
            char_color = [
                int(255 * abs(math.sin(self.time + i * 0.5))),
                int(255 * abs(math.sin(self.time + i * 0.5 + 2))),
                int(255 * abs(math.sin(self.time + i * 0.5 + 4)))
            ]
            char_surface = self.font_title.render(char, True, char_color)
            char_width = char_surface.get_width()
            self.draw_glowing_text(char, self.font_title, title_x, title_y, char_color)
            title_x += char_width
        
        # Draw subtitle
        subtitle_y = 200
        self.draw_glowing_text("AI GHOST DEV BY LE VAN HUNG", self.font_medium, 
                             (SCREEN_WIDTH - self.font_medium.size("AI GHOST DEV BY LE VAN HUNG")[0]) // 2, 
                             subtitle_y, WHITE, CYAN)
        
        # Draw level selection
        selection_start_y = 280  # Moved up slightly to fit all 5 levels
        for level_num in range(1, self.max_level + 1):
            level_data = LEVELS[level_num]
            y_pos = selection_start_y + (level_num - 1) * 65  # Reduced spacing from 80 to 65
            
            # Create selection glow effect
            if level_num == self.selected_level:
                # Draw selection background with animated border
                selection_width = 400  # Reduced width to center better
                selection_height = 50  
                selection_x = (SCREEN_WIDTH - selection_width) // 2
                selection_y = y_pos - 12  
                
                # Animated border
                border_pulse = abs(math.sin(self.time * 3)) * 100 + 155
                border_color = (int(border_pulse), int(border_pulse/2), int(border_pulse))
                
                # Draw multiple border layers for glow effect
                for thickness in range(6, 0, -1):  
                    alpha = 30 + (6 - thickness) * 15
                    border_surface = pygame.Surface((selection_width + thickness * 2, 
                                                  selection_height + thickness * 2), pygame.SRCALPHA)
                    border_rect = pygame.Rect(0, 0, selection_width + thickness * 2, 
                                            selection_height + thickness * 2)
                    pygame.draw.rect(border_surface, (*border_color, alpha), border_rect, thickness)
                    self.screen.blit(border_surface, (selection_x - thickness, selection_y - thickness))
                
                # Draw selection background
                bg_surface = pygame.Surface((selection_width, selection_height), pygame.SRCALPHA)
                bg_rect = pygame.Rect(0, 0, selection_width, selection_height)
                pygame.draw.rect(bg_surface, (50, 50, 100, 150), bg_rect)
                self.screen.blit(bg_surface, (selection_x, selection_y))
                
                text_color = YELLOW
                glow_color = ORANGE
            else:
                text_color = WHITE
                glow_color = CYAN
            
            # Draw level text (centered without considering dots)
            level_text = f"LEVEL {level_num}"
            if level_data['name']:
                level_text += f" - {level_data['name']}"
            
            text_width = self.font_medium.size(level_text)[0]
            text_x = (SCREEN_WIDTH - text_width) // 2
            
            self.draw_glowing_text(level_text, self.font_medium, text_x, y_pos, text_color, glow_color)
            
            # Draw difficulty indicators based on ghost_speed (positioned after text)
            difficulty_x = text_x + text_width + 20
            ghost_speed = level_data.get('ghost_speed', 1.0)
            red_dots = int(ghost_speed * 10)  # Direct mapping: 1.3 * 10 = 13 red dots
            
            for i in range(16):
                dot_color = RED if i < red_dots else (50, 50, 50)
                pygame.draw.circle(self.screen, dot_color, (difficulty_x + i * 8, y_pos + 15), 3)
        
        # Draw instruction text directly below level 5 (no panel background)
        instruction_y = selection_start_y + 4 * 65 + 70  # Right below level 5
        instruction_text = "THE NUMBER OF RED BALLS CORRESPONDS TO THE SPEED LEVEL OF GHOST AI"
        
        # Use smaller font
        small_font = pygame.font.Font(None, 18)
        text_surface = small_font.render(instruction_text, True, WHITE)
        
        # Center the text
        text_x = (SCREEN_WIDTH - text_surface.get_width()) // 2
        self.screen.blit(text_surface, (text_x, instruction_y))