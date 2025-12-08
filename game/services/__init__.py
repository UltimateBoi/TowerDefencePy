"""
Services Module
Handles backend communication, authentication, and session management.
"""

from .backend_client import backend_client
from .google_oauth_client import google_oauth_client
from .session_manager import session_manager
from .firebase_service import firebase_service
from .google_auth_service import google_auth_service

__all__ = ['backend_client', 'google_oauth_client', 'session_manager', 'firebase_service', 'google_auth_service']
