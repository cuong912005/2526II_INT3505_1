from flask import Flask, request, jsonify
import time

app = Flask(__name__)

def logging_middleware(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] {request.method} {request.path}")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def auth_middleware(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "No token"}), 401
        print(f"[AUTH] Token verified: {token}")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def rate_limit_middleware(func):
    def wrapper(*args, **kwargs):
        time.sleep(0.1)
        print(f"[RATE-LIMIT] Request processed")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route('/api/public', methods=['GET'])
@logging_middleware
def public_endpoint():
    return jsonify({"message": "Public data"}), 200

@app.route('/api/protected', methods=['GET'])
@logging_middleware
@auth_middleware
@rate_limit_middleware
def protected_endpoint():
    return jsonify({"message": "Protected data", "secret": "xyz123"}), 200

@app.route('/api/admin', methods=['GET'])
@logging_middleware
@auth_middleware
def admin_endpoint():
    return jsonify({"message": "Admin only data"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5005)
