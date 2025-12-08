"""
Profile Dropdown Panel
Displays user stats and logout option in a dropdown menu
"""

import pygame
from typing import Optional, Tuple
from game.services.firebase_service import firebase_service


class ProfileDropdownPanel:
    """Dropdown panel for user profile with stats and logout."""
    
    def __init__(self):
        """Initialize the profile dropdown panel."""
        self.visible = False
        self.panel_width = 280
        self.panel_height = 300
        self.panel_x = 20
        self.panel_y = 80  # Below the profile widget
        self._last_hover_state = False
        
        # Colors
        self.bg_color = (45, 55, 45)  # Dark green background
        self.text_color = (255, 255, 255)
        self.hover_color = (60, 80, 60)
        self.border_color = (80, 100, 80)
        
        # Fonts
        self.header_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.stat_font = pygame.font.SysFont('Arial', 18)
        self.small_font = pygame.font.SysFont('Arial', 16)
        
        # Logout button
        self.logout_button = pygame.Rect(
            self.panel_x + 20,
            self.panel_y + self.panel_height - 50,
            self.panel_width - 40,
            35
        )
        
        # Stats data
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'highest_round': 0,
            'tower_damage': 0,
            'bloons_popped': 0,
            'total_gold': 0
        }
        
        self.load_stats()
    
    def load_stats(self):
        """Load user stats from Firebase."""
        try:
            current_user = firebase_service.get_current_user()
            if current_user and firebase_service.is_online():
                user_stats = firebase_service.get_stats()
                if user_stats:
                    self.stats['games_played'] = user_stats.get('totalGamesPlayed', 0)
                    self.stats['games_won'] = user_stats.get('totalWins', 0)
                    self.stats['highest_round'] = user_stats.get('highestRound', 0)
                    self.stats['tower_damage'] = user_stats.get('totalTowerDamage', 0)
                    self.stats['bloons_popped'] = user_stats.get('totalBloonsPopped', 0)
                    self.stats['total_gold'] = user_stats.get('totalMoneyEarned', 0)
        except Exception as e:
            print(f"Error loading stats: {e}")
    
    def toggle(self):
        """Toggle panel visibility."""
        self.visible = not self.visible
        if self.visible:
            self.load_stats()  # Refresh stats when opening
    
    def show(self):
        """Show the panel."""
        self.visible = True
        self.load_stats()
    
    def hide(self):
        """Hide the panel."""
        self.visible = False
    
    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        Handle mouse events.
        
        Args:
            event: Pygame event
            mouse_pos: Current mouse position
            
        Returns:
            'logout' if logout button clicked, None otherwise
        """
        if not self.visible:
            return None
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if clicked outside panel to close
            panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
            if not panel_rect.collidepoint(mouse_pos):
                self.hide()
                return None
            
            # Check logout button
            if self.logout_button.collidepoint(mouse_pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                return 'logout'
        
        return None
    
    def draw(self, screen: pygame.Surface, mouse_pos: Tuple[int, int]):
        """
        Draw the dropdown panel.
        
        Args:
            screen: Pygame surface to draw on
            mouse_pos: Current mouse position for hover effects
        """
        if not self.visible:
            return
        
        # Update cursor only if hover state changes
        hovering = self.logout_button.collidepoint(mouse_pos)
        if hovering != self._last_hover_state:
            if hovering:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self._last_hover_state = hovering
        
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        
        # Draw main panel background with rounded corners
        pygame.draw.rect(screen, self.bg_color, panel_rect, border_radius=12)
        pygame.draw.rect(screen, self.border_color, panel_rect, width=2, border_radius=12)
        
        # Get current user
        current_user = firebase_service.get_current_user()
        username = current_user.get('displayName', 'Player') if current_user else 'Player'
        
        # Draw header with username
        header_y = self.panel_y + 15
        header_text = self.header_font.render(username, True, self.text_color)
        screen.blit(header_text, (self.panel_x + 20, header_y))
        
        # Draw divider line
        divider_y = header_y + 35
        pygame.draw.line(
            screen,
            self.border_color,
            (self.panel_x + 10, divider_y),
            (self.panel_x + self.panel_width - 10, divider_y),
            2
        )
        
        # Draw stats
        stats_y = divider_y + 15
        line_height = 28
        
        stats_display = [
            ('Games played:', self.stats['games_played']),
            ('Games won:', self.stats['games_won']),
            ('Highest round:', self.stats['highest_round']),
            ('Tower damage:', self.stats['tower_damage']),
            ('Bloons popped:', self.stats['bloons_popped']),
            ('Total gold:', self.stats['total_gold'])
        ]
        
        for i, (label, value) in enumerate(stats_display):
            y_pos = stats_y + i * line_height
            
            # Draw label
            label_text = self.stat_font.render(label, True, (200, 200, 200))
            screen.blit(label_text, (self.panel_x + 20, y_pos))
            
            # Draw value (right-aligned)
            value_text = self.stat_font.render(str(value), True, self.text_color)
            value_x = self.panel_x + self.panel_width - 20 - value_text.get_width()
            screen.blit(value_text, (value_x, y_pos))
        
        # Draw logout button with hover effect
        button_color = self.hover_color if self.logout_button.collidepoint(mouse_pos) else (180, 50, 50)
        pygame.draw.rect(screen, button_color, self.logout_button, border_radius=8)
        pygame.draw.rect(screen, (200, 80, 80), self.logout_button, width=2, border_radius=8)
        
        logout_text = self.small_font.render("Logout", True, self.text_color)
        logout_text_rect = logout_text.get_rect(center=self.logout_button.center)
        screen.blit(logout_text, logout_text_rect)
