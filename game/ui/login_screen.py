"""
Login Screen UI
Provides Google Sign-In authentication interface for Firebase.
"""

import pygame
import sys
import webbrowser
from typing import Optional, Tuple
from game.services.firebase_service import firebase_service
from game.services.google_auth_service import google_auth_service
from game.services.session_manager import session_manager


class LoginScreen:
    """Login screen for user authentication."""
    
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
        self.oauth_setup_required = False
        
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
            pygame.display.flip()
            
            # Perform Google OAuth flow
            user_info = google_auth_service.sign_in_with_google()
            
            if user_info:
                # Extract user details
                email = user_info.get('email', 'unknown@gmail.com')
                display_name = user_info.get('name', email.split('@')[0])
                user_id = user_info.get('sub', user_info.get('id', ''))
                
                # Set current user in Firebase service
                firebase_service.set_current_user(
                    user_id=f"google_{user_id}",
                    email=email,
                    display_name=display_name
                )
                
                # Save session for persistence
                session_data = {
                    'user_id': f"google_{user_id}",
                    'email': email,
                    'display_name': display_name,
                    'id_token': user_info.get('id_token'),
                    'access_token': user_info.get('access_token'),
                    'refresh_token': user_info.get('refresh_token'),
                }
                session_manager.save_session(session_data)
                
                print(f"Successfully logged in as: {display_name} ({email})")
                self.info_message = f"Welcome, {display_name}!"
                self.loading = False
                return 'continue'
            else:
                self.error_message = "Google Sign-In was cancelled or failed"
                self.loading = False
                return None
            
        except Exception as e:
            self.error_message = f"Sign-in error: {str(e)}"
            self.loading = False
            print(f"ERROR: Error during sign-in: {e}")
            return None
    
    def _login_as_guest(self) -> str:
        """Login as a guest user."""
        import time
        guest_id = f"guest_{int(time.time())}"
        
        firebase_service.set_current_user(
            user_id=guest_id,
            email=f"{guest_id}@guest.local",
            display_name=f"Guest_{int(time.time()) % 10000}"
        )
        
        print(f"Logged in as guest: {guest_id}")
        return 'continue'
    
    def draw(self):
        """Draw the login screen."""
        self.screen.fill(self.bg_color)
        
        # Title
        title = self.title_font.render("Tower Defense", True, self.text_color)
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.font.render("Sign in to sync your progress across devices", True, self.info_color)
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Update cursor based on hover
        hovering = (self.google_button.collidepoint(mouse_pos) or 
                   self.guest_button.collidepoint(mouse_pos) or 
                   self.skip_button.collidepoint(mouse_pos))
        if hovering:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Google Sign-In button
        google_color = self.google_button_hover if self.google_button.collidepoint(mouse_pos) else self.google_button_color
        pygame.draw.rect(self.screen, google_color, self.google_button, border_radius=8)
        
        # Google logo placeholder (G icon)
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
        
        # Google button text
        google_text = self.font.render("Sign in with Google", True, self.text_color)
        text_x = self.google_button.x + 80
        text_y = self.google_button.centery - google_text.get_height() // 2
        self.screen.blit(google_text, (text_x, text_y))
        
        # Guest button
        guest_color = self.guest_button_hover if self.guest_button.collidepoint(mouse_pos) else self.guest_button_color
        pygame.draw.rect(self.screen, guest_color, self.guest_button, border_radius=8)
        guest_text = self.font.render("Continue as Guest", True, self.text_color)
        guest_text_rect = guest_text.get_rect(center=self.guest_button.center)
        self.screen.blit(guest_text, guest_text_rect)
        
        # Skip button (play offline)
        skip_color = (100, 100, 100) if self.skip_button.collidepoint(mouse_pos) else (70, 70, 70)
        pygame.draw.rect(self.screen, skip_color, self.skip_button, border_radius=5)
        skip_text = self.small_font.render("Play Offline", True, (200, 200, 200))
        skip_text_rect = skip_text.get_rect(center=self.skip_button.center)
        self.screen.blit(skip_text, skip_text_rect)
        
        # Error message
        if self.error_message:
            error_surface = self.small_font.render(self.error_message, True, self.error_color)
            error_rect = error_surface.get_rect(center=(self.width // 2, self.height // 2 + 280))
            self.screen.blit(error_surface, error_rect)
        
        # Info message
        if self.info_message:
            info_surface = self.small_font.render(self.info_message, True, self.info_color)
            info_rect = info_surface.get_rect(center=(self.width // 2, self.height // 2 + 250))
            self.screen.blit(info_surface, info_rect)
        
        # Error message
        if self.error_message:
            error_y = self.height // 2 + 310
            error_text = self.small_font.render(self.error_message, True, self.error_color)
            error_rect = error_text.get_rect(center=(self.width // 2, error_y))
            self.screen.blit(error_text, error_rect)
        
        # Info message (loading, etc.)
        if self.info_message:
            info_y = self.height // 2 + 310 if not self.error_message else self.height // 2 + 340
            info_text_surface = self.small_font.render(self.info_message, True, (100, 200, 255))
            info_text_rect = info_text_surface.get_rect(center=(self.width // 2, info_y))
            self.screen.blit(info_text_surface, info_text_rect)
        
        # Loading indicator
        if self.loading:
            loading_text = self.font.render("Authenticating...", True, (100, 200, 255))
            loading_rect = loading_text.get_rect(center=(self.width // 2, self.height // 2 - 80))
            self.screen.blit(loading_text, loading_rect)
        
        # Bottom info text
        info_text = self.small_font.render("Secure cloud sync with Google account", True, (150, 150, 150))
        info_rect = info_text.get_rect(center=(self.width // 2, self.height - 130))
        self.screen.blit(info_text, info_rect)
        
        pygame.display.flip()
    
    def _try_auto_login(self) -> Optional[str]:
        """Attempt to restore previous session."""
        if self.auto_login_attempted or self.skip_auto_login:
            return None
        
        self.auto_login_attempted = True
        
        # Check if session exists
        if not session_manager.has_session():
            return None
        
        self.info_message = "Restoring previous session..."
        self.loading = True
        self.draw()
        
        try:
            # Load session data
            session_data = session_manager.load_session()
            
            if session_data:
                user_id = session_data.get('user_id')
                email = session_data.get('email')
                display_name = session_data.get('display_name')
                
                # Restore user session
                firebase_service.set_current_user(
                    user_id=user_id,
                    email=email,
                    display_name=display_name
                )
                
                print(f"Session restored: {display_name} ({email})")
                self.info_message = f"Welcome back, {display_name}!"
                self.loading = False
                return 'continue'
            else:
                # Invalid session, clear it
                session_manager.clear_session()
                self.loading = False
                return None
                
        except Exception as e:
            print(f"Error restoring session: {e}")
            session_manager.clear_session()
            self.loading = False
            self.error_message = "Session expired. Please sign in again."
            return None
    
    def run(self) -> str:
        """
        Run the login screen loop.
        
        Returns:
            'continue' when user is ready to proceed
        """
        clock = pygame.time.Clock()
        
        # Try auto-login first
        auto_login_result = self._try_auto_login()
        if auto_login_result:
            return auto_login_result
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                result = self.handle_event(event)
                if result == 'continue':
                    return result
            
            self.draw()
            clock.tick(60)
