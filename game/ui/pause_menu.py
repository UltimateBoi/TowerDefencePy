"""
Pause menu and settings UI for the game
"""
import pygame
from ..constants import WHITE, BLACK, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT


class PauseMenu:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.visible = False
        
        # Menu dimensions
        self.menu_width = 400
        self.menu_height = 300
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Button settings
        self.button_width = 200
        self.button_height = 50
        self.button_spacing = 20
        
        # Calculate button positions
        button_start_y = self.menu_y + 100
        self.resume_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y,
            self.button_width,
            self.button_height
        )
        
        self.main_menu_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y + self.button_height + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        self.quit_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y + 2 * (self.button_height + self.button_spacing),
            self.button_width,
            self.button_height
        )
        
    def show(self):
        """Show the pause menu"""
        self.visible = True
        
    def hide(self):
        """Hide the pause menu"""
        self.visible = False
        
    def toggle(self):
        """Toggle pause menu visibility"""
        self.visible = not self.visible
        
    def handle_click(self, mouse_pos) -> str:
        """Handle mouse clicks on menu buttons. Returns action string."""
        if not self.visible:
            return "none"
            
        if self.resume_button.collidepoint(mouse_pos):
            return "resume"
        elif self.main_menu_button.collidepoint(mouse_pos):
            return "main_menu"
        elif self.quit_button.collidepoint(mouse_pos):
            return "quit"
        
        return "none"
    
    def draw(self, screen):
        """Draw the pause menu"""
        if not self.visible:
            return
            
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw menu background
        menu_rect = pygame.Rect(self.menu_x, self.menu_y, self.menu_width, self.menu_height)
        pygame.draw.rect(screen, WHITE, menu_rect)
        pygame.draw.rect(screen, BLACK, menu_rect, 3)
        
        # Draw title
        title_text = self.font.render("PAUSED", True, BLACK)
        title_rect = title_text.get_rect(center=(self.menu_x + self.menu_width // 2, self.menu_y + 40))
        screen.blit(title_text, title_rect)
        
        # Draw buttons
        self._draw_button(screen, self.resume_button, "Resume", (100, 200, 100))
        self._draw_button(screen, self.main_menu_button, "Main Menu", (200, 200, 100))
        self._draw_button(screen, self.quit_button, "Quit Game", (200, 100, 100))
        
    def _draw_button(self, screen, button_rect, text, color):
        """Draw a button with text"""
        # Draw button background
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        
        # Draw button text
        text_surface = self.button_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)


class SettingsIcon:
    def __init__(self):
        self.size = 40
        self.x = SCREEN_WIDTH - self.size - 10
        self.y = 10
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
    def draw(self, screen):
        """Draw the settings gear icon"""
        # Draw gear background
        pygame.draw.circle(screen, GRAY, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)
        pygame.draw.circle(screen, BLACK, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2, 2)
        
        # Draw gear teeth (simplified)
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        
        # Draw inner circle
        pygame.draw.circle(screen, WHITE, (center_x, center_y), self.size // 4)
        pygame.draw.circle(screen, BLACK, (center_x, center_y), self.size // 4, 1)
        
        # Draw gear teeth as small rectangles
        tooth_width = 4
        tooth_height = 8
        for i in range(8):
            angle = i * 45  # 8 teeth, 45 degrees apart
            import math
            x = center_x + (self.size // 2 - tooth_height // 2) * math.cos(math.radians(angle))
            y = center_y + (self.size // 2 - tooth_height // 2) * math.sin(math.radians(angle))
            
            tooth_rect = pygame.Rect(x - tooth_width // 2, y - tooth_height // 2, tooth_width, tooth_height)
            pygame.draw.rect(screen, BLACK, tooth_rect)
    
    def is_clicked(self, mouse_pos) -> bool:
        """Check if the settings icon was clicked"""
        return self.rect.collidepoint(mouse_pos)
