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
    
    def __init__(self, position: Tuple[int, int], range_val: int = 100, damage: int = 1, 
                 fire_rate: float = 1.0, tower_type: str = "dart_monkey", 
                 pierce: int = 1, projectiles: int = 1):
        """Initialize the tower with BTD6-style parameters.

        Args:
            position (Tuple[int, int]): The position of the tower.
            range_val (int, optional): The attack range of the tower. Defaults to 100.
            damage (int, optional): The damage dealt by the tower. Defaults to 1.
            fire_rate (float, optional): The fire rate of the tower (shots per second). Defaults to 1.0.
            tower_type (str, optional): The type of tower. Defaults to "dart_monkey".
            pierce (int, optional): How many bloons projectiles can hit. Defaults to 1.
            projectiles (int, optional): Number of projectiles fired per shot. Defaults to 1.
        """
        self.position = position
        self.range = range_val
        self.damage = damage
        self.fire_rate = fire_rate # shots per second
        self.last_shot_time = 0
        self.target: Optional['Bloon'] = None
        self.tower_type = tower_type
        self.selected = False
        
        # BTD6 mechanics
        self.pierce = pierce
        self.projectiles = projectiles
        self.projectile_speed = 8.0
        self.targeting_mode = "first"  # first, last, close, strong
        
        # Special abilities
        self.can_see_camo = False
        self.can_pop_lead = False
        self.can_pop_frozen = True
        self.has_seeking = False
        self.explosion_radius = 0
        self.slow_effect = 0  # Seconds of slow applied
        self.special_effects = []  # List of special effects like "ricochet", "chain_lightning"
        
        # Upgrade tracking
        self.upgrade_levels = {"path1": 0, "path2": 0, "path3": 0}
        self.total_spent = 0
        self.base_cost = 0  # Will be set when tower is created
        
    def set_base_cost(self, cost: int):
        """Set the base cost of this tower (for sell price calculation)"""
        self.base_cost = cost
        self.total_spent = cost
        
    def get_sell_price(self) -> int:
        """Calculate sell price based on BTD6 formula (70% of total spent, rounded down)"""
        return int(self.total_spent * 0.7)
        
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the tower was clicked"""
        dx = pos[0] - self.position[0]
        dy = pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.TOWER_RADIUS
    
    def apply_upgrade(self, path: str, upgrade_data: dict):
        """Apply an upgrade to this tower"""
        stats = upgrade_data.get('stats', {})
        upgrade_cost = upgrade_data.get('cost', 0)
        
        # Track spending for sell price calculation
        self.total_spent += upgrade_cost
        
        # Apply stat modifications (add to current values, not set)
        if 'damage' in stats:
            self.damage += stats['damage']
        if 'range' in stats:
            self.range += stats['range']
        if 'fire_rate' in stats:
            self.fire_rate += stats['fire_rate']
        if 'pierce' in stats:
            self.pierce += stats['pierce']
        if 'projectiles' in stats:
            self.projectiles = stats['projectiles']
        if 'projectile_speed' in stats:
            self.projectile_speed += stats['projectile_speed']
        if 'explosion_radius' in stats:
            self.explosion_radius = stats['explosion_radius']
        if 'slow_effect' in stats:
            self.slow_effect = stats['slow_effect']
        
        # Special abilities
        if 'can_see_camo' in stats:
            self.can_see_camo = stats['can_see_camo']
        if 'can_pop_lead' in stats:
            self.can_pop_lead = stats['can_pop_lead']
        if 'has_seeking' in stats:
            self.has_seeking = stats['has_seeking']
        if 'special_effects' in stats:
            self.special_effects.extend(stats['special_effects'])
        
        # Track upgrade level
        path_num = path[-1] # Extract number from "path1", "path2", etc.
        self.upgrade_levels[path] += 1
        
        print(f"Tower upgraded: {upgrade_data['name']} - New stats: DMG:{self.damage} RNG:{self.range} FR:{self.fire_rate:.2f} PIERCE:{self.pierce}")
        print(f"Total spent: ${self.total_spent}, Sell value: ${self.get_sell_price()}")

    def can_target_bloon(self, bloon: 'Bloon') -> bool:
        """Check if this tower can target a specific bloon type"""
        # Add camo detection logic
        if hasattr(bloon, 'is_camo') and bloon.is_camo and not self.can_see_camo:
            return False
        
        # Add lead popping logic
        if hasattr(bloon, 'is_lead') and bloon.is_lead and not self.can_pop_lead:
            return False
            
        return True

    def can_shoot(self, current_time: float) -> bool:
        return current_time - self.last_shot_time >= (1000 / self.fire_rate) # Convert to milliseconds
    
    def find_target(self, bloons: List['Bloon']) -> Optional['Bloon']:
        """Find a target bloon based on targeting mode"""
        targets_in_range = []
        
        for bloon in bloons:
            if not bloon.alive:
                continue
                
            distance = ((self.position[0] - bloon.position[0]) ** 2 + (self.position[1] - bloon.position[1]) ** 2) ** 0.5
            if distance <= self.range and self.can_target_bloon(bloon):
                targets_in_range.append((bloon, distance))
        
        if not targets_in_range:
            return None
        
        # Sort based on targeting mode
        if self.targeting_mode == "first":
            # Target bloon that has traveled furthest along the path
            return max(targets_in_range, key=lambda x: x[0].path_index)[0]
        elif self.targeting_mode == "last":
            # Target bloon that has traveled least along the path
            return min(targets_in_range, key=lambda x: x[0].path_index)[0]
        elif self.targeting_mode == "close":
            # Target closest bloon
            return min(targets_in_range, key=lambda x: x[1])[0]
        elif self.targeting_mode == "strong":
            # Target bloon with highest health
            return max(targets_in_range, key=lambda x: x[0].health)[0]
        else:
            # Default to first targeting
            return max(targets_in_range, key=lambda x: x[0].path_index)[0]
    
    def fire_projectiles(self, target: 'Bloon', current_time: float) -> list:
        """Fire projectiles at target and return list of projectile objects"""
        if not self.can_shoot(current_time):
            return []
            
        self.last_shot_time = current_time
        from .projectile import Projectile
        import math
        
        projectiles = []
        
        if self.tower_type == "tack_shooter":
            # Fire projectiles in all directions (8 directions for Tack Shooter)
            directions = 8
            for i in range(directions):
                angle = (2 * math.pi * i) / directions
                proj_x = self.position[0] + math.cos(angle) * 30
                proj_y = self.position[1] + math.sin(angle) * 30
                
                # Calculate target position in that direction
                target_x = self.position[0] + math.cos(angle) * self.range
                target_y = self.position[1] + math.sin(angle) * self.range
                
                projectile = Projectile(
                    start_pos=(proj_x, proj_y),
                    target_pos=(target_x, target_y),
                    damage=self.damage,
                    speed=self.projectile_speed,
                    pierce=self.pierce,
                    has_seeking=self.has_seeking
                )
                projectiles.append(projectile)
        else:
            # Standard single or multi-projectile towers (like Dart Monkey)
            for i in range(self.projectiles):
                # Add slight spread for multiple projectiles
                spread_angle = 0
                if self.projectiles > 1:
                    spread_angle = (i - (self.projectiles - 1) / 2) * 0.1  # Small spread
                
                # Calculate angle to target
                dx = target.position[0] - self.position[0]
                dy = target.position[1] - self.position[1]
                base_angle = math.atan2(dy, dx)
                final_angle = base_angle + spread_angle
                
                # Calculate projectile spawn position
                spawn_distance = 15  # Distance from tower center
                proj_x = self.position[0] + math.cos(final_angle) * spawn_distance
                proj_y = self.position[1] + math.sin(final_angle) * spawn_distance
                
                projectile = Projectile(
                    start_pos=(proj_x, proj_y),
                    target_pos=target.position,
                    damage=self.damage,
                    speed=self.projectile_speed,
                    pierce=self.pierce,
                    has_seeking=self.has_seeking
                )
                projectiles.append(projectile)
        
        return projectiles

    def shoot(self, current_time: float) -> Optional['Projectile']:
        """Legacy method for compatibility - use fire_projectiles instead"""
        if self.target and self.target.alive and self.can_shoot(current_time):
            projectiles = self.fire_projectiles(self.target, current_time)
            return projectiles[0] if projectiles else None
        return None
    
    def update(self, bloons: List['Bloon'], current_time: float) -> List['Projectile']:
        """Update tower and return list of projectiles fired this frame"""
        # Find new target if current target is invalid
        if not self.target or not self.target.alive:
            self.target = self.find_target(bloons)
        
        # Fire projectiles at target
        if self.target and self.target.alive:
            return self.fire_projectiles(self.target, current_time)
        
        return []
    
    def cycle_targeting_mode(self):
        """Cycle through targeting modes: first -> last -> close -> strong -> first"""
        modes = ["first", "last", "close", "strong"]
        current_index = modes.index(self.targeting_mode)
        next_index = (current_index + 1) % len(modes)
        self.targeting_mode = modes[next_index]
        print(f"Tower targeting mode changed to: {self.targeting_mode}")

    def get_targeting_mode_display(self) -> str:
        """Get display string for current targeting mode"""
        mode_names = {
            "first": "First",
            "last": "Last", 
            "close": "Close",
            "strong": "Strong"
        }
        return mode_names.get(self.targeting_mode, "First")

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
        
        # Show targeting mode when selected
        if self.selected:
            font = pygame.font.SysFont(None, 20)
            mode_text = font.render(f"Target: {self.get_targeting_mode_display()}", True, (255, 255, 255))
            text_rect = mode_text.get_rect(center=(self.position[0], self.position[1] - 40))
            
            # Draw background for text
            padding = 5
            bg_rect = text_rect.inflate(padding * 2, padding * 2)
            pygame.draw.rect(screen, (0, 0, 0), bg_rect)
            
            screen.blit(mode_text, text_rect)
