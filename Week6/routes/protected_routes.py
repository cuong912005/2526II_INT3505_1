from flask import Blueprint, request, jsonify
from decorators import require_auth, require_scope, require_role
from config import USERS_DB

protected_bp = Blueprint('protected', __name__)


@protected_bp.route('/products', methods=['GET'])
@require_auth
@require_scope('read:products')
def get_products():
    products = [
        {'id': 1, 'name': 'Laptop', 'price': 1000},
        {'id': 2, 'name': 'Mouse', 'price': 50},
        {'id': 3, 'name': 'Keyboard', 'price': 80}
    ]
    
    return jsonify({
        'data': products,
        'current_user': request.current_user['username'],
        'roles': request.current_user['roles']
    }), 200


@protected_bp.route('/products', methods=['POST'])
@require_auth
@require_scope('write:products')
def create_product():
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('price'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    product = {
        'id': 4,
        'name': data['name'],
        'price': data['price'],
        'created_by': request.current_user['username']
    }
    
    return jsonify({
        'message': 'Product created successfully',
        'data': product
    }), 201


@protected_bp.route('/admin/users', methods=['GET'])
@require_auth
@require_role('admin')
def list_users():
    users = [
        {'id': u['id'], 'email': u['email'], 'roles': u['roles']} 
        for u in USERS_DB.values()
    ]
    
    return jsonify({
        'data': users,
        'accessed_by': request.current_user['username']
    }), 200


@protected_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_auth
@require_role('admin')
def delete_user(user_id):
    return jsonify({
        'message': f'User {user_id} deleted successfully',
        'deleted_by': request.current_user['username']
    }), 200


@protected_bp.route('/orders', methods=['GET'])
@require_auth
@require_role('user')
def get_orders():
    orders = [
        {'id': 1, 'user_id': request.current_user['user_id'], 'total': 150},
        {'id': 2, 'user_id': request.current_user['user_id'], 'total': 250}
    ]
    
    return jsonify({
        'data': orders,
        'user': request.current_user['username']
    }), 200
