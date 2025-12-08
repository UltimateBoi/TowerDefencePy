"""
Firebase Service Module
Handles all Firebase operations including authentication, Firestore database operations,
and cloud synchronization for the Tower Defense game.
"""

import os
import json
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore, auth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class FirebaseService:
    """
    Manages Firebase authentication and Firestore database operations.
    Provides methods for user authentication, saving/loading game state,
    tracking stats, and syncing settings across devices.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one Firebase instance exists."""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Firebase connection and authentication."""
        if self._initialized:
            return
            
        self._initialized = True
        self.db = None
        self.current_user = None
        self.user_id = None
        self.offline_mode = False
        
        # Try to initialize Firebase
        try:
            self._initialize_firebase()
        except Exception as e:
            print(f"Firebase initialization failed: {e}")
            print("Running in offline mode")
            self.offline_mode = True
    
    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK with credentials."""
        try:
            # Check if already initialized
            firebase_admin.get_app()
        except ValueError:
            # Not initialized, so initialize it
            project_id = os.getenv('FIREBASE_PROJECT_ID')
            
            # Use service account key file
            cred = credentials.Certificate('firebase-credentials.json')
            
            firebase_admin.initialize_app(cred, {
                'projectId': project_id,
            })
        
        # Get Firestore client
        self.db = firestore.client()
        print("Firebase initialized successfully")
    
    def is_online(self) -> bool:
        """Check if Firebase service is available."""
        return not self.offline_mode and self.db is not None
    
    # ==================== Authentication ====================
    
    def create_custom_token(self, user_id: str) -> Optional[str]:
        """
        Create a custom authentication token for a user.
        This can be used for testing or custom authentication flows.
        """
        try:
            custom_token = auth.create_custom_token(user_id)
            return custom_token.decode('utf-8')
        except Exception as e:
            print(f"Error creating custom token: {e}")
            return None
    
    def verify_token(self, id_token: str) -> Optional[Dict[str, Any]]:
        """Verify an ID token and return the decoded token."""
        try:
            decoded_token = auth.verify_id_token(id_token)
            return decoded_token
        except Exception as e:
            print(f"Error verifying token: {e}")
            return None
    
    def set_current_user(self, user_id: str, email: str, display_name: str = None):
        """Set the current authenticated user."""
        self.user_id = user_id
        self.current_user = {
            'uid': user_id,
            'email': email,
            'displayName': display_name or email.split('@')[0]
        }
        
        # Create or update user document in Firestore
        if self.is_online():
            self._initialize_user_document()
    
    def logout(self):
        """Logout current user and clear session."""
        from game.services.session_manager import session_manager
        
        self.user_id = None
        self.current_user = None
        
        # Clear saved session
        session_manager.clear_session()
        
        print("User logged out successfully")
    
    def _initialize_user_document(self):
        """Initialize user document in Firestore if it doesn't exist."""
        if not self.is_online() or not self.user_id:
            return
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                # Create new user document with default values
                user_data = {
                    'email': self.current_user.get('email'),
                    'displayName': self.current_user.get('displayName'),
                    'createdAt': firestore.SERVER_TIMESTAMP,
                    'lastLogin': firestore.SERVER_TIMESTAMP,
                }
                user_ref.set(user_data)
                
                # Initialize stats subcollection
                stats_ref = user_ref.collection('stats').document('overall')
                stats_ref.set({
                    'totalGamesPlayed': 0,
                    'totalWins': 0,
                    'totalLosses': 0,
                    'highestRound': 0,
                    'totalBloonsPopped': 0,
                    'totalMoneyEarned': 0,
                    'favoriteMap': '',
                    'lastUpdated': firestore.SERVER_TIMESTAMP
                })
                
                # Initialize settings
                settings_ref = user_ref.collection('settings').document('preferences')
                settings_ref.set({
                    'musicVolume': 0.7,
                    'soundEffectsVolume': 0.8,
                    'autoStart': False,
                    'graphicsQuality': 'high',
                    'lastModified': firestore.SERVER_TIMESTAMP
                })
                
                print(f"Created new user document for {self.user_id}")
            else:
                # Update last login
                user_ref.update({
                    'lastLogin': firestore.SERVER_TIMESTAMP
                })
                print(f"User {self.user_id} logged in")
                
        except Exception as e:
            print(f"Error initializing user document: {e}")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get the current authenticated user."""
        return self.current_user
    
    def logout(self):
        """Log out the current user."""
        self.current_user = None
        self.user_id = None
    
    # ==================== Game State Management ====================
    
    def save_game(self, game_data: Dict[str, Any], game_id: str = None) -> Optional[str]:
        """
        Save game state to Firestore.
        
        Args:
            game_data: Dictionary containing game state
            game_id: Optional game ID, generates new one if not provided
            
        Returns:
            Game ID if successful, None otherwise
        """
        if not self.is_online() or not self.user_id:
            print("Cannot save game: offline or not authenticated")
            return None
        
        try:
            # Generate game ID if not provided
            if game_id is None:
                game_id = f"game_{int(time.time())}"
            
            # Prepare game data
            save_data = {
                'mapName': game_data.get('map_name', 'map1'),
                'difficulty': game_data.get('difficulty', 'medium'),
                'gameMode': game_data.get('game_mode', 'normal'),
                'currentRound': game_data.get('current_round', 0),
                'money': game_data.get('money', 0),
                'lives': game_data.get('lives', 0),
                'towers': game_data.get('towers', []),
                'gameState': game_data.get('additional_state', {}),
                'lastSaved': firestore.SERVER_TIMESTAMP
            }
            
            # Save to Firestore
            user_ref = self.db.collection('users').document(self.user_id)
            game_ref = user_ref.collection('savedGames').document(game_id)
            game_ref.set(save_data)
            
            print(f"Game saved successfully: {game_id}")
            return game_id
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return None
    
    def load_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        Load game state from Firestore.
        
        Args:
            game_id: ID of the game to load
            
        Returns:
            Game data dictionary if successful, None otherwise
        """
        if not self.is_online() or not self.user_id:
            print("Cannot load game: offline or not authenticated")
            return None
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            game_ref = user_ref.collection('savedGames').document(game_id)
            game_doc = game_ref.get()
            
            if game_doc.exists:
                game_data = game_doc.to_dict()
                print(f"Game loaded successfully: {game_id}")
                return game_data
            else:
                print(f"Game not found: {game_id}")
                return None
                
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saved_games(self) -> List[Dict[str, Any]]:
        """
        List all saved games for the current user.
        
        Returns:
            List of saved game metadata
        """
        if not self.is_online() or not self.user_id:
            return []
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            games_ref = user_ref.collection('savedGames')
            
            # Get all saved games, ordered by last saved
            games = games_ref.order_by('lastSaved', direction=firestore.Query.DESCENDING).stream()
            
            saved_games = []
            for game in games:
                game_data = game.to_dict()
                game_data['id'] = game.id
                saved_games.append(game_data)
            
            return saved_games
            
        except Exception as e:
            print(f"Error listing saved games: {e}")
            return []
    
    def delete_saved_game(self, game_id: str) -> bool:
        """
        Delete a saved game.
        
        Args:
            game_id: ID of the game to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_online() or not self.user_id:
            return False
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            game_ref = user_ref.collection('savedGames').document(game_id)
            game_ref.delete()
            
            print(f"Game deleted successfully: {game_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting game: {e}")
            return False
    
    # ==================== Stats Management ====================
    
    def update_stats(self, stats: Dict[str, Any]):
        """
        Update user statistics.
        
        Args:
            stats: Dictionary of stats to update
        """
        if not self.is_online() or not self.user_id:
            return
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            stats_ref = user_ref.collection('stats').document('overall')
            
            # Add timestamp
            stats['lastUpdated'] = firestore.SERVER_TIMESTAMP
            
            # Update stats (merge to not overwrite existing data)
            stats_ref.set(stats, merge=True)
            
            print("Stats updated successfully")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def get_stats(self) -> Optional[Dict[str, Any]]:
        """
        Get user statistics.
        
        Returns:
            Stats dictionary if successful, None otherwise
        """
        if not self.is_online() or not self.user_id:
            return None
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            stats_ref = user_ref.collection('stats').document('overall')
            stats_doc = stats_ref.get()
            
            if stats_doc.exists:
                return stats_doc.to_dict()
            else:
                return None
                
        except Exception as e:
            print(f"Error getting stats: {e}")
            return None
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """
        Increment a specific stat by a given amount.
        
        Args:
            stat_name: Name of the stat to increment
            amount: Amount to increment by (default 1)
        """
        if not self.is_online() or not self.user_id:
            return
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            stats_ref = user_ref.collection('stats').document('overall')
            
            stats_ref.update({
                stat_name: firestore.Increment(amount),
                'lastUpdated': firestore.SERVER_TIMESTAMP
            })
            
        except Exception as e:
            print(f"Error incrementing stat {stat_name}: {e}")
    
    # ==================== Settings Management ====================
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Save user settings to Firestore.
        
        Args:
            settings: Dictionary of settings to save
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_online() or not self.user_id:
            return False
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            settings_ref = user_ref.collection('settings').document('preferences')
            
            # Add timestamp
            settings['lastModified'] = firestore.SERVER_TIMESTAMP
            
            # Save settings
            settings_ref.set(settings, merge=True)
            
            print("Settings saved successfully")
            return True
            
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def load_settings(self) -> Optional[Dict[str, Any]]:
        """
        Load user settings from Firestore.
        
        Returns:
            Settings dictionary if successful, None otherwise
        """
        if not self.is_online() or not self.user_id:
            return None
        
        try:
            user_ref = self.db.collection('users').document(self.user_id)
            settings_ref = user_ref.collection('settings').document('preferences')
            settings_doc = settings_ref.get()
            
            if settings_doc.exists:
                return settings_doc.to_dict()
            else:
                return None
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            return None
    
    # ==================== Leaderboard ====================
    
    def get_leaderboard(self, stat_name: str = 'highestRound', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get leaderboard for a specific stat.
        
        Args:
            stat_name: Name of stat to rank by
            limit: Number of top players to return
            
        Returns:
            List of player data with rankings
        """
        if not self.is_online():
            return []
        
        try:
            # Query all users' stats
            users_ref = self.db.collection('users')
            
            leaderboard = []
            for user_doc in users_ref.stream():
                user_id = user_doc.id
                stats_ref = users_ref.document(user_id).collection('stats').document('overall')
                stats_doc = stats_ref.get()
                
                if stats_doc.exists:
                    stats = stats_doc.to_dict()
                    user_data = user_doc.to_dict()
                    
                    leaderboard.append({
                        'userId': user_id,
                        'displayName': user_data.get('displayName', 'Anonymous'),
                        stat_name: stats.get(stat_name, 0),
                        'stats': stats
                    })
            
            # Sort by the specified stat
            leaderboard.sort(key=lambda x: x.get(stat_name, 0), reverse=True)
            
            # Return top N
            return leaderboard[:limit]
            
        except Exception as e:
            print(f"Error getting leaderboard: {e}")
            return []


# Global Firebase service instance
firebase_service = FirebaseService()
