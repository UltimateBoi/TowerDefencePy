"""
Tower Upgrades Screen - Allows players to view towers and their upgrade paths
Inspired by BTD6's upgrade system with multi-tier paths and exponential costs
"""
import pygame
import json
import math
import sys
import os
from typing import Dict, List, Optional, Tuple

# Add the parent directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.ButtonUtil import TextButton
from utils.TextUtil import TextUtil


class TowerCard:
    """Represents a tower card in the grid display"""
    def __init__(self, tower_id: str, tower_data: Dict, x: int, y: int, width: int = 140, height: int = 160):
        self.tower_id = tower_id
        self.tower_data = tower_data
        self.rect = pygame.Rect(x, y, width, height)
        self.selected = False
        self.hover = False
        
    def draw(self, screen: pygame.Surface):
        """Draw the tower card"""
        # Card background
        color = (70, 70, 70) if not self.selected else (100, 150, 100)
        if self.hover and not self.selected:
            color = (90, 90, 90)
        
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=10)
        
        # Tower icon (simple colored circle)
        icon_radius = 30
        icon_center = (self.rect.centerx, self.rect.y + 45)
        icon_color = tuple(self.tower_data.get('icon_color', [139, 69, 19]))
        pygame.draw.circle(screen, icon_color, icon_center, icon_radius)
        pygame.draw.circle(screen, (255, 255, 255), icon_center, icon_radius, 2)
        
        # Tower name
        font = pygame.font.SysFont(None, 24)
        name_text = font.render(self.tower_data['name'], True, (255, 255, 255))
        name_rect = name_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 85)
        screen.blit(name_text, name_rect)
        
        # Base cost
        cost_font = pygame.font.SysFont(None, 20)
        cost_text = cost_font.render(f"${self.tower_data['base_cost']}", True, (255, 255, 0))
        cost_rect = cost_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 110)
        screen.blit(cost_text, cost_rect)
        
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if the card was clicked"""
        return self.rect.collidepoint(pos)
        
    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state"""
        self.hover = self.rect.collidepoint(pos)


class UpgradePathDisplay:
    """Displays the upgrade paths for a selected tower"""
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.tower_data: Optional[Dict] = None
        self.difficulty = "E" # E=Easy, M=Medium, H=Hard, I=Impoppable
        
    def set_tower(self, tower_data: Dict):
        """Set the tower to display upgrade paths for"""
        self.tower_data = tower_data
        
    def draw(self, screen: pygame.Surface, difficulty_multipliers: Dict[str, float]):
        """Draw the upgrade paths display"""
        if not self.tower_data:
            # Show placeholder text
            font = pygame.font.SysFont(None, 48)
            text = font.render("Select a tower to view upgrades", True, (150, 150, 150))
            text_rect = text.get_rect(center=self.rect.center)
            screen.blit(text, text_rect)
            return
            
        # Background
        pygame.draw.rect(screen, (50, 50, 50), self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2, border_radius=10)
        
        # Tower info header
        header_height = 80
        header_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, header_height)
        pygame.draw.rect(screen, (40, 40, 40), header_rect, border_radius=5)
        
        # Tower name and description
        name_font = pygame.font.SysFont(None, 36)
        desc_font = pygame.font.SysFont(None, 24)
        
        name_text = name_font.render(self.tower_data['name'], True, (255, 255, 255))
        desc_text = desc_font.render(self.tower_data['description'], True, (200, 200, 200))
        
        screen.blit(name_text, (header_rect.x + 10, header_rect.y + 10))
        screen.blit(desc_text, (header_rect.x + 10, header_rect.y + 45))
        
        # Difficulty selector
        diff_x = header_rect.right - 150
        diff_font = pygame.font.SysFont(None, 24)
        diff_label = diff_font.render("Difficulty:", True, (255, 255, 255))
        screen.blit(diff_label, (diff_x, header_rect.y + 10))
        
        # Difficulty buttons
        diff_options = ["E", "M", "H", "I"]
        diff_colors = [(0, 255, 0), (255, 255, 0), (255, 165, 0), (255, 0, 0)]
        for i, (diff, color) in enumerate(zip(diff_options, diff_colors)):
            diff_rect = pygame.Rect(diff_x + i * 25, header_rect.y + 35, 20, 20)
            if self.difficulty == diff:
                pygame.draw.rect(screen, color, diff_rect)
            else:
                pygame.draw.rect(screen, (100, 100, 100), diff_rect)
            pygame.draw.rect(screen, (255, 255, 255), diff_rect, 1)
            
            # Difficulty letter
            diff_text = pygame.font.SysFont(None, 16).render(diff, True, (0, 0, 0) if self.difficulty == diff else (255, 255, 255))
            text_rect = diff_text.get_rect(center=diff_rect.center)
            screen.blit(diff_text, text_rect)
        
        # Base stats
        stats_y = header_rect.bottom + 20
        stats_font = pygame.font.SysFont(None, 20)
        stats_text = "Base Stats: "
        base_stats = self.tower_data['base_stats']
        for stat, value in base_stats.items():
            stats_text += f"{stat.replace('_', ' ').title()}: {value}  "
        
        stats_surface = stats_font.render(stats_text, True, (255, 255, 255))
        screen.blit(stats_surface, (self.rect.x + 20, stats_y))
        
        # Upgrade paths
        paths_y = stats_y + 40
        path_width = (self.rect.width - 60) // 3
        path_height = self.rect.height - (paths_y - self.rect.y) - 20
        
        upgrade_paths = self.tower_data.get('upgrade_paths', {})
        path_names = list(upgrade_paths.keys())
        
        for i, path_name in enumerate(path_names):
            path_x = self.rect.x + 20 + i * (path_width + 10)
            path_rect = pygame.Rect(path_x, paths_y, path_width, path_height)
            self.draw_upgrade_path(screen, upgrade_paths[path_name], path_rect, difficulty_multipliers)
    
    def draw_upgrade_path(self, screen: pygame.Surface, path_data: Dict, path_rect: pygame.Rect, difficulty_multipliers: Dict[str, float]):
        """Draw a single upgrade path"""
        # Path background
        pygame.draw.rect(screen, (60, 60, 60), path_rect, border_radius=5)
        pygame.draw.rect(screen, (150, 150, 150), path_rect, 1, border_radius=5)
        
        # Path header
        header_font = pygame.font.SysFont(None, 24)
        name_text = header_font.render(path_data['name'], True, (255, 255, 255))
        name_rect = name_text.get_rect(centerx=path_rect.centerx, y=path_rect.y + 5)
        screen.blit(name_text, name_rect)
        
        desc_font = pygame.font.SysFont(None, 16)
        desc_text = desc_font.render(path_data['description'], True, (200, 200, 200))
        desc_rect = desc_text.get_rect(centerx=path_rect.centerx, y=path_rect.y + 25)
        screen.blit(desc_text, desc_rect)
        
        # Upgrades
        upgrades = path_data.get('upgrades', [])
        upgrade_height = (path_rect.height - 60) // 5
        
        for i, upgrade in enumerate(upgrades):
            upgrade_y = path_rect.y + 50 + i * upgrade_height
            upgrade_rect = pygame.Rect(path_rect.x + 5, upgrade_y, path_rect.width - 10, upgrade_height - 2)
            
            # Upgrade background (tier color)
            tier_colors = [(100, 100, 100), (0, 150, 0), (0, 100, 200), (150, 100, 0), (200, 0, 100)]
            tier_color = tier_colors[min(i, len(tier_colors) - 1)]
            pygame.draw.rect(screen, tier_color, upgrade_rect, border_radius=3)
            pygame.draw.rect(screen, (255, 255, 255), upgrade_rect, 1, border_radius=3)
            
            # Upgrade name
            name_font = pygame.font.SysFont(None, 18)
            name_surface = name_font.render(upgrade['name'], True, (255, 255, 255))
            screen.blit(name_surface, (upgrade_rect.x + 5, upgrade_rect.y + 2))
            
            # Upgrade cost (with difficulty multiplier)
            base_cost = upgrade['cost']
            multiplier = difficulty_multipliers.get(self.difficulty, 1.0)
            final_cost = int(base_cost * multiplier)
            
            cost_font = pygame.font.SysFont(None, 16)
            cost_surface = cost_font.render(f"${final_cost}", True, (255, 255, 0))
            cost_rect = cost_surface.get_rect(right=upgrade_rect.right - 5, y=upgrade_rect.y + 2)
            screen.blit(cost_surface, cost_rect)
            
            # Upgrade description
            desc_font = pygame.font.SysFont(None, 14)
            desc_surface = desc_font.render(upgrade['description'], True, (200, 200, 200))
            screen.blit(desc_surface, (upgrade_rect.x + 5, upgrade_rect.y + 20))
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle clicks on the upgrade paths (e.g., difficulty selection)"""
        if not self.tower_data:
            return
            
        # Check difficulty buttons
        header_rect = pygame.Rect(self.rect.x + 10, self.rect.y + 10, self.rect.width - 20, 80)
        diff_x = header_rect.right - 150
        diff_options = ["E", "M", "H", "I"]
        
        for i, diff in enumerate(diff_options):
            diff_rect = pygame.Rect(diff_x + i * 25, header_rect.y + 35, 20, 20)
            if diff_rect.collidepoint(pos):
                self.difficulty = diff
                break


class TowerUpgradesScreen:
    """Main tower upgrades screen class"""
    
    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.towers_data: Dict = {}
        self.difficulty_multipliers: Dict[str, float] = {}
        self.tower_cards: List[TowerCard] = []
        self.selected_tower: Optional[str] = None
        
        # UI Layout
        self.sidebar_width = 330  # Expanded from 300 to 380
        self.upgrade_panel_x = self.sidebar_width + 15  # Reduced from 20 to 15 for better balance
        self.upgrade_panel_width = self.screen_width - self.upgrade_panel_x - 20
        
        # Create upgrade display
        self.upgrade_display = UpgradePathDisplay(
            self.upgrade_panel_x, 80, 
            self.upgrade_panel_width, self.screen_height - 160
        )
        
        # Back button
        self.back_button = TextButton(
            "back", 20, self.screen_height - 60, 100, 40, 
            "Back", color=(200, 50, 50), radius=10
        )
        
        # Load tower data
        self.load_tower_data()
        self.create_tower_cards()
        
    def load_tower_data(self):
        """Load tower data from JSON file"""
        try:
            with open("data/towers.json", "r") as f:
                data = json.load(f)
                self.towers_data = data.get("towers", {})
                self.difficulty_multipliers = data.get("difficulty_multipliers", {"E": 1.0, "M": 1.2, "H": 1.5, "I": 2.0})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading tower data: {e}")
            # Fallback data
            self.towers_data = {
                "dart_tower": {
                    "name": "Dart Tower",
                    "description": "Basic tower that shoots darts",
                    "base_cost": 100,
                    "base_stats": {"damage": 1, "range": 100, "fire_rate": 1.0},
                    "icon_color": [139, 69, 19],
                    "upgrade_paths": {}
                }
            }
            self.difficulty_multipliers = {"E": 1.0, "M": 1.2, "H": 1.5, "I": 2.0}
    
    def create_tower_cards(self):
        """Create tower cards for the sidebar"""
        self.tower_cards = []
        card_width = 140
        card_height = 160
        cards_per_row = 2
        start_x = 20
        start_y = 100
        
        tower_ids = list(self.towers_data.keys())
        for i, tower_id in enumerate(tower_ids):
            row = i // cards_per_row
            col = i % cards_per_row
            x = start_x + col * (card_width + 10)
            y = start_y + row * (card_height + 20)
            
            card = TowerCard(tower_id, self.towers_data[tower_id], x, y, card_width, card_height)
            self.tower_cards.append(card)
    
    def update(self, events: List[pygame.event.Event], mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        Update the tower upgrades screen
        Returns: "back" if back button clicked, None otherwise
        """
        # Handle events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check back button
                if self.back_button.is_clicked(*mouse_pos):
                    return "back"
                
                # Check tower cards
                for card in self.tower_cards:
                    if card.handle_click(mouse_pos):
                        # Deselect all cards
                        for c in self.tower_cards:
                            c.selected = False
                        # Select clicked card
                        card.selected = True
                        self.selected_tower = card.tower_id
                        self.upgrade_display.set_tower(card.tower_data)
                        break
                
                # Check upgrade display clicks
                self.upgrade_display.handle_click(mouse_pos)
        
        # Update hover states
        for card in self.tower_cards:
            card.handle_hover(mouse_pos)
        
        return None
    
    def draw(self, screen: pygame.Surface):
        """Draw the tower upgrades screen"""
        # Background
        screen.fill((30, 30, 30))
        
        # Title
        title_font = pygame.font.SysFont(None, 48)
        title_text = title_font.render("Tower Upgrades", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.screen_width // 2, y=20)
        screen.blit(title_text, title_rect)
        
        # Sidebar background
        sidebar_rect = pygame.Rect(0, 0, self.sidebar_width, self.screen_height)
        pygame.draw.rect(screen, (40, 40, 40), sidebar_rect)
        pygame.draw.line(screen, (100, 100, 100), (self.sidebar_width, 0), (self.sidebar_width, self.screen_height), 2)
        
        # Sidebar title
        sidebar_font = pygame.font.SysFont(None, 32)
        sidebar_title = sidebar_font.render("Towers", True, (255, 255, 255))
        screen.blit(sidebar_title, (20, 60))
        
        # Draw tower cards
        for card in self.tower_cards:
            card.draw(screen)
        
        # Draw upgrade display
        self.upgrade_display.draw(screen, self.difficulty_multipliers)
        
        # Draw back button
        self.back_button.draw(screen)
        
        # Instructions
        if not self.selected_tower:
            instruction_font = pygame.font.SysFont(None, 24)
            instruction_text = instruction_font.render("Click on a tower to view its upgrade paths", True, (150, 150, 150))
            instruction_rect = instruction_text.get_rect(centerx=self.screen_width // 2, y=self.screen_height - 30)
            screen.blit(instruction_text, instruction_rect)


# Example usage for testing
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Tower Upgrades Screen Test")
    clock = pygame.time.Clock()
    
    upgrades_screen = TowerUpgradesScreen()
    running = True
    
    while running:
        events = pygame.event.get()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        result = upgrades_screen.update(events, mouse_pos)
        if result == "back":
            print("Back button clicked!")
        
        upgrades_screen.draw(screen)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
