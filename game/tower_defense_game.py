"""
Main Tower Defense Game class
"""
import pygame
import json
from typing import List, Tuple, Optional

# Import game constants
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, RED,
    STARTING_MONEY, STARTING_LIVES, TOWER_COST
)

# Import game entities
from .entities.bloon import Bloon
from .entities.tower import Tower
from .entities.projectile import Projectile
from .entities.bloon_types import BloonType

# Import game systems
from .systems.wave import Wave
from .systems.game_map import GameMap
from .ui.game_ui import GameUI


class TowerDefenseGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.wave_number = 1
        self.game_over = False
        
        # Game objects
        self.load_map()
        self.bloons: List[Bloon] = []
        self.towers: List[Tower] = []
        self.projectiles: List[Projectile] = []
        
        # Wave management
        self.current_wave: Optional[Wave] = None
        self.waves = self.create_waves()
        self.wave_active = False
        
        # UI
        self.ui = GameUI()
        
    def load_map(self):
        # Default map data
        default_map = {
            "path": [
                (50, 360), (200, 360), (200, 200), (400, 200),
                (400, 500), (600, 500), (600, 300), (800, 300),
                (800, 600), (1000, 600), (1000, 200), (1230, 200)
            ],
            "spawn_point": (50, 360),
            "end_point": (1230, 200)
        }
        
        # Try to load from JSON file
        try:
            with open("maps/map1.json", "r") as f:
                map_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            map_data = default_map
            
        self.game_map = GameMap(map_data)
    
    def create_waves(self) -> List[Wave]:
        waves = []
        # Wave 1: 10 red bloons
        waves.append(Wave([BloonType.RED], [10], 800))
        # Wave 2: 15 red bloons
        waves.append(Wave([BloonType.RED], [15], 600))
        # Wave 3: 10 red, 5 blue
        waves.append(Wave([BloonType.RED, BloonType.BLUE], [10, 5], 500))
        # Wave 4: 5 red, 10 blue, 3 green
        waves.append(Wave([BloonType.RED, BloonType.BLUE, BloonType.GREEN], [5, 10, 3], 400))
        
        return waves
    
    def start_wave(self):
        if self.wave_number <= len(self.waves):
            self.current_wave = self.waves[self.wave_number - 1]
            self.wave_active = True
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.wave_active:
                    self.start_wave()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.place_tower(mouse_pos)
    
    def place_tower(self, position: Tuple[int, int]):
        if self.money >= TOWER_COST and self.game_map.can_place_tower(position):
            self.towers.append(Tower(position))
            self.money -= TOWER_COST
    
    def update(self):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Spawn bloons
        if self.wave_active and self.current_wave:
            new_bloon = self.current_wave.spawn_next_bloon(current_time, self.game_map.path)
            if new_bloon:
                self.bloons.append(new_bloon)
            
            # Check if wave is complete
            if self.current_wave.is_complete() and all(not bloon.alive or bloon.reached_end for bloon in self.bloons):
                self.wave_active = False
                self.wave_number += 1
                # Clear dead bloons
                self.bloons = [bloon for bloon in self.bloons if bloon.alive and not bloon.reached_end]
        
        # Update bloons
        for bloon in self.bloons[:]:
            bloon.update()
            if bloon.reached_end:
                self.lives -= 1
                self.bloons.remove(bloon)
                if self.lives <= 0:
                    self.game_over = True
        
        # Update towers and create projectiles
        for tower in self.towers:
            projectile = tower.update(self.bloons, current_time)
            if projectile:
                self.projectiles.append(projectile)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.alive:
                self.projectiles.remove(projectile)
        
        # Remove dead bloons and award money
        for bloon in self.bloons[:]:
            if not bloon.alive:
                self.money += bloon.reward
                self.bloons.remove(bloon)
    
    def draw(self):
        # Draw map
        self.game_map.draw(self.screen)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw bloons
        for bloon in self.bloons:
            bloon.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self.ui.draw(self.screen, self.money, self.lives, self.wave_number)
        
        # Draw game over screen
        if self.game_over:
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
        # Draw wave start hint
        if not self.wave_active and self.wave_number <= len(self.waves) and not self.game_over:
            hint_text = pygame.font.SysFont(None, 36).render("Press SPACE to start next wave", True, WHITE)
            text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(hint_text, text_rect)
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Don't quit pygame, just close the game window
        pygame.display.quit()


def main():
    game = TowerDefenseGame()
    game.run()


if __name__ == "__main__":
    main()
