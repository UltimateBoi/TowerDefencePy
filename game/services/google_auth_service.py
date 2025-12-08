"""
Google OAuth Authentication Service
Handles Google Sign-In using OAuth2 flow with local server
"""

import json
import webbrowser
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class GoogleAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    
    auth_code = None
    
    def do_GET(self):
        """Handle OAuth callback."""
        # Parse the callback URL
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        
        if 'code' in params:
            GoogleAuthHandler.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            success_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login Successful - Tower Defense</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        padding: 60px 50px;
                        text-align: center;
                        max-width: 500px;
                        animation: slideIn 0.5s ease-out;
                    }
                    @keyframes slideIn {
                        from {
                            opacity: 0;
                            transform: translateY(-30px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    .checkmark {
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 30px;
                        animation: scaleIn 0.5s ease-out 0.2s both;
                    }
                    @keyframes scaleIn {
                        from {
                            transform: scale(0);
                        }
                        to {
                            transform: scale(1);
                        }
                    }
                    .checkmark svg {
                        width: 50px;
                        height: 50px;
                    }
                    h1 {
                        color: #2d3748;
                        font-size: 32px;
                        margin-bottom: 15px;
                        font-weight: 700;
                    }
                    p {
                        color: #718096;
                        font-size: 18px;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }
                    .game-info {
                        background: #f7fafc;
                        border-radius: 12px;
                        padding: 20px;
                        margin-top: 30px;
                    }
                    .game-info p {
                        color: #4a5568;
                        font-size: 14px;
                        margin: 0;
                    }
                    .spinner {
                        width: 40px;
                        height: 40px;
                        border: 4px solid #e2e8f0;
                        border-top-color: #667eea;
                        border-radius: 50%;
                        animation: spin 0.8s linear infinite;
                        margin: 20px auto 0;
                    }
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="checkmark">
                        <svg fill="none" stroke="white" stroke-width="3" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
                        </svg>
                    </div>
                    <h1>Login Successful!</h1>
                    <p>You've successfully authenticated with Google.<br>You can now close this window and return to the game.</p>
                    <div class="game-info">
                        <p><strong>Tower Defense</strong><br>Your progress will be synced across all devices</p>
                    </div>
                    <div class="spinner"></div>
                </div>
                <script>
                    // Auto-close after 2 seconds
                    setTimeout(() => {
                        window.close();
                        // If window.close() fails (popup blockers), show message
                        setTimeout(() => {
                            document.querySelector('.spinner').style.display = 'none';
                            document.querySelector('.game-info').innerHTML = '<p style="color: #667eea; font-weight: 600;">You can safely close this tab now</p>';
                        }, 500);
                    }, 2000);
                </script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login Failed - Tower Defense</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }
                    .container {
                        background: white;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        padding: 60px 50px;
                        text-align: center;
                        max-width: 500px;
                        animation: slideIn 0.5s ease-out;
                    }
                    @keyframes slideIn {
                        from {
                            opacity: 0;
                            transform: translateY(-30px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    .error-icon {
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin: 0 auto 30px;
                        animation: scaleIn 0.5s ease-out 0.2s both;
                    }
                    @keyframes scaleIn {
                        from {
                            transform: scale(0);
                        }
                        to {
                            transform: scale(1);
                        }
                    }
                    .error-icon svg {
                        width: 50px;
                        height: 50px;
                    }
                    h1 {
                        color: #2d3748;
                        font-size: 32px;
                        margin-bottom: 15px;
                        font-weight: 700;
                    }
                    p {
                        color: #718096;
                        font-size: 18px;
                        line-height: 1.6;
                        margin-bottom: 30px;
                    }
                    .actions {
                        display: flex;
                        gap: 15px;
                        justify-content: center;
                        flex-wrap: wrap;
                    }
                    .btn {
                        padding: 12px 30px;
                        border-radius: 10px;
                        font-size: 16px;
                        font-weight: 600;
                        text-decoration: none;
                        display: inline-block;
                        transition: transform 0.2s, box-shadow 0.2s;
                        cursor: pointer;
                        border: none;
                    }
                    .btn:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
                    }
                    .btn-primary {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .btn-secondary {
                        background: #e2e8f0;
                        color: #4a5568;
                    }
                    .error-details {
                        background: #fff5f5;
                        border-left: 4px solid #f56565;
                        border-radius: 8px;
                        padding: 15px;
                        margin-top: 30px;
                        text-align: left;
                    }
                    .error-details p {
                        color: #742a2a;
                        font-size: 14px;
                        margin: 0;
                    }
                    .error-details strong {
                        display: block;
                        margin-bottom: 8px;
                        color: #c53030;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error-icon">
                        <svg fill="none" stroke="white" stroke-width="3" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </div>
                    <h1>Login Failed</h1>
                    <p>We couldn't complete your Google Sign-In.<br>This might happen if you cancelled the login or denied permissions.</p>
                    <div class="actions">
                        <button class="btn btn-primary" onclick="window.close()">Close Window</button>
                        <button class="btn btn-secondary" onclick="location.reload()">Try Again</button>
                    </div>
                    <div class="error-details">
                        <strong>Troubleshooting Tips:</strong>
                        <p>• Make sure you allow all requested permissions<br>
                        • Check your internet connection<br>
                        • Try using a different browser<br>
                        • Or play offline in the game menu</p>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress server logs."""
        pass


class GoogleAuthService:
    """Service for Google OAuth authentication."""
    
    def __init__(self):
        self.api_key = os.getenv('FIREBASE_API_KEY')
        self.project_id = os.getenv('FIREBASE_PROJECT_ID')
        self.redirect_uri = "http://localhost:8080"
        self.server = None
        self.server_thread = None
        
        # OAuth endpoints
        self.auth_endpoint = "https://accounts.google.com/o/oauth2/v2/auth"
        self.token_endpoint = "https://oauth2.googleapis.com/token"
        self.userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        
        # Load OAuth credentials
        self.client_id = None
        self.client_secret = None
        self._load_oauth_credentials()
        
    def _load_oauth_credentials(self) -> bool:
        """Load OAuth client configuration from google-oauth-credentials.json"""
        try:
            with open('google-oauth-credentials.json', 'r') as f:
                creds = json.load(f)
                web_config = creds.get('web', creds.get('installed', {}))
                self.client_id = web_config.get('client_id')
                self.client_secret = web_config.get('client_secret')
                return self.client_id is not None
        except FileNotFoundError:
            print("WARNING: OAuth credentials file not found")
            return False
        except Exception as e:
            print(f"Error loading OAuth credentials: {e}")
            return False
    
    def start_local_server(self):
        """Start local HTTP server for OAuth callback."""
        self.server = HTTPServer(('localhost', 8080), GoogleAuthHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def stop_local_server(self):
        """Stop local HTTP server."""
        if self.server:
            self.server.shutdown()
            self.server = None
    
    def sign_in_with_google(self) -> Optional[Dict[str, Any]]:
        """
        Initiate Google Sign-In flow.
        Opens browser for user authentication.
        
        Returns:
            User info dict if successful, None otherwise
        """
        if not self.client_id or not self.client_secret:
            print("ERROR: OAuth credentials not configured")
            print("\nSetup required:")
            print("1. Ensure google-oauth-credentials.json exists in project root")
            print("2. File should contain client_id and client_secret")
            return None
        
        try:
            # Reset auth code
            GoogleAuthHandler.auth_code = None
            
            # Start local server
            self.start_local_server()
            
            # Build authorization URL
            params = {
                'client_id': self.client_id,
                'redirect_uri': self.redirect_uri,
                'response_type': 'code',
                'scope': 'openid email profile',
                'access_type': 'offline',
                'prompt': 'select_account'
            }
            
            auth_url = f"{self.auth_endpoint}?{urllib.parse.urlencode(params)}"
            
            # Open browser
            print("Opening browser for Google Sign-In...")
            webbrowser.open(auth_url)
            
            # Wait for callback (with timeout)
            import time
            timeout = 120  # 2 minutes
            start_time = time.time()
            
            while GoogleAuthHandler.auth_code is None:
                if time.time() - start_time > timeout:
                    print("Authentication timed out")
                    self.stop_local_server()
                    return None
                time.sleep(0.5)
            
            auth_code = GoogleAuthHandler.auth_code
            self.stop_local_server()
            
            # Exchange code for tokens
            print("Exchanging authorization code for tokens...")
            token_response = self.exchange_code_for_token(auth_code, self.client_id, self.client_secret)
            
            if not token_response:
                return None
            
            access_token = token_response.get('access_token')
            id_token = token_response.get('id_token')
            
            # Get user info
            print("Fetching user information...")
            user_info = self.get_user_info(access_token)
            
            if user_info:
                print(f"Successfully signed in as: {user_info.get('email')}")
                # Add tokens to user info for Firebase authentication
                user_info['id_token'] = id_token
                user_info['access_token'] = access_token
                return user_info
            
            return None
            
        except Exception as e:
            print(f"ERROR: Error during Google Sign-In: {e}")
            self.stop_local_server()
            return None
    
    def exchange_code_for_token(self, auth_code: str, client_id: str, client_secret: str) -> Optional[Dict[str, str]]:
        """
        Exchange authorization code for access token.
        
        Args:
            auth_code: Authorization code from OAuth callback
            client_id: OAuth client ID
            client_secret: OAuth client secret
            
        Returns:
            Token dict if successful, None otherwise
        """
        try:
            response = requests.post(self.token_endpoint, data={
                'code': auth_code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code'
            })
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ERROR: Token exchange failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"ERROR: Error exchanging code for token: {e}")
            return None
    
    def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get user information from Google.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            User info dict if successful, None otherwise
        """
        try:
            response = requests.get(
                self.userinfo_endpoint,
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get user info: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def sign_in_with_custom_token(self, custom_token: str) -> Optional[Dict[str, Any]]:
        """
        Sign in to Firebase using a custom token.
        
        Args:
            custom_token: Custom token from Firebase Admin SDK
            
        Returns:
            User credentials if successful, None otherwise
        """
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithCustomToken?key={self.api_key}"
            response = requests.post(url, json={
                'token': custom_token,
                'returnSecureToken': True
            })
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"ERROR: Token exchange failed: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error signing in with custom token: {e}")
            return None


# Global instance
google_auth_service = GoogleAuthService()
