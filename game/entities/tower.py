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
    def __init__(self, position: Tuple[int, int], range_val: int = 100, damage: int = 1, fire_rate: float = 1.0):
        self.position = position
        self.range = range_val
        self.damage = damage
        self.fire_rate = fire_rate # shots per second
        self.last_shot_time = 0
        self.target: Optional['Bloon'] = None
        
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
        # Draw tower base
        pygame.draw.circle(screen, BROWN, self.position, 20)
        # Draw cannon
        pygame.draw.circle(screen, GRAY, self.position, 15)
        
        # Draw range circle when selected (for now, always show)
        pygame.draw.circle(screen, (128, 128, 128, 50), self.position, self.range, 1)
