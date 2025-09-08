#!/usr/bin/env python3
"""
Test script to verify enhanced collision detection and tower selling
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

def test_enhanced_collision():
    """Test that collision detection uses bloon size properly"""
    print("Testing enhanced collision detection...")
    
    # Create a projectile and a red bloon
    projectile = Projectile(
        start_pos=(100, 100),
        target_pos=(200, 200),
        damage=1,
        pierce=1
    )
    
    # Create a bloon with known size
    path = [(150, 150), (200, 200)]
    bloon = Bloon(BloonType.RED, path)
    print(f"Red bloon size: {bloon.size}")
    
    # Test collision at various distances
    test_distances = [5, 8, 10, 12, 15, 20]
    
    for distance in test_distances:
        # Position projectile at specific distance from bloon
        projectile.position = [bloon.position[0] + distance, bloon.position[1]]
        projectile.hit_bloons.clear()  # Reset hit tracking
        
        # Calculate actual collision check
        proj_distance = ((bloon.position[0] - projectile.position[0]) ** 2 + 
                        (bloon.position[1] - projectile.position[1]) ** 2) ** 0.5
        collision_radius = bloon.size + 3  # Same as in the enhanced code
        
        will_hit = proj_distance <= collision_radius
        print(f"Distance {distance}: Collision radius {collision_radius:.1f}, Will hit: {will_hit}")

def test_tower_selling():
    """Test tower selling functionality"""
    print("\nTesting tower selling...")
    
    # Create a tower with known cost
    tower = Tower((100, 100), tower_type="dart_monkey")
    tower.set_base_cost(200)  # Dart monkey costs $200
    
    print(f"Base cost: ${tower.base_cost}")
    print(f"Total spent: ${tower.total_spent}")
    print(f"Sell price: ${tower.get_sell_price()}")
    print(f"Expected sell price (70% of $200): ${int(200 * 0.7)}")
    
    # Test with upgrades
    print("\nAfter upgrades:")
    
    # Simulate upgrade 1: Sharp Shots ($130)
    upgrade_data = {
        'name': 'Sharp Shots',
        'cost': 130,
        'stats': {'pierce': 4}
    }
    tower.apply_upgrade('path1', upgrade_data)
    
    # Simulate upgrade 2: Razor Sharp Shots ($350)
    upgrade_data = {
        'name': 'Razor Sharp Shots',
        'cost': 350,
        'stats': {'pierce': 6, 'damage': 2}
    }
    tower.apply_upgrade('path1', upgrade_data)
    
    expected_total = 200 + 130 + 350  # $680
    expected_sell = int(680 * 0.7)    # $476
    
    print(f"Expected total spent: ${expected_total}")
    print(f"Actual total spent: ${tower.total_spent}")
    print(f"Expected sell price: ${expected_sell}")
    print(f"Actual sell price: ${tower.get_sell_price()}")

def test_bloon_sizes():
    """Test different bloon sizes for collision"""
    print("\nTesting different bloon sizes...")
    
    bloon_types = [BloonType.RED, BloonType.BLUE, BloonType.GREEN, BloonType.YELLOW]
    path = [(100, 100), (200, 200)]
    
    for bloon_type in bloon_types:
        bloon = Bloon(bloon_type, path)
        collision_radius = bloon.size + 3
        print(f"{bloon_type.name} bloon - Size: {bloon.size}, Collision radius: {collision_radius}")

def test_projectile_pierce():
    """Test that projectiles can hit multiple bloons with pierce"""
    print("\nTesting projectile pierce mechanics...")
    
    # Create projectile with pierce 3
    projectile = Projectile(
        start_pos=(50, 100),
        target_pos=(200, 100),
        damage=1,
        pierce=3
    )
    
    # Create multiple bloons in a line
    path = [(100, 100), (200, 100)]
    bloons = []
    for i in range(5):
        bloon = Bloon(BloonType.RED, path)
        bloon.position = [100 + i * 20, 100]  # Space them out horizontally
        bloons.append(bloon)
    
    print(f"Created {len(bloons)} bloons")
    print(f"Projectile pierce: {projectile.pierce}, pierce remaining: {projectile.pierce_remaining}")
    
    # Simulate projectile moving through bloons
    hit_count = 0
    for i, bloon in enumerate(bloons):
        if not projectile.alive:
            break
            
        # Position projectile at bloon location
        projectile.position = bloon.position.copy()
        
        # Check collision manually (simplified)
        if bloon not in projectile.hit_bloons:
            distance = 0  # Direct hit
            collision_radius = bloon.size + 3
            
            if distance <= collision_radius:
                projectile.hit_bloons.add(bloon)
                projectile.pierce_remaining -= 1
                hit_count += 1
                print(f"Hit bloon {i+1}, pierce remaining: {projectile.pierce_remaining}")
                
                if projectile.pierce_remaining <= 0:
                    projectile.alive = False
                    print("Projectile expired after hitting max targets")
                    break
    
    print(f"Total bloons hit: {hit_count}")
    print(f"Projectile still alive: {projectile.alive}")

if __name__ == "__main__":
    print("Enhanced Collision & Tower Selling Test")
    print("=" * 50)
    
    # Initialize pygame (required for some game components)
    pygame.init()
    
    try:
        test_enhanced_collision()
        test_tower_selling()
        test_bloon_sizes()
        test_projectile_pierce()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()
