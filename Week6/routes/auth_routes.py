from flask import Blueprint, request, jsonify
import bcrypt
from models import TokenManager
from decorators import require_auth
from config import USERS_DB, TOKEN_BLACKLIST, ACCESS_TOKEN_EXPIRATION

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['POST'])
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


@auth_bp.route('/refresh', methods=['POST'])
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


@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    token = request.token
    TOKEN_BLACKLIST.add(token)
    
    return jsonify({'message': 'Logged out successfully'}), 200
