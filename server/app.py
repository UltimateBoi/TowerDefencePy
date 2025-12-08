"""
Tower Defense Game - Backend API Server
Handles all Firebase operations server-side to keep credentials secure.
This server should be deployed separately and the API_URL should point to it.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from dotenv import load_dotenv
from functools import wraps
import json

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Initialize Firebase Admin SDK
try:
    # Try to load from environment variable first (for production)
    if os.getenv('FIREBASE_CREDENTIALS_JSON'):
        cred_dict = json.loads(os.getenv('FIREBASE_CREDENTIALS_JSON'))
        cred = credentials.Certificate(cred_dict)
    else:
        # Fall back to local file (for development)
        cred = credentials.Certificate('../firebase-credentials.json')
    
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✓ Firebase Admin SDK initialized successfully")
except Exception as e:
    print(f"✗ Failed to initialize Firebase: {e}")
    db = None


def require_auth(f):
    """Decorator to require valid Firebase ID token."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No authorization token provided'}), 401
        
        id_token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify the ID token
            decoded_token = auth.verify_id_token(id_token)
            request.user_id = decoded_token['uid']
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401
    
    return decorated_function


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'online',
        'firebase': db is not None
    })


@app.route('/api/auth/exchange-code', methods=['POST'])
def exchange_code():
    """Exchange OAuth authorization code for ID token."""
    import requests as req
    
    data = request.json
    code = data.get('code')
    
    if not code:
        return jsonify({'error': 'No authorization code provided'}), 400
    
    # Get Google OAuth credentials from environment
    client_id = os.getenv('GOOGLE_CLIENT_ID')
    client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return jsonify({'error': 'OAuth credentials not configured on server'}), 500
    
    # Exchange code for tokens
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:8080',
        'grant_type': 'authorization_code'
    }
    
    try:
        response = req.post(token_url, data=token_data, timeout=10)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({'error': 'Token exchange failed', 'details': response.json()}), 400
    
    except Exception as e:
        return jsonify({'error': 'Token exchange error', 'details': str(e)}), 500


@app.route('/api/auth/verify', methods=['POST'])
def verify_token():
    """Verify a Google OAuth ID token and return user info."""
    import requests as req
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests
    
    data = request.json
    token = data.get('idToken')
    
    if not token:
        return jsonify({'error': 'No ID token provided'}), 400
    
    try:
        # Verify the Google ID token
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        
        # Verify with Google's token verification endpoint
        idinfo = id_token.verify_oauth2_token(
            token, 
            google_requests.Request(), 
            client_id
        )
        
        # Extract user info from token
        user_id = idinfo['sub']
        email = idinfo.get('email', '')
        display_name = idinfo.get('name', email.split('@')[0])
        photo_url = idinfo.get('picture', '')
        email_verified = idinfo.get('email_verified', False)
        
        # Get or create user document in Firestore
        user_ref = db.collection('users').document(f"google_{user_id}")
        user_doc = user_ref.get()
        
        user_data = {
            'uid': f"google_{user_id}",
            'email': email,
            'displayName': display_name,
            'photoURL': photo_url,
            'emailVerified': email_verified
        }
        
        # Create user document if it doesn't exist
        if not user_doc.exists:
            user_ref.set({
                'email': email,
                'displayName': display_name,
                'photoURL': photo_url,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'lastLogin': firestore.SERVER_TIMESTAMP
            })
        else:
            # Update last login
            user_ref.update({
                'lastLogin': firestore.SERVER_TIMESTAMP
            })
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    
    except Exception as e:
        return jsonify({'error': 'Token verification failed', 'details': str(e)}), 401


@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Get user statistics."""
    try:
        user_id = request.user_id
        stats_ref = db.collection('users').document(user_id).collection('stats').document('game_stats')
        stats_doc = stats_ref.get()
        
        if stats_doc.exists:
            return jsonify(stats_doc.to_dict())
        else:
            # Return default stats
            default_stats = {
                'totalGamesPlayed': 0,
                'totalWins': 0,
                'highestRound': 0,
                'totalTowerDamage': 0,
                'totalBloonsPopped': 0,
                'totalMoneyEarned': 0
            }
            return jsonify(default_stats)
    
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'details': str(e)}), 500


@app.route('/api/stats', methods=['POST'])
@require_auth
def update_stats():
    """Update user statistics."""
    try:
        user_id = request.user_id
        stats_data = request.json
        
        stats_ref = db.collection('users').document(user_id).collection('stats').document('game_stats')
        stats_ref.set(stats_data, merge=True)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': 'Failed to update stats', 'details': str(e)}), 500


@app.route('/api/game/save', methods=['POST'])
@require_auth
def save_game():
    """Save game state."""
    try:
        user_id = request.user_id
        game_data = request.json
        
        save_ref = db.collection('users').document(user_id).collection('saves').document('current_game')
        save_ref.set({
            'gameState': game_data,
            'savedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': 'Failed to save game', 'details': str(e)}), 500


@app.route('/api/game/load', methods=['GET'])
@require_auth
def load_game():
    """Load game state."""
    try:
        user_id = request.user_id
        
        save_ref = db.collection('users').document(user_id).collection('saves').document('current_game')
        save_doc = save_ref.get()
        
        if save_doc.exists:
            return jsonify(save_doc.to_dict())
        else:
            return jsonify({'gameState': None}), 404
    
    except Exception as e:
        return jsonify({'error': 'Failed to load game', 'details': str(e)}), 500


@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """Get user settings."""
    try:
        user_id = request.user_id
        
        settings_ref = db.collection('users').document(user_id).collection('settings').document('preferences')
        settings_doc = settings_ref.get()
        
        if settings_doc.exists:
            return jsonify(settings_doc.to_dict())
        else:
            return jsonify({}), 404
    
    except Exception as e:
        return jsonify({'error': 'Failed to get settings', 'details': str(e)}), 500


@app.route('/api/settings', methods=['POST'])
@require_auth
def update_settings():
    """Update user settings."""
    try:
        user_id = request.user_id
        settings_data = request.json
        
        settings_ref = db.collection('users').document(user_id).collection('settings').document('preferences')
        settings_ref.set(settings_data, merge=True)
        
        return jsonify({'success': True})
    
    except Exception as e:
        return jsonify({'error': 'Failed to update settings', 'details': str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
