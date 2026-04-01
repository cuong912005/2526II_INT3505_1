import jwt
import secrets
from datetime import datetime
from typing import Dict
from config import (
    ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET, ACCESS_TOKEN_EXPIRATION,
    REFRESH_TOKEN_EXPIRATION, OAUTH_AUTH_CODE_EXPIRATION, OAUTH_ACCESS_TOKEN_EXPIRATION,
    OAUTH_CLIENTS, OAUTH_AUTH_CODES, OAUTH_TOKENS, TOKEN_BLACKLIST
)


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


class OAuth2Manager:
    @staticmethod
    def validate_client(client_id: str, client_secret: str = None) -> Dict:
        client = OAUTH_CLIENTS.get(client_id)
        
        if not client:
            raise Exception('Invalid client_id')
        
        if client_secret and client.get('client_secret') != client_secret:
            raise Exception('Invalid client_secret')
        
        return client

    @staticmethod
    def validate_redirect_uri(client_id: str, redirect_uri: str) -> bool:
        client = OAUTH_CLIENTS.get(client_id)
        
        if not client:
            return False
        
        return redirect_uri in client.get('redirect_uris', [])

    @staticmethod
    def generate_authorization_code(client_id: str, user_id: int, 
                                    username: str, scopes: list) -> str:
        code = secrets.token_urlsafe(32)
        
        OAUTH_AUTH_CODES[code] = {
            'client_id': client_id,
            'user_id': user_id,
            'username': username,
            'scopes': scopes,
            'expires_at': datetime.utcnow() + OAUTH_AUTH_CODE_EXPIRATION,
            'used': False
        }
        
        return code

    @staticmethod
    def redeem_authorization_code(code: str, client_id: str) -> Dict:
        auth_code_data = OAUTH_AUTH_CODES.get(code)
        
        if not auth_code_data:
            raise Exception('Invalid authorization code')
        
        if auth_code_data['used']:
            OAUTH_AUTH_CODES.pop(code, None)
            raise Exception('Authorization code already used - possible attack')
        
        if auth_code_data['expires_at'] < datetime.utcnow():
            raise Exception('Authorization code expired')
        
        if auth_code_data['client_id'] != client_id:
            raise Exception('Client ID mismatch')
        
        auth_code_data['used'] = True
        
        return auth_code_data

    @staticmethod
    def generate_oauth_access_token(user_id: int, username: str, 
                                   scopes: list, client_id: str) -> str:
        payload = {
            'user_id': user_id,
            'username': username,
            'scopes': scopes,
            'client_id': client_id,
            'exp': datetime.utcnow() + OAUTH_ACCESS_TOKEN_EXPIRATION,
            'iat': datetime.utcnow(),
            'type': 'oauth_access'
        }
        
        token = jwt.encode(payload, ACCESS_TOKEN_SECRET, algorithm='HS256')
        
        OAUTH_TOKENS[token] = {
            'client_id': client_id,
            'user_id': user_id,
            'scopes': scopes,
            'expires_at': payload['exp']
        }
        
        return token

    @staticmethod
    def verify_oauth_token(token: str) -> Dict:
        try:
            payload = jwt.decode(token, ACCESS_TOKEN_SECRET, algorithms=['HS256'])
            
            if payload.get('type') != 'oauth_access':
                raise jwt.InvalidTokenError('Invalid token type')
            
            if token not in OAUTH_TOKENS:
                raise jwt.InvalidTokenError('Token not found in store')
            
            return payload
        except jwt.ExpiredSignatureError:
            raise Exception('OAuth token has expired')
        except jwt.InvalidTokenError as e:
            raise Exception(f'Invalid OAuth token: {str(e)}')

    @staticmethod
    def validate_scopes(requested_scopes: list, allowed_scopes: list) -> list:
        if not requested_scopes:
            return allowed_scopes
        
        validated = [s for s in requested_scopes if s in allowed_scopes]
        
        if not validated:
            raise Exception('No valid scopes requested')
        
        return validated
