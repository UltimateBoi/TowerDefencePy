"""
Game UI system for displaying HUD elements
"""
import pygame
from ..constants import WHITE, SCREEN_HEIGHT


class GameUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
    def draw(self, screen, money: int, lives: int, wave_number: int):
        # Draw money
        money_text = self.font.render(f"Money: ${money}", True, WHITE)
        screen.blit(money_text, (10, 10))
        
        # Draw lives
        lives_text = self.font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        
        # Draw wave
        wave_text = self.font.render(f"Wave: {wave_number}", True, WHITE)
        screen.blit(wave_text, (10, 90))
        
        # Draw tower placement hint
        hint_text = self.small_font.render("Click to place tower ($10)", True, WHITE)
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))
