"""
Game map system for handling map data and rendering
"""
import pygame
from typing import Tuple
from ..constants import BROWN, GREEN, RED


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
