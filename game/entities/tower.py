"""
Tower entity class
"""
import pygame
import math
from typing import List, Tuple, Optional, TYPE_CHECKING
from ..constants import BROWN, GRAY

if TYPE_CHECKING:
    from .bloon import Bloon
    from .projectile import Projectile


class Tower:
    TOWER_RADIUS = 20 # Class constant for tower collision radius
    
    def __init__(self, position: Tuple[int, int], range_val: int = 100, damage: int = 1, fire_rate: float = 1.0, tower_type: str = "dart_monkey"):
        """Initialize the tower with the given parameters.

        Args:
            position (Tuple[int, int]): The position of the tower.
            range_val (int, optional): The attack range of the tower. Defaults to 100.
            damage (int, optional): The damage dealt by the tower. Defaults to 1.
            fire_rate (float, optional): The fire rate of the tower (shots per second). Defaults to 1.0.
            tower_type (str, optional): The type of tower. Defaults to "dart_monkey".
        """
        self.position = position
        self.range = range_val
        self.damage = damage
        self.fire_rate = fire_rate # shots per second
        self.last_shot_time = 0
        self.target: Optional['Bloon'] = None
        self.tower_type = tower_type
        self.selected = False
        
        # Upgrade tracking
        self.upgrade_levels = {"path1": 0, "path2": 0, "path3": 0}
        self.total_spent = 0
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the tower was clicked"""
        dx = pos[0] - self.position[0]
        dy = pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.TOWER_RADIUS
    
    def apply_upgrade(self, path: str, upgrade_data: dict):
        """Apply an upgrade to this tower"""
        stats = upgrade_data.get('stats', {})
        
        # Apply stat modifications (add to current values, not set)
        if 'damage' in stats:
            self.damage += stats['damage']
        if 'range' in stats:
            self.range += stats['range']
        if 'fire_rate' in stats:
            self.fire_rate += stats['fire_rate']
        
        # Track upgrade level
        path_num = path[-1] # Extract number from "path1", "path2", etc.
        self.upgrade_levels[path] += 1
        
        print(f"Tower upgraded: {upgrade_data['name']} - New stats: DMG:{self.damage} RNG:{self.range} FR:{self.fire_rate:.2f}")

    def can_shoot(self, current_time: float) -> bool:
        return current_time - self.last_shot_time >= (1000 / self.fire_rate) # Convert to milliseconds
    
    def find_target(self, bloons: List['Bloon']) -> Optional['Bloon']:
        targets_in_range = []
        for bloon in bloons:
            if not bloon.alive:
                continue
                
            dx = bloon.position[0] - self.position[0]
            dy = bloon.position[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.range:
                targets_in_range.append((bloon, distance))
        
        if targets_in_range:
            # Target the bloon that's furthest along the path
            return max(targets_in_range, key=lambda x: x[0].path_index)[0]
        return None
    
    def shoot(self, current_time: float) -> Optional['Projectile']:
        if self.target and self.target.alive and self.can_shoot(current_time):
            self.last_shot_time = current_time
            from .projectile import Projectile
            return Projectile(self.position, self.target, self.damage)
        return None
    
    def update(self, bloons: List['Bloon'], current_time: float) -> Optional['Projectile']:
        # Find new target if current target is invalid
        if not self.target or not self.target.alive:
            self.target = self.find_target(bloons)
        
        # Shoot at target
        return self.shoot(current_time)
    
    def draw(self, screen):
        """Draw the tower"""
        # Only draw range when selected
        if self.selected:
            # Create a surface for the semi-transparent range circle
            range_surface = pygame.Surface((self.range * 2, self.range * 2), pygame.SRCALPHA)
            
            # Draw semi-transparent fill (light gray with 30% opacity)
            pygame.draw.circle(range_surface, (128, 128, 128, 77), (self.range, self.range), self.range)
            
            # Blit the semi-transparent surface to the main screen
            screen.blit(range_surface, (self.position[0] - self.range, self.position[1] - self.range))
            
            # Draw thick outline (3 pixels thick, darker gray)
            pygame.draw.circle(screen, (96, 96, 96), self.position, self.range, 3)

        # Draw tower base - green if selected, brown if not
        color = (0, 200, 0) if self.selected else BROWN
        pygame.draw.circle(screen, color, self.position, self.TOWER_RADIUS)
        
        # Draw cannon
        pygame.draw.circle(screen, GRAY, self.position, 15)
        
        # Show upgrade indicators
        if any(level > 0 for level in self.upgrade_levels.values()):
            # Draw small upgrade indicators
            upgrade_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)] # Red, Green, Blue for each path
            for i, (path, level) in enumerate(self.upgrade_levels.items()):
                if level > 0:
                    indicator_pos = (
                        self.position[0] + 15 * math.cos(i * 2 * math.pi / 3),
                        self.position[1] + 15 * math.sin(i * 2 * math.pi / 3)
                    )
                    pygame.draw.circle(screen, upgrade_colors[i], (int(indicator_pos[0]), int(indicator_pos[1])), 3)
                    
                    # Draw level number
                    font = pygame.font.SysFont(None, 14)
                    level_text = font.render(str(level), True, (255, 255, 255))
                    text_rect = level_text.get_rect(center=(int(indicator_pos[0]), int(indicator_pos[1])))
                    screen.blit(level_text, text_rect)
