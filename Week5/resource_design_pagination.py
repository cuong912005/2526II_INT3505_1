from flask import Flask, request, jsonify
from datetime import datetime
from enum import Enum

app = Flask(__name__)

# Data Models
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Order:
    def __init__(self, id, user_id, total, created_at):
        self.id = id
        self.user_id = user_id
        self.total = total
        self.created_at = created_at

class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

# Sample Data
users_db = [User(i, f"User{i}", f"user{i}@email.com") for i in range(1, 21)]
orders_db = [Order(i, (i % 5) + 1, 100 + i * 10, datetime(2025, 1, i % 28 + 1)) for i in range(1, 51)]
products_db = [Product(i, f"Product{i}", 10 * i, 100 - i * 5) for i in range(1, 31)]

# ========== RESOURCE TREE DESIGN ==========
# GET    /users                          - List all users
# GET    /users/{id}                     - Get user detail
# POST   /users                          - Create user
# GET    /users/{id}/orders              - List user's orders
# POST   /users/{id}/orders              - Create order for user
# GET    /users/{id}/orders/{order_id}   - Get specific order
# GET    /products                       - List all products
# GET    /products/{id}                  - Get product detail
# GET    /orders                         - List all orders
# GET    /orders/{id}                    - Get order detail

# ========== PAGINATION STRATEGY 1: OFFSET/LIMIT ==========
@app.route('/users', methods=['GET'])
def get_users_offset_limit():
    # offset=10&limit=5 -> skip 10, take 5
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    
    total = len(users_db)
    paginated = users_db[offset:offset + limit]
    
    return jsonify({
        'data': [{'id': u.id, 'name': u.name, 'email': u.email} for u in paginated],
        'pagination': {'offset': offset, 'limit': limit, 'total': total, 'has_more': offset + limit < total}
    })

# ========== PAGINATION STRATEGY 2: PAGE-BASED ==========
@app.route('/products', methods=['GET'])
def get_products_page_based():
    # page=1&page_size=10 -> page 1 with 10 items per page
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 10))
    
    total = len(products_db)
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    paginated = products_db[offset:offset + page_size]
    
    return jsonify({
        'data': [{'id': p.id, 'name': p.name, 'price': p.price, 'stock': p.stock} for p in paginated],
        'pagination': {'page': page, 'page_size': page_size, 'total_pages': total_pages, 'total_items': total}
    })

# ========== PAGINATION STRATEGY 3: CURSOR-BASED ==========
@app.route('/orders', methods=['GET'])
def get_orders_cursor_based():
    # cursor=next_12&limit=10 -> get 10 items after cursor_id=12
    cursor = request.args.get('cursor', None)
    limit = int(request.args.get('limit', 10))
    
    if cursor:
        cursor_id = int(cursor.split('_')[1])
        start_index = next((i for i, o in enumerate(orders_db) if o.id > cursor_id), len(orders_db))
    else:
        start_index = 0
    
    paginated = orders_db[start_index:start_index + limit]
    next_cursor = f"next_{paginated[-1].id}" if len(paginated) == limit else None
    
    return jsonify({
        'data': [{'id': o.id, 'user_id': o.user_id, 'total': o.total, 'created_at': o.created_at.isoformat()} for o in paginated],
        'pagination': {'next_cursor': next_cursor, 'has_more': next_cursor is not None}
    })

# ========== NESTED RESOURCES ==========
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    # Get user's orders with offset/limit pagination
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    
    user_orders = [o for o in orders_db if o.user_id == user_id]
    total = len(user_orders)
    paginated = user_orders[offset:offset + limit]
    
    return jsonify({
        'user_id': user_id,
        'data': [{'id': o.id, 'total': o.total, 'created_at': o.created_at.isoformat()} for o in paginated],
        'pagination': {'offset': offset, 'limit': limit, 'total': total, 'has_more': offset + limit < total}
    })

@app.route('/users/<int:user_id>/orders/<int:order_id>', methods=['GET'])
def get_user_order(user_id, order_id):
    # Get specific order for user
    order = next((o for o in orders_db if o.id == order_id and o.user_id == user_id), None)
    if not order:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'id': order.id, 'user_id': order.user_id, 'total': order.total})

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    # Get user by ID
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email})

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # Get product detail
    product = next((p for p in products_db if p.id == product_id), None)
    if not product:
        return jsonify({'error': 'Not Found'}), 404
    return jsonify({'id': product.id, 'name': product.name, 'price': product.price, 'stock': product.stock})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
