import os
from datetime import timedelta
import bcrypt

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-super-secret-session-key-2024')
ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', 'your-super-secret-access-key-2024')
REFRESH_TOKEN_SECRET = os.environ.get('REFRESH_TOKEN_SECRET', 'your-super-secret-refresh-key-2024')

ACCESS_TOKEN_EXPIRATION = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)

OAUTH2_ENABLED = True
OAUTH_AUTH_CODE_EXPIRATION = timedelta(minutes=10)
OAUTH_ACCESS_TOKEN_EXPIRATION = timedelta(hours=1)

OAUTH_CLIENTS = {
    'web-app-client': {
        'client_id': 'web-app-client',
        'client_secret': 'web-app-secret-12345',
        'name': 'Web Application',
        'redirect_uris': [
            'http://localhost:3000/oauth/callback',
            'http://localhost:8000/callback'
        ],
        'allowed_scopes': ['read:products', 'write:products', 'read:orders', 'write:orders'],
        'grant_types': ['authorization_code', 'refresh_token']
    },
    'mobile-app-client': {
        'client_id': 'mobile-app-client',
        'client_secret': 'mobile-app-secret-67890',
        'name': 'Mobile Application',
        'redirect_uris': [
            'myapp://oauth/callback'
        ],
        'allowed_scopes': ['read:products', 'read:orders'],
        'grant_types': ['authorization_code', 'refresh_token']
    },
    'backend-service': {
        'client_id': 'backend-service',
        'client_secret': 'backend-service-secret-99999',
        'name': 'Backend Service',
        'redirect_uris': [],
        'allowed_scopes': ['read:products', 'write:products', 'read:orders', 'write:orders'],
        'grant_types': ['client_credentials']
    }
}

OAUTH_AUTH_CODES = {}
OAUTH_TOKENS = {}

REQUIRE_HTTPS = False
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'https://yourdomain.com']
TOKEN_BLACKLIST = set()

USERS_DB = {
    'alice': {
        'id': 1,
        'password_hash': bcrypt.hashpw(b'alice123', bcrypt.gensalt()).decode('utf-8'),
        'email': 'alice@example.com',
        'roles': ['admin', 'user'],
        'scopes': ['read:products', 'write:products', 'read:orders', 'write:orders']
    },
    'bob': {
        'id': 2,
        'password_hash': bcrypt.hashpw(b'bob456', bcrypt.gensalt()).decode('utf-8'),
        'email': 'bob@example.com',
        'roles': ['user'],
        'scopes': ['read:products', 'read:orders']
    },
    'charlie': {
        'id': 3,
        'password_hash': bcrypt.hashpw(b'charlie789', bcrypt.gensalt()).decode('utf-8'),
        'email': 'charlie@example.com',
        'roles': ['moderator'],
        'scopes': ['read:products', 'read:users', 'read:orders']
    }
}
