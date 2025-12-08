"""
In-game tower upgrade panel for selecting and upgrading towers during gameplay
"""
import pygame
import json
import math
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..entities.tower import Tower

class InGameUpgradePanel:
    """Simple upgrade panel that appears when a tower is selected during gameplay"""
    
    def __init__(self, x: int, y: int, width: int = 300, height: int = 200):
        self.rect = pygame.Rect(x, y, width, height)
        self.selected_tower: Optional['Tower'] = None
        self.towers_data: Dict = {}
        self.difficulty_multiplier = 1.0
        self.visible = False
        
        # Cache fonts to avoid recreating them every frame (major performance improvement)
        self.font_title = pygame.font.SysFont(None, 24)
        self.font_name = pygame.font.SysFont(None, 20)
        self.font_stats = pygame.font.SysFont(None, 16)
        self.font_button = pygame.font.SysFont(None, 16)
        self.font_instruction = pygame.font.SysFont(None, 14)
        
        # Load tower data
        self.load_tower_data()
    
    def load_tower_data(self):
        """Load tower data from JSON file"""
        try:
            with open("data/towers.json", "r") as f:
                data = json.load(f)
                self.towers_data = data.get("towers", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading tower data: {e}")
            self.towers_data = {}
    
    def set_selected_tower(self, tower: Optional['Tower']):
        """Set the currently selected tower"""
        self.selected_tower = tower
        self.visible = tower is not None
    
    def get_upgrade_cost(self, path: str, level: int) -> int:
        """Calculate the cost of the next upgrade for a specific path"""
        if not self.selected_tower or self.selected_tower.tower_type not in self.towers_data:
            return 0
        
        tower_data = self.towers_data[self.selected_tower.tower_type]
        upgrade_paths = tower_data.get('upgrade_paths', {})
        
        if path not in upgrade_paths:
            return 0
        
        upgrades = upgrade_paths[path].get('upgrades', [])
        if level >= len(upgrades):
            return 0 # Max level reached
        
        base_cost = upgrades[level]['cost']
        return int(base_cost * self.difficulty_multiplier)
    
    def can_upgrade(self, path: str, player_money: int) -> bool:
        """Check if the tower can be upgraded on the given path"""
        if not self.selected_tower:
            return False
        
        current_level = self.selected_tower.upgrade_levels.get(path, 0)
        
        # Check BTD6 rule: can only upgrade if other paths aren't too high
        other_paths = [p for p in ['path1', 'path2', 'path3'] if p != path]
        other_levels = [self.selected_tower.upgrade_levels.get(p, 0) for p in other_paths]
        
        # BTD6 rule: If any other path is level 3+, this path can't go beyond level 2
        if any(level >= 3 for level in other_levels) and current_level >= 2:
            return False
        
        # Check if we've reached max level (5)
        if current_level >= 5:
            return False
        
        # Check if player has enough money
        cost = self.get_upgrade_cost(path, current_level)
        return player_money >= cost and cost > 0
    
    def upgrade_tower(self, path: str, player_money: int) -> int:
        """Upgrade the tower and return the cost (0 if upgrade failed)"""
        if not self.can_upgrade(path, player_money):
            return 0
        
        tower_data = self.towers_data[self.selected_tower.tower_type]
        upgrade_paths = tower_data.get('upgrade_paths', {})
        upgrades = upgrade_paths[path].get('upgrades', [])
        
        current_level = self.selected_tower.upgrade_levels.get(path, 0)
        upgrade_data = upgrades[current_level]
        cost = self.get_upgrade_cost(path, current_level)
        
        # Apply the upgrade
        self.selected_tower.apply_upgrade(path, upgrade_data)
        
        return cost
    
    def draw(self, screen: pygame.Surface, player_money: int):
        """Draw the upgrade panel"""
        if not self.visible or not self.selected_tower:
            return
        
        # Panel background
        pygame.draw.rect(screen, (40, 40, 40), self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=10)
        
        # Title
        title = self.font_title.render("Tower Upgrades", True, (255, 255, 255))
        title_rect = title.get_rect(centerx=self.rect.centerx, y=self.rect.y + 10)
        screen.blit(title, title_rect)
        
        # Tower info
        if self.selected_tower.tower_type in self.towers_data:
            tower_data = self.towers_data[self.selected_tower.tower_type]
            tower_name = tower_data.get('name', 'Unknown Tower')
            
            name_text = self.font_name.render(tower_name, True, (255, 255, 255))
            name_rect = name_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 35)
            screen.blit(name_text, name_rect)
        
        # Current stats
        stats_y = self.rect.y + 60
        stats_text = f"DMG: {self.selected_tower.damage}  RNG: {self.selected_tower.range}  SPD: {self.selected_tower.fire_rate:.1f}"
        stats_surface = self.font_stats.render(stats_text, True, (200, 200, 200))
        stats_rect = stats_surface.get_rect(centerx=self.rect.centerx, y=stats_y)
        screen.blit(stats_surface, stats_rect)
        
        # Upgrade buttons
        button_width = 80
        button_height = 30
        button_y = self.rect.y + 90
        
        paths = ['path1', 'path2', 'path3']
        path_names = ['Path 1', 'Path 2', 'Path 3']
        button_colors = [(200, 100, 100), (100, 200, 100), (100, 100, 200)]
        
        for i, (path, name, color) in enumerate(zip(paths, path_names, button_colors)):
            button_x = self.rect.x + 20 + i * (button_width + 10)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            # Check if upgrade is available
            can_upgrade = self.can_upgrade(path, player_money)
            current_level = self.selected_tower.upgrade_levels.get(path, 0)
            cost = self.get_upgrade_cost(path, current_level)
            
            # Button color based on availability
            if can_upgrade:
                button_color = color
            else:
                button_color = (60, 60, 60)
            
            pygame.draw.rect(screen, button_color, button_rect, border_radius=5)
            pygame.draw.rect(screen, (255, 255, 255), button_rect, 1, border_radius=5)
            
            # Button text
            level_text = f"Lv {current_level}"
            level_surface = self.font_button.render(level_text, True, (255, 255, 255))
            level_rect = level_surface.get_rect(centerx=button_rect.centerx, y=button_rect.y + 2)
            screen.blit(level_surface, level_rect)
            
            # Cost text
            if cost > 0:
                cost_text = f"${cost}"
                cost_surface = self.font_button.render(cost_text, True, (255, 255, 0) if can_upgrade else (100, 100, 100))
                cost_rect = cost_surface.get_rect(centerx=button_rect.centerx, y=button_rect.y + 15)
                screen.blit(cost_surface, cost_rect)
            else:
                max_text = "MAX"
                max_surface = self.font_button.render(max_text, True, (200, 200, 200))
                max_rect = max_surface.get_rect(centerx=button_rect.centerx, y=button_rect.y + 15)
                screen.blit(max_surface, max_rect)
            
            # Store button rect for click detection
            setattr(self, f"{path}_button", button_rect)
        
        # Instructions
        instr_text = "Click upgrade buttons to improve tower"
        instr_surface = self.font_instruction.render(instr_text, True, (150, 150, 150))
        instr_rect = instr_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 135)
        screen.blit(instr_surface, instr_rect)
        
        # Money display
        money_text = f"Money: ${player_money}"
        money_surface = self.font_stats.render(money_text, True, (255, 255, 0))
        money_rect = money_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 155)
        screen.blit(money_surface, money_rect)
        
        # Sell price display
        if self.selected_tower:
            sell_price = self.selected_tower.get_sell_price()
            sell_text = f"Sell value: ${sell_price} (X key)"
            sell_surface = self.font_stats.render(sell_text, True, (255, 100, 100))
            sell_rect = sell_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 175)
            screen.blit(sell_surface, sell_rect)
    
    def handle_click(self, pos: Tuple[int, int], player_money: int) -> int:
        """Handle clicks on upgrade buttons. Returns money spent."""
        if not self.visible or not self.selected_tower:
            return 0
        
        paths = ['path1', 'path2', 'path3']
        for path in paths:
            button = getattr(self, f"{path}_button", None)
            if button and button.collidepoint(pos):
                return self.upgrade_tower(path, player_money)
        
        return 0
