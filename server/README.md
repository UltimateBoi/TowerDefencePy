# Tower Defense Backend API

This is the backend server for the Tower Defense game. It handles all Firebase operations server-side to keep credentials secure.

## Deployment

### Quick Deploy to Render.com (Free)

1. Sign up at [render.com](https://render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Root Directory**: `server`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add environment variable:
   - `FIREBASE_CREDENTIALS_JSON`: Paste your entire `firebase-credentials.json` as a single-line JSON string
6. Deploy!

### Environment Variables

Required:

- `FIREBASE_CREDENTIALS_JSON`: Your Firebase service account credentials as JSON string

Optional:

- `FLASK_ENV`: Set to `production` for production deployment
- `PORT`: Port to run on (default: 5000)

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your Firebase credentials

# Run server
python app.py
```

The server will start on `http://localhost:5000`

## 📡 API Endpoints

### Health Check

```
GET /api/health
```

Returns backend status.

### Authentication

```
POST /api/auth/verify
Body: {"idToken": "..."}
```

Verifies Google OAuth ID token and returns user info.

### User Stats

```
GET /api/stats
Headers: Authorization: Bearer <id_token>
```

Get user statistics.

```
POST /api/stats
Headers: Authorization: Bearer <id_token>
Body: {"totalGamesPlayed": 10, ...}
```

Update user statistics.

### Game Save/Load

```
POST /api/game/save
Headers: Authorization: Bearer <id_token>
Body: {"gameState": {...}}
```

Save game state.

```
GET /api/game/load
Headers: Authorization: Bearer <id_token>
```

Load saved game state.

### Settings

```
GET /api/settings
Headers: Authorization: Bearer <id_token>
```

Get user settings.

```
POST /api/settings
Headers: Authorization: Bearer <id_token>
Body: {"volume": 0.8, ...}
```

Update user settings.

## Security

- All endpoints (except `/health`) require authentication
- ID tokens are verified with Firebase
- CORS enabled for development (configure for production)
- Firebase credentials stored securely on server

## Troubleshooting

### "Failed to initialize Firebase"

- Check `FIREBASE_CREDENTIALS_JSON` environment variable
- Ensure JSON is properly formatted (no line breaks in env var)
- Verify Firebase service account has correct permissions

### CORS errors

- Update CORS configuration in `app.py` for your domain
- Or deploy client and server on same domain

### 401 Unauthorized

- Ensure ID token is being sent in `Authorization` header
- Token may have expired (valid for 1 hour)
- Verify token with Google before sending to backend

## License

Same as main project (MIT)
