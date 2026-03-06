from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='.')
CORS(app)

# Dữ liệu mẫu
users = [
    {"id": 1, "name": "Nguyen Van A", "email": "a@example.com"},
    {"id": 2, "name": "Tran Thi B", "email": "b@example.com"}
]

# Web page - CLIENT-SERVER
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ========== UNIFORM INTERFACE - CRUD Operations ==========

# C - CREATE: Tạo user mới (POST)
@app.route('/api/users', methods=['POST'])
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
    
    return jsonify(new_user), 201

# R - READ: Lấy tất cả users (GET)
@app.route('/api/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

# R - READ: Lấy 1 user theo ID (GET)
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Tìm user theo ID
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user), 200

# U - UPDATE: Cập nhật user (PUT)
@app.route('/api/users/<int:user_id>', methods=['PUT'])
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
    
    return jsonify(user), 200

# D - DELETE: Xóa user (DELETE)
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    
    # Tìm user theo ID
    user = next((u for u in users if u["id"] == user_id), None)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Xóa user khỏi danh sách
    users = [u for u in users if u["id"] != user_id]
    
    return jsonify({"message": "User deleted successfully"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=3000)
