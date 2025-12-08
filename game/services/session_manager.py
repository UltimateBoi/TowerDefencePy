"""
Session Manager Module
Handles user session persistence across app restarts.
Stores and retrieves authentication tokens securely.
"""

import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class SessionManager:
    """Manages user session persistence."""
    
    def __init__(self):
        """Initialize session manager with local storage path."""
        # Store session in user's home directory
        self.session_dir = Path.home() / '.towerdefense'
        self.session_file = self.session_dir / 'session.json'
        
        # Create directory if it doesn't exist
        self.session_dir.mkdir(exist_ok=True)
    
    def save_session(self, user_data: Dict[str, Any]) -> bool:
        """
        Save user session data to local storage.
        
        Args:
            user_data: Dictionary containing user_id, email, display_name, and tokens
            
        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Only save necessary data
            session_data = {
                'user_id': user_data.get('user_id'),
                'email': user_data.get('email'),
                'display_name': user_data.get('display_name'),
                'id_token': user_data.get('id_token'),
                'access_token': user_data.get('access_token'),
                'refresh_token': user_data.get('refresh_token'),
            }
            
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
            
            # Set file permissions (read/write for owner only on Unix)
            if os.name != 'nt':  # Not Windows
                os.chmod(self.session_file, 0o600)
            
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """
        Load user session data from local storage.
        
        Returns:
            Dictionary with session data if exists, None otherwise
        """
        try:
            if not self.session_file.exists():
                return None
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            return session_data
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def clear_session(self) -> bool:
        """
        Clear saved session data (logout).
        
        Returns:
            True if cleared successfully, False otherwise
        """
        try:
            if self.session_file.exists():
                self.session_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing session: {e}")
            return False
    
    def has_session(self) -> bool:
        """Check if a session exists."""
        return self.session_file.exists()


# Global instance
session_manager = SessionManager()
