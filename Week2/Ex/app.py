from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from functools import wraps
from datetime import datetime, timedelta
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

app = Flask(__name__, static_folder='.')
CORS(app)

# Dữ liệu mẫu
users = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com"},
    {"id": 2, "name": "Tran Thi B", "email": "b@example.com"}
]

# JWT demo configuration (hard-coded secret for demo)
JWT_SECRET = 'dev-secret-for-demo'
# In-memory store to track issued refresh tokens (simple demo)
valid_refresh_tokens = set()

# Web page - CLIENT-SERVER
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ========== STATELESS - Authentication ==========



# STATELESS: Login để lấy token
@app.route('/api/login', methods=['POST'])
def login():
    # Server cấp access + refresh token (demo)
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username and password:
        access_payload = {
            'sub': username,
            'type': 'access',
            'exp': datetime.utcnow() + timedelta(minutes=15)
        }
        refresh_payload = {
            'sub': username,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=7)
        }

        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm='HS256')

        # normalize bytes -> str for PyJWT compatibility
        if isinstance(access_token, bytes):
            access_token = access_token.decode('utf-8')
        if isinstance(refresh_token, bytes):
            refresh_token = refresh_token.decode('utf-8')

        # store refresh token (simple revocation support)
        valid_refresh_tokens.add(refresh_token)

        return jsonify({"access_token": access_token, "refresh_token": refresh_token, "message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

# REFRESH: Tạo access token mới từ refresh token
@app.route('/api/refresh', methods=['POST'])
def refresh():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Missing or invalid token"}), 401

    refresh_token = auth_header.replace('Bearer ', '')

    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=['HS256'])
    except ExpiredSignatureError:
        return jsonify({"error": "Refresh token expired"}), 401
    except InvalidTokenError:
        return jsonify({"error": "Invalid refresh token"}), 401

    if payload.get('type') != 'refresh':
        return jsonify({"error": "Invalid token type"}), 401

    # check stored refresh tokens
    if refresh_token not in valid_refresh_tokens:
        return jsonify({"error": "Refresh token revoked or unknown"}), 401

    username = payload.get('sub')
    new_access_payload = {
        'sub': username,
        'type': 'access',
        'exp': datetime.utcnow() + timedelta(minutes=15)
    }

    new_access = jwt.encode(new_access_payload, JWT_SECRET, algorithm='HS256')
    if isinstance(new_access, bytes):
        new_access = new_access.decode('utf-8')

    return jsonify({"access_token": new_access}), 200

# ========== CACHEABLE - HTTP Caching Headers ==========

def set_cache_control(duration=300):
    """Decorator để thêm Cache-Control header"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            response = make_response(f(*args, **kwargs))
            
            # Nếu response là tuple (data, status_code)
            if isinstance(response, tuple):
                data, status_code = response
                response = make_response(jsonify(data if isinstance(data, dict) else data), status_code)
            
            # Thêm Cache-Control header
            response.headers['Cache-Control'] = f'public, max-age={duration}'
            response.headers['Last-Modified'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            
            return response
        
        return decorated
    return decorator

# ========== UNIFORM INTERFACE - CRUD Operations ==========

# C - CREATE: Tạo user mới (POST) - Không cache
@app.route('/api/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.get_json()
    
    # Kiểm tra dữ liệu bắt buộc
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Missing name or email"}), 400
    
    # Tạo user mới với ID tự tăng
    new_user = {
        "id": max([u["id"] for u in users]) + 1 if users else 1,
        "name": data["name"],
        "email": data["email"]
    }
    users.append(new_user)
    
    response = make_response(jsonify(new_user), 201)
    # POST không cache (dữ liệu mới tạo)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# R - READ: Lấy tất cả users (GET) - Cache 5 phút
@app.route('/api/users', methods=['GET'])
@jwt_required()
@set_cache_control(duration=300)
def get_users():
    return jsonify(users), 200

# R - READ: Lấy 1 user theo ID (GET) - Cache 5 phút
@app.route('/api/users/<int:user_id>', methods=['GET'])
@jwt_required()
@set_cache_control(duration=300)
def get_user(user_id):
    # Tìm user theo ID
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user), 200

# U - UPDATE: Cập nhật user (PUT) - Không cache
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@require_token
def update_user(user_id):
    # Tìm user theo ID
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Cập nhật các trường nếu có trong request
    if "name" in data:
        user["name"] = data["name"]
    if "email" in data:
        user["email"] = data["email"]
    
    response = make_response(jsonify(user), 200)
    # PUT không cache (dữ liệu vừa cập nhật)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# D - DELETE: Xóa user (DELETE) - Không cache
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_token
def delete_user(user_id):
    global users
    
    # Tìm user theo ID
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Xóa user khỏi danh sách
    users = [u for u in users if u["id"] != user_id]
    
    response = make_response(jsonify({"message": "User deleted successfully"}), 200)
    # DELETE không cache (dữ liệu vừa xóa)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

if __name__ == '__main__':
    app.run(debug=True, port=3000)
