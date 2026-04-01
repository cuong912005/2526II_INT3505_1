from flask import Blueprint

from .auth_routes import auth_bp
from .oauth_routes import oauth_bp
from .protected_routes import protected_bp
from .public_routes import public_bp

__all__ = ['auth_bp', 'oauth_bp', 'protected_bp', 'public_bp']
