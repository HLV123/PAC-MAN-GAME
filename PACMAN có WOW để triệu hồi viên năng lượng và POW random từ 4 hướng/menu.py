import pygame
from settings import *
from levels import LEVELS

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        self.selected_level = 1
        self.max_level = len(LEVELS)

    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_level = max(1, self.selected_level - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_level = min(self.max_level, self.selected_level + 1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.selected_level
            elif event.key == pygame.K_ESCAPE:
                return "quit"
        return None

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BLACK)
        
        title_text = self.font_large.render("PAC-MAN GAME", True, YELLOW)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.font_medium.render("Select Level", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 160))
        self.screen.blit(subtitle_text, subtitle_rect)

        start_y = 220
        for level_num in range(1, self.max_level + 1):
            level_data = LEVELS[level_num]
            y_pos = start_y + (level_num - 1) * 60
            
            if level_num == self.selected_level:
                selection_rect = pygame.Rect(150, y_pos - 10, SCREEN_WIDTH - 300, 50)
                pygame.draw.rect(self.screen, (50, 50, 100), selection_rect)
                text_color = YELLOW
            else:
                text_color = WHITE

            level_text = f"LEVEL {level_num} {level_data['name']}"
            level_surface = self.font_small.render(level_text, True, text_color)
            text_rect = level_surface.get_rect(center=(SCREEN_WIDTH//2, y_pos + 10))
            self.screen.blit(level_surface, text_rect)

        instructions = [
            "Use UP/DOWN to select",
            "Press ENTER to start",
            "Press ESC to quit"
        ]
        
        for i, instruction in enumerate(instructions):
            inst_surface = self.font_small.render(instruction, True, WHITE)
            inst_rect = inst_surface.get_rect(center=(SCREEN_WIDTH//2, 520 + i * 30))
            self.screen.blit(inst_surface, inst_rect)