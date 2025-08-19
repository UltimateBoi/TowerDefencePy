"""
Projectile entity class
"""
import pygame
import math
from typing import Tuple, TYPE_CHECKING
from ..constants import BLACK

if TYPE_CHECKING:
    from .bloon import Bloon


class Projectile:
    def __init__(self, start_pos: Tuple[float, float], target: 'Bloon', damage: int, speed: float = 5.0):
        self.position = [float(start_pos[0]), float(start_pos[1])]
        self.target = target
        self.damage = damage
        self.speed = speed
        self.alive = True
        
    def update(self):
        if not self.alive or not self.target.alive:
            self.alive = False
            return
            
        # Move towards target
        dx = self.target.position[0] - self.position[0]
        dy = self.target.position[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5:  # Hit target
            self.target.take_damage(self.damage)
            self.alive = False
        else:
            # Move towards target
            self.position[0] += (dx / distance) * self.speed
            self.position[1] += (dy / distance) * self.speed
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, BLACK, (int(self.position[0]), int(self.position[1])), 3)
