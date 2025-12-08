"""
Quick test to verify font caching optimization in UI panels
This script can be run to ensure the panels work correctly with cached fonts
"""
import pygame
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.ui.ingame_upgrade_panel import InGameUpgradePanel
from game.ui.tower_selection_panel import TowerSelectionPanel

def test_font_caching():
    """Test that fonts are properly cached"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    
    # Create panels
    upgrade_panel = InGameUpgradePanel(50, 50, 300, 200)
    selection_panel = TowerSelectionPanel()
    
    # Verify fonts are cached in upgrade panel
    print("Testing InGameUpgradePanel...")
    assert hasattr(upgrade_panel, 'font_title'), "font_title not cached!"
    assert hasattr(upgrade_panel, 'font_name'), "font_name not cached!"
    assert hasattr(upgrade_panel, 'font_stats'), "font_stats not cached!"
    assert hasattr(upgrade_panel, 'font_button'), "font_button not cached!"
    assert hasattr(upgrade_panel, 'font_instruction'), "font_instruction not cached!"
    print("✓ InGameUpgradePanel fonts cached correctly")
    
    # Verify fonts are cached in selection panel
    print("\nTesting TowerSelectionPanel...")
    assert hasattr(selection_panel, 'font_toggle'), "font_toggle not cached!"
    assert hasattr(selection_panel, 'font_cost'), "font_cost not cached!"
    assert hasattr(selection_panel, 'font_afford'), "font_afford not cached!"
    print("✓ TowerSelectionPanel fonts cached correctly")
    
    # Verify TowerButton class fonts
    from game.ui.tower_selection_panel import TowerButton
    print("\nTesting TowerButton...")
    assert TowerButton._font_name is not None, "TowerButton._font_name not cached!"
    assert TowerButton._font_cost is not None, "TowerButton._font_cost not cached!"
    print("✓ TowerButton fonts cached correctly at class level")
    
    # Run a quick visual test
    print("\nRunning visual test for 3 seconds...")
    print("Press ESC to exit early")
    
    fps_samples = []
    running = True
    start_time = pygame.time.get_ticks()
    
    while running and (pygame.time.get_ticks() - start_time) < 3000:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Draw everything
        screen.fill((30, 30, 30))
        
        # Draw selection panel
        selection_panel.draw(screen, 1000)
        
        # Draw upgrade panel (even though no tower is selected)
        upgrade_panel.draw(screen, 1000)
        
        pygame.display.flip()
        clock.tick(60)
        fps_samples.append(clock.get_fps())
    
    # Calculate average FPS
    if fps_samples:
        avg_fps = sum(fps_samples) / len(fps_samples)
        print(f"\n✓ Visual test complete. Average FPS: {avg_fps:.1f}")
        
        if avg_fps > 55:
            print("✓ Performance looks good!")
        else:
            print("⚠ FPS might be lower than expected")
    
    pygame.quit()
    print("\n✅ All tests passed! Font caching is working correctly.")

if __name__ == "__main__":
    test_font_caching()
