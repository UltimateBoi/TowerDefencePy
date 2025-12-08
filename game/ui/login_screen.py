"""
Login Screen UI (Backend API Version)
Uses backend API for authentication - no Firebase credentials needed client-side.
"""

import pygame
import sys
import webbrowser
from typing import Optional, Tuple
from game.services.backend_client import backend_client
from game.services.google_oauth_client import google_oauth_client
from game.services.session_manager import session_manager


class LoginScreen:
    """Login screen for user authentication via backend API."""
    
    def __init__(self, screen: pygame.Surface, skip_auto_login: bool = False):
        """
        Initialize the login screen.
        
        Args:
            screen: Pygame display surface
            skip_auto_login: If True, skip automatic session restoration
        """
        self.screen = screen
        self.skip_auto_login = skip_auto_login
        self.width = screen.get_width()
        self.height = screen.get_height()
        
        # Colors
        self.bg_color = (30, 30, 40)
        self.text_color = (255, 255, 255)
        self.google_button_color = (66, 133, 244)  # Google blue
        self.google_button_hover = (51, 103, 214)
        self.guest_button_color = (100, 100, 110)
        self.guest_button_hover = (120, 120, 130)
        self.error_color = (220, 50, 50)
        self.info_color = (180, 180, 180)
        
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        self.tiny_font = pygame.font.SysFont('Arial', 14)
        self.g_font = pygame.font.SysFont('Arial', 28, bold=True)
        
        # Buttons
        button_y_start = self.height // 2 + 20
        self.google_button = pygame.Rect(self.width // 2 - 200, button_y_start, 400, 60)
        self.guest_button = pygame.Rect(self.width // 2 - 200, button_y_start + 80, 400, 50)
        self.skip_button = pygame.Rect(self.width // 2 - 100, self.height - 80, 200, 40)
        
        # State
        self.error_message = ""
        self.info_message = ""
        self.loading = False
        self.current_hover = None  # Track hover state to avoid redundant updates
        
        # Check for existing session
        self.auto_login_attempted = False
        
        # Pre-render static text surfaces (cache)
        self._cache_static_surfaces()
    
    def _cache_static_surfaces(self):
        """Pre-render static text to improve performance."""
        # Title and subtitle (never change)
        self.title_surface = self.title_font.render("Tower Defense", True, self.text_color)
        self.title_rect = self.title_surface.get_rect(center=(self.width // 2, self.height // 3))
        
        self.subtitle_surface = self.font.render("Please sign in to continue", True, self.info_color)
        self.subtitle_rect = self.subtitle_surface.get_rect(center=(self.width // 2, self.height // 3 + 60))
        
        # Button text (never changes)
        self.google_text_surface = self.font.render("Sign in with Google", True, self.text_color)
        self.guest_text_surface = self.small_font.render("Continue as Guest (Offline)", True, self.text_color)
        self.skip_text_surface = self.small_font.render("Skip", True, self.text_color)
        
        # Google "G" icon text
        self.g_text_surface = self.g_font.render("G", True, self.google_button_color)
        
        # Calculate positions once
        self.google_text_pos = (
            self.google_button.x + 80,
            self.google_button.centery - self.google_text_surface.get_height() // 2
        )
        self.guest_text_rect = self.guest_text_surface.get_rect(center=self.guest_button.center)
        self.skip_text_rect = self.skip_text_surface.get_rect(center=self.skip_button.center)
        
        # Google icon circle position
        self.icon_center = (self.google_button.x + 40, self.google_button.y + 30)
        self.g_text_rect = self.g_text_surface.get_rect(center=self.icon_center)
        
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle pygame events.
        
        Args:
            event: Pygame event
            
        Returns:
            'continue' to proceed to game, None to stay on login screen
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check button clicks
            if self.google_button.collidepoint(event.pos):
                return self._sign_in_with_google()
            elif self.guest_button.collidepoint(event.pos):
                return self._login_as_guest()
            elif self.skip_button.collidepoint(event.pos):
                return 'continue'  # Skip login, play offline
        
        return None
    
    def _sign_in_with_google(self) -> Optional[str]:
        """
        Initiate Google Sign-In flow.
        Opens browser for OAuth authentication.
        """
        try:
            self.info_message = "Opening browser for Google Sign-In..."
            self.loading = True
            self.draw()
            pygame.display.flip()
            
            # Perform Google OAuth flow (client-side only)
            id_token = google_oauth_client.sign_in_with_google()
            
            if id_token:
                self.info_message = "Verifying with server..."
                self.draw()
                pygame.display.flip()
                
                # Verify token with backend
                if backend_client.set_id_token(id_token):
                    user = backend_client.get_current_user()
                    
                    if user:
                        display_name = user.get('displayName', 'Player')
                        
                        # Save session
                        session_manager.save_session({
                            'id_token': id_token,
                            'user': user
                        })
                        
                        self.info_message = f"Welcome, {display_name}!"
                        self.loading = False
                        self.draw()
                        pygame.display.flip()
                        pygame.time.wait(1000)
                        
                        return 'continue'
                    else:
                        self.error_message = "Failed to get user information"
                else:
                    self.error_message = "Authentication failed. Please try again."
            else:
                self.error_message = "Google Sign-In was cancelled or failed"
            
            self.loading = False
            
        except Exception as e:
            print(f"Error during Google Sign-In: {e}")
            self.error_message = f"Sign-in error: {str(e)}"
            self.loading = False
        
        return None
    
    def _login_as_guest(self) -> Optional[str]:
        """
        Continue as guest (offline mode).
        """
        self.info_message = "Playing as guest (offline mode)"
        backend_client.offline_mode = True
        return 'continue'
    
    def _try_auto_login(self):
        """Attempt to restore previous session."""
        if self.auto_login_attempted or self.skip_auto_login:
            return
        
        self.auto_login_attempted = True
        
        if not session_manager.has_session():
            return
        
        self.info_message = "Restoring session..."
        self.draw()
        pygame.display.flip()
        
        try:
            session = session_manager.load_session()
            
            if session and 'id_token' in session:
                # Verify token with backend
                if backend_client.set_id_token(session['id_token']):
                    user = backend_client.get_current_user()
                    
                    if user:
                        display_name = user.get('displayName', 'Player')
                        self.info_message = f"Welcome back, {display_name}!"
                        self.draw()
                        pygame.display.flip()
                        pygame.time.wait(1000)
                        
                        # Session restored successfully
                        return
                
                # Token invalid, clear session
                session_manager.clear_session()
                self.info_message = "Session expired. Please sign in again."
        
        except Exception as e:
            print(f"Error restoring session: {e}")
            self.info_message = "Could not restore session"
    
    def draw(self):
        """Draw the login screen."""
        self.screen.fill(self.bg_color)
        
        # Draw cached static text
        self.screen.blit(self.title_surface, self.title_rect)
        self.screen.blit(self.subtitle_surface, self.subtitle_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Update cursor only when hover state changes
        new_hover = None
        if self.google_button.collidepoint(mouse_pos):
            new_hover = 'google'
        elif self.guest_button.collidepoint(mouse_pos):
            new_hover = 'guest'
        elif self.skip_button.collidepoint(mouse_pos):
            new_hover = 'skip'
        
        if new_hover != self.current_hover:
            if new_hover:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            self.current_hover = new_hover
        
        # Draw Google Sign-In button
        google_color = self.google_button_hover if new_hover == 'google' else self.google_button_color
        pygame.draw.rect(self.screen, google_color, self.google_button, border_radius=8)
        
        # Google logo (G icon) - cached positions
        pygame.draw.circle(self.screen, (255, 255, 255), self.icon_center, 20)
        self.screen.blit(self.g_text_surface, self.g_text_rect)
        
        # Google button text (cached surface and position)
        self.screen.blit(self.google_text_surface, self.google_text_pos)
        
        # Draw Guest button
        guest_color = self.guest_button_hover if new_hover == 'guest' else self.guest_button_color
        pygame.draw.rect(self.screen, guest_color, self.guest_button, border_radius=8)
        self.screen.blit(self.guest_text_surface, self.guest_text_rect)
        
        # Draw Skip button
        skip_color = (80, 80, 90) if new_hover == 'skip' else (60, 60, 70)
        pygame.draw.rect(self.screen, skip_color, self.skip_button, border_radius=6)
        self.screen.blit(self.skip_text_surface, self.skip_text_rect)
        
        # Draw info/error messages
        if self.loading:
            loading_text = self.font.render("Loading...", True, self.info_color)
            loading_rect = loading_text.get_rect(center=(self.width // 2, self.height - 150))
            self.screen.blit(loading_text, loading_rect)
        
        if self.info_message:
            info_text = self.small_font.render(self.info_message, True, self.info_color)
            info_rect = info_text.get_rect(center=(self.width // 2, self.height - 150))
            self.screen.blit(info_text, info_rect)
        
        if self.error_message:
            error_text = self.small_font.render(self.error_message, True, self.error_color)
            error_rect = error_text.get_rect(center=(self.width // 2, self.height - 150))
            self.screen.blit(error_text, error_rect)
        
        # Draw backend status indicator
        status_color = (0, 200, 0) if backend_client.is_online() else (200, 0, 0)
        status_text = "Online" if backend_client.is_online() else "Offline"
        status_render = self.tiny_font.render(f"Backend: {status_text}", True, status_color)
        self.screen.blit(status_render, (10, self.height - 25))
    
    def run(self):
        """Run the login screen loop."""
        # Try auto-login first
        self._try_auto_login()
        
        # If auto-login succeeded, exit immediately
        if backend_client.get_current_user():
            return
        
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                result = self.handle_event(event)
                if result == 'continue':
                    running = False
            
            self.draw()
            pygame.display.flip()
            clock.tick(60)
