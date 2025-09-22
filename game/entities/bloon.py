"""
Bloon entity class
"""
import pygame
import math
from typing import List, Tuple
from .bloon_types import BloonType, BLOON_PROPERTIES
from ..constants import BLACK, GREEN


class Bloon:
    def __init__(self, bloon_type: BloonType, path: List[Tuple[int, int]]):
        """Initialize the bloon with the given type and path.

        Args:
            bloon_type (BloonType): The type of the bloon.
            path (List[Tuple[int, int]]): The path the bloon will follow.
        """
        self.type = bloon_type
        self.properties = BLOON_PROPERTIES[bloon_type]
        self.health = self.properties.health
        self.max_health = self.properties.health
        self.speed = self.properties.speed
        self.reward = self.properties.reward
        self.color = self.properties.color
        self.size = self.properties.size
        
        self.path = path
        self.path_index = 0
        self.position = [float(path[0][0]), float(path[0][1])]
        self.alive = True
        self.reached_end = False
        
        # BTD6-style properties for targeting
        self.is_camo = False  # Can be detected by camo-detection towers only
        self.is_lead = False  # Requires lead-popping power
        self.path_position = 0.0  # Progress along path (0.0 to 1.0)
        
    def update(self):
        if not self.alive or self.reached_end:
            return
            
        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            self.path_position = 1.0  # Reached end of path
            return
            
        # Move towards next waypoint - optimized
        target = self.path[self.path_index + 1]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance_squared = dx * dx + dy * dy
        
        if distance_squared < 25: # Close enough to waypoint (5^2 = 25)
            self.path_index += 1
        else:
            # Move towards target - avoid sqrt when possible
            if distance_squared > 0:
                distance = math.sqrt(distance_squared)
                self.position[0] += (dx / distance) * self.speed
                self.position[1] += (dy / distance) * self.speed
        
        # Update path position for targeting priority
        self.path_position = self.path_index / max(1, len(self.path) - 1)
    
    def take_damage(self, damage: int):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
            return True # Bloon popped
        return False
    
    def draw(self, screen):
        if not self.alive:
            return
            
        # Draw bloon
        pygame.draw.circle(screen, self.color, 
                         (int(self.position[0]), int(self.position[1])), self.size)
        
        # Draw health indicator if damaged
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            bar_width = self.size * 2
            bar_height = 4
            bar_x = int(self.position[0] - bar_width // 2)
            bar_y = int(self.position[1] - self.size - 8)
            
            # Background
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
            # Health
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_ratio), bar_height))
