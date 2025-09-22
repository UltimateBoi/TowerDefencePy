"""
Main Tower Defense Game class
"""
import pygame
import json
import subprocess
import math
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
from .ui.ingame_upgrade_panel import InGameUpgradePanel
from .ui.tower_selection_panel import TowerSelectionPanel
from .ui.mode_selection import GameModeSelection


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
        
        # Performance optimizations - cache fonts
        self.cached_fonts = {
            'large': pygame.font.SysFont(None, 72),
            'medium': pygame.font.SysFont(None, 36),
            'small': pygame.font.SysFont(None, 24)
        }
        
        # Game state
        self.money = STARTING_MONEY
        self.lives = STARTING_LIVES
        self.wave_number = 1
        self.game_over = False
        self.paused = False
        
        # Settings
        self.auto_start_rounds = False
        self.auto_start_delay = 3000 # 3 seconds delay before auto start
        self.wave_completed_time = 0 # Track when wave was completed
        self.show_fps = False
        
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
        self.mode_selection = GameModeSelection()
        
        # Tower selection and upgrade system
        self.selected_tower: Optional[Tower] = None
        self.upgrade_panel = InGameUpgradePanel(SCREEN_WIDTH - 320, 100)
        self.tower_selection_panel = TowerSelectionPanel()
        self.settings_icon = SettingsIcon()
        self.current_menu = "none" # Track which menu is open: "none", "pause", "settings", "mode_selection"
        
        # Game mode settings
        self.game_mode = "normal" # "normal" or "sandbox"
        self.sandbox_mode = False
        self.sandbox_bloon_type = BloonType.RED # Default bloon type for sandbox spawning
        
        # Drag and drop state
        self.dragging_tower = False
        self.drag_start_pos = None
        
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
                elif event.key == pygame.K_t and not self.paused:
                    # Toggle tower selection panel visibility
                    self.tower_selection_panel.visible = not self.tower_selection_panel.visible
                elif event.key == pygame.K_b and self.sandbox_mode and not self.paused:
                    # Cycle through bloon types in sandbox mode
                    bloon_types = [BloonType.RED, BloonType.BLUE, BloonType.GREEN, BloonType.YELLOW]
                    current_index = bloon_types.index(self.sandbox_bloon_type)
                    self.sandbox_bloon_type = bloon_types[(current_index + 1) % len(bloon_types)]
                elif event.key == pygame.K_TAB and not self.paused:
                    # Cycle targeting mode for selected tower
                    if self.selected_tower:
                        self.selected_tower.cycle_targeting_mode()
                elif event.key == pygame.K_DELETE and not self.paused:
                    # Sell selected tower (DELETE key)
                    if self.selected_tower:
                        self.sell_tower(self.selected_tower)
                        self.selected_tower = None
                elif event.key == pygame.K_x and not self.paused:
                    # Sell selected tower (X key, like BTD6)
                    if self.selected_tower:
                        self.sell_tower(self.selected_tower)
                        self.selected_tower = None
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if event.button == 1: # Left click
                    # Handle settings menu clicks
                    if self.current_menu == "settings":
                        action = self.settings_menu.handle_click(mouse_pos)
                        if action == "back":
                            self.settings_menu.hide()
                            self.pause_menu.show()
                            self.current_menu = "pause"
                        elif action == "toggle_auto_start":
                            self.auto_start_rounds = self.settings_menu.auto_start_rounds
                        elif action == "toggle_placement_mode":
                            # Placement mode changed, deselect any current tower selection
                            self.tower_selection_panel.deselect_tower()
                        elif action == "toggle_fps_counter":
                            self.show_fps = self.settings_menu.show_fps
                    # Handle mode selection clicks
                    elif self.current_menu == "mode_selection":
                        action = self.mode_selection.handle_click(mouse_pos)
                        if action == "normal_mode":
                            self.mode_selection.hide()
                            self.current_menu = "none"
                            self.game_mode = "normal"
                            self.sandbox_mode = False
                        elif action == "sandbox_mode":
                            self.mode_selection.hide()
                            self.current_menu = "none"
                            self.game_mode = "sandbox"
                            self.sandbox_mode = True
                            # Set sandbox mode properties
                            self.money = 999999 # Infinite money
                            self.lives = 999999 # Infinite lives
                        elif action == "back":
                            self.mode_selection.hide()
                            self.current_menu = "none"
                            return # Return to main menu
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
                            self.settings_menu.show_fps = self.show_fps
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
                        # First check if clicking on tower selection panel
                        selected_tower_id = self.tower_selection_panel.handle_click(mouse_pos, self.money)
                        if selected_tower_id:
                            # Tower type selected
                            if self.settings_menu.drag_drop_placement:
                                # Start drag mode
                                self.dragging_tower = True
                                self.drag_start_pos = mouse_pos
                            # For click mode, tower is selected and ready for placement on next click
                        # Check if clicking on upgrade panel
                        elif self.upgrade_panel.visible and self.upgrade_panel.rect.collidepoint(mouse_pos):
                            money_spent = self.upgrade_panel.handle_click(mouse_pos, self.money)
                            self.money -= money_spent
                        else:
                            # Check if clicking on existing tower for selection
                            clicked_tower = None
                            for tower in self.towers:
                                if tower.is_clicked(mouse_pos):
                                    clicked_tower = tower
                                    break
                            
                            if clicked_tower:
                                # Check if clicking on already selected tower
                                if clicked_tower == self.selected_tower:
                                    # Deselect the clicked tower
                                    clicked_tower.selected = False
                                    self.selected_tower = None
                                    self.upgrade_panel.set_selected_tower(None)
                                else:
                                    # Select a different tower - deselect all first
                                    for tower in self.towers:
                                        tower.selected = False
                                    # Select the clicked tower
                                    clicked_tower.selected = True
                                    self.selected_tower = clicked_tower
                                    self.upgrade_panel.set_selected_tower(clicked_tower)
                                    # Deselect tower type selection
                                    self.tower_selection_panel.deselect_tower()
                            else:
                                # No tower clicked, try to place new tower (click mode only)
                                if (not self.settings_menu.drag_drop_placement and 
                                    self.tower_selection_panel.selected_tower_id):
                                    self.place_tower(mouse_pos)
                                # Deselect all towers when placing new one
                                for tower in self.towers:
                                    tower.selected = False
                                self.selected_tower = None
                                self.upgrade_panel.set_selected_tower(None)
                        
                        # Handle sandbox mode bloon spawning
                        if self.sandbox_mode and not self.tower_selection_panel.selected_tower_id:
                            # Check if click is on the game map (not on UI)
                            game_area_rect = pygame.Rect(0, 0, SCREEN_WIDTH - 320, SCREEN_HEIGHT) # Exclude UI panels
                            if game_area_rect.collidepoint(mouse_pos):
                                self.spawn_bloon(mouse_pos)
                
                elif event.button == 3: # Right click - deselect
                    if not self.paused and not self.game_over:
                        # Deselect tower type selection
                        self.tower_selection_panel.deselect_tower()
                        # Deselect any selected towers
                        for tower in self.towers:
                            tower.selected = False
                        self.selected_tower = None
                        self.upgrade_panel.set_selected_tower(None)
                        
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.dragging_tower: # Left click release in drag mode
                    mouse_pos = pygame.mouse.get_pos()
                    if not self.paused and not self.game_over:
                        # Place tower at release position
                        if self.tower_selection_panel.selected_tower_id:
                            self.place_tower(mouse_pos)
                    self.dragging_tower = False
                    self.drag_start_pos = None
    
    def place_tower(self, position: Tuple[int, int]):
        selected_tower_id = self.tower_selection_panel.selected_tower_id
        if not selected_tower_id:
            return # No tower type selected
        
        tower_cost = self.tower_selection_panel.get_tower_cost(selected_tower_id)
        
        if self.money >= tower_cost and self.game_map.can_place_tower(position, self.towers):
            # Get tower stats from data
            tower_data = self.tower_selection_panel.get_selected_tower_data()
            if tower_data:
                base_stats = tower_data.get('base_stats', {})
                range_val = base_stats.get('range', 32) * 3 # Scale up range for gameplay
                damage = base_stats.get('damage', 1)
                fire_rate = base_stats.get('fire_rate', 0.95)
                pierce = base_stats.get('pierce', 1)
                projectiles = base_stats.get('projectiles', 1)
                
                # Create tower with proper stats
                new_tower = Tower(
                    position, 
                    range_val=range_val, 
                    damage=damage, 
                    fire_rate=fire_rate,
                    pierce=pierce,
                    projectiles=projectiles,
                    tower_type=selected_tower_id
                )
                new_tower.set_base_cost(tower_cost)
                self.towers.append(new_tower)
                self.money -= tower_cost
    
    def sell_tower(self, tower: 'Tower'):
        """Sell a tower and get money back"""
        if tower in self.towers:
            sell_price = tower.get_sell_price()
            self.money += sell_price
            self.towers.remove(tower)
            
            # Clear selection if this tower was selected
            if hasattr(self, 'upgrade_panel') and self.upgrade_panel.selected_tower == tower:
                self.upgrade_panel.set_selected_tower(None)
            
            print(f"Tower sold for ${sell_price}")
            return sell_price
        return 0
    
    def spawn_bloon(self, position: Tuple[int, int], bloon_type: BloonType = None):
        """Spawn a bloon at the given position in sandbox mode"""
        if bloon_type is None:
            bloon_type = self.sandbox_bloon_type
            
        # Find the closest point on the path to the clicked position
        closest_index = 0
        min_distance = float('inf')
        
        for i, path_point in enumerate(self.game_map.path):
            dx = path_point[0] - position[0]
            dy = path_point[1] - position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        # Create a custom path starting from the clicked position to the closest path point,
        # then continue with the rest of the path
        custom_path = [position] + self.game_map.path[closest_index:]
        
        # Create and add the bloon
        new_bloon = Bloon(bloon_type, custom_path)
        self.bloons.append(new_bloon)
    
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
                self.wave_completed_time = current_time # Record when wave was completed
                # Clear dead bloons
                self.bloons = [bloon for bloon in self.bloons if bloon.alive and not bloon.reached_end]
        
        # Update bloons - use list comprehension for better performance
        bloons_to_remove = []
        for bloon in self.bloons:
            bloon.update()
            if bloon.reached_end:
                self.lives -= 1
                bloons_to_remove.append(bloon)
                if self.lives <= 0:
                    self.game_over = True
        
        # Remove bloons that reached the end
        for bloon in bloons_to_remove:
            self.bloons.remove(bloon)
        
        # Update towers and create projectiles
        for tower in self.towers:
            new_projectiles = tower.update(self.bloons, current_time)
            if new_projectiles:
                self.projectiles.extend(new_projectiles)
        
        # Update projectiles - avoid copying list
        projectiles_to_remove = []
        for projectile in self.projectiles:
            projectile.update(self.bloons)
            if not projectile.alive:
                projectiles_to_remove.append(projectile)
        
        # Remove dead projectiles
        for projectile in projectiles_to_remove:
            self.projectiles.remove(projectile)
        
        # Remove dead bloons and award money - use list comprehension
        dead_bloons = []
        for bloon in self.bloons:
            if not bloon.alive:
                self.money += bloon.reward
                dead_bloons.append(bloon)
        
        # Remove dead bloons
        for bloon in dead_bloons:
            self.bloons.remove(bloon)
        
        # Update tower selection panel hover state (only when needed)
        if not self.paused and not self.game_over:
            mouse_pos = pygame.mouse.get_pos()
            self.tower_selection_panel.handle_hover(mouse_pos)
        
        # Clean up dead objects less frequently to improve performance
        if len(self.bloons) > 100 or len(self.projectiles) > 200:
            self.bloons = [bloon for bloon in self.bloons if bloon.alive and not bloon.reached_end]
            self.projectiles = [proj for proj in self.projectiles if proj.alive]
    
    def draw(self):
        # Draw map
        self.game_map.draw(self.screen)
        
        # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
        # Draw tower placement preview using tower selection panel
        if not self.paused and not self.game_over:
            mouse_pos = pygame.mouse.get_pos()
            self.tower_selection_panel.draw_placement_preview(self.screen, mouse_pos, self.game_map, self.towers, self.money)
            
            # Draw drag line if in drag mode
            if self.dragging_tower and self.drag_start_pos:
                pygame.draw.line(self.screen, (255, 255, 0), self.drag_start_pos, mouse_pos, 3)
                # Draw "DRAG TO PLACE" text - use cached font
                drag_text = self.cached_fonts['small'].render("DRAG TO PLACE", True, (255, 255, 0))
                text_pos = (mouse_pos[0] + 20, mouse_pos[1] - 30)
                self.screen.blit(drag_text, text_pos)
        
        # Draw bloons
        for bloon in self.bloons:
            bloon.draw(self.screen)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw UI
        self.ui.draw(self.screen, self.money, self.lives, self.wave_number, self.paused)
        
        # Draw game mode indicator - use cached fonts
        if self.sandbox_mode:
            mode_text = self.cached_fonts['small'].render(f"SANDBOX MODE - Click to spawn {self.sandbox_bloon_type.value.upper()} bloons (Press B to cycle)", True, WHITE)
            mode_rect = mode_text.get_rect(topleft=(10, 10))
            self.screen.blit(mode_text, mode_rect)
        else:
            mode_text = self.cached_fonts['small'].render("NORMAL MODE", True, WHITE)
            mode_rect = mode_text.get_rect(topleft=(10, 10))
            self.screen.blit(mode_text, mode_rect)
        
        # Draw tower selection panel
        if not self.paused and not self.game_over:
            self.tower_selection_panel.draw(self.screen, self.money)
        
        # Draw tower upgrade panel
        self.upgrade_panel.draw(self.screen, self.money)
        
        # Draw settings icon (always visible, not when game over)
        if not self.game_over:
            self.settings_icon.draw(self.screen)
        
        # Draw FPS counter if enabled - use cached font
        if self.show_fps:
            fps = int(self.clock.get_fps())
            fps_text = self.cached_fonts['small'].render(f"FPS: {fps}", True, WHITE)
            fps_rect = fps_text.get_rect(topright=(SCREEN_WIDTH - 60, 10))
            self.screen.blit(fps_text, fps_rect)
        
        # Draw game over screen - use cached font
        if self.game_over:
            game_over_text = self.cached_fonts['large'].render("GAME OVER", True, RED)
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
                    hint_text = self.cached_fonts['medium'].render(f"Next wave starts in {seconds_remaining} seconds", True, WHITE)
                    text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(hint_text, text_rect)
                    
                    # Show manual override hint
                    override_text = self.cached_fonts['small'].render("Press SPACE to start immediately", True, WHITE)
                    override_rect = override_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
                    self.screen.blit(override_text, override_rect)
                else:
                    hint_text = self.cached_fonts['medium'].render("Starting next wave...", True, WHITE)
                    text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                    self.screen.blit(hint_text, text_rect)
            else:
                # Show manual start hint
                hint_text = self.cached_fonts['medium'].render("Press SPACE to start next wave", True, WHITE)
                text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
                self.screen.blit(hint_text, text_rect)
        
        # Draw menus (always last to appear on top)
        if self.current_menu == "pause":
            self.pause_menu.draw(self.screen)
        elif self.current_menu == "settings":
            self.settings_menu.draw(self.screen)
        elif self.current_menu == "mode_selection":
            self.mode_selection.draw(self.screen)
        
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
