"""
Google OAuth Client Service
Handles Google Sign-In OAuth2 flow (client-side only).
The ID token is sent to the backend for verification.
No Firebase credentials needed client-side.
"""

import json
import webbrowser
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict
import requests
import os
from dotenv import load_dotenv

load_dotenv()


class GoogleAuthHandler(BaseHTTPRequestHandler):
    """HTTP handler for OAuth callback."""
    
    auth_code = None
    
    def do_GET(self):
        """Handle OAuth callback."""
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
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body {
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                    }
                    .container {
                        text-align: center;
                        background: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        padding: 3rem;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        max-width: 400px;
                        animation: slideUp 0.5s ease-out;
                    }
                    @keyframes slideUp {
                        from { opacity: 0; transform: translateY(30px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                    .checkmark {
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        background: #4CAF50;
                        margin: 0 auto 1.5rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 3rem;
                        animation: scaleIn 0.3s ease-out 0.2s both;
                    }
                    @keyframes scaleIn {
                        from { transform: scale(0); }
                        to { transform: scale(1); }
                    }
                    h1 { font-size: 2rem; margin-bottom: 1rem; }
                    p { font-size: 1.1rem; opacity: 0.9; margin-bottom: 1.5rem; }
                    .note { font-size: 0.9rem; opacity: 0.7; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="checkmark">✓</div>
                    <h1>Login Successful!</h1>
                    <p>You can now close this window and return to the game.</p>
                    <p class="note">This window will close automatically in 3 seconds...</p>
                </div>
                <script>
                    setTimeout(() => window.close(), 3000);
                </script>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())
        else:
            error = params.get('error', ['Unknown error'])[0]
            GoogleAuthHandler.auth_code = None
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Login Failed - Tower Defense</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                    }}
                    .container {{
                        text-align: center;
                        background: rgba(255, 255, 255, 0.1);
                        backdrop-filter: blur(10px);
                        padding: 3rem;
                        border-radius: 20px;
                        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                        max-width: 400px;
                    }}
                    .error-icon {{
                        width: 80px;
                        height: 80px;
                        border-radius: 50%;
                        background: #f44336;
                        margin: 0 auto 1.5rem;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 3rem;
                    }}
                    h1 {{ font-size: 2rem; margin-bottom: 1rem; }}
                    p {{ font-size: 1.1rem; opacity: 0.9; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="error-icon">✗</div>
                    <h1>Login Failed</h1>
                    <p>Error: {error}</p>
                    <p style="margin-top: 1rem;">Please close this window and try again.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


class GoogleOAuthClient:
    """
    Handles Google OAuth2 authentication flow (client-side).
    ID tokens are verified server-side.
    """
    
    def __init__(self):
        """Initialize OAuth client with public client ID."""
        # This OAuth Client ID is public and safe to include in source code
        # It's restricted to only work with your authorized redirect URIs
        self.client_id = os.getenv(
            'GOOGLE_CLIENT_ID',
            '1234567890-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com'  # Replace with your public client ID
        )
        self.redirect_uri = 'http://localhost:8080'
        self.scope = 'openid email profile'
    
    def sign_in_with_google(self) -> Optional[str]:
        """
        Initiate Google Sign-In flow.
        Returns the ID token if successful, None otherwise.
        """
        print("Starting Google Sign-In...")
        
        # Build authorization URL
        auth_url = self._build_auth_url()
        
        # Start local server to handle callback
        server = HTTPServer(('localhost', 8080), GoogleAuthHandler)
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()
        
        # Open browser for user to sign in
        webbrowser.open(auth_url)
        print("Browser opened for Google Sign-In. Waiting for callback...")
        
        # Wait for callback
        server_thread.join(timeout=120)
        
        auth_code = GoogleAuthHandler.auth_code
        GoogleAuthHandler.auth_code = None
        
        if not auth_code:
            print("Failed to get authorization code")
            return None
        
        # Exchange authorization code for tokens
        token_data = self._exchange_code_for_token(auth_code)
        
        if token_data and 'id_token' in token_data:
            print("Successfully obtained ID token")
            return token_data['id_token']
        
        return None
    
    def _build_auth_url(self) -> str:
        """Build Google OAuth authorization URL."""
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': self.scope,
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        query_string = urllib.parse.urlencode(params)
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    def _exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """
        Exchange authorization code for tokens via backend server.
        This keeps the client secret secure on the server.
        """
        # Get backend URL from environment or use default
        backend_url = os.getenv('BACKEND_API_URL', 'https://towerdefencepy.onrender.com')
        
        try:
            response = requests.post(
                f'{backend_url}/api/auth/exchange-code',
                json={'code': code},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                error_data = response.json()
                print(f"Token exchange failed: {error_data.get('error')}")
                return None
        
        except Exception as e:
            print(f"Error exchanging code for token: {e}")
            return None


# Global instance
google_oauth_client = GoogleOAuthClient()
