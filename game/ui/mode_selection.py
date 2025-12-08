"""
Game Mode Selection Screen
Allows players to choose between Normal and Sandbox modes
"""
import pygame
from ..constants import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GREEN, BLUE, GRAY


class GameModeSelection:
    """Screen for selecting game mode (Normal vs Sandbox)"""

    def __init__(self):
        self.font = pygame.font.SysFont(None, 48)
        self.button_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.visible = False
        self._last_hover_state = False

        # Menu dimensions
        self.menu_width = 600
        self.menu_height = 500
        self.menu_x = (SCREEN_WIDTH - self.menu_width) // 2
        self.menu_y = (SCREEN_HEIGHT - self.menu_height) // 2

        # Button settings
        self.button_width = 250
        self.button_height = 60
        self.button_spacing = 30

        # Normal mode button
        self.normal_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            self.menu_y + 120,
            self.button_width,
            self.button_height
        )

        # Sandbox mode button
        self.sandbox_button = pygame.Rect(
            self.menu_x + (self.menu_width - self.button_width) // 2,
            self.menu_y + 280,
            self.button_width,
            self.button_height
        )

        # Back button
        self.back_button = pygame.Rect(
            self.menu_x + (self.menu_width - 120) // 2,
            self.menu_y + self.menu_height - 60,
            120,
            40
        )

    def show(self):
        """Show the mode selection screen"""
        self.visible = True

    def hide(self):
        """Hide the mode selection screen"""
        self.visible = False

    def handle_click(self, mouse_pos) -> str:
        """Handle mouse clicks. Returns action string."""
        if not self.visible:
            return "none"

        if self.normal_button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return "normal_mode"
        elif self.sandbox_button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return "sandbox_mode"
        elif self.back_button.collidepoint(mouse_pos):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            return "back"

        return "none"

    def draw(self, screen):
        """Draw the mode selection screen"""
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
        title_text = self.font.render("SELECT GAME MODE", True, BLACK)
        title_rect = title_text.get_rect(center=(self.menu_x + self.menu_width // 2, self.menu_y + 50))
        screen.blit(title_text, title_rect)
        
        # Check for hover and update cursor only when state changes
        mouse_pos = pygame.mouse.get_pos()
        hovering = (self.normal_button.collidepoint(mouse_pos) or 
                   self.sandbox_button.collidepoint(mouse_pos) or 
                   self.back_button.collidepoint(mouse_pos))
        
        if hovering != self._last_hover_state:
            if hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self._last_hover_state = hovering

        # Draw normal mode button with hover effect
        normal_color = (0, 200, 70) if self.normal_button.collidepoint(mouse_pos) else GREEN
        pygame.draw.rect(screen, normal_color, self.normal_button)
        pygame.draw.rect(screen, BLACK, self.normal_button, 2)

        normal_title = self.button_font.render("NORMAL MODE", True, BLACK)
        normal_rect = normal_title.get_rect(center=self.normal_button.center)
        screen.blit(normal_title, normal_rect)

        # Normal mode description
        normal_desc_lines = [
            "• Standard tower defense gameplay",
            "• Earn money by popping bloons",
            "• Limited lives - game over if lost",
            "• Progressive difficulty waves"
        ]

        for i, line in enumerate(normal_desc_lines):
            desc_text = self.small_font.render(line, True, BLACK)
            desc_rect = desc_text.get_rect(centerx=self.menu_x + self.menu_width // 2,
                                         y=self.normal_button.bottom + 15 + i * 20)
            screen.blit(desc_text, desc_rect)

        # Draw sandbox mode button with hover effect
        sandbox_color = (100, 160, 255) if self.sandbox_button.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(screen, sandbox_color, self.sandbox_button)
        pygame.draw.rect(screen, BLACK, self.sandbox_button, 2)

        sandbox_title = self.button_font.render("SANDBOX MODE", True, BLACK)
        sandbox_rect = sandbox_title.get_rect(center=self.sandbox_button.center)
        screen.blit(sandbox_title, sandbox_rect)

        # Sandbox mode description
        sandbox_desc_lines = [
            "• Unlimited money and lives",
            "• Click anywhere to spawn bloons",
            "• Test tower setups and strategies",
            "• No game over - experiment freely"
        ]

        for i, line in enumerate(sandbox_desc_lines):
            desc_text = self.small_font.render(line, True, BLACK)
            desc_rect = desc_text.get_rect(centerx=self.menu_x + self.menu_width // 2,
                                         y=self.sandbox_button.bottom + 15 + i * 20)
            screen.blit(desc_text, desc_rect)

        # Draw back button with hover effect
        back_color = (170, 170, 170) if self.back_button.collidepoint(mouse_pos) else GRAY
        pygame.draw.rect(screen, back_color, self.back_button)
        pygame.draw.rect(screen, BLACK, self.back_button, 2)

        back_text = self.button_font.render("Back", True, BLACK)
        back_rect = back_text.get_rect(center=self.back_button.center)
        screen.blit(back_text, back_rect)
