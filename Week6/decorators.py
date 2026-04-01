from flask import request, jsonify
from functools import wraps
from models import TokenManager, OAuth2Manager


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
