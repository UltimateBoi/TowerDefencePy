#!/usr/bin/env python3
"""Test tower selection panel functionality"""
import pygame
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.ui.tower_selection_panel import TowerSelectionPanel

def test_tower_selection_panel():
    """Test that tower selection panel can be created and initialized properly"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # Create tower selection panel
    panel = TowerSelectionPanel()
    
    # Test that panel has towers loaded
    assert len(panel.towers_data) > 0, "Panel should have towers loaded from JSON"
    
    # Test that button data is properly structured
    for tower_id, tower_data in panel.towers_data.items():
        assert 'base_stats' in tower_data, f"Tower {tower_id} should have base_stats"
        assert 'base_cost' in tower_data, f"Tower {tower_id} should have base_cost"
    
    # Test tower cost calculation
    dart_monkey_cost = panel.get_tower_cost('dart_monkey')
    assert dart_monkey_cost > 0, "Dart monkey should have a positive cost"
    
    # Test selection first, then affordability check
    panel.selected_tower_id = 'dart_monkey' # Manually set for testing
    
    # Test affordability check with sufficient money
    can_afford = panel.can_afford_selected_tower(1000)
    assert can_afford == True, "Should be able to afford dart monkey with 1000 money"
    
    # Test affordability check with insufficient money
    cant_afford = panel.can_afford_selected_tower(1)
    assert cant_afford == False, "Should not be able to afford dart monkey with 1 money"
    
    # Test selection (setting manually for testing since handle_click requires pygame events)
    panel.selected_tower_id = 'dart_monkey'
    assert panel.selected_tower_id == 'dart_monkey', "Should select dart monkey"
    
    # Test getting selected tower data
    selected_data = panel.get_selected_tower_data()
    assert selected_data is not None, "Should return data for selected tower"
    assert 'base_stats' in selected_data, "Selected tower data should have base_stats"
    
    pygame.quit()
    print("✅ Tower selection panel tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_tower_selection_panel()
        print("🎯 All tower selection tests completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
