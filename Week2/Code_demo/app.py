from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

users = [
    {"id": 1, "name": "Nguyen Thac Cuong", "email": "cuong@gmail.com"},
    {"id": 2, "name": "Nguyen Ngọc Dinh", "email": "dinh@gmail.com"},
    {"id": 3, "name": "Nguyen Phi Anh ", "email": "anh@gmail.com"},
    {"id": 4, "name": "Hoang Quoc Bao", "email": "bao@gmail.com"},
    {"id": 5, "name": "Mai Kha Anh", "email": "anh@gmail.com"}
]

request_count = {}

@app.route('/users', methods=['GET'])
def get_users():
    return jsonify(users), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    if "email" in data:
        user["email"] = data["email"]
    if "name" in data:
        user["name"] = data["name"]
    
    return jsonify(user), 200

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if not data or "name" not in data or "email" not in data:
        return jsonify({"error": "Missing required fields"}), 400
    
    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "email": data["email"]
    }
    users.append(new_user)
    return jsonify(new_user), 201

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    global users
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    users = [u for u in users if u["id"] != user_id]
    return jsonify({"message": "User deleted"}), 200

@app.route('/rate-limit', methods=['GET'])
def rate_limit():
    ip = request.remote_addr
    request_count[ip] = request_count.get(ip, 0) + 1
    
    if request_count[ip] > 5:
        return jsonify({"error": "Too many requests"}), 429
    
    return jsonify({"message": "OK", "count": request_count[ip]}), 200

@app.route('/error', methods=['GET'])
def trigger_error():
    result = 1 / 0
    return jsonify({"result": result}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(429)
def too_many_requests(error):
    return jsonify({"error": "Rate limit exceeded"}), 429

if __name__ == '__main__':
    app.run(debug=True, port=5000)
