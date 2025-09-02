"""
Game UI system for displaying HUD elements
"""
import pygame
from ..constants import WHITE, SCREEN_HEIGHT


class GameUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
    def draw(self, screen, money: int, lives: int, wave_number: int, paused: bool = False):
        """Draw the game UI elements.

        Args:
            screen (pygame.Surface): The surface to draw the UI on.
            money (int): The current amount of money.
            lives (int): The current number of lives.
            wave_number (int): The current wave number.
            paused (bool, optional): Whether the game is paused. Defaults to False.
        """
        # Draw money
        money_text = self.font.render(f"Money: ${money}", True, WHITE)
        screen.blit(money_text, (10, 40))
        
        # Draw lives
        lives_text = self.font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 80))
        
        # Draw wave
        wave_text = self.font.render(f"Wave: {wave_number}", True, WHITE)
        screen.blit(wave_text, (10, 120))
        
        # Draw pause indicator
        if paused:
            pause_text = self.font.render("PAUSED", True, (255, 255, 0))
            screen.blit(pause_text, (10, 160))
        
        # Draw controls hint (moved down to replace tower placement hint)
        controls_text = self.small_font.render("ESC: Pause | T: Toggle Towers | Right Click: Deselect | Click gear icon: Settings", True, WHITE)
        screen.blit(controls_text, (10, SCREEN_HEIGHT - 30))
