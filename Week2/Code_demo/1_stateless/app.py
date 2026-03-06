from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if username == 'admin' and password == '123':
        token = f"token_{username}_abc123"
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/profile', methods=['GET'])
def profile():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401
    
    token = auth_header.replace('Bearer ', '')
    
    if 'admin' in token:
        return jsonify({"username": "admin", "role": "administrator"}), 200
    
    return jsonify({"error": "Invalid token"}), 401

@app.route('/data', methods=['GET'])
def get_data():
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({"error": "Unauthorized"}), 401
    
    return jsonify({"data": [1, 2, 3, 4, 5]}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5001)
