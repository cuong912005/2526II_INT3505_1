from flask import Flask, jsonify, request, send_file

app = Flask(__name__)


# Dữ liệu 
products = [
    {"id": 1, "name": "Laptop", "price": 1000, "category": "electronics", "status": "active"},
    {"id": 2, "name": "Mouse", "price": 20, "category": "electronics", "status": "active"},
    {"id": 3, "name": "Book", "price": 15, "category": "books", "status": "inactive"}
]

next_id = 4


# ============================================================================
# 1. CONSISTENCY (Nhất quán)
# - Nhất quán trong cấu trúc response
# - Nhất quán trong format lỗi
# - Nhất quán trong HTTP methods
# ============================================================================

# CONSISTENCY: Cấu trúc response luôn giống nhau cho danh sách
@app.route('/api/v1/products', methods=['GET'])
def get_products():
    # Filtering
    category = request.args.get('category')
    status = request.args.get('status')
    
    # Pagination
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    
    result = products.copy()
    
    if category:
        result = [p for p in result if p['category'] == category]
    if status:
        result = [p for p in result if p['status'] == status]
    
    # CONSISTENCY: Response structure luôn có data, page, limit, total
    return jsonify({
        "data": result,
        "page": page,
        "limit": limit,
        "total": len(result)
    }), 200


# CONSISTENCY: GET 1 item - response trả về object trực tiếp
@app.route('/api/v1/products/<int:id>', methods=['GET'])
def get_product(id):
    product = next((p for p in products if p['id'] == id), None)
    
    if not product:
        # CONSISTENCY: Error format chuẩn với code, message, details
        return jsonify({
            "error": {
                "code": "PRODUCT_NOT_FOUND",
                "message": f"Product with ID {id} not found",
                "details": "Please check the product ID"
            }
        }), 404
    
    return jsonify(product), 200


# CONSISTENCY: POST tạo mới - luôn trả về 201 Created
@app.route('/api/v1/products', methods=['POST'])
def create_product():
    global next_id
    data = request.get_json()
    
    # Validation
    if not data or 'name' not in data or 'price' not in data:
        # CONSISTENCY: Error format giống nhau
        return jsonify({
            "error": {
                "code": "INVALID_INPUT",
                "message": "Name and price are required",
                "details": "Please provide valid product data"
            }
        }), 400
    
    new_product = {
        "id": next_id,
        "name": data['name'],
        "price": data['price'],
        "category": data.get('category', 'other'),
        "status": data.get('status', 'active')
    }
    
    products.append(new_product)
    next_id += 1
    
    # CONSISTENCY: Status code 201 cho tạo mới
    return jsonify(new_product), 201


# CONSISTENCY: PUT cập nhật toàn bộ - luôn trả về 200 OK
@app.route('/api/v1/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = next((p for p in products if p['id'] == id), None)
    
    if not product:
        return jsonify({
            "error": {
                "code": "PRODUCT_NOT_FOUND",
                "message": f"Product with ID {id} not found",
                "details": "Cannot update non-existent product"
            }
        }), 404
    
    data = request.get_json()
    
    if not data or 'name' not in data or 'price' not in data:
        return jsonify({
            "error": {
                "code": "INVALID_INPUT",
                "message": "Name and price are required for full update",
                "details": "Use PATCH for partial update"
            }
        }), 400
    
    # PUT = cập nhật toàn bộ
    product['name'] = data['name']
    product['price'] = data['price']
    product['category'] = data.get('category', 'other')
    product['status'] = data.get('status', 'active')
    
    return jsonify(product), 200


# CONSISTENCY: PATCH cập nhật một phần - luôn trả về 200 OK
@app.route('/api/v1/products/<int:id>', methods=['PATCH'])
def patch_product(id):
    product = next((p for p in products if p['id'] == id), None)
    
    if not product:
        return jsonify({
            "error": {
                "code": "PRODUCT_NOT_FOUND",
                "message": f"Product with ID {id} not found",
                "details": "Cannot update non-existent product"
            }
        }), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "error": {
                "code": "INVALID_INPUT",
                "message": "No data provided",
                "details": "Please provide fields to update"
            }
        }), 400
    
    # PATCH = chỉ cập nhật fields có trong request
    if 'name' in data:
        product['name'] = data['name']
    if 'price' in data:
        product['price'] = data['price']
    if 'category' in data:
        product['category'] = data['category']
    if 'status' in data:
        product['status'] = data['status']
    
    return jsonify(product), 200


# CONSISTENCY: DELETE luôn trả về 204 No Content
@app.route('/api/v1/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    global products
    
    product = next((p for p in products if p['id'] == id), None)
    
    if not product:
        return jsonify({
            "error": {
                "code": "PRODUCT_NOT_FOUND",
                "message": f"Product with ID {id} not found",
                "details": "Cannot delete non-existent product"
            }
        }), 404
    
    products = [p for p in products if p['id'] != id]
    
    # CONSISTENCY: DELETE thành công = 204 No Content
    return '', 204


# ============================================================================
# 2. CLARITY (Dễ hiểu)
# - Plural nouns: /products (không phải /product)
# - Lowercase: /products (không phải /Products)
# - Hyphens: /product-categories (không phải /productCategories)
# - Không dùng động từ trong URL
# ============================================================================

# BAD: /getProducts (có động từ)
# GOOD: GET /api/v1/products (HTTP method chỉ rõ action)

# BAD: /product/1 (singular)
# GOOD: /api/v1/products/1 (plural noun)

# BAD: /productCategories (camelCase)
# GOOD: /api/v1/product-categories (kebab-case với hyphens)


# ============================================================================
# 3. EXTENSIBILITY (Dễ mở rộng)
# - Versioning: /api/v1/, /api/v2/
# - Query params cho filtering, sorting, pagination
# - Response structure linh hoạt
# ============================================================================

# EXTENSIBILITY: API version 2 với response structure khác
@app.route('/api/v2/products', methods=['GET'])
def get_products_v2():
    # v2 có thể thay đổi cấu trúc response
    result = [
        {
            "id": p['id'],
            "info": {  
                "name": p['name'],
                "price": p['price']
            },
            "metadata": {  
                "category": p['category'],
                "status": p['status']
            }
        }
        for p in products
    ]
    
    return jsonify({
        "version": "2.0",
        "data": result,
        "total": len(result)
    }), 200


# EXTENSIBILITY: Query params cho filtering và sorting
@app.route('/api/v1/products/search', methods=['GET'])
def search_products():
    # Filtering
    category = request.args.get('category')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    
    # Sorting
    sort_by = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    
    result = products.copy()
    
    # Apply filters
    if category:
        result = [p for p in result if p['category'] == category]
    if min_price:
        result = [p for p in result if p['price'] >= min_price]
    if max_price:
        result = [p for p in result if p['price'] <= max_price]
    
    # Apply sorting
    reverse = (order == 'desc')
    result = sorted(result, key=lambda x: x.get(sort_by, 0), reverse=reverse)
    
    return jsonify({
        "data": result,
        "total": len(result),
        "filters": {
            "category": category,
            "min_price": min_price,
            "max_price": max_price,
            "sort": sort_by,
            "order": order
        }
    }), 200


# ============================================================================
# 4. VERSIONING (Phiên bản API)
# - URI Versioning: /api/v1/products, /api/v2/products
# - Header Versioning: Accept: application/vnd.api.v1+json
# - Query Parameter Versioning: /products?version=1
# ============================================================================

#  URI Versioning (Phổ biến nhất)
# Ưu điểm: Dễ hiểu, dễ test, dễ routing
# Nhược điểm: URL thay đổi khi version thay đổi

# V1: Trả về thông tin cơ bản
@app.route('/api/v1/users/<int:user_id>', methods=['GET'])
def get_user_v1(user_id):
    user = {
        "id": user_id,
        "name": "John Doe",
        "email": "john@example.com"
    }
    return jsonify(user), 200


# V2: Thêm nhiều thông tin hơn, structure khác
@app.route('/api/v2/users/<int:user_id>', methods=['GET'])
def get_user_v2(user_id):
    user = {
        "id": user_id,
        "profile": {
            "fullName": "John Doe",  # Đổi tên field
            "firstName": "John",      # Tách riêng
            "lastName": "Doe"
        },
        "contact": {
            "email": "john@example.com",
            "phone": "+84123456789"   # Thêm field mới
        },
        "metadata": {
            "createdAt": "2024-01-01",
            "status": "active"
        }
    }
    return jsonify(user), 200


#  Header Versioning
# Ưu điểm: URI sạch hơn, không thay đổi URL
# Nhược điểm: Khó test hơn, cần check header

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_header_version(user_id):
    # Lấy version từ header
    api_version = request.headers.get('API-Version', 'v1')
    
    if api_version == 'v2':
        # Version 2: Cấu trúc mới
        user = {
            "id": user_id,
            "profile": {
                "fullName": "John Doe",
                "firstName": "John",
                "lastName": "Doe"
            },
            "contact": {
                "email": "john@example.com",
                "phone": "+84123456789"
            }
        }
    else:
        # Version 1: Cấu trúc cũ (default)
        user = {
            "id": user_id,
            "name": "John Doe",
            "email": "john@example.com"
        }
    
    return jsonify({
        "version": api_version,
        "data": user
    }), 200


# Query Parameter Versioning
# Ưu điểm: Dễ test, không cần thay đổi header
# Nhược điểm: Có thể làm URL dài hơn

@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer_query_version(customer_id):
    # Lấy version từ query parameter
    version = request.args.get('v', 'v1')
    
    if version == 'v2':
        # Version 2
        customer = {
            "customerId": customer_id,
            "personalInfo": {
                "name": "Jane Smith",
                "age": 30
            },
            "orderHistory": {
                "totalOrders": 15,
                "totalSpent": 5000
            }
        }
    else:
        # Version 1 (default)
        customer = {
            "id": customer_id,
            "name": "Jane Smith",
            "orders": 15
        }
    
    return jsonify({
        "apiVersion": version,
        "data": customer
    }), 200


# VERSIONING: Deprecation Warning (Cảnh báo version cũ)
@app.route('/api/v1/products/deprecated', methods=['GET'])
def get_deprecated_endpoint():
    return jsonify({
        "warning": "This endpoint is deprecated and will be removed in v3",
        "message": "Please migrate to /api/v2/products",
        "deprecatedAt": "2024-06-01",
        "sunsetDate": "2025-01-01",
        "data": products
    }), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
