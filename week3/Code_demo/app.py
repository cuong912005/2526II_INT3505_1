"""
REST API Best Practices Demo
Demonstrates all 8 key principles of API consistency and design
"""

from flask import Flask, request, jsonify
from datetime import datetime
from functools import wraps
import re

app = Flask(__name__)


products = [
    {"id": 1, "name": "Laptop Dell XPS 13", "price": 25000000, "category": "electronics", "stock": 15, "created_at": "2026-01-15T10:30:00Z"},
    {"id": 2, "name": "iPhone 15 Pro", "price": 30000000, "category": "electronics", "stock": 25, "created_at": "2026-02-10T14:20:00Z"},
    {"id": 3, "name": "Samsung Galaxy S24", "price": 22000000, "category": "electronics", "stock": 30, "created_at": "2026-02-15T09:15:00Z"},
]

users = [
    {"id": 1, "username": "john-doe", "email": "john@example.com", "role": "admin", "created_at": "2026-01-01T00:00:00Z"},
    {"id": 2, "username": "jane-smith", "email": "jane@example.com", "role": "user", "created_at": "2026-01-05T00:00:00Z"},
]

orders = [
    {"id": 1, "user_id": 1, "product_id": 1, "quantity": 2, "status": "completed", "created_at": "2026-03-01T10:00:00Z"},
    {"id": 2, "user_id": 2, "product_id": 2, "quantity": 1, "status": "pending", "created_at": "2026-03-05T15:30:00Z"},
]


# 2 & 5. RESPONSE & ERROR FORMAT - Chuẩn hóa định dạng phản hồi

def success_response(data, message="Success", status_code=200, meta=None):
    """Định dạng chuẩn cho response thành công"""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if meta:
        response["meta"] = meta
    return jsonify(response), status_code

def error_response(message, status_code=400, error_code=None, details=None):
    """Định dạng chuẩn cho response lỗi"""
    response = {
        "success": False,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    if error_code:
        response["error_code"] = error_code
    if details:
        response["details"] = details
    return jsonify(response), status_code


# VERSIONING 
def api_version(version):
    """Decorator để quản lý phiên bản API"""
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Có thể thêm logic xử lý version ở đây
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 3 & 4 & 7. URL STRUCTURE, HTTP METHODS & NAMING CONVENTIONS

@app.route('/api/v1/products', methods=['GET'])
@api_version('v1')
def get_products():
    """
    GET /api/v1/products?
    Lấy danh sách sản phẩm với hỗ trợ query parameters
    
    Query Parameters:
    - category: Lọc theo danh mục
    - min_price: Giá tối thiểu
    - max_price: Giá tối đa
    - sort_by: Sắp xếp theo (price, name, created_at)
    - order: asc hoặc desc
    - page: Số trang (default: 1)
    - limit: Số items mỗi trang (default: 10)
    """
    # 6. QUERY PARAMETERS
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    # Lọc dữ liệu
    filtered_products = products.copy()
    
    if category:
        filtered_products = [p for p in filtered_products if p['category'] == category]
    
    if min_price:
        filtered_products = [p for p in filtered_products if p['price'] >= min_price]
    
    if max_price:
        filtered_products = [p for p in filtered_products if p['price'] <= max_price]
    
    # Sắp xếp
    if sort_by in ['price', 'name', 'created_at']:
        reverse = (order == 'desc')
        filtered_products.sort(key=lambda x: x[sort_by], reverse=reverse)
    
    # Phân trang
    total = len(filtered_products)
    start = (page - 1) * limit
    end = start + limit
    paginated_products = filtered_products[start:end]
    
    # Meta data cho pagination
    meta = {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit
    }
    
    return success_response(paginated_products, meta=meta)

@app.route('/api/v1/products/<int:product_id>', methods=['GET'])
@api_version('v1')
def get_product(product_id):
    """
    GET /api/v1/products/{id}
    Lấy thông tin chi tiết một sản phẩm
    """
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return error_response(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND"
        )
    
    return success_response(product)

@app.route('/api/v1/products', methods=['POST'])
@api_version('v1')
def create_product():
    """
    POST /api/v1/products
    Tạo sản phẩm mới
    
    Request Body:
    {
        "name": "Product Name",
        "price": 1000000,
        "category": "electronics",
        "stock": 10
    }
    """
    data = request.get_json()
    
    # Validation
    required_fields = ['name', 'price', 'category', 'stock']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return error_response(
            message="Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"missing_fields": missing_fields}
        )
    
    # Tạo product mới
    new_product = {
        "id": max([p['id'] for p in products]) + 1 if products else 1,
        "name": data['name'],
        "price": data['price'],
        "category": data['category'],
        "stock": data['stock'],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    products.append(new_product)
    
    return success_response(
        new_product,
        message="Product created successfully",
        status_code=201
    )

@app.route('/api/v1/products/<int:product_id>', methods=['PUT'])
@api_version('v1')
def update_product(product_id):
    """
    PUT /api/v1/products/{id}
    Cập nhật toàn bộ thông tin sản phẩm
    """
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return error_response(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND"
        )
    
    data = request.get_json()
    
    # PUT yêu cầu cập nhật toàn bộ
    required_fields = ['name', 'price', 'category', 'stock']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return error_response(
            message="PUT requires all fields",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"missing_fields": missing_fields}
        )
    
    # Cập nhật
    product.update({
        'name': data['name'],
        'price': data['price'],
        'category': data['category'],
        'stock': data['stock']
    })
    
    return success_response(product, message="Product updated successfully")

@app.route('/api/v1/products/<int:product_id>', methods=['PATCH'])
@api_version('v1')
def partial_update_product(product_id):
    """
    PATCH /api/v1/products/{id}
    Cập nhật một phần thông tin sản phẩm
    """
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return error_response(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND"
        )
    
    data = request.get_json()
    
    # PATCH cho phép cập nhật một phần
    allowed_fields = ['name', 'price', 'category', 'stock']
    for field in allowed_fields:
        if field in data:
            product[field] = data[field]
    
    return success_response(product, message="Product partially updated successfully")

@app.route('/api/v1/products/<int:product_id>', methods=['DELETE'])
@api_version('v1')
def delete_product(product_id):
    """
    DELETE /api/v1/products/{id}
    Xóa sản phẩm
    """
    global products
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return error_response(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND"
        )
    
    products = [p for p in products if p['id'] != product_id]
    
    return success_response(
        None,
        message="Product deleted successfully",
        status_code=204
    )

# ==================== USERS ENDPOINTS ====================
@app.route('/api/v1/users', methods=['GET'])
@api_version('v1')
def get_users():
    """GET /api/v1/users - Lấy danh sách users"""
    role = request.args.get('role')
    
    filtered_users = users
    if role:
        filtered_users = [u for u in users if u['role'] == role]
    
    return success_response(filtered_users)

@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
@api_version('v1')
def get_user(user_id):
    """GET /api/v1/users/{id} - Lấy thông tin user"""
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return error_response(
            message="User not found",
            status_code=404,
            error_code="USER_NOT_FOUND"
        )
    
    return success_response(user)

@app.route('/api/v1/users', methods=['POST'])
@api_version('v1')
def create_user():
    """POST /api/v1/users - Tạo user mới"""
    data = request.get_json()
    
    required_fields = ['username', 'email', 'role']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return error_response(
            message="Validation failed",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"missing_fields": missing_fields}
        )
    
    # Validate username format (lowercase with hyphens)
    if not re.match(r'^[a-z0-9-]+$', data['username']):
        return error_response(
            message="Invalid username format",
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"hint": "Username must be lowercase with hyphens only"}
        )
    
    # Validate email
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data['email']):
        return error_response(
            message="Invalid email format",
            status_code=422,
            error_code="VALIDATION_ERROR"
        )
    
    new_user = {
        "id": max([u['id'] for u in users]) + 1 if users else 1,
        "username": data['username'],
        "email": data['email'],
        "role": data['role'],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    users.append(new_user)
    
    return success_response(
        new_user,
        message="User created successfully",
        status_code=201
    )

# ==================== ORDERS ENDPOINTS ====================
# Ví dụ về nested resources
@app.route('/api/v1/users/<int:user_id>/orders', methods=['GET'])
@api_version('v1')
def get_user_orders(user_id):
    """
    GET /api/v1/users/{user_id}/orders
    Lấy danh sách orders của một user (Nested Resource)
    """
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return error_response(
            message="User not found",
            status_code=404,
            error_code="USER_NOT_FOUND"
        )
    
    user_orders = [o for o in orders if o['user_id'] == user_id]
    
    return success_response(user_orders)

@app.route('/api/v1/orders', methods=['GET'])
@api_version('v1')
def get_orders():
    """GET /api/v1/orders - Lấy tất cả orders với filter"""
    status = request.args.get('status')
    user_id = request.args.get('user_id', type=int)
    
    filtered_orders = orders
    
    if status:
        filtered_orders = [o for o in filtered_orders if o['status'] == status]
    
    if user_id:
        filtered_orders = [o for o in filtered_orders if o['user_id'] == user_id]
    
    return success_response(filtered_orders)

@app.route('/api/v1/orders/<int:order_id>', methods=['GET'])
@api_version('v1')
def get_order(order_id):
    """GET /api/v1/orders/{id} - Lấy thông tin order"""
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order:
        return error_response(
            message="Order not found",
            status_code=404,
            error_code="ORDER_NOT_FOUND"
        )
    
    return success_response(order)

# ==================== SPECIAL ACTIONS ====================
# Sử dụng động từ cho các action đặc biệt
@app.route('/api/v1/products/<int:product_id>/check-availability', methods=['POST'])
@api_version('v1')
def check_product_availability(product_id):
    """
    POST /api/v1/products/{id}/check-availability
    Action endpoint - Kiểm tra tình trạng còn hàng
    """
    data = request.get_json()
    quantity = data.get('quantity', 1)
    
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return error_response(
            message="Product not found",
            status_code=404,
            error_code="PRODUCT_NOT_FOUND"
        )
    
    available = product['stock'] >= quantity
    
    return success_response({
        "product_id": product_id,
        "requested_quantity": quantity,
        "available_stock": product['stock'],
        "is_available": available
    })

@app.route('/api/v1/orders/<int:order_id>/cancel', methods=['POST'])
@api_version('v1')
def cancel_order(order_id):
    """
    POST /api/v1/orders/{id}/cancel
    Action endpoint - Hủy đơn hàng
    """
    order = next((o for o in orders if o['id'] == order_id), None)
    
    if not order:
        return error_response(
            message="Order not found",
            status_code=404,
            error_code="ORDER_NOT_FOUND"
        )
    
    if order['status'] == 'completed':
        return error_response(
            message="Cannot cancel completed order",
            status_code=400,
            error_code="INVALID_OPERATION"
        )
    
    order['status'] = 'cancelled'
    
    return success_response(order, message="Order cancelled successfully")

# ==================== API INFO & HEALTH CHECK ====================
@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return success_response({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

@app.route('/api/v1', methods=['GET'])
def api_info():
    """API information endpoint"""
    return success_response({
        "name": "REST API Best Practices Demo",
        "version": "1.0.0",
        "description": "Demonstration of 8 REST API best practices",
        "endpoints": {
            "products": "/api/v1/products",
            "users": "/api/v1/users",
            "orders": "/api/v1/orders",
            "health": "/api/v1/health"
        }
    })

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return error_response(
        message="Endpoint not found",
        status_code=404,
        error_code="ENDPOINT_NOT_FOUND"
    )

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return error_response(
        message="Method not allowed",
        status_code=405,
        error_code="METHOD_NOT_ALLOWED"
    )

@app.errorhandler(500)
def internal_server_error(error):
    """Handle 500 errors"""
    return error_response(
        message="Internal server error",
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR"
    )

# ==================== MAIN ====================
if __name__ == '__main__':
    
    app.run(debug=True, port=5000)
