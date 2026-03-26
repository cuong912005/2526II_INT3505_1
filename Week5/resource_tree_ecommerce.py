from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# Simulated databases
users_db = {1: {'id': 1, 'name': 'Alice', 'email': 'alice@email.com'}, 2: {'id': 2, 'name': 'Bob', 'email': 'bob@email.com'}}
products_db = {i: {'id': i, 'name': f'Product{i}', 'price': 10+i*5, 'stock': 100-i*3} for i in range(1, 21)}
orders_db = {i: {'id': i, 'user_id': (i%2)+1, 'total': 50+i*20, 'items': []} for i in range(1, 11)}

# Helper: Apply pagination
def apply_pagination(items, strategy='offset', offset=0, limit=10, page=1, page_size=10, cursor=None):
    if strategy == 'offset':
        start, end = offset, offset + limit
        paginated = items[start:end]
        return {'data': paginated, 'pagination': {'offset': offset, 'limit': limit, 'total': len(items), 'has_more': end < len(items)}}
    elif strategy == 'page':
        total_pages = (len(items) + page_size - 1) // page_size
        start = (page - 1) * page_size
        paginated = items[start:start + page_size]
        return {'data': paginated, 'pagination': {'page': page, 'page_size': page_size, 'total_pages': total_pages}}
    elif strategy == 'cursor':
        cursor_pos = 0 if not cursor else int(cursor.split('_')[1])
        paginated = items[cursor_pos:cursor_pos + limit]
        next_cursor = f"next_{cursor_pos + limit}" if cursor_pos + limit < len(items) else None
        return {'data': paginated, 'pagination': {'next_cursor': next_cursor, 'has_more': next_cursor is not None}}

# ========== RESOURCE TREE IMPLEMENTATION ==========

# Users Collection (offset/limit)
@app.route('/users', methods=['GET'])
def list_users():
    offset, limit = int(request.args.get('offset', 0)), int(request.args.get('limit', 10))
    users = list(users_db.values())
    result = apply_pagination(users, 'offset', offset, limit)
    return jsonify(result)

# User Detail
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = users_db.get(user_id)
    return jsonify(user) if user else jsonify({'error': 'Not Found'}), 404 if not user else 200

# User's Orders (nested resource, use offset/limit)
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def list_user_orders(user_id):
    if user_id not in users_db:
        return jsonify({'error': 'User not found'}), 404
    offset, limit = int(request.args.get('offset', 0)), int(request.args.get('limit', 10))
    orders = [o for o in orders_db.values() if o['user_id'] == user_id]
    result = apply_pagination(orders, 'offset', offset, limit)
    return jsonify(result)

# User's Specific Order
@app.route('/users/<int:user_id>/orders/<int:order_id>', methods=['GET'])
def get_user_order(user_id, order_id):
    order = orders_db.get(order_id)
    if not order or order['user_id'] != user_id:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify(order), 200

# Products Collection (page-based)
@app.route('/products', methods=['GET'])
def list_products():
    page, page_size = int(request.args.get('page', 1)), int(request.args.get('page_size', 10))
    products = list(products_db.values())
    result = apply_pagination(products, 'page', page=page, page_size=page_size)
    return jsonify(result)

# Product Detail
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = products_db.get(product_id)
    return jsonify(product) if product else jsonify({'error': 'Not Found'}), 404 if not product else 200

# Orders Collection (cursor-based)
@app.route('/orders', methods=['GET'])
def list_orders():
    limit = int(request.args.get('limit', 10))
    cursor = request.args.get('cursor', None)
    orders = list(orders_db.values())
    result = apply_pagination(orders, 'cursor', limit=limit, cursor=cursor)
    return jsonify(result)

# Order Detail
@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = orders_db.get(order_id)
    return jsonify(order) if order else jsonify({'error': 'Not Found'}), 404 if not order else 200

# ========== RESOURCE TREE STRUCTURE REFERENCE ==========
# /users                                  GET   List users (offset/limit)
# /users                                  POST  Create user
# /users/{id}                             GET   Get user
# /users/{id}                             PUT   Update user
# /users/{id}                             DELETE Delete user
# /users/{id}/orders                      GET   List user's orders (offset/limit)
# /users/{id}/orders                      POST  Create order for user
# /users/{id}/orders/{order_id}           GET   Get user's order
# /users/{id}/orders/{order_id}           PUT   Update order
# /users/{id}/orders/{order_id}           DELETE Cancel order
#
# /products                               GET   List products (page-based)
# /products                               POST  Create product (admin)
# /products/{id}                          GET   Get product
# /products/{id}                          PUT   Update product
# /products/{id}                          DELETE Delete product
#
# /orders                                 GET   List all orders (cursor-based)
# /orders                                 POST  Create order
# /orders/{id}                            GET   Get order
# /orders/{id}                            PUT   Update order
# /orders/{id}                            DELETE Delete order

if __name__ == '__main__':
    print("Resource Tree API running on http://localhost:5000")
    print("\nQUICK TEST URLS:")
    print("  GET http://localhost:5000/users?offset=0&limit=5")
    print("  GET http://localhost:5000/products?page=1&page_size=5")
    print("  GET http://localhost:5000/orders?limit=5")
    print("  GET http://localhost:5000/users/1")
    print("  GET http://localhost:5000/users/1/orders?offset=0&limit=10")
    app.run(debug=True, port=5000)
