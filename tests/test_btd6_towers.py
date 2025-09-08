#!/usr/bin/env python3
"""
Test script to verify BTD6-style tower mechanics are working
"""
import pygame
import sys
import os

# Add the current directory to the path so we can import our game modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.entities.tower import Tower
from game.entities.bloon import Bloon
from game.entities.bloon_types import BloonType
from game.entities.projectile import Projectile

def test_tower_creation():
    """Test that towers are created with BTD6 properties"""
    print("Testing tower creation...")
    
    # Test Dart Monkey
    dart_monkey = Tower((100, 100), tower_type="dart_monkey", pierce=1, projectiles=1)
    print(f"Dart Monkey - Pierce: {dart_monkey.pierce}, Projectiles: {dart_monkey.projectiles}")
    print(f"Dart Monkey - Targeting: {dart_monkey.targeting_mode}")
    print(f"Dart Monkey - Can see camo: {dart_monkey.can_see_camo}")
    
    # Test Tack Shooter  
    tack_shooter = Tower((200, 200), tower_type="tack_shooter", pierce=1, projectiles=8)
    print(f"Tack Shooter - Pierce: {tack_shooter.pierce}, Projectiles: {tack_shooter.projectiles}")
    print(f"Tack Shooter - Targeting: {tack_shooter.targeting_mode}")

def test_targeting_modes():
    """Test targeting mode cycling"""
    print("\nTesting targeting modes...")
    
    tower = Tower((100, 100), tower_type="dart_monkey")
    print(f"Initial mode: {tower.targeting_mode}")
    
    tower.cycle_targeting_mode()
    print(f"After cycle 1: {tower.targeting_mode}")
    
    tower.cycle_targeting_mode()
    print(f"After cycle 2: {tower.targeting_mode}")
    
    tower.cycle_targeting_mode()  
    print(f"After cycle 3: {tower.targeting_mode}")
    
    tower.cycle_targeting_mode()
    print(f"After cycle 4 (should be back to first): {tower.targeting_mode}")

def test_projectile_creation():
    """Test projectile creation with BTD6 mechanics"""
    print("\nTesting projectile creation...")
    
    # Create a basic projectile
    proj = Projectile(
        start_pos=(100, 100),
        target_pos=(200, 200),
        damage=2,
        pierce=3,
        has_seeking=True
    )
    
    print(f"Projectile - Damage: {proj.damage}, Pierce: {proj.pierce}")
    print(f"Projectile - Has seeking: {proj.has_seeking}")
    print(f"Projectile - Pierce remaining: {proj.pierce_remaining}")

def test_bloon_properties():
    """Test bloon BTD6 properties"""
    print("\nTesting bloon properties...")
    
    # Create a test path
    path = [(0, 100), (100, 100), (200, 100)]
    bloon = Bloon(BloonType.RED, path)
    
    print(f"Bloon - Is camo: {bloon.is_camo}")
    print(f"Bloon - Is lead: {bloon.is_lead}")
    print(f"Bloon - Path position: {bloon.path_position}")
    
    # Simulate bloon movement
    bloon.update()
    print(f"After update - Path position: {bloon.path_position}")

def test_multi_projectiles():
    """Test firing multiple projectiles"""
    print("\nTesting multi-projectile firing...")
    
    # Create towers with proper projectile counts
    dart_monkey = Tower((100, 100), tower_type="dart_monkey", projectiles=1)
    tack_shooter = Tower((200, 200), tower_type="tack_shooter", projectiles=8)
    
    # Create a target bloon
    path = [(300, 300), (400, 400)]
    target_bloon = Bloon(BloonType.RED, path)
    
    # Set last_shot_time to allow firing (simulate time has passed)
    import time
    current_time = time.time() * 1000  # Convert to milliseconds
    dart_monkey.last_shot_time = current_time - 2000  # 2 seconds ago
    tack_shooter.last_shot_time = current_time - 2000  # 2 seconds ago
    
    # Test dart monkey projectiles (should be 1)
    dart_projectiles = dart_monkey.fire_projectiles(target_bloon, current_time)
    print(f"Dart Monkey fired {len(dart_projectiles)} projectiles")
    
    # Test tack shooter projectiles (should be 8 in all directions)
    tack_projectiles = tack_shooter.fire_projectiles(target_bloon, current_time)
    print(f"Tack Shooter fired {len(tack_projectiles)} projectiles")

if __name__ == "__main__":
    print("BTD6 Tower Mechanics Test")
    print("=" * 40)
    
    # Initialize pygame (required for some game components)
    pygame.init()
    
    try:
        test_tower_creation()
        test_targeting_modes()
        test_projectile_creation()
        test_bloon_properties()
        test_multi_projectiles()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
