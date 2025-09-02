"""
Tower Selection Panel - BTD6-style tower placement interface
Allows players to select tower types before placing them
"""
import pygame
import json
import math
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING

class TowerButton:
    """Represents a tower selection button"""
    
    def __init__(self, tower_id: str, tower_data: Dict, x: int, y: int, width: int = 60, height: int = 80):
        self.tower_id = tower_id
        self.tower_data = tower_data
        self.rect = pygame.Rect(x, y, width, height)
        self.selected = False
        self.hover = False
        self.affordable = True
        
    def draw(self, screen: pygame.Surface, player_money: int):
        """Draw the tower button"""
        # Check if player can afford this tower
        self.affordable = player_money >= self.tower_data.get('base_cost', 0)
        
        # Button background
        if self.selected:
            color = (100, 200, 100) # Green when selected
        elif self.hover and self.affordable:
            color = (80, 80, 120) # Light gray when hovering
        elif self.affordable:
            color = (60, 60, 80) # Dark gray when affordable
        else:
            color = (40, 40, 40) # Very dark when unaffordable
        
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        
        # Border
        border_color = (255, 255, 255) if self.affordable else (100, 100, 100)
        border_width = 3 if self.selected else 1
        pygame.draw.rect(screen, border_color, self.rect, border_width, border_radius=8)
        
        # Tower icon (colored circle based on tower type)
        icon_radius = 18
        icon_center = (self.rect.centerx, self.rect.y + 25)
        icon_color = tuple(self.tower_data.get('icon_color', [139, 69, 19]))
        
        # Dim the icon if unaffordable
        if not self.affordable:
            icon_color = tuple(c // 3 for c in icon_color)
        
        pygame.draw.circle(screen, icon_color, icon_center, icon_radius)
        pygame.draw.circle(screen, border_color, icon_center, icon_radius, 2)
        
        # Tower name (shortened)
        font = pygame.font.SysFont(None, 14)
        name = self.tower_data.get('name', 'Tower')
        # Shorten long names
        if len(name) > 8:
            if 'Monkey' in name:
                name = name.replace(' Monkey', '')
            elif 'Shooter' in name:
                name = name.replace(' Shooter', '')
        
        name_color = (255, 255, 255) if self.affordable else (100, 100, 100)
        name_text = font.render(name, True, name_color)
        name_rect = name_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 48)
        screen.blit(name_text, name_rect)
        
        # Cost
        cost_font = pygame.font.SysFont(None, 12)
        cost = self.tower_data.get('base_cost', 0)
        cost_color = (255, 255, 0) if self.affordable else (100, 100, 50)
        cost_text = cost_font.render(f"${cost}", True, cost_color)
        cost_rect = cost_text.get_rect(centerx=self.rect.centerx, y=self.rect.y + 62)
        screen.blit(cost_text, cost_rect)
    
    def handle_click(self, pos: Tuple[int, int]) -> bool:
        """Check if button was clicked"""
        return self.rect.collidepoint(pos) and self.affordable
    
    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover state"""
        self.hover = self.rect.collidepoint(pos)


class TowerSelectionPanel:
    """Panel for selecting tower types before placement - Horizontal layout at top"""
    
    def __init__(self):
        # Horizontal layout at the top center of the screen
        from ..constants import SCREEN_WIDTH
        
        self.button_width = 80
        self.button_height = 100
        self.button_spacing = 10
        self.visible = True # Toggleable visibility
        
        # Calculate panel dimensions and position
        self.num_towers = 4 # We'll have 4 tower types
        panel_width = (self.button_width + self.button_spacing) * self.num_towers - self.button_spacing + 20 # 20 for padding
        self.x = (SCREEN_WIDTH - panel_width) // 2 # Center horizontally
        self.y = 10 # Top of screen with small margin
        self.width = panel_width
        self.height = self.button_height + 40 # Extra space for toggle button
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Toggle button for showing/hiding panel
        self.toggle_button_rect = pygame.Rect(self.x + self.width - 25, self.y + 5, 20, 20)
        
        # Tower data
        self.towers_data: Dict = {}
        self.tower_buttons: List[TowerButton] = []
        self.selected_tower_id: Optional[str] = None
        self.placement_mode = False
        
        # Load tower data
        self.load_tower_data()
        self.create_tower_buttons()
    
    def load_tower_data(self):
        """Load tower data from JSON file"""
        try:
            with open("data/towers.json", "r") as f:
                data = json.load(f)
                self.towers_data = data.get("towers", {})
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading tower data: {e}")
            self.towers_data = {}
    
    def create_tower_buttons(self):
        """Create tower selection buttons arranged horizontally"""
        self.tower_buttons = []
        
        # Create buttons for each tower type, arranged horizontally
        for i, (tower_id, tower_data) in enumerate(self.towers_data.items()):
            button_x = self.x + 10 + i * (self.button_width + self.button_spacing)
            button_y = self.y + 30 # Fixed Y position in horizontal layout
            button = TowerButton(tower_id, tower_data, button_x, button_y, self.button_width, self.button_height)
            self.tower_buttons.append(button)
    
    def get_selected_tower_data(self) -> Optional[Dict]:
        """Get data for currently selected tower"""
        if self.selected_tower_id and self.selected_tower_id in self.towers_data:
            return self.towers_data[self.selected_tower_id]
        return None
    
    def get_selected_tower_stats(self) -> Tuple[int, int, int]:
        """Get stats for selected tower (range, damage, cost)"""
        tower_data = self.get_selected_tower_data()
        if tower_data:
            base_stats = tower_data.get('base_stats', {})
            range_val = base_stats.get('range', 100) * 3 # Scale up range for visual display
            damage = base_stats.get('damage', 1)
            cost = tower_data.get('base_cost', 200)
            return range_val, damage, cost
        return 100, 1, 200 # Default values
    
    def can_afford_selected_tower(self, player_money: int) -> bool:
        """Check if player can afford the selected tower"""
        tower_data = self.get_selected_tower_data()
        if tower_data:
            cost = tower_data.get('base_cost', 0)
            return player_money >= cost
        return False
    
    def get_tower_cost(self, tower_id: str) -> int:
        """Get the cost of a specific tower"""
        if tower_id in self.towers_data:
            return self.towers_data[tower_id].get('base_cost', 0)
        return 0
    
    def draw(self, screen: pygame.Surface, player_money: int):
        """Draw the tower selection panel"""
        # Draw toggle button (always visible)
        toggle_color = (100, 200, 100) if self.visible else (200, 100, 100)
        pygame.draw.rect(screen, toggle_color, self.toggle_button_rect, border_radius=3)
        pygame.draw.rect(screen, (255, 255, 255), self.toggle_button_rect, 2, border_radius=3)
        
        # Toggle button icon (+ or -)
        font = pygame.font.SysFont(None, 16)
        icon = "-" if self.visible else "+"
        icon_text = font.render(icon, True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=self.toggle_button_rect.center)
        screen.blit(icon_text, icon_rect)
        
        # Only draw the panel if it's visible
        if not self.visible:
            return
            
        # Panel background
        pygame.draw.rect(screen, (40, 40, 50), self.rect, border_radius=10)
        pygame.draw.rect(screen, (150, 150, 150), self.rect, 2, border_radius=10)
        
        # Title
        font = pygame.font.SysFont(None, 20)
        title_text = font.render("Select Tower", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.rect.centerx, y=self.y + 8)
        screen.blit(title_text, title_rect)
        
        # Draw tower buttons
        for button in self.tower_buttons:
            button.draw(screen, player_money)
        
        # Instructions at bottom
        if self.selected_tower_id:
            instr_font = pygame.font.SysFont(None, 12)
            instr_text = "Click map\nto place"
            lines = instr_text.split('\n')
            for i, line in enumerate(lines):
                line_surface = instr_font.render(line, True, (200, 200, 200))
                line_rect = line_surface.get_rect(centerx=self.rect.centerx, 
                                                y=self.rect.bottom - 30 + i * 12)
                screen.blit(line_surface, line_rect)
        else:
            instr_font = pygame.font.SysFont(None, 12)
            instr_text = "Select\na tower"
            lines = instr_text.split('\n')
            for i, line in enumerate(lines):
                line_surface = instr_font.render(line, True, (150, 150, 150))
                line_rect = line_surface.get_rect(centerx=self.rect.centerx, 
                                                y=self.rect.bottom - 30 + i * 12)
                screen.blit(line_surface, line_rect)
    
    def draw_placement_preview(self, screen: pygame.Surface, mouse_pos: Tuple[int, int], 
                             game_map, towers, player_money: int = 1000):
        """Draw tower placement preview at mouse position"""
        # Only draw if panel is visible and tower is selected
        if not self.visible or not self.selected_tower_id:
            return
        
        # Check if can place at this position
        can_place = game_map.can_place_tower(mouse_pos, towers)
        
        tower_range, damage, cost = self.get_selected_tower_stats()
        affordable = self.can_afford_selected_tower(player_money)
        
        # Color based on placement validity and affordability
        if not affordable:
            color = (100, 100, 100, 80) # Gray for unaffordable
            border_color = (100, 100, 100)
        elif can_place:
            color = (0, 255, 0, 80) # Green for valid
            border_color = (0, 255, 0)
        else:
            color = (255, 0, 0, 80) # Red for invalid
            border_color = (255, 0, 0)
        
        # Draw range circle
        range_surface = pygame.Surface((tower_range * 2, tower_range * 2), pygame.SRCALPHA)
        pygame.draw.circle(range_surface, color, (tower_range, tower_range), tower_range)
        pygame.draw.circle(range_surface, (*border_color, 150), (tower_range, tower_range), tower_range, 3)
        screen.blit(range_surface, (mouse_pos[0] - tower_range, mouse_pos[1] - tower_range))
        
        # Draw tower preview
        from ..entities.tower import Tower
        tower_radius = Tower.TOWER_RADIUS
        
        # Tower body
        pygame.draw.circle(screen, border_color, mouse_pos, tower_radius)
        
        # Tower icon color
        tower_data = self.get_selected_tower_data()
        if tower_data:
            icon_color = tuple(tower_data.get('icon_color', [139, 69, 19]))
            if not affordable:
                icon_color = tuple(c // 2 for c in icon_color)
            pygame.draw.circle(screen, icon_color, mouse_pos, tower_radius - 3)
        
        # Cost display
        if affordable:
            cost_font = pygame.font.SysFont(None, 24)
            cost_text = cost_font.render(f"${cost}", True, (255, 255, 255))
            cost_rect = cost_text.get_rect(center=(mouse_pos[0], mouse_pos[1] - tower_radius - 20))
            pygame.draw.rect(screen, (0, 0, 0, 128), cost_rect.inflate(4, 2))
            screen.blit(cost_text, cost_rect)
        else:
            # "Can't afford" message
            afford_font = pygame.font.SysFont(None, 20)
            afford_text = afford_font.render("Can't afford", True, (255, 255, 255))
            afford_rect = afford_text.get_rect(center=(mouse_pos[0], mouse_pos[1] - tower_radius - 20))
            pygame.draw.rect(screen, (0, 0, 0, 128), afford_rect.inflate(4, 2))
            screen.blit(afford_text, afford_rect)
    
    def handle_click(self, pos: Tuple[int, int], player_money: int) -> Optional[str]:
        """Handle clicks on tower buttons and toggle button. Returns selected tower ID or None."""
        # Check toggle button first (always available)
        if self.toggle_button_rect.collidepoint(pos):
            self.visible = not self.visible
            return None
        
        # Only handle tower button clicks if panel is visible
        if not self.visible:
            return None
            
        # Check if clicking inside panel
        if not self.rect.collidepoint(pos):
            return None
        
        # Check tower buttons
        for button in self.tower_buttons:
            if button.handle_click(pos):
                # Check if clicking on already selected tower type
                if button.tower_id == self.selected_tower_id:
                    # Deselect the tower type
                    self.deselect_tower()
                    return None
                else:
                    # Select a different tower type - deselect all first
                    for b in self.tower_buttons:
                        b.selected = False
                    
                    # Select clicked button
                    button.selected = True
                    self.selected_tower_id = button.tower_id
                    self.placement_mode = True
                    return button.tower_id
        
        return None
    
    def handle_hover(self, pos: Tuple[int, int]):
        """Update hover states"""
        # Only handle hover if panel is visible
        if not self.visible:
            return
            
        for button in self.tower_buttons:
            button.handle_hover(pos)
    
    def deselect_tower(self):
        """Deselect current tower"""
        self.selected_tower_id = None
        self.placement_mode = False
        for button in self.tower_buttons:
            button.selected = False
