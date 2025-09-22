"""
Projectile entity class with BTD6-style mechanics
"""
import pygame
import math
from typing import Tuple, TYPE_CHECKING, List, Optional
from ..constants import BLACK

if TYPE_CHECKING:
    from .bloon import Bloon


class Projectile:
    def __init__(self, start_pos: Tuple[float, float], target_pos: Tuple[float, float] = None, 
                 damage: int = 1, speed: float = 5.0, pierce: int = 1, has_seeking: bool = False):
        """Initialize the projectile with BTD6-style parameters.

        Args:
            start_pos (Tuple[float, float]): The starting position of the projectile.
            target_pos (Tuple[float, float]): The target position (for non-seeking projectiles).
            damage (int): The damage dealt by the projectile.
            speed (float): The speed of the projectile.
            pierce (int): How many bloons this projectile can hit before expiring.
            has_seeking (bool): Whether the projectile seeks targets automatically.
        """
        self.position = [float(start_pos[0]), float(start_pos[1])]
        self.target_pos = target_pos if target_pos else start_pos
        self.damage = damage
        self.speed = speed
        self.pierce = pierce
        self.pierce_remaining = pierce
        self.has_seeking = has_seeking
        self.alive = True
        self.hit_bloons = set()  # Track which bloons we've already hit
        
        # Calculate initial direction
        if target_pos:
            dx = target_pos[0] - start_pos[0]
            dy = target_pos[1] - start_pos[1]
            distance = math.sqrt(dx * dx + dy * dy)
            if distance > 0:
                self.velocity = [dx / distance * speed, dy / distance * speed]
            else:
                self.velocity = [0, 0]
        else:
            self.velocity = [0, 0]
        
        self.lifetime = 0
        self.max_lifetime = 300  # Projectiles expire after 5 seconds at 60fps

    def find_nearest_target(self, bloons: List['Bloon']) -> Optional['Bloon']:
        """Find the nearest bloon that hasn't been hit yet"""
        if not self.has_seeking:
            return None
            
        nearest_bloon = None
        nearest_distance = float('inf')
        
        for bloon in bloons:
            if not bloon.alive or bloon in self.hit_bloons:
                continue
                
            distance = math.sqrt(
                (bloon.position[0] - self.position[0]) ** 2 + 
                (bloon.position[1] - self.position[1]) ** 2
            )
            
            if distance < nearest_distance and distance < 100:  # Seeking range
                nearest_distance = distance
                nearest_bloon = bloon
                
        return nearest_bloon

    def update(self, bloons: List['Bloon'] = None):
        """Update projectile position and handle collisions"""
        if not self.alive:
            return
            
        self.lifetime += 1
        if self.lifetime > self.max_lifetime:
            self.alive = False
            return
        
        # Seeking behavior - optimized distance calculation
        if self.has_seeking and bloons:
            target = self.find_nearest_target(bloons)
            if target:
                dx = target.position[0] - self.position[0]
                dy = target.position[1] - self.position[1]
                distance_squared = dx * dx + dy * dy
                if distance_squared > 0:
                    # Only calculate sqrt when we need the actual distance
                    distance = math.sqrt(distance_squared)
                    self.velocity[0] = (dx / distance) * self.speed
                    self.velocity[1] = (dy / distance) * self.speed
        
        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        
        # Check for collisions with bloons - optimized
        if bloons:
            for bloon in bloons:
                if not bloon.alive or bloon in self.hit_bloons:
                    continue
                
                # Use squared distance to avoid sqrt calculation
                dx = bloon.position[0] - self.position[0]
                dy = bloon.position[1] - self.position[1]
                distance_squared = dx * dx + dy * dy
                
                # Enhanced collision detection - use bloon's actual size plus small projectile buffer
                collision_radius = bloon.size + 3  # Bloon radius + small projectile radius
                collision_radius_squared = collision_radius * collision_radius
                
                if distance_squared <= collision_radius_squared:
                    bloon.take_damage(self.damage)
                    self.hit_bloons.add(bloon)
                    self.pierce_remaining -= 1
                    
                    if self.pierce_remaining <= 0:
                        self.alive = False
                        break
        
        # Check if projectile is off-screen (basic bounds checking)
        if (self.position[0] < -50 or self.position[0] > 850 or 
            self.position[1] < -50 or self.position[1] > 650):
            self.alive = False
    
    def draw(self, screen):
        """Draw the projectile"""
        if self.alive:
            # Draw projectile as a small circle
            pygame.draw.circle(screen, BLACK, (int(self.position[0]), int(self.position[1])), 3)
            
            # Optional: Draw trail for seeking projectiles
            if self.has_seeking:
                pygame.draw.circle(screen, (255, 255, 0), (int(self.position[0]), int(self.position[1])), 2)
