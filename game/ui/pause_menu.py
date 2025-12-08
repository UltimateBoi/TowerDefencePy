"""
Pause menu and settings UI for the game
"""
import pygame
from ..constants import WHITE, BLACK, GRAY, SCREEN_WIDTH, SCREEN_HEIGHT


class SettingsMenu:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 32)
        self.label_font = pygame.font.SysFont(None, 36)
        self.visible = False
        
        # Settings state
        self.auto_start_rounds = False
        self.drag_drop_placement = False # False = click to place, True = drag and drop
        self.show_fps = False
        
        # Menu dimensions
        self.menu_width = 600
        self.menu_height = 600 # Increased height for new setting
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2
        
        # Button settings
        self.button_width = 120
        self.button_height = 40
        self.toggle_size = 20
        
        # Auto start setting position
        self.auto_start_label_x = self.menu_x + 30
        self.auto_start_label_y = self.menu_y + 100
        self.auto_start_toggle_x = self.menu_x + self.menu_width - 80
        self.auto_start_toggle_y = self.auto_start_label_y + 5
        
        # Placement mode setting position
        self.placement_label_x = self.menu_x + 30
        self.placement_label_y = self.menu_y + 160
        self.placement_toggle_x = self.menu_x + self.menu_width - 80
        self.placement_toggle_y = self.placement_label_y + 5
        
        # FPS counter setting position
        self.fps_label_x = self.menu_x + 30
        self.fps_label_y = self.menu_y + 220
        self.fps_toggle_x = self.menu_x + self.menu_width - 80
        self.fps_toggle_y = self.fps_label_y + 5
        
        # Back button
        self.back_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            self.menu_y + self.menu_height - 80,
            self.button_width,
            self.button_height
        )
        
    def show(self):
        """Show the settings menu"""
        self.visible = True
        
    def hide(self):
        """Hide the settings menu"""
        self.visible = False
        
    def handle_click(self, mouse_pos) -> str:
        """Handle mouse clicks on settings. Returns action string."""
        if not self.visible:
            return "none"
            
        # Check auto start toggle
        auto_toggle_rect = pygame.Rect(
            self.auto_start_toggle_x, self.auto_start_toggle_y,
            self.toggle_size, self.toggle_size
        )
        if auto_toggle_rect.collidepoint(mouse_pos):
            self.auto_start_rounds = not self.auto_start_rounds
            return "toggle_auto_start"
        
        # Check placement mode toggle
        placement_toggle_rect = pygame.Rect(
            self.placement_toggle_x, self.placement_toggle_y,
            self.toggle_size, self.toggle_size
        )
        if placement_toggle_rect.collidepoint(mouse_pos):
            self.drag_drop_placement = not self.drag_drop_placement
            return "toggle_placement_mode"
        
        # Check FPS counter toggle
        fps_toggle_rect = pygame.Rect(
            self.fps_toggle_x, self.fps_toggle_y,
            self.toggle_size, self.toggle_size
        )
        if fps_toggle_rect.collidepoint(mouse_pos):
            self.show_fps = not self.show_fps
            return "toggle_fps_counter"
            
        # Check back button
        if self.back_button.collidepoint(mouse_pos):
            return "back"
        
        return "none"
    
    def draw(self, screen):
        """Draw the settings menu"""
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
        title_text = self.font.render("SETTINGS", True, BLACK)
        title_rect = title_text.get_rect(center=(self.menu_x + self.menu_width // 2, self.menu_y + 40))
        screen.blit(title_text, title_rect)
        
        # Draw auto start setting
        auto_start_text = self.label_font.render("Auto Start Rounds:", True, BLACK)
        screen.blit(auto_start_text, (self.auto_start_label_x, self.auto_start_label_y))
        
        # Draw toggle checkbox
        toggle_rect = pygame.Rect(
            self.auto_start_toggle_x, self.auto_start_toggle_y,
            self.toggle_size, self.toggle_size
        )
        pygame.draw.rect(screen, WHITE, toggle_rect)
        pygame.draw.rect(screen, BLACK, toggle_rect, 2)
        
        if self.auto_start_rounds:
            # Draw checkmark
            pygame.draw.line(screen, (0, 150, 0), 
                           (self.auto_start_toggle_x + 4, self.auto_start_toggle_y + 10),
                           (self.auto_start_toggle_x + 8, self.auto_start_toggle_y + 14), 3)
            pygame.draw.line(screen, (0, 150, 0),
                           (self.auto_start_toggle_x + 8, self.auto_start_toggle_y + 14),
                           (self.auto_start_toggle_x + 16, self.auto_start_toggle_y + 6), 3)
        
        # Draw setting description
        desc_text = self.button_font.render("Automatically start the next wave when ready", True, GRAY)
        screen.blit(desc_text, (self.auto_start_label_x, self.auto_start_label_y + 30))
        
        # Draw placement mode setting
        placement_text = self.label_font.render("Tower Placement Mode:", True, BLACK)
        screen.blit(placement_text, (self.placement_label_x, self.placement_label_y))
        
        # Draw placement mode toggle checkbox
        placement_toggle_rect = pygame.Rect(
            self.placement_toggle_x, self.placement_toggle_y,
            self.toggle_size, self.toggle_size
        )
        pygame.draw.rect(screen, WHITE, placement_toggle_rect)
        pygame.draw.rect(screen, BLACK, placement_toggle_rect, 2)
        
        if self.drag_drop_placement:
            # Draw checkmark
            pygame.draw.line(screen, (0, 150, 0), 
                           (self.placement_toggle_x + 4, self.placement_toggle_y + 10),
                           (self.placement_toggle_x + 8, self.placement_toggle_y + 14), 3)
            pygame.draw.line(screen, (0, 150, 0),
                           (self.placement_toggle_x + 8, self.placement_toggle_y + 14),
                           (self.placement_toggle_x + 16, self.placement_toggle_y + 6), 3)
        
        # Draw placement mode description
        mode_text = "Drag and Drop" if self.drag_drop_placement else "Click to Place"
        placement_desc_text = self.button_font.render(f"Current mode: {mode_text}", True, GRAY)
        screen.blit(placement_desc_text, (self.placement_label_x, self.placement_label_y + 30))
        
        # Draw FPS counter setting
        fps_text = self.label_font.render("Show FPS Counter:", True, BLACK)
        screen.blit(fps_text, (self.fps_label_x, self.fps_label_y))
        
        # Draw FPS toggle checkbox
        fps_toggle_rect = pygame.Rect(
            self.fps_toggle_x, self.fps_toggle_y,
            self.toggle_size, self.toggle_size
        )
        pygame.draw.rect(screen, WHITE, fps_toggle_rect)
        pygame.draw.rect(screen, BLACK, fps_toggle_rect, 2)
        
        if self.show_fps:
            # Draw checkmark
            pygame.draw.line(screen, (0, 150, 0), 
                           (self.fps_toggle_x + 4, self.fps_toggle_y + 10),
                           (self.fps_toggle_x + 8, self.fps_toggle_y + 14), 3)
            pygame.draw.line(screen, (0, 150, 0),
                           (self.fps_toggle_x + 8, self.fps_toggle_y + 14),
                           (self.fps_toggle_x + 16, self.fps_toggle_y + 6), 3)
        
        # Draw FPS description
        fps_desc_text = self.button_font.render("Display frames per second in top-right corner", True, GRAY)
        screen.blit(fps_desc_text, (self.fps_label_x, self.fps_label_y + 30))
        
        # Draw back button
        self._draw_button(screen, self.back_button, "Back", (150, 150, 150))
        
    def _draw_button(self, screen, button_rect, text, color):
        """Draw a button with text"""
        # Draw button background
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)
        
        # Draw button text
        text_surface = self.button_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)


class PauseMenu:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.visible = False
        
        # Menu dimensions
        self.menu_width = 400
        self.menu_height = 400 # Expanded from 350 to 400
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
        
        self.settings_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y + self.button_height + self.button_spacing,
            self.button_width,
            self.button_height
        )
        
        self.main_menu_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y + 2 * (self.button_height + self.button_spacing),
            self.button_width,
            self.button_height
        )
        
        self.quit_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            button_start_y + 3 * (self.button_height + self.button_spacing),
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
        elif self.settings_button.collidepoint(mouse_pos):
            return "settings"
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
        self._draw_button(screen, self.settings_button, "Settings", (100, 150, 200))
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
            angle = i * 45 # 8 teeth, 45 degrees apart
            import math
            x = center_x + (self.size // 2 - tooth_height // 2) * math.cos(math.radians(angle))
            y = center_y + (self.size // 2 - tooth_height // 2) * math.sin(math.radians(angle))
            
            tooth_rect = pygame.Rect(x - tooth_width // 2, y - tooth_height // 2, tooth_width, tooth_height)
            pygame.draw.rect(screen, BLACK, tooth_rect)
    
    def is_clicked(self, mouse_pos) -> bool:
        """Check if the settings icon was clicked"""
        return self.rect.collidepoint(mouse_pos)
