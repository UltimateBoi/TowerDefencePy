#!/usr/bin/env python3
"""
Test script for FPS counter settings
"""
import pygame
pygame.init()

from game.ui.pause_menu import SettingsMenu

def test_fps_setting():
    menu = SettingsMenu()
    print('Initial show_fps:', menu.show_fps)
    
    # Simulate clicking on FPS toggle (position doesn't matter for this test)
    # We need to set the toggle position first
    menu.fps_toggle_x = 100
    menu.fps_toggle_y = 100
    
    # Click on the toggle
    action = menu.handle_click((105, 105))  # Click inside the toggle rect
    print('Action returned:', action)
    print('After toggle show_fps:', menu.show_fps)
    
    # Click again
    action2 = menu.handle_click((105, 105))
    print('Second action returned:', action2)
    print('After second toggle show_fps:', menu.show_fps)

if __name__ == "__main__":
    test_fps_setting()
