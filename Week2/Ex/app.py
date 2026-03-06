from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS
from functools import wraps
from datetime import datetime

app = Flask(__name__, static_folder='.')
CORS(app)

# Dữ liệu mẫu
users = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com"},
    {"id": 2, "name": "Tran Thi B", "email": "b@example.com"}
]

# STATELESS: Lưu token giả (trong thực tế dùng JWT)
valid_tokens = {}

# Web page - CLIENT-SERVER
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ========== STATELESS - Authentication ==========

# STATELESS: Login để lấy token
@app.route('/api/login', methods=['POST'])
def login():
    # Server không lưu session, chỉ cấp token
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # Kiểm tra thông tin đơn giản
    if username and password:
        # Tạo token đơn giản (thực tế dùng JWT)
        token = f"token_{username}_{len(valid_tokens) + 1}"
        valid_tokens[token] = username
        
        return jsonify({"token": token, "message": "Login successful"}), 200
    
    return jsonify({"error": "Invalid credentials"}), 401

# STATELESS: Decorator kiểm tra token
def require_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Lấy token từ header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid token"}), 401
        
        token = auth_header.replace('Bearer ', '')
        
        # Kiểm tra token có hợp lệ không
        if token not in valid_tokens:
            return jsonify({"error": "Invalid token"}), 401
        
        # Token hợp lệ, tiếp tục xử lý request
        return f(*args, **kwargs)
    
    return decorated

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
@require_token
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
@require_token
@set_cache_control(duration=300)
def get_users():
    return jsonify(users), 200

# R - READ: Lấy 1 user theo ID (GET) - Cache 5 phút
@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_token
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
