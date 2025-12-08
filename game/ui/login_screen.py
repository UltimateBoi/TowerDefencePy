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
        
        # Buttons
        button_y_start = self.height // 2 + 20
        self.google_button = pygame.Rect(self.width // 2 - 200, button_y_start, 400, 60)
        self.guest_button = pygame.Rect(self.width // 2 - 200, button_y_start + 80, 400, 50)
        self.skip_button = pygame.Rect(self.width // 2 - 100, self.height - 80, 200, 40)
        
        # State
        self.error_message = ""
        self.info_message = ""
        self.loading = False
        
        # Check for existing session
        self.auto_login_attempted = False
        
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
        
        # Draw title
        title = self.title_font.render("Tower Defense", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title, title_rect)
        
        # Draw subtitle
        subtitle = self.font.render("Please sign in to continue", True, self.info_color)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, self.height // 3 + 60))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Get mouse position for hover effects
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw Google Sign-In button
        google_color = self.google_button_hover if self.google_button.collidepoint(mouse_pos) else self.google_button_color
        pygame.draw.rect(self.screen, google_color, self.google_button, border_radius=8)
        
        # Google logo (G icon)
        icon_size = 40
        icon_rect = pygame.Rect(
            self.google_button.x + 20,
            self.google_button.y + 10,
            icon_size,
            icon_size
        )
        pygame.draw.circle(self.screen, (255, 255, 255), icon_rect.center, icon_size // 2)
        
        # Draw "G" letter
        g_font = pygame.font.SysFont('Arial', 28, bold=True)
        g_text = g_font.render("G", True, self.google_button_color)
        g_rect = g_text.get_rect(center=icon_rect.center)
        self.screen.blit(g_text, g_rect)
        
        # Google button text (offset to the right of icon)
        google_text = self.font.render("Sign in with Google", True, self.text_color)
        text_x = self.google_button.x + 80
        text_y = self.google_button.centery - google_text.get_height() // 2
        self.screen.blit(google_text, (text_x, text_y))
        
        # Draw Guest button
        guest_color = self.guest_button_hover if self.guest_button.collidepoint(mouse_pos) else self.guest_button_color
        pygame.draw.rect(self.screen, guest_color, self.guest_button, border_radius=8)
        
        guest_text = self.small_font.render("Continue as Guest (Offline)", True, self.text_color)
        guest_text_rect = guest_text.get_rect(center=self.guest_button.center)
        self.screen.blit(guest_text, guest_text_rect)
        
        # Draw Skip button
        skip_color = (80, 80, 90) if self.skip_button.collidepoint(mouse_pos) else (60, 60, 70)
        pygame.draw.rect(self.screen, skip_color, self.skip_button, border_radius=6)
        
        skip_text = self.small_font.render("Skip", True, self.text_color)
        skip_text_rect = skip_text.get_rect(center=self.skip_button.center)
        self.screen.blit(skip_text, skip_text_rect)
        
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
