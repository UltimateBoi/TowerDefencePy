"""
Game map system for handling map data and rendering
"""
import pygame
import math
from typing import Tuple, List
from ..constants import BROWN, GREEN, RED


class GameMap:
    def __init__(self, map_data: dict):
        self.path = map_data.get("path", [])
        self.spawn_point = map_data.get("spawn_point", (50, 360))
        self.end_point = map_data.get("end_point", (1230, 360))
        self.placeable_areas = map_data.get("placeable_areas", [])
        
    def can_place_tower(self, position: Tuple[int, int], towers: List = None, tower_radius: int = None) -> bool:
        """
        Check if a tower can be placed at the given position
        
        Args:
            position: (x, y) position where tower wants to be placed
            towers: List of existing towers to check for collisions
            tower_radius: Radius of the tower for collision detection (defaults to Tower.TOWER_RADIUS)
            
        Returns:
            True if tower can be placed, False otherwise
        """
        if tower_radius is None:
            # Import here to avoid circular import
            from ..entities.tower import Tower
            tower_radius = Tower.TOWER_RADIUS
            
        x, y = position
        
        # Check if position is on the path
        if self._is_on_path(position, tower_radius):
            return False
            
        # Check if position collides with existing towers
        if towers and self._collides_with_towers(position, towers, tower_radius):
            return False
            
        # Check if position is within screen bounds (with margin for tower radius)
        if (x - tower_radius < 0 or x + tower_radius > 1280 or 
            y - tower_radius < 0 or y + tower_radius > 720):
            return False
            
        return True
    
    def _is_on_path(self, position: Tuple[int, int], tower_radius: int) -> bool:
        """Check if tower would overlap with the path"""
        if len(self.path) < 2:
            return False
            
        x, y = position
        path_width = 30 # Path is drawn with width 30
        
        # Check each path segment
        for i in range(len(self.path) - 1):
            start_point = self.path[i]
            end_point = self.path[i + 1]
            
            # Calculate distance from tower center to path segment
            distance = self._point_to_line_distance((x, y), start_point, end_point)
            
            # If tower would overlap with path (including buffer)
            if distance < tower_radius + path_width // 2:
                return True
                
        # Also check spawn and end points
        spawn_distance = math.sqrt((x - self.spawn_point[0])**2 + (y - self.spawn_point[1])**2)
        end_distance = math.sqrt((x - self.end_point[0])**2 + (y - self.end_point[1])**2)
        
        if spawn_distance < tower_radius + 25 or end_distance < tower_radius + 25:
            return True
            
        return False
    
    def _collides_with_towers(self, position: Tuple[int, int], towers: List, tower_radius: int) -> bool:
        """Check if tower would overlap with existing towers"""
        x, y = position
        
        for tower in towers:
            tower_x, tower_y = tower.position
            distance = math.sqrt((x - tower_x)**2 + (y - tower_y)**2)
            
            # Check if towers would overlap (each tower needs its radius of space)
            if distance < tower_radius * 2:
                return True
                
        return False
    
    def _point_to_line_distance(self, point: Tuple[int, int], line_start: Tuple[int, int], line_end: Tuple[int, int]) -> float:
        """Calculate the shortest distance from a point to a line segment"""
        px, py = point
        x1, y1 = line_start
        x2, y2 = line_end
        
        # Vector from line_start to line_end
        dx = x2 - x1
        dy = y2 - y1
        
        # If the line segment has zero length
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Parameter t represents position along the line segment
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        # Clamp t to [0, 1] to stay within the line segment
        t = max(0, min(1, t))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Return distance from point to closest point on line
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
        
    def draw(self, screen):
        # Draw grass background
        screen.fill((34, 139, 34))
        
        # Draw path
        if len(self.path) > 1:
            pygame.draw.lines(screen, BROWN, False, self.path, 30)
        
        # Draw spawn and end points
        pygame.draw.circle(screen, GREEN, self.spawn_point, 25)
        pygame.draw.circle(screen, RED, self.end_point, 25)
