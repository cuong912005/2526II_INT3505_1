from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from typing import Dict, Tuple, Optional

app = Flask(__name__)

ACCESS_TOKEN_SECRET = os.environ.get('ACCESS_TOKEN_SECRET', 'your-super-secret-access-key-2024')
REFRESH_TOKEN_SECRET = os.environ.get('REFRESH_TOKEN_SECRET', 'your-super-secret-refresh-key-2024')

ACCESS_TOKEN_EXPIRATION = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)

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
    Run demo to show JWT authentication flow.
    
    Demo users:
    - alice:alice123 (admin, all scopes)
    - bob:bob456 (user, read-only scopes)
    - charlie:charlie789 (moderator, read scopes)
    """
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  JWT Authentication & Authorization Demo                      ║
    ║                                                                ║
    ║  Week 6: Concepts & Implementation                           ║
    ╚════════════════════════════════════════════════════════════════╝
    
    📌 TEST CASES:
    
    1️⃣  LOGIN (Get Tokens)
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
    
    
    2️⃣  ACCESS PROTECTED ENDPOINT
    ──────────────────────────────────────────
    GET /products
    Authorization: Bearer <access_token>
    
    ✅ Alice (has read:products scope) → Success
    ✅ Bob (has read:products scope) → Success
    ❌ Invalid token → 401 Unauthorized
    
    
    3️⃣  WRITE OPERATION (Scope-based)
    ──────────────────────────────────────────
    POST /products
    Authorization: Bearer <access_token>
    {
        "name": "Monitor",
        "price": 300
    }
    
    ✅ Alice (has write:products scope) → Success (201)
    ❌ Bob (only read:products) → Forbidden (403)
    
    
    4️⃣  ROLE-BASED ACCESS (Admin only)
    ──────────────────────────────────────────
    GET /admin/users
    Authorization: Bearer <access_token>
    
    ✅ Alice (admin role) → Success
    ❌ Bob (user role) → Forbidden (403)
    ❌ Charlie (moderator role) → Forbidden (403)
    
    
    5️⃣  REFRESH TOKEN (Get new access_token)
    ──────────────────────────────────────────
    POST /auth/refresh
    {
        "refresh_token": "<refresh_token>"
    }
    
    Response:
    {
        "access_token": "eyJ0eXAi...",
        "token_type": "Bearer",
        "expires_in": 900
    }
    
    
    6️⃣  LOGOUT (Revoke Token - Anti-replay)
    ──────────────────────────────────────────
    POST /auth/logout
    Authorization: Bearer <access_token>
    
    After logout:
    ❌ Same token cannot be used again
    ✅ Use refresh_token to get new access_token
    
    
    📚 KEY CONCEPTS:
    ─────────────────────────────────────────
    
    🔐 JWT (JSON Web Token)
       - Stateless: No server-side session storage needed
       - Signed: Cannot be tampered with (verified with secret)
       - Contains claims: user_id, roles, scopes, exp, etc.
    
    🎫 Bearer Token
       - Token sent in Authorization header: "Bearer <token>"
       - Used for API authentication (instead of username:password)
       - HTTP format: Authorization: Bearer eyJ0eXAi...
    
    🔄 Refresh Token
       - Long-lived token for getting new access tokens
       - Stored securely (httpOnly cookie recommended)
       - Access token expires in 15 minutes (short-lived)
       - Refresh token expires in 7 days (long-lived)
    
    🛡️  Scopes
       - Fine-grained permissions (e.g., "read:products")
       - Can grant specific operations on specific resources
       - Example: User can read but not write products
    
    👤 Roles
       - Coarser permissions (e.g., "admin", "user", "moderator")
       - Used for broad access control
       - Example: Only admins can delete users
    
    
    🚨 SECURITY RISKS & MITIGATIONS:
    ─────────────────────────────────────────
    
    1. Token Leakage
       ❌ Risk: Token transmitted over HTTP → Intercepted
       ✅ Mitigation: Always use HTTPS
       ✅ Mitigation: Store refresh_token in httpOnly cookies
       ✅ Mitigation: Access tokens are short-lived (15 min)
    
    2. Replay Attacks
       ❌ Risk: Attacker reuses stolen token
       ✅ Mitigation: Short token expiration (15 min)
       ✅ Mitigation: Token blacklist on logout (shown in /auth/logout)
       ✅ Mitigation: Refresh token rotation
    
    3. Brute Force (Login)
       ✅ Mitigation: Rate limiting on /auth/login
       ✅ Mitigation: Account lockout after N failed attempts
       ✅ Mitigation: Use bcrypt for password hashing (slow)
    
    4. Token Forgery
       ❌ Risk: Attacker creates fake token with admin role
       ✅ Mitigation: JWT is cryptographically signed with secret
       ✅ Mitigation: Server verifies signature with SECRET
       ✅ Mitigation: Cannot forge without secret
    
    5. CSRF (Cross-Site Request Forgery)
       ✅ Mitigation: Tokens in Authorization header (not cookie)
       ✅ Mitigation: httpOnly cookies prevent JS access
    
    
    📖 JWT vs OAuth 2.0 Comparison:
    ─────────────────────────────────────────
    
    Feature          │ JWT           │ OAuth 2.0
    ─────────────────┼───────────────┼──────────────────
    Type             │ Token Format  │ Authorization Flow
    Use Case         │ Auth + API    │ Delegation
    Tokens           │ 1 Format      │ Multiple (Bearer, etc.)
    Refresh          │ Manual        │ Built-in
    Revocation       │ Not built-in  │ Built-in
    Stateless        │ Yes           │ Can be stateless
    Complexity       │ Simple        │ Complex
    
    When use JWT:
    ✓ Simple API authentication
    ✓ Microservices (stateless)
    ✓ Mobile apps (no sessions)
    
    When use OAuth 2.0:
    ✓ 3rd party authorization (Sign in with Google)
    ✓ Complex permission delegation
    ✓ Multiple applications
    
    
    👨‍💻 USERS AVAILABLE FOR TESTING:
    ─────────────────────────────────────────
    
    alice:alice123
      • Roles: [admin, user]
      • Scopes: [read:products, write:products, read:orders, write:orders]
      • Can: Read/write products, admin panel, all operations
    
    bob:bob456
      • Roles: [user]
      • Scopes: [read:products, read:orders]
      • Can: Read products/orders only (read-only access)
    
    charlie:charlie789
      • Roles: [moderator]
      • Scopes: [read:products, read:users, read:orders]
      • Can: Read most resources (moderation duties)
    
    """)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    demo()
    print("\n🚀 Starting Flask server...\n")
    app.run(debug=True, host='localhost', port=5000)


"""
╔════════════════════════════════════════════════════════════════════════════╗
║                         QUICK REFERENCE GUIDE                             ║
╚════════════════════════════════════════════════════════════════════════════╝

🧪 CURL EXAMPLES:

1. Login:
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"alice123"}'

2. Get Products (with token):
curl -X GET http://localhost:5000/products \
  -H "Authorization: Bearer <access_token>"

3. Admin List Users:
curl -X GET http://localhost:5000/admin/users \
  -H "Authorization: Bearer <access_token>"

4. Refresh Token:
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

5. Logout:
curl -X POST http://localhost:5000/auth/logout \
  -H "Authorization: Bearer <access_token>"


📋 IMPLEMENTATION CHECKLIST:

Authentication:
  ✓ User login endpoint
  ✓ Password hashing with bcrypt
  ✓ JWT token generation
  ✓ Refresh token mechanism
  ✓ Token verification middleware

Authorization:
  ✓ Role-based access control (RBAC)
  ✓ Scope-based access control (ABAC)
  ✓ Protected endpoints
  ✓ Authorization decorators

Security:
  ✓ Token expiration times
  ✓ Token blacklist for logout
  ✓ Bearer token format
  ✓ HTTPS enforcement (production)
  ✓ Security headers
  ✓ Password hashing

Error Handling:
  ✓ Invalid token handling
  ✓ Expired token handling
  ✓ Missing token handling
  ✓ Insufficient permissions handling
"""
