from flask import Flask, request, jsonify, redirect, url_for, session
from functools import wraps
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import secrets
from typing import Dict, Tuple, Optional
from urllib.parse import urlencode, parse_qs, urlparse

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-super-secret-session-key-2024')

ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', 'your-super-secret-access-key-2024')
REFRESH_TOKEN_SECRET = os.environ.get('REFRESH_TOKEN_SECRET', 'your-super-secret-refresh-key-2024')

ACCESS_TOKEN_EXPIRATION = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)

# OAuth 2.0 Configuration
OAUTH2_ENABLED = True
OAUTH_AUTH_CODE_EXPIRATION = timedelta(minutes=10)
OAUTH_ACCESS_TOKEN_EXPIRATION = timedelta(hours=1)

# OAuth 2.0 Registered Clients Database
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

# OAuth 2.0 Authorization Codes Store (in-memory, use Redis in production)
OAUTH_AUTH_CODES = {}  # {code: {client_id, user_id, scopes, expires_at, username}}
OAUTH_TOKENS = {}  # {token: {client_id, user_id, scopes, expires_at}}

REQUIRE_HTTPS = False
CORS_ALLOWED_ORIGINS = ['http://localhost:3000', 'https://yourdomain.com']

TOKEN_BLACKLIST = set()

USERS_DB = {
    'alice': {
        'id': 1,
        'password_hash': bcrypt.hashpw(b'alice123', bcrypt.gensalt()).decode('utf-8'),
        'email': 'alice@example.com',
        'roles': ['admin', 'user'],  # Multiple roles
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

class TokenManager:

    @staticmethod
    def generate_access_token(user_id: int, username: str, roles: list, scopes: list) -> str:
        payload = {
            'user_id': user_id,
            'username': username,
            'roles': roles,
            'scopes': scopes,
            'exp': datetime.utcnow() + ACCESS_TOKEN_EXPIRATION,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm='HS256')

    @staticmethod
    def generate_refresh_token(user_id: int, username: str) -> str:
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + REFRESH_TOKEN_EXPIRATION,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(payload, REFRESH_TOKEN_SECRET, algorithm='HS256')

    @staticmethod
    def verify_access_token(token: str) -> Dict:
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=['HS256'])
            
            if token in TOKEN_BLACKLIST:
                raise jwt.InvalidTokenError('Token has been revoked')
            if payload.get('type') != 'access':
                raise jwt.InvalidTokenError('Invalid token type')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Token has expired')
        except jwt.InvalidTokenError as e:
            raise Exception(f'Invalid token: {str(e)}')

    @staticmethod
    def verify_refresh_token(token: str) -> Dict:
        try:
            payload = jwt.decode(token, REFRESH_TOKEN_SECRET, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise jwt.InvalidTokenError('Invalid token type')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('Refresh token has expired')
        except jwt.InvalidTokenError as e:
            raise Exception(f'Invalid refresh token: {str(e)}')


# ============================================================================
# OAUTH 2.0 MANAGER
# ============================================================================

class OAuth2Manager:
    """
    Implements OAuth 2.0 Authorization Server (RFC 6749)
    Supports: Authorization Code Flow, Client Credentials Flow
    """

    @staticmethod
    def validate_client(client_id: str, client_secret: str = None) -> Dict:
        """Validate OAuth 2.0 client credentials"""
        client = OAUTH_CLIENTS.get(client_id)
        
        if not client:
            raise Exception('Invalid client_id')
        
        if client_secret and client.get('client_secret') != client_secret:
            raise Exception('Invalid client_secret')
        
        return client

    @staticmethod
    def validate_redirect_uri(client_id: str, redirect_uri: str) -> bool:
        """Validate that redirect_uri is registered for the client"""
        client = OAUTH_CLIENTS.get(client_id)
        
        if not client:
            return False
        
        return redirect_uri in client.get('redirect_uris', [])

    @staticmethod
    def generate_authorization_code(client_id: str, user_id: int, 
                                    username: str, scopes: list) -> str:
        """Generate authorization code (valid for 10 minutes)"""
        code = secrets.token_urlsafe(32)
        
        OAUTH_AUTH_CODES[code] = {
            'client_id': client_id,
            'user_id': user_id,
            'username': username,
            'scopes': scopes,
            'expires_at': datetime.utcnow() + OAUTH_AUTH_CODE_EXPIRATION,
            'used': False
        }
        
        return code

    @staticmethod
    def redeem_authorization_code(code: str, client_id: str) -> Dict:
        """Exchange authorization code for access token"""
        auth_code_data = OAUTH_AUTH_CODES.get(code)
        
        if not auth_code_data:
            raise Exception('Invalid authorization code')
        
        if auth_code_data['used']:
            # Code reuse detected - security violation
            OAUTH_AUTH_CODES.pop(code, None)
            raise Exception('Authorization code already used - possible attack')
        
        if auth_code_data['expires_at'] < datetime.utcnow():
            raise Exception('Authorization code expired')
        
        if auth_code_data['client_id'] != client_id:
            raise Exception('Client ID mismatch')
        
        # Mark as used
        auth_code_data['used'] = True
        
        return auth_code_data

    @staticmethod
    def generate_oauth_access_token(user_id: int, username: str, 
                                   scopes: list, client_id: str) -> str:
        """Generate OAuth 2.0 access token"""
        payload = {
            'user_id': user_id,
            'username': username,
            'scopes': scopes,
            'client_id': client_id,
            'exp': datetime.utcnow() + OAUTH_ACCESS_TOKEN_EXPIRATION,
            'iat': datetime.utcnow(),
            'type': 'oauth_access'
        }
        
        token = jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm='HS256')
        
        OAUTH_TOKENS[token] = {
            'client_id': client_id,
            'user_id': user_id,
            'scopes': scopes,
            'expires_at': payload['exp']
        }
        
        return token

    @staticmethod
    def verify_oauth_token(token: str) -> Dict:
        """Verify OAuth 2.0 access token"""
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=['HS256'])
            
            if payload.get('type') != 'oauth_access':
                raise jwt.InvalidTokenError('Invalid token type')
            
            if token not in OAUTH_TOKENS:
                raise jwt.InvalidTokenError('Token not found in store')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('OAuth token has expired')
        except jwt.InvalidTokenError as e:
            raise Exception(f'Invalid OAuth token: {str(e)}')

    @staticmethod
    def validate_scopes(requested_scopes: list, allowed_scopes: list) -> list:
        """Validate and return intersection of requested and allowed scopes"""
        if not requested_scopes:
            return allowed_scopes  # Grant all allowed scopes
        
        # Only grant scopes that are both requested and allowed
        validated = [s for s in requested_scopes if s in allowed_scopes]
        
        if not validated:
            raise Exception('No valid scopes requested')
        
        return validated


# ============================================================================
# AUTHENTICATION & AUTHORIZATION DECORATORS
# ============================================================================

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Missing Authorization header'}), 401
        
        try:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid Authorization header format'}), 401
            
            token = parts[1]
            payload = TokenManager.verify_access_token(token)
            
            request.current_user = payload
            request.token = token
            
            return f(*args, **kwargs)
        
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function


def require_role(*required_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_roles = request.current_user.get('roles', [])
            
            if not any(role in user_roles for role in required_roles):
                return jsonify({
                    'error': f'Insufficient permissions. Required roles: {required_roles}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_scope(*required_scopes):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(request, 'current_user'):
                return jsonify({'error': 'Not authenticated'}), 401
            
            user_scopes = request.current_user.get('scopes', [])
            
            if not all(scope in user_scopes for scope in required_scopes):
                return jsonify({
                    'error': f'Insufficient scopes. Required: {required_scopes}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator


def require_oauth(*required_scopes):
    """OAuth 2.0 token authentication decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'Missing Authorization header'}), 401
            
            try:
                parts = auth_header.split()
                if len(parts) != 2 or parts[0].lower() != 'bearer':
                    return jsonify({'error': 'Invalid Authorization header format'}), 401
                
                token = parts[1]
                payload = OAuth2Manager.verify_oauth_token(token)
                
                if required_scopes:
                    user_scopes = payload.get('scopes', [])
                    if not all(scope in user_scopes for scope in required_scopes):
                        return jsonify({
                            'error': f'Insufficient scopes. Required: {required_scopes}'
                        }), 403
                
                request.oauth_user = payload
                request.oauth_token = token
                
                return f(*args, **kwargs)
            
            except Exception as e:
                return jsonify({'error': str(e)}), 401
        
        return decorated_function
    return decorator


# ============================================================================
# ROUTES: AUTHENTICATION
# ============================================================================

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    username = data['username'].lower()
    password = data['password']
    
    user = USERS_DB.get(username)
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    access_token = TokenManager.generate_access_token(
        user_id=user['id'],
        username=username,
        roles=user['roles'],
        scopes=user['scopes']
    )
    
    refresh_token = TokenManager.generate_refresh_token(
        user_id=user['id'],
        username=username
    )
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'Bearer',
        'expires_in': int(ACCESS_TOKEN_EXPIRATION.total_seconds()),
        'user': {
            'id': user['id'],
            'username': username,
            'email': user['email'],
            'roles': user['roles']
        }
    }), 200


@app.route('/auth/refresh', methods=['POST'])
def refresh():
    data = request.get_json()
    
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Missing refresh_token'}), 400
    
    try:
        refresh_token = data['refresh_token']
        payload = TokenManager.verify_refresh_token(refresh_token)
        
        user_id = payload['user_id']
        username = payload['username']
        
        user = next((u for u in USERS_DB.values() if u['id'] == user_id), None)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        access_token = TokenManager.generate_access_token(
            user_id=user_id,
            username=username,
            roles=user['roles'],
            scopes=user['scopes']
        )
        
        return jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': int(ACCESS_TOKEN_EXPIRATION.total_seconds())
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@app.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    token = request.token
    TOKEN_BLACKLIST.add(token)
    
    return jsonify({'message': 'Logged out successfully'}), 200


# ============================================================================
# ROUTES: OAUTH 2.0 AUTHORIZATION SERVER
# ============================================================================

@app.route('/oauth/authorize', methods=['GET'])
def oauth_authorize():
    """
    OAuth 2.0 Authorization Endpoint (RFC 6749 Section 3.1)
    Authorization Code Flow - User grants permission
    
    Query Parameters:
    - response_type: "code" (required)
    - client_id: Registered client ID (required)
    - redirect_uri: Where to send user back (required)
    - scope: Space-separated scopes (optional)
    - state: CSRF protection token (recommended)
    """
    
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope', '').split()
    state = request.args.get('state', '')
    
    # Validation
    if response_type != 'code':
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'response_type must be "code"'
        }), 400
    
    try:
        client = OAuth2Manager.validate_client(client_id)
    except Exception as e:
        return jsonify({
            'error': 'invalid_client',
            'error_description': str(e)
        }), 400
    
    if not OAuth2Manager.validate_redirect_uri(client_id, redirect_uri):
        return jsonify({
            'error': 'invalid_request',
            'error_description': 'Invalid redirect_uri'
        }), 400
    
    # Check if user is already authenticated
    if 'user_id' not in session:
        # Redirect to login page
        login_url = url_for('login_page', next=request.url, _external=True)
        return redirect(login_url)
    
    # User already authenticated - grant authorization code
    try:
        validated_scopes = OAuth2Manager.validate_scopes(scope, client.get('allowed_scopes', []))
        
        auth_code = OAuth2Manager.generate_authorization_code(
            client_id=client_id,
            user_id=session['user_id'],
            username=session['username'],
            scopes=validated_scopes
        )
        
        # Redirect back to client with authorization code
        redirect_params = {
            'code': auth_code,
            'state': state
        }
        
        callback_url = f"{redirect_uri}?{urlencode(redirect_params)}"
        return redirect(callback_url)
    
    except Exception as e:
        return jsonify({
            'error': 'server_error',
            'error_description': str(e)
        }), 500


@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    """
    OAuth 2.0 Token Endpoint (RFC 6749 Section 3.2)
    Exchange authorization code for access token
    
    Supports:
    1. Authorization Code Flow
    2. Client Credentials Flow
    3. Refresh Token Flow
    """
    
    data = request.get_json() or {}
    grant_type = data.get('grant_type')
    
    # ===================================================
    # 1. Authorization Code Flow
    # ===================================================
    if grant_type == 'authorization_code':
        code = data.get('code')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        redirect_uri = data.get('redirect_uri')
        
        try:
            # Validate client
            client = OAuth2Manager.validate_client(client_id, client_secret)
            
            # Validate grant type
            if 'authorization_code' not in client.get('grant_types', []):
                return jsonify({
                    'error': 'unauthorized_client',
                    'error_description': 'Client not allowed to use authorization_code grant'
                }), 400
            
            # Redeem authorization code
            code_data = OAuth2Manager.redeem_authorization_code(code, client_id)
            
            # Generate OAuth access token
            access_token = OAuth2Manager.generate_oauth_access_token(
                user_id=code_data['user_id'],
                username=code_data['username'],
                scopes=code_data['scopes'],
                client_id=client_id
            )
            
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': int(OAUTH_ACCESS_TOKEN_EXPIRATION.total_seconds()),
                'scope': ' '.join(code_data['scopes']),
                'user': {
                    'id': code_data['user_id'],
                    'username': code_data['username']
                }
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': 'invalid_grant',
                'error_description': str(e)
            }), 400
    
    # ===================================================
    # 2. Client Credentials Flow (Server-to-Server)
    # ===================================================
    elif grant_type == 'client_credentials':
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        scope = data.get('scope', '').split()
        
        try:
            # Validate client
            client = OAuth2Manager.validate_client(client_id, client_secret)
            
            # Validate grant type
            if 'client_credentials' not in client.get('grant_types', []):
                return jsonify({
                    'error': 'unauthorized_client',
                    'error_description': 'Client not allowed to use client_credentials grant'
                }), 400
            
            # Validate scopes
            validated_scopes = OAuth2Manager.validate_scopes(scope, client.get('allowed_scopes', []))
            
            # Generate access token (for service, user_id = 0)
            access_token = OAuth2Manager.generate_oauth_access_token(
                user_id=0,
                username=client_id,
                scopes=validated_scopes,
                client_id=client_id
            )
            
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': int(OAUTH_ACCESS_TOKEN_EXPIRATION.total_seconds()),
                'scope': ' '.join(validated_scopes)
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': 'invalid_client',
                'error_description': str(e)
            }), 400
    
    # ===================================================
    # 3. Refresh Token Flow
    # ===================================================
    elif grant_type == 'refresh_token':
        refresh_token = data.get('refresh_token')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        
        try:
            # Validate client
            client = OAuth2Manager.validate_client(client_id, client_secret)
            
            # Verify refresh token
            payload = TokenManager.verify_refresh_token(refresh_token)
            
            # Generate new access token
            access_token = OAuth2Manager.generate_oauth_access_token(
                user_id=payload['user_id'],
                username=payload['username'],
                scopes=payload.get('scopes', []),
                client_id=client_id
            )
            
            return jsonify({
                'access_token': access_token,
                'token_type': 'Bearer',
                'expires_in': int(OAUTH_ACCESS_TOKEN_EXPIRATION.total_seconds())
            }), 200
        
        except Exception as e:
            return jsonify({
                'error': 'invalid_grant',
                'error_description': str(e)
            }), 400
    
    else:
        return jsonify({
            'error': 'unsupported_grant_type',
            'error_description': f'Grant type "{grant_type}" is not supported'
        }), 400


@app.route('/oauth/clients', methods=['GET'])
def oauth_list_clients():
    """List OAuth 2.0 registered clients (admin only)"""
    clients = []
    for client_id, client_info in OAUTH_CLIENTS.items():
        clients.append({
            'client_id': client_info['client_id'],
            'name': client_info['name'],
            'redirect_uris': client_info['redirect_uris'],
            'allowed_scopes': client_info['allowed_scopes'],
            'grant_types': client_info['grant_types']
        })
    return jsonify({'clients': clients}), 200


@app.route('/oauth/login', methods=['POST'])
def oauth_login():
    """
    Login page for OAuth 2.0 flow
    In real app, this would show login HTML
    """
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password')
    
    user = USERS_DB.get(username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Store in session
    session['user_id'] = user['id']
    session['username'] = username
    
    return jsonify({
        'message': 'Logged in successfully for OAuth flow',
        'user': {
            'id': user['id'],
            'username': username,
            'email': user['email']
        }
    }), 200


@app.route('/oauth/introspect', methods=['POST'])
def oauth_introspect():
    """
    OAuth 2.0 Token Introspection (RFC 7662)
    Allows clients to check if a token is valid and get its claims
    """
    data = request.get_json() or {}
    token = data.get('token')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not token:
        return jsonify({'error': 'invalid_request'}), 400
    
    try:
        # Validate client
        client = OAuth2Manager.validate_client(client_id, client_secret)
        
        # Verify token
        payload = OAuth2Manager.verify_oauth_token(token)
        
        return jsonify({
            'active': True,
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'client_id': payload.get('client_id'),
            'scope': ' '.join(payload.get('scopes', [])),
            'exp': int(payload['exp'].timestamp()) if isinstance(payload['exp'], datetime) else payload['exp']
        }), 200
    
    except Exception as e:
        return jsonify({'active': False}), 200


@app.route('/oauth/revoke', methods=['POST'])
def oauth_revoke():
    """
    OAuth 2.0 Token Revocation (RFC 7009)
    Allows clients to revoke tokens
    """
    data = request.get_json() or {}
    token = data.get('token')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not token:
        return jsonify({'error': 'invalid_request'}), 400
    
    try:
        # Validate client
        client = OAuth2Manager.validate_client(client_id, client_secret)
        
        # Revoke token
        OAUTH_TOKENS.pop(token, None)
        TOKEN_BLACKLIST.add(token)
        
        return jsonify({'message': 'Token revoked successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/oauth/login-page', methods=['GET'])
def login_page():
    """Simple OAuth login page (for browser-based flow)"""
    next_url = request.args.get('next', '')
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>OAuth 2.0 Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 50px; }}
            .login-form {{ max-width: 400px; margin: auto; border: 1px solid #ddd; padding: 20px; }}
            input {{ width: 100%; padding: 8px; margin: 10px 0; box-sizing: border-box; }}
            button {{ width: 100%; padding: 10px; background: #007bff; color: white; border: none; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <div class="login-form">
            <h2>OAuth 2.0 Login</h2>
            <form method="POST" action="/oauth/login">
                <input type="text" name="username" placeholder="Username" required />
                <input type="password" name="password" placeholder="Password" required />
                <input type="hidden" name="next" value="{next_url}" />
                <button type="submit">Login</button>
            </form>
            <hr>
            <p>Demo users:</p>
            <ul>
                <li>alice / alice123</li>
                <li>bob / bob456</li>
                <li>charlie / charlie789</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return html, 200, {'Content-Type': 'text/html'}


# ============================================================================
# ROUTES: PROTECTED RESOURCES
# ============================================================================

@app.route('/products', methods=['GET'])
@require_auth
@require_scope('read:products')
def get_products():
    products = [
        {'id': 1, 'name': 'Laptop', 'price': 1000},
        {'id': 2, 'name': 'Mouse', 'price': 50},
        {'id': 3, 'name': 'Keyboard', 'price': 80}
    ]
    
    return jsonify({
        'data': products,
        'current_user': request.current_user['username'],
        'roles': request.current_user['roles']
    }), 200


@app.route('/products', methods=['POST'])
@require_auth
@require_scope('write:products')
def create_product():
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    product = {
        'id': 4,
        'name': data['name'],
        'price': data['price'],
        'created_by': request.current_user['username']
    }
    
    return jsonify({
        'message': 'Product created successfully',
        'data': product
    }), 201


@app.route('/admin/users', methods=['GET'])
@require_auth
@require_role('admin')
def list_users():
    users = [
        {'id': u['id'], 'email': u['email'], 'roles': u['roles']} 
        for u in USERS_DB.values()
    ]
    
    return jsonify({
        'data': users,
        'accessed_by': request.current_user['username']
    }), 200


@app.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    return jsonify({
        'message': f'User {user_id} deleted successfully',
        'deleted_by': request.current_user['username']
    }), 200


@app.route('/orders', methods=['GET'])
@require_auth
@require_role('user')
def get_orders():
    orders = [
        {'id': 1, 'user_id': request.current_user['user_id'], 'total': 150},
        {'id': 2, 'user_id': request.current_user['user_id'], 'total': 250}
    ]
    
    return jsonify({
        'data': orders,
        'user': request.current_user['username']
    }), 200


# ============================================================================
# ROUTES: PUBLIC & INFO
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/auth/info', methods=['GET'])
@require_auth
def get_token_info():
    return jsonify({
        'token_info': request.current_user,
        'token_expires_at': datetime.utcfromtimestamp(
            request.current_user['exp']
        ).isoformat()
    }), 200


# ============================================================================
# ERROR HANDLERS & SECURITY
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.before_request
def security_headers():
    pass  # Will be applied in after_request


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if REQUIRE_HTTPS:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


if __name__ == '__main__':
    """
    Run demo to show JWT authentication + OAuth 2.0 authorization server.
    
    Demo users:
    - alice:alice123 (admin, all scopes)
    - bob:bob456 (user, read-only scopes)
    - charlie:charlie789 (moderator, read scopes)
    
    Demo OAuth 2.0 Clients:
    - web-app-client / web-app-secret-12345
    - mobile-app-client / mobile-app-secret-67890
    - backend-service / backend-service-secret-99999
    """
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  JWT Authentication + OAuth 2.0 Authorization Server Demo     ║
    ║                                                                ║
    ║  Week 6: Authentication & Authorization                       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    
    # ══════════════════════════════════════════════════════════════
    # PART 1: TRADITIONAL JWT AUTHENTICATION
    # ══════════════════════════════════════════════════════════════
    
    📌 LOGIN (Get JWT Tokens)
    ──────────────────────────────────────────
    POST /auth/login
    {
        "username": "alice",
        "password": "alice123"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAi...",
        "refresh_token": "eyJ0eXAi...",
        "token_type": "Bearer",
        "expires_in": 900
    }
    
    
    # ══════════════════════════════════════════════════════════════
    # PART 2: OAUTH 2.0 AUTHORIZATION CODE FLOW
    # ══════════════════════════════════════════════════════════════
    
    🔄 STEP 1: Authorization Endpoint (User Login & Consent)
    ──────────────────────────────────────────
    Redirect user to:
    /oauth/authorize?
      response_type=code
      &client_id=web-app-client
      &redirect_uri=http://localhost:3000/oauth/callback
      &scope=read:products%20write:products
      &state=random-state-123
    
    User logs in:
    POST /oauth/login
    {
        "username": "alice",
        "password": "alice123"
    }
    
    Server redirects back:
    http://localhost:3000/oauth/callback?
      code=<authorization_code>
      &state=random-state-123
    
    
    🔄 STEP 2: Token Endpoint (Exchange Code for Token)
    ──────────────────────────────────────────
    POST /oauth/token
    {
        "grant_type": "authorization_code",
        "code": "<authorization_code>",
        "client_id": "web-app-client",
        "client_secret": "web-app-secret-12345",
        "redirect_uri": "http://localhost:3000/oauth/callback"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAi...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read:products write:products",
        "user": {
            "id": 1,
            "username": "alice"
        }
    }
    
    
    # ══════════════════════════════════════════════════════════════
    # PART 3: OAUTH 2.0 CLIENT CREDENTIALS FLOW  
    # (Server-to-Server Authentication)
    # ══════════════════════════════════════════════════════════════
    
    🔐 Get Token (No User Interaction)
    ──────────────────────────────────────────
    POST /oauth/token
    {
        "grant_type": "client_credentials",
        "client_id": "backend-service",
        "client_secret": "backend-service-secret-99999",
        "scope": "read:products write:products"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAi...",
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read:products write:products"
    }
    
    Then use token for API requests:
    GET /products
    Authorization: Bearer <access_token>
    
    
    # ══════════════════════════════════════════════════════════════
    # PART 4: TOKEN MANAGEMENT ENDPOINTS
    # ══════════════════════════════════════════════════════════════
    
    📋 Token Introspection (Check if token valid)
    ──────────────────────────────────────────
    POST /oauth/introspect
    {
        "token": "<access_token>",
        "client_id": "web-app-client",
        "client_secret": "web-app-secret-12345"
    }
    
    Response:
    {
        "active": true,
        "user_id": 1,
        "username": "alice",
        "client_id": "web-app-client",
        "scope": "read:products write:products",
        "exp": 1672567890
    }
    
    
    🔄 Token Refresh
    ──────────────────────────────────────────
    POST /oauth/token
    {
        "grant_type": "refresh_token",
        "refresh_token": "<refresh_token>",
        "client_id": "web-app-client",
        "client_secret": "web-app-secret-12345"
    }
    
    
    🔴 Token Revocation
    ──────────────────────────────────────────
    POST /oauth/revoke
    {
        "token": "<access_token>",
        "client_id": "web-app-client", 
        "client_secret": "web-app-secret-12345"
    }
    
    
    # ══════════════════════════════════════════════════════════════
    # REGISTERED OAUTH 2.0 CLIENTS
    # ══════════════════════════════════════════════════════════════
    
    1️⃣  Web Application
        Client ID: web-app-client
        Client Secret: web-app-secret-12345
        Redirect URIs: http://localhost:3000/oauth/callback
        Grant Types: authorization_code, refresh_token
        Allowed Scopes: read:products, write:products, read:orders, write:orders
    
    2️⃣  Mobile Application
        Client ID: mobile-app-client
        Client Secret: mobile-app-secret-67890
        Redirect URIs: myapp://oauth/callback
        Grant Types: authorization_code, refresh_token
        Allowed Scopes: read:products, read:orders
    
    3️⃣  Backend Service (Microservice)
        Client ID: backend-service
        Client Secret: backend-service-secret-99999
        Redirect URIs: (none - uses client credentials flow)
        Grant Types: client_credentials
        Allowed Scopes: read:products, write:products, read:orders, write:orders
    
    
    # ══════════════════════════════════════════════════════════════
    # TESTING OAUTH 2.0 FLOWS
    # ══════════════════════════════════════════════════════════════
    
    Postman Collection:
    1. Set client_id = "web-app-client" in your requests
    2. Set client_secret = "web-app-secret-12345"
    3. Use authorization_code flow for user-facing apps
    4. Use client_credentials for backend services
    
    
    # ══════════════════════════════════════════════════════════════
    # OAUTH 2.0 vs JWT COMPARISON
    # ══════════════════════════════════════════════════════════════
    
    JWT:
      ✓ Simple, stateless
      ✓ Good for APIs
      ✓ Self-contained (all claims in token)
      ✗ No built-in revocation
      ✗ No client management
    
    OAuth 2.0:
      ✓ Authorization framework
      ✓ Multiple grant types for different scenarios
      ✓ Built-in refresh token flow
      ✓ Client management and registration
      ✓ Token introspection and revocation
      ✗ More complex to implement
      ✗ Stateful (token store needed)
    
    This demo combines both:
      → Use OAuth 2.0 for access control and client management
      → Use JWT for token format and claims
    
    """)
    
    print("\n🚀 Starting Flask server on http://localhost:5000\n")
    app.run(debug=True, host='localhost', port=5000)


"""
╔════════════════════════════════════════════════════════════════════════════╗
║                    OAUTH 2.0 IMPLEMENTATION NOTES                         ║
╚════════════════════════════════════════════════════════════════════════════╝

OAUTH 2.0 GRANT TYPES IMPLEMENTED:

1. Authorization Code Flow (User-Facing Apps)
   ├─ User clicks "Login with MyApp"
   ├─ Redirected to /oauth/authorize to grant permission
   ├─ Server redirects back with authorization code
   ├─ App exchanges code for access token at /oauth/token
   └─ Use Case: Web apps, mobile apps with browser login

2. Client Credentials Flow (Server-to-Server)
   ├─ Service sends client_id + client_secret
   ├─ Receives access token without user interaction
   ├─ Use Case: Microservices, backend jobs, batch processing
   └─ No refresh token (short-lived token fine for services)

3. Refresh Token Flow (Token Rotation)
   ├─ Get new access token using refresh_token
   ├─ Extends user session without re-login
   └─ Use Case: Mobile apps, long-lived sessions

TOKEN ENDPOINTS:

/oauth/authorize
  • Initiates OAuth flow
  • User logs in and grants scopes
  • Returns authorization code

/oauth/token
  • Exchanges authorization code for access token
  • Supports: authorization_code, client_credentials, refresh_token
  • Returns: access_token, token_type, expires_in, scope

/oauth/introspect
  • Check if token is valid
  • Returns token claims and expiration
  • RFC 7662

/oauth/revoke
  • Revoke/blacklist a token
  • Prevents token reuse
  • RFC 7009

/oauth/clients
  • List registered OAuth clients

SECURITY BEST PRACTICES:

✓ Use HTTPS in production (not just HTTP)
✓ Store secrets securely (environment variables)
✓ Validate redirect_uri exactly
✓ Use short-lived access tokens (1 hour)
✓ Use long-lived refresh tokens (7 days)
✓ Implement token rotation (revoke old, issue new)
✓ Detect code reuse (authorization_code_already_used_error)
✓ Use state parameter to prevent CSRF
✓ Validate client credentials on token endpoint
✓ Rate limit /auth/login to prevent brute force
✓ Log all OAuth events for auditing

COMPARING WITH STANDARD IMPLEMENTATIONS:

Our Implementation:
  → In-memory storage (demo/testing only)
  → Works with custom JWT format
  → Simple OAuth server features

Production-Grade:
  → Use database or Redis for token storage
  → More OAuth 2.0 extensions (PKCE, implicit flow)
  → OpenID Connect for user info
  → Third-party IdP integration (Google, GitHub)
  → Rate limiting and throttling
  → Audit logging and monitoring

"""
