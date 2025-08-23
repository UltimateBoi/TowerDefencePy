#!/usr/bin/env python3
"""
Test script for the Tower Defense Game
Tests core game mechanics without GUI
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Import from the refactored game structure
from game.entities import Bloon, Tower, Projectile, BloonType
from game.systems import Wave, GameMap

def test_bloon_creation():
    """Test bloon creation and properties"""
    path = [(0, 0), (100, 0), (100, 100)]
    red_bloon = Bloon(BloonType.RED, path)
    
    assert red_bloon.health == 1
    assert red_bloon.speed == 1.0
    assert red_bloon.reward == 1
    assert red_bloon.alive == True
    print("✓ Bloon creation test passed")

def test_bloon_movement():
    """Test bloon movement along path"""
    path = [(0, 0), (100, 0), (100, 100)]
    bloon = Bloon(BloonType.RED, path)
    
    initial_pos = bloon.position[:]
    bloon.update()
    
   # Bloon should move towards next waypoint
    assert bloon.position[0] > initial_pos[0] or bloon.position[1] != initial_pos[1]
    print("✓ Bloon movement test passed")

def test_tower_targeting():
    """Test tower targeting system"""
    path = [(0, 0), (100, 0)]
    bloon = Bloon(BloonType.RED, path)
    tower = Tower((50, 0), range_val=60)
    
    target = tower.find_target([bloon])
    assert target == bloon
    print("✓ Tower targeting test passed")

def test_projectile_collision():
    """Test projectile hitting bloon"""
    path = [(0, 0), (100, 0)]
    bloon = Bloon(BloonType.BLUE, path) # 2 health
    projectile = Projectile((0, 0), bloon, damage=1)
    
    initial_health = bloon.health
    projectile.update() # Should hit immediately due to close distance
    
    assert bloon.health < initial_health
    print("✓ Projectile collision test passed")

def test_wave_spawning():
    """Test wave bloon spawning"""
    wave = Wave([BloonType.RED], [3], spawn_delay=0) # No delay for testing
    path = [(0, 0), (100, 0)]
    
    bloons_spawned = 0
    for i in range(5): # Try to spawn more than available
        bloon = wave.spawn_next_bloon(i * 1000, path)
        if bloon:
            bloons_spawned += 1
    
    assert bloons_spawned == 3 # Should only spawn 3 bloons
    assert wave.is_complete()
    print("✓ Wave spawning test passed")

def test_game_map():
    """Test game map functionality"""
    map_data = {
        "path": [(0, 0), (100, 0), (100, 100)],
        "spawn_point": (0, 0),
        "end_point": (100, 100)
    }
    
    game_map = GameMap(map_data)
    assert len(game_map.path) == 3
    assert game_map.spawn_point == (0, 0)
    assert game_map.end_point == (100, 100)
    print("✓ Game map test passed")

def test_tower_placement_collision():
    """Test tower placement collision detection"""
    from game.entities.tower import Tower
    
    map_data = {
        "path": [(50, 100), (150, 100), (250, 100)],
        "spawn_point": (50, 100),
        "end_point": (250, 100)
    }
    
    game_map = GameMap(map_data)
    towers = []
    
    # Test valid placement away from path
    assert game_map.can_place_tower((200, 200), towers)
    
    # Test invalid placement on path
    assert not game_map.can_place_tower((100, 100), towers)
    
    # Test invalid placement near spawn point
    assert not game_map.can_place_tower((50, 100), towers)
    
    # Place a tower and test collision with existing towers
    towers.append(Tower((200, 200)))
    
    # Test valid placement away from existing tower
    assert game_map.can_place_tower((300, 300), towers)
    
    # Test invalid placement too close to existing tower
    assert not game_map.can_place_tower((210, 210), towers)
    
    print("✓ Tower placement collision test passed")

def run_all_tests():
    """Run all tests"""
    print("Running Tower Defense Game Tests...")
    print("=" * 40)
    
    try:
        test_bloon_creation()
        test_bloon_movement()
        test_tower_targeting()
        test_projectile_collision()
        test_wave_spawning()
        test_game_map()
        test_tower_placement_collision()
        
        print("=" * 40)
        print("✓ All tests passed! The game mechanics are working correctly.")
        return True
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
