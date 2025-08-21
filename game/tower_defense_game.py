"""
Main Tower Defense Game class
"""
import pygame
import json
import subprocess
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
from .ui.pause_menu import PauseMenu, SettingsIcon, SettingsMenu


def get_git_commit_hash():
    """Get the current git commit hash (short version)"""
    try:
        result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                              capture_output=True, text=True, cwd='.')
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_window_title():
    """Get the window title with git commit hash"""
    commit_hash = get_git_commit_hash()
    return f"Tower Defense Game - git-{commit_hash}"


class TowerDefenseGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(get_window_title())
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game state
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.wave_number = 1
        self.game_over = False
        self.paused = False
        
        # Settings
        self.auto_start_rounds = False
        self.auto_start_delay = 3000  # 3 seconds delay before auto start
        self.wave_completed_time = 0  # Track when wave was completed
        
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
        self.pause_menu = PauseMenu()
        self.settings_menu = SettingsMenu()
        self.settings_icon = SettingsIcon()
        self.current_menu = "none"  # Track which menu is open: "none", "pause", "settings"
        
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
                if event.key == pygame.K_ESCAPE:
                    if self.current_menu == "settings":
                        self.settings_menu.hide()
                        self.pause_menu.show()
                        self.current_menu = "pause"
                    elif self.current_menu == "pause":
                        self.pause_menu.hide()
                        self.current_menu = "none"
                        self.paused = False
                    else:
                        self.pause_menu.show()
                        self.current_menu = "pause"
                        self.paused = True
                elif event.key == pygame.K_SPACE and not self.wave_active and not self.paused:
                    self.start_wave()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    
                    # Handle settings menu clicks
                    if self.current_menu == "settings":
                        action = self.settings_menu.handle_click(mouse_pos)
                        if action == "back":
                            self.settings_menu.hide()
                            self.pause_menu.show()
                            self.current_menu = "pause"
                        elif action == "toggle_auto_start":
                            self.auto_start_rounds = self.settings_menu.auto_start_rounds
                    # Handle pause menu clicks
                    elif self.current_menu == "pause":
                        action = self.pause_menu.handle_click(mouse_pos)
                        if action == "resume":
                            self.pause_menu.hide()
                            self.current_menu = "none"
                            self.paused = False
                        elif action == "settings":
                            self.pause_menu.hide()
                            self.settings_menu.show()
                            self.settings_menu.auto_start_rounds = self.auto_start_rounds
                            self.current_menu = "settings"
                        elif action == "main_menu":
                            self.running = False
                            return # Exit to main menu
                        elif action == "quit":
                            pygame.quit()
                            exit()
                    # Handle settings icon click
                    elif self.settings_icon.is_clicked(mouse_pos):
                        self.pause_menu.show()
                        self.current_menu = "pause"
                        self.paused = True
                    # Handle tower placement (only when not paused)
                    elif not self.paused:
                        self.place_tower(mouse_pos)
    
    def place_tower(self, position: Tuple[int, int]):
        if self.money >= TOWER_COST and self.game_map.can_place_tower(position):
            self.towers.append(Tower(position))
            self.money -= TOWER_COST
    
    def update(self):
        if self.game_over or self.paused:
            return
            
        current_time = pygame.time.get_ticks()
        
        # Auto start rounds logic
        if (not self.wave_active and self.auto_start_rounds and 
            self.wave_completed_time > 0 and 
            current_time - self.wave_completed_time >= self.auto_start_delay and
            self.wave_number <= len(self.waves)):
            self.start_wave()
            self.wave_completed_time = 0
        
        # Spawn bloons
        if self.wave_active and self.current_wave:
            new_bloon = self.current_wave.spawn_next_bloon(current_time, self.game_map.path)
            if new_bloon:
                self.bloons.append(new_bloon)
            
            # Check if wave is complete
            if self.current_wave.is_complete() and all(not bloon.alive or bloon.reached_end for bloon in self.bloons):
                self.wave_active = False
                self.wave_number += 1
                self.wave_completed_time = current_time  # Record when wave was completed
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
        self.ui.draw(self.screen, self.money, self.lives, self.wave_number, self.paused)
        
        # Draw settings icon (always visible, not when game over)
        if not self.game_over:
            self.settings_icon.draw(self.screen)
        
        # Draw game over screen
        if self.game_over:
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
        # Draw wave start hint or auto start countdown
        if not self.wave_active and self.wave_number <= len(self.waves) and not self.game_over and not self.paused:
            current_time = pygame.time.get_ticks()
            if self.auto_start_rounds and self.wave_completed_time > 0:
                # Show countdown for auto start
                time_remaining = self.auto_start_delay - (current_time - self.wave_completed_time)
                if time_remaining > 0:
                    seconds_remaining = int(time_remaining / 1000) + 1
                    hint_text = pygame.font.SysFont(None, 36).render(f"Next wave starts in {seconds_remaining} seconds", True, WHITE)
                    text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(hint_text, text_rect)
                    
                    # Show manual override hint
                    override_text = pygame.font.SysFont(None, 24).render("Press SPACE to start immediately", True, WHITE)
                    override_rect = override_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
                    self.screen.blit(override_text, override_rect)
                else:
                    hint_text = pygame.font.SysFont(None, 36).render("Starting next wave...", True, WHITE)
                    text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(hint_text, text_rect)
            else:
                # Show manual start hint
                hint_text = pygame.font.SysFont(None, 36).render("Press SPACE to start next wave", True, WHITE)
                text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                self.screen.blit(hint_text, text_rect)
        
        # Draw menus (always last to appear on top)
        if self.current_menu == "pause":
            self.pause_menu.draw(self.screen)
        elif self.current_menu == "settings":
            self.settings_menu.draw(self.screen)
        
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
