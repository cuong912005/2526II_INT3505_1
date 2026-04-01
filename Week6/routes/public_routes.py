from flask import Blueprint, request, jsonify
from datetime import datetime
from decorators import require_auth
from config import REQUIRE_HTTPS

public_bp = Blueprint('public', __name__)


@public_bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}), 200


@public_bp.route('/auth/info', methods=['GET'])
@require_auth
def get_token_info():
    return jsonify({
        'token_info': request.current_user,
        'token_expires_at': datetime.utcfromtimestamp(
            request.current_user['exp']
        ).isoformat()
    }), 200


@public_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404


@public_bp.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500
