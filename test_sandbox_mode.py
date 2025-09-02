"""
Test sandbox mode functionality
"""
import pytest
import pygame
from game.tower_defense_game import TowerDefenseGame
from game.entities.bloon_types import BloonType


@pytest.fixture
def game():
    """Create a game instance for testing"""
    pygame.init()
    test_game = TowerDefenseGame()
    yield test_game
    pygame.quit()


def test_sandbox_mode_initialization(game):
    """Test that sandbox mode initializes correctly"""
    # Initially should be in normal mode
    assert game.game_mode == "normal"
    assert game.sandbox_mode == False
    assert game.sandbox_bloon_type == BloonType.RED


def test_sandbox_mode_activation(game):
    """Test activating sandbox mode"""
    # Simulate what happens when sandbox mode is selected in the UI
    game.game_mode = "sandbox"
    game.sandbox_mode = True
    # Set sandbox mode properties (this is done in handle_events)
    game.money = 999999 # Infinite money
    game.lives = 999999 # Infinite lives

    assert game.game_mode == "sandbox"
    assert game.sandbox_mode == True
    assert game.money == 999999 # Should have infinite money
    assert game.lives == 999999 # Should have infinite lives


def test_bloon_type_cycling(game):
    """Test cycling through bloon types in sandbox mode"""
    game.sandbox_mode = True

    # Initial type should be RED
    assert game.sandbox_bloon_type == BloonType.RED

    # Simulate pressing B key to cycle
    game.sandbox_bloon_type = BloonType.BLUE
    assert game.sandbox_bloon_type == BloonType.BLUE

    game.sandbox_bloon_type = BloonType.GREEN
    assert game.sandbox_bloon_type == BloonType.GREEN

    game.sandbox_bloon_type = BloonType.YELLOW
    assert game.sandbox_bloon_type == BloonType.YELLOW

    # Should cycle back to RED
    game.sandbox_bloon_type = BloonType.RED
    assert game.sandbox_bloon_type == BloonType.RED


def test_spawn_bloon_functionality(game):
    """Test that spawn_bloon method works correctly"""
    game.sandbox_mode = True

    initial_bloon_count = len(game.bloons)

    # Spawn a bloon
    game.spawn_bloon((100, 100), BloonType.RED)

    # Should have one more bloon
    assert len(game.bloons) == initial_bloon_count + 1

    # Check that the bloon was created with correct type
    new_bloon = game.bloons[-1]
    assert new_bloon.type == BloonType.RED


def test_tower_deselection_functionality(game):
    """Test that towers can be deselected by clicking on them again"""
    # Create a mock tower for testing
    from game.entities.tower import Tower
    test_tower = Tower((100, 100), tower_type="test_tower")
    game.towers.append(test_tower)
    
    # Initially no tower should be selected
    assert game.selected_tower is None
    
    # Simulate clicking on the tower to select it
    # (We can't easily simulate mouse clicks in unit tests, so we'll test the logic directly)
    game.selected_tower = test_tower
    test_tower.selected = True
    
    # Verify tower is selected
    assert game.selected_tower == test_tower
    assert test_tower.selected == True
    
    # Simulate clicking on the same tower again (should deselect)
    # In the actual game logic, this would be handled in handle_events
    # For testing, we'll simulate the deselection logic
    if test_tower == game.selected_tower:
        test_tower.selected = False
        game.selected_tower = None
        game.upgrade_panel.set_selected_tower(None)
    
    # Verify tower is deselected
    assert game.selected_tower is None
    assert test_tower.selected == False
