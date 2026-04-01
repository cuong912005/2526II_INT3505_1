from flask import Blueprint, request, jsonify, redirect, url_for, session
from urllib.parse import urlencode
from datetime import datetime
import bcrypt
from models import TokenManager, OAuth2Manager
from config import (
    USERS_DB, OAUTH_CLIENTS, OAUTH_AUTH_CODES, OAUTH_TOKENS,
    OAUTH_ACCESS_TOKEN_EXPIRATION, TOKEN_BLACKLIST
)

oauth_bp = Blueprint('oauth', __name__, url_prefix='/oauth')


@oauth_bp.route('/authorize', methods=['GET'])
def oauth_authorize():
    response_type = request.args.get('response_type')
    client_id = request.args.get('client_id')
    redirect_uri = request.args.get('redirect_uri')
    scope = request.args.get('scope', '').split()
    state = request.args.get('state', '')
    
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
    
    if 'user_id' not in session:
        login_url = url_for('oauth.login_page', next=request.url, _external=True)
        return redirect(login_url)
    
    try:
        validated_scopes = OAuth2Manager.validate_scopes(scope, client.get('allowed_scopes', []))
        
        auth_code = OAuth2Manager.generate_authorization_code(
            client_id=client_id,
            user_id=session['user_id'],
            username=session['username'],
            scopes=validated_scopes
        )
        
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


@oauth_bp.route('/token', methods=['POST'])
def oauth_token():
    data = request.get_json() or {}
    grant_type = data.get('grant_type')
    
    if grant_type == 'authorization_code':
        code = data.get('code')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        redirect_uri = data.get('redirect_uri')
        
        try:
            client = OAuth2Manager.validate_client(client_id, client_secret)
            
            if 'authorization_code' not in client.get('grant_types', []):
                return jsonify({
                    'error': 'unauthorized_client',
                    'error_description': 'Client not allowed to use authorization_code grant'
                }), 400
            
            code_data = OAuth2Manager.redeem_authorization_code(code, client_id)
            
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
    
    elif grant_type == 'client_credentials':
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        scope = data.get('scope', '').split()
        
        try:
            client = OAuth2Manager.validate_client(client_id, client_secret)
            
            if 'client_credentials' not in client.get('grant_types', []):
                return jsonify({
                    'error': 'unauthorized_client',
                    'error_description': 'Client not allowed to use client_credentials grant'
                }), 400
            
            validated_scopes = OAuth2Manager.validate_scopes(scope, client.get('allowed_scopes', []))
            
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
    
    elif grant_type == 'refresh_token':
        refresh_token = data.get('refresh_token')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        
        try:
            client = OAuth2Manager.validate_client(client_id, client_secret)
            payload = TokenManager.verify_refresh_token(refresh_token)
            
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


@oauth_bp.route('/clients', methods=['GET'])
def oauth_list_clients():
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


@oauth_bp.route('/login', methods=['POST'])
def oauth_login():
    data = request.get_json()
    username = data.get('username', '').lower()
    password = data.get('password')
    
    user = USERS_DB.get(username)
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
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


@oauth_bp.route('/introspect', methods=['POST'])
def oauth_introspect():
    data = request.get_json() or {}
    token = data.get('token')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not token:
        return jsonify({'error': 'invalid_request'}), 400
    
    try:
        client = OAuth2Manager.validate_client(client_id, client_secret)
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


@oauth_bp.route('/revoke', methods=['POST'])
def oauth_revoke():
    data = request.get_json() or {}
    token = data.get('token')
    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    
    if not token:
        return jsonify({'error': 'invalid_request'}), 400
    
    try:
        client = OAuth2Manager.validate_client(client_id, client_secret)
        
        OAUTH_TOKENS.pop(token, None)
        TOKEN_BLACKLIST.add(token)
        
        return jsonify({'message': 'Token revoked successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@oauth_bp.route('/login-page', methods=['GET'])
def login_page():
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
