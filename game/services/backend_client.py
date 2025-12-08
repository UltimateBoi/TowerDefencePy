"""
Backend API Client
Communicates with the backend server for all Firebase operations.
No Firebase credentials are stored client-side.
"""

import requests
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class BackendAPIClient:
    """
    Client for communicating with the backend API server.
    All Firebase operations are handled server-side.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(BackendAPIClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize API client."""
        if self._initialized:
            return
            
        self._initialized = True
        
        # API URL - defaults to your deployed backend
        # Users can override with .env file for local development
        self.api_url = os.getenv(
            'BACKEND_API_URL',
            'https://towerdefencepy.onrender.com'
        )
        
        self.id_token = None
        self.current_user = None
        self.offline_mode = False
        
        print(f"Backend API Client initialized: {self.api_url}")
    
    def is_online(self) -> bool:
        """Check if backend API is online."""
        if self.offline_mode:
            return False
        
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=5)
            return response.status_code == 200 and response.json().get('status') == 'online'
        except Exception:
            return False
    
    def set_id_token(self, id_token: str) -> bool:
        """
        Set the Firebase ID token for authenticated requests.
        Verifies the token with the backend.
        """
        try:
            response = requests.post(
                f"{self.api_url}/api/auth/verify",
                json={'idToken': id_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.id_token = id_token
                self.current_user = data.get('user')
                self.offline_mode = False
                return True
            else:
                print(f"Token verification failed: {response.json().get('error')}")
                return False
        
        except Exception as e:
            print(f"Error verifying token: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user info."""
        return self.current_user
    
    def logout(self):
        """Clear authentication."""
        self.id_token = None
        self.current_user = None
        
        # Clear session
        from .session_manager import session_manager
        session_manager.clear_session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {'Content-Type': 'application/json'}
        if self.id_token:
            headers['Authorization'] = f'Bearer {self.id_token}'
        return headers
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """Get user statistics from backend."""
        if not self.id_token:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/api/stats",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get stats: {response.json().get('error')}")
                return None
        
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    def update_stats(self, stats: Dict[str, Any]) -> bool:
        """Update user statistics on backend."""
        if not self.id_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/stats",
                headers=self._get_headers(),
                json=stats,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"Error updating stats: {e}")
            return False
    
    def save_game(self, game_state: Dict[str, Any]) -> bool:
        """Save game state to backend."""
        if not self.id_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/game/save",
                headers=self._get_headers(),
                json=game_state,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self) -> Optional[Dict[str, Any]]:
        """Load game state from backend."""
        if not self.id_token:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/api/game/load",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('gameState')
            else:
                return None
        
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Get user settings from backend."""
        if not self.id_token:
            return None
        
        try:
            response = requests.get(
                f"{self.api_url}/api/settings",
                headers=self._get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error getting settings: {e}")
            return None
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update user settings on backend."""
        if not self.id_token:
            return False
        
        try:
            response = requests.post(
                f"{self.api_url}/api/settings",
                headers=self._get_headers(),
                json=settings,
                timeout=10
            )
            
            return response.status_code == 200
        
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False


# Global instance
backend_client = BackendAPIClient()
