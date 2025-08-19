import pygame
import json
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)

class BloonType(Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"

@dataclass
class BloonProperties:
    health: int
    speed: float
    reward: int
    color: Tuple[int, int, int]
    size: int

# Bloon type properties
BLOON_PROPERTIES = {
    BloonType.RED: BloonProperties(1, 1.0, 1, RED, 15),
    BloonType.BLUE: BloonProperties(2, 1.2, 2, BLUE, 15),
    BloonType.GREEN: BloonProperties(3, 1.5, 3, GREEN, 15),
    BloonType.YELLOW: BloonProperties(4, 2.0, 4, YELLOW, 15),
}

class Bloon:
    def __init__(self, bloon_type: BloonType, path: List[Tuple[int, int]]):
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
        
    def update(self):
        if not self.alive or self.reached_end:
            return
            
        if self.path_index >= len(self.path) - 1:
            self.reached_end = True
            return
            
       # Move towards next waypoint
        target = self.path[self.path_index + 1]
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < 5: # Close enough to waypoint
            self.path_index += 1
        else:
           # Move towards target
            self.position[0] += (dx / distance) * self.speed
            self.position[1] += (dy / distance) * self.speed
    
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

class Projectile:
    def __init__(self, start_pos: Tuple[float, float], target: Bloon, damage: int, speed: float = 5.0):
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
        
        if distance < 5: # Hit target
            self.target.take_damage(self.damage)
            self.alive = False
        else:
           # Move towards target
            self.position[0] += (dx / distance) * self.speed
            self.position[1] += (dy / distance) * self.speed
    
    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, BLACK, (int(self.position[0]), int(self.position[1])), 3)

class Tower:
    def __init__(self, position: Tuple[int, int], range_val: int = 100, damage: int = 1, fire_rate: float = 1.0):
        self.position = position
        self.range = range_val
        self.damage = damage
        self.fire_rate = fire_rate # shots per second
        self.last_shot_time = 0
        self.target: Optional[Bloon] = None
        
    def can_shoot(self, current_time: float) -> bool:
        return current_time - self.last_shot_time >= (1000 / self.fire_rate) # Convert to milliseconds
    
    def find_target(self, bloons: List[Bloon]) -> Optional[Bloon]:
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
    
    def shoot(self, current_time: float) -> Optional[Projectile]:
        if self.target and self.target.alive and self.can_shoot(current_time):
            self.last_shot_time = current_time
            return Projectile(self.position, self.target, self.damage)
        return None
    
    def update(self, bloons: List[Bloon], current_time: float) -> Optional[Projectile]:
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

class Wave:
    def __init__(self, bloon_types: List[BloonType], counts: List[int], spawn_delay: float = 1000):
        self.bloon_types = bloon_types
        self.counts = counts
        self.spawn_delay = spawn_delay # milliseconds between spawns
        self.spawned = 0
        self.total_bloons = sum(counts)
        self.last_spawn_time = 0
        self.current_type_index = 0
        self.current_type_count = 0
        
    def spawn_next_bloon(self, current_time: float, path: List[Tuple[int, int]]) -> Optional[Bloon]:
        if self.spawned >= self.total_bloons:
            return None
            
        if current_time - self.last_spawn_time < self.spawn_delay:
            return None
        
       # Spawn bloon of current type
        if self.current_type_index < len(self.bloon_types):
            bloon_type = self.bloon_types[self.current_type_index]
            bloon = Bloon(bloon_type, path)
            
            self.spawned += 1
            self.current_type_count += 1
            self.last_spawn_time = current_time
            
           # Move to next type if current type is exhausted
            if self.current_type_count >= self.counts[self.current_type_index]:
                self.current_type_index += 1
                self.current_type_count = 0
            
            return bloon
        
        return None
    
    def is_complete(self) -> bool:
        return self.spawned >= self.total_bloons

class GameMap:
    def __init__(self, map_data: dict):
        self.path = map_data.get("path", [])
        self.spawn_point = map_data.get("spawn_point", (50, 360))
        self.end_point = map_data.get("end_point", (1230, 360))
        self.placeable_areas = map_data.get("placeable_areas", [])
        
    def can_place_tower(self, position: Tuple[int, int]) -> bool:
       # Simple implementation: can place anywhere except on path
       # In a real game, you'd check against placeable_areas
        return True # For now, allow placing anywhere
    
    def draw(self, screen):
       # Draw grass background
        screen.fill((34, 139, 34))
        
       # Draw path
        if len(self.path) > 1:
            pygame.draw.lines(screen, BROWN, False, self.path, 30)
        
       # Draw spawn and end points
        pygame.draw.circle(screen, GREEN, self.spawn_point, 25)
        pygame.draw.circle(screen, RED, self.end_point, 25)

class GameUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
    def draw(self, screen, money: int, lives: int, wave_number: int):
       # Draw money
        money_text = self.font.render(f"Money: ${money}", True, WHITE)
        screen.blit(money_text, (10, 10))
        
       # Draw lives
        lives_text = self.font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(lives_text, (10, 50))
        
       # Draw wave
        wave_text = self.font.render(f"Wave: {wave_number}", True, WHITE)
        screen.blit(wave_text, (10, 90))
        
       # Draw tower placement hint
        hint_text = self.small_font.render("Click to place tower ($10)", True, WHITE)
        screen.blit(hint_text, (10, SCREEN_HEIGHT - 30))

class TowerDefenseGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tower Defense Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
       # Game state
        self.money = 50
        self.lives = 20
        self.wave_number = 1
        self.game_over = False
        
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
                if event.key == pygame.K_SPACE and not self.wave_active:
                    self.start_wave()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.place_tower(mouse_pos)
    
    def place_tower(self, position: Tuple[int, int]):
        tower_cost = 10
        if self.money >= tower_cost and self.game_map.can_place_tower(position):
            self.towers.append(Tower(position))
            self.money -= tower_cost
    
    def update(self):
        if self.game_over:
            return
            
        current_time = pygame.time.get_ticks()
        
       # Spawn bloons
        if self.wave_active and self.current_wave:
            new_bloon = self.current_wave.spawn_next_bloon(current_time, self.game_map.path)
            if new_bloon:
                self.bloons.append(new_bloon)
            
           # Check if wave is complete
            if self.current_wave.is_complete() and all(not bloon.alive or bloon.reached_end for bloon in self.bloons):
                self.wave_active = False
                self.wave_number += 1
               # Clear dead bloons
                self.bloons = [bloon for bloon in self.bloons if bloon.alive and not bloon.reached_end]
        
       # Update bloons
        for bloon in self.bloons[:]:
            bloon.update()
            if bloon.reached_end:
                self.lives -= 1
                self.bloons.remove(bloon)
                if self.lives <= 0:
                    self.game_over = True
        
       # Update towers and create projectiles
        for tower in self.towers:
            projectile = tower.update(self.bloons, current_time)
            if projectile:
                self.projectiles.append(projectile)
        
       # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.alive:
                self.projectiles.remove(projectile)
        
       # Remove dead bloons and award money
        for bloon in self.bloons[:]:
            if not bloon.alive:
                self.money += bloon.reward
                self.bloons.remove(bloon)
    
    def draw(self):
       # Draw map
        self.game_map.draw(self.screen)
        
       # Draw towers
        for tower in self.towers:
            tower.draw(self.screen)
        
       # Draw bloons
        for bloon in self.bloons:
            bloon.draw(self.screen)
        
       # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
       # Draw UI
        self.ui.draw(self.screen, self.money, self.lives, self.wave_number)
        
       # Draw game over screen
        if self.game_over:
            game_over_text = pygame.font.SysFont(None, 72).render("GAME OVER", True, RED)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(game_over_text, text_rect)
        
       # Draw wave start hint
        if not self.wave_active and self.wave_number <= len(self.waves) and not self.game_over:
            hint_text = pygame.font.SysFont(None, 36).render("Press SPACE to start next wave", True, WHITE)
            text_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(hint_text, text_rect)
        
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
