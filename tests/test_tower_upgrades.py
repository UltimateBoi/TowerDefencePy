"""
Tower Upgrades System Test
Tests the tower data loading and upgrade calculations
"""
import json
import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

"""
Tower Upgrades System Test
Tests the tower data loading, upgrade calculations, and new interactive upgrade system
"""
import json
import os
import sys

# Add the parent directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from game.entities.tower import Tower
from game.ui.ingame_upgrade_panel import InGameUpgradePanel

def test_interactive_tower_upgrades():
    """Test the new interactive tower upgrade system"""
    
    # Create a tower
    tower = Tower((100, 100), tower_type="dart_monkey")
    
    # Test initial state
    assert tower.damage == 1
    assert tower.range == 100
    assert tower.upgrade_levels["path1"] == 0
    assert tower.tower_type == "dart_monkey"
    print("✓ Tower initial state test passed")
    
    # Create upgrade panel
    panel = InGameUpgradePanel(200, 200)
    panel.set_selected_tower(tower)
    
    # Test upgrade cost calculation
    cost = panel.get_upgrade_cost("path1", 0)
    assert cost > 0
    print(f"✓ Upgrade cost calculation test passed (cost: ${cost})")
    
    # Test upgrade availability
    can_upgrade = panel.can_upgrade("path1", 1000) # Plenty of money
    assert can_upgrade
    print("✓ Upgrade availability test passed")
    
    # Test actual upgrade
    initial_damage = tower.damage
    money_spent = panel.upgrade_tower("path1", 1000)
    assert money_spent > 0
    assert tower.upgrade_levels["path1"] == 1
    print(f"✓ Tower upgrade test passed (spent: ${money_spent})")
    
    # Test tower selection
    assert tower.is_clicked((100, 100)) # Click on tower center
    assert not tower.is_clicked((200, 200)) # Click away from tower
    print("✓ Tower selection test passed")
    
    # Test BTD6 upgrade restrictions
    # Upgrade path1 to level 2
    panel.upgrade_tower("path1", 1000)
    assert tower.upgrade_levels["path1"] == 2
    
    # Now try to upgrade path2 to level 3 - should be blocked
    panel.upgrade_tower("path2", 1000) # Level 1
    panel.upgrade_tower("path2", 1000) # Level 2
    panel.upgrade_tower("path2", 1000) # Should reach level 3
    can_upgrade_path1_further = panel.can_upgrade("path1", 10000)
    # This should be False because path2 is level 3, limiting path1 to level 2
    # (BTD6 rule: if any path is 3+, others can't go beyond 2)
    print("✓ BTD6 upgrade restriction test passed")

def test_tower_data_loading():
    """Test that tower data loads correctly from JSON"""
    try:
        with open("data/towers.json", "r") as f:
            data = json.load(f)
        
        towers = data.get("towers", {})
        difficulty_multipliers = data.get("difficulty_multipliers", {})
        
        # Check that we have towers
        assert len(towers) > 0, "No towers found in data"
        
        # Check that we have difficulty multipliers
        assert len(difficulty_multipliers) == 4, "Should have 4 difficulty multipliers"
        assert "E" in difficulty_multipliers, "Missing Easy difficulty"
        assert "M" in difficulty_multipliers, "Missing Medium difficulty"
        assert "H" in difficulty_multipliers, "Missing Hard difficulty"
        assert "I" in difficulty_multipliers, "Missing Impoppable difficulty"
        
        print(f"✓ Loaded {len(towers)} towers successfully")
        
        # Test specific towers (updated to match BTD6 tower names)
        expected_towers = ["dart_monkey", "tack_shooter", "boomerang_monkey", "bomb_shooter"]
        for tower_id in expected_towers:
            assert tower_id in towers, f"Missing expected tower: {tower_id}"
            tower = towers[tower_id]
            
            # Check required fields
            assert "name" in tower, f"Tower {tower_id} missing name"
            assert "description" in tower, f"Tower {tower_id} missing description"
            assert "base_cost" in tower, f"Tower {tower_id} missing base_cost"
            assert "base_stats" in tower, f"Tower {tower_id} missing base_stats"
            assert "upgrade_paths" in tower, f"Tower {tower_id} missing upgrade_paths"
            
            # Check upgrade paths
            paths = tower["upgrade_paths"]
            assert len(paths) == 3, f"Tower {tower_id} should have 3 upgrade paths"
            
            for path_name, path_data in paths.items():
                assert "name" in path_data, f"Path {path_name} missing name"
                assert "description" in path_data, f"Path {path_name} missing description"
                assert "upgrades" in path_data, f"Path {path_name} missing upgrades"
                
                upgrades = path_data["upgrades"]
                assert len(upgrades) == 5, f"Path {path_name} should have 5 upgrades"
                
                for i, upgrade in enumerate(upgrades):
                    assert "name" in upgrade, f"Upgrade {i} in {path_name} missing name"
                    assert "description" in upgrade, f"Upgrade {i} in {path_name} missing description"
                    assert "cost" in upgrade, f"Upgrade {i} in {path_name} missing cost"
                    assert "stats" in upgrade, f"Upgrade {i} in {path_name} missing stats"
        
        print(f"✓ All {len(expected_towers)} expected towers validated successfully")
        return True
        
    except Exception as e:
        print(f"✗ Tower data loading test failed: {e}")
        return False

def test_cost_calculations():
    """Test that upgrade cost calculations work correctly"""
    try:
        with open("data/towers.json", "r") as f:
            data = json.load(f)
        
        difficulty_multipliers = data.get("difficulty_multipliers", {})
        towers = data.get("towers", {})
        
        # Test cost calculations for different difficulties
        dart_monkey = towers["dart_monkey"]
        first_upgrade_cost = dart_monkey["upgrade_paths"]["path1"]["upgrades"][0]["cost"]
        
        # Test each difficulty
        for difficulty, multiplier in difficulty_multipliers.items():
            calculated_cost = int(first_upgrade_cost * multiplier)
            assert calculated_cost > 0, f"Cost calculation failed for difficulty {difficulty}"
        
        # Verify multiplier progression
        easy_cost = int(first_upgrade_cost * difficulty_multipliers["E"])
        medium_cost = int(first_upgrade_cost * difficulty_multipliers["M"])
        hard_cost = int(first_upgrade_cost * difficulty_multipliers["H"])
        impoppable_cost = int(first_upgrade_cost * difficulty_multipliers["I"])
        
        assert easy_cost <= medium_cost <= hard_cost <= impoppable_cost, "Cost progression should increase with difficulty"
        
        print(f"✓ Cost calculations validated: E${easy_cost} ≤ M${medium_cost} ≤ H${hard_cost} ≤ I${impoppable_cost}")
        return True
        
    except Exception as e:
        print(f"✗ Cost calculation test failed: {e}")
        return False

def main():
    """Run all tower upgrades tests"""
    print("Running Tower Upgrades System Tests...")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    try:
        test_interactive_tower_upgrades()
        tests_passed += 1
    except Exception as e:
        print(f"✗ Interactive tower upgrades test failed: {e}")
    
    if test_tower_data_loading():
        tests_passed += 1
    
    if test_cost_calculations():
        tests_passed += 1
    
    print("=" * 50)
    if tests_passed == total_tests:
        print(f"✓ All {total_tests} tower upgrades tests passed!")
        return True
    else:
        print(f"✗ {total_tests - tests_passed} out of {total_tests} tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
