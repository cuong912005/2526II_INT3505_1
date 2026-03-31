# 📖 Week 5: Resource Tree Design & Pagination Strategies

---

## 1️⃣ RESOURCE TREE & DATA MODELING

### 1.1 Thiết kế Resource Tree phù hợp với Domain

**Khái niệm**

Resource Tree là cách tổ chức các API endpoint theo mối quan hệ giữa các tài nguyên (resources) trong business domain.

**Mục tiêu:**
- ✅ Phản ánh structure của business domain
- ✅ API dễ hiểu và nhất quán
- ✅ Thể hiện quan hệ giữa resources (1-to-many, many-to-many)

**Ví dụ Domain: Hệ thống bán hàng (E-commerce)**

Các resource chính:
- Users
- Orders
- Products
- Reviews
- Addresses

**Resource Tree Structure:**
```
/users
  /users/{id}
  /users/{id}/orders
  /users/{id}/addresses

/orders
  /orders/{id}
  /orders/{id}/items

/products
  /products/{id}
  /products/{id}/reviews
```

**API Endpoints ví dụ:**

```python
# Lấy danh sách đơn hàng của user
GET /users/{id}/orders

# Lấy items trong order
GET /orders/{id}/items

# Lấy reviews của product
GET /products/{id}/reviews

# CRUD operations
GET    /users               # lấy tất cả user
POST   /users               # tạo user
GET    /users/{id}          # lấy user cụ thể
PUT    /users/{id}          # cập nhật user
DELETE /users/{id}          # xóa user

GET    /users/{id}/orders   # lấy các đơn hàng của user cụ thể
POST   /users/{id}/orders   # tạo đơn hàng cho user cụ thể
```

**Nguyên tắc thiết kế Resource Tree:**

1. ✅ **Plural resource names:**
   - `/users` (not `/user`)
   - `/products` (not `/product`)

2. ✅ **Use ID cho resource cụ thể:**
   - `/users/{id}`
   - `/orders/{id}`

3. ✅ **Nested resources cho relationship:**
   - `/users/{id}/orders`
   - `/products/{id}/reviews`

4. ❌ **Không nesting quá sâu:**
   - ❌ `/users/{id}/orders/{orderId}/items/{itemId}`
   - ✅ `/orders/{id}/items`

---

### 1.2 Thiết kế Mô hình Dữ liệu (Data Model) cho Domain

**Khái niệm**

Data Model mô tả:
- Các entity (bảng dữ liệu)
- Attributes (cột, trường)
- Relationships (quan hệ giữa các entity)

**Entity chính cho E-commerce:**

```
User: id, name, email
Product: id, name, price, stock
Order: id, user_id, status, total_price
OrderItem: id, order_id, product_id, quantity, price
Review: id, user_id, product_id, rating, comment
Address: id, user_id, street, city, country
```

**Entity Relationships (ER Diagram):**

```
User
  ├─ 1 ------ N Orders
  ├─ 1 ------ N Reviews
  └─ 1 ------ N Addresses

Order
  └─ 1 ------ N OrderItems

Product
  ├─ 1 ------ N OrderItems
  └─ 1 ------ N Reviews
```

**SQL Table Creation Example:**

```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE
);

CREATE TABLE products (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  price DECIMAL(10, 2)
);

CREATE TABLE orders (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  status VARCHAR(20),
  total_price DECIMAL(10, 2),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE order_items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  order_id INT,
  product_id INT,
  quantity INT,
  price DECIMAL(10, 2),
  FOREIGN KEY (order_id) REFERENCES orders(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE reviews (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  product_id INT,
  rating INT,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);
```

**Mapping Data Model → API Endpoints:**

| Data Model | API Endpoint | Purpose |
|-----------|------------|---------|
| Users table | `/users` | List all users |
| Single user | `/users/{id}` | Get user detail |
| User's orders | `/users/{id}/orders` | User's orders (nested) |
| Orders table | `/orders` | List all orders |
| Single order | `/orders/{id}` | Get order detail |
| Order items | `/orders/{id}/items` | Get items in order (nested) |
| Products table | `/products` | List all products |
| Single product | `/products/{id}` | Get product detail |
| Product reviews | `/products/{id}/reviews` | Product's reviews (nested) |

**Flask Implementation ví dụ:**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# Nested resource: User's orders
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def get_user_orders(user_id):
    # Kiểm tra user tồn tại
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Lấy orders của user
    user_orders = [o for o in orders_db if o.user_id == user_id]
    
    # Phân trang
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    paginated = user_orders[offset:offset + limit]
    
    return jsonify({
        'data': [{'id': o.id, 'status': o.status, 'total': o.total_price} for o in paginated],
        'pagination': {'offset': offset, 'limit': limit, 'total': len(user_orders)}
    })

# Nested resource: Order items
@app.route('/orders/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    order = next((o for o in orders_db if o.id == order_id), None)
    if not order:
        return jsonify({'error': 'Order not found'}), 404
    
    items = [i for i in order_items_db if i.order_id == order_id]
    return jsonify({
        'order_id': order_id,
        'items': [{'product_id': i.product_id, 'quantity': i.quantity} for i in items]
    })
```

**Lợi ích của thiết kế tốt:**

✅ **API dễ hiểu** - Phản ánh business domain
✅ **Dễ mở rộng** - Thêm resource mới theo pattern  
✅ **Dễ maintain** - Backend code sạch, logical
✅ **Nhất quán** - Client biết cách organize API
✅ **Scalable** - Query optimization dễ dàng

---

## 2️⃣ PAGINATION STRATEGIES - CHI TIẾT

### 2.1 OFFSET / LIMIT PAGINATION

**Cách hoạt động**

Client gửi:
```
GET /users?offset=20&limit=10
```

SQL:
```sql
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

Ý nghĩa:
- `offset = 20`: Bỏ qua 20 record đầu
- `limit = 10`: Lấy 10 record tiếp theo (record 21-30)

**Code Example**:
```python
def paginate_offset_limit(data, offset=0, limit=10):
    total = len(data)
    paginated = data[offset:offset + limit]
    return {
        'data': paginated,
        'pagination': {
            'offset': offset,
            'limit': limit,
            'total': total,
            'has_more': offset + limit < total
        }
    }
```

**Ưu điểm** ✔
- Đơn giản, dễ hiểu
- Hỗ trợ tốt trong SQL
- Dễ debug
- Dễ jump đến vị trí bất kỳ: `offset=0`, `offset=100`, `offset=1000`

**Nhược điểm** ❌

1. **Chậm với dataset lớn** 🐢
   - DB phải scan và bỏ qua rất nhiều record
   - `OFFSET 1,000,000` → DB phải đọc 1 triệu record

2. **Data inconsistency** 🔄
   - Nếu dữ liệu thay đổi trong lúc phân trang
   - Ví dụ:
     ```
     Page 1: id 1 2 3 4 5 (offset=0, limit=5)
     
     [Có user mới insert: id=0]
     
     Page 2: id 4 5 6 7 8 (offset=5, limit=5)
     
     ⚠️ Kết quả: record 4,5 bị duplicate!
     ```

**Khi nào dùng**: Dashboard, Admin panel, Dataset nhỏ

---

### 2.2 PAGE-BASED PAGINATION

**Cách hoạt động**

Client gửi:
```
GET /users?page=3&pageSize=10
```

Server convert:
```python
offset = (page - 1) * pageSize  # (3-1) * 10 = 20
```

SQL:
```sql
SELECT * FROM users
ORDER BY id
LIMIT 10 OFFSET 20;
```

**Code Example**:
```python
def paginate_page_based(data, page=1, page_size=10):
    total = len(data)
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    paginated = data[offset:offset + page_size]
    
    return {
        'data': paginated,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_items': total
        }
    }
```

**Ưu điểm** ✔
- API dễ dùng cho frontend
- UI quen thuộc: `[1] 2 3 4 5 6 7 [Next]`
- User friendly

**Nhược điểm** ❌
- **Thực chất vẫn là offset** - gặp các vấn đề giống offset/limit:
  - Slow với large dataset
  - Inconsistent khi data thay đổi

**Khi nào dùng**: UI pagination, CMS, Admin system, Blog posts

---

### 2.3 CURSOR-BASED PAGINATION ⭐ (Best Practice)

**Cách hoạt động**

Không dùng offset.

Thay vào đó dùng **cursor** (id hoặc timestamp).

Client gửi:
```
GET /users?limit=10&cursor=42
```

SQL:
```sql
SELECT * FROM users
WHERE id > 42
ORDER BY id
LIMIT 10;
```

Server trả:
```json
{
  "data": [user43, user44, ..., user52],
  "nextCursor": 52,
  "hasMore": true
}
```

**Ví dụ thực tế - Social Media Feed**

Page 1:
```
GET /posts?limit=5

Result: [post1, post2, post3, post4, post5]
nextCursor=5
```

Page 2:
```
GET /posts?cursor=5&limit=5

Result: [post6, post7, post8, post9, post10]
nextCursor=10
```

**Code Example**:
```python
def paginate_cursor_based(data, cursor=None, limit=10):
    if cursor:
        cursor_id = int(cursor)
        # phần tử đầu tiên có id > cursor_id
        start_index = next((i for i, item in enumerate(data) if item.id > cursor_id), len(data))
    else:
        start_index = 0
    
    paginated = data[start_index:start_index + limit]
    next_cursor = paginated[-1].id if len(paginated) == limit else None
    
    return {
        'data': paginated,
        'pagination': {
            'nextCursor': next_cursor,
            'hasMore': next_cursor is not None
        }
    }
```

**Ưu điểm** ✔

1. **Performance rất tốt** ⚡
   - DB dùng index: `WHERE id > 42`
   - Không cần scan hàng triệu row
   - Luôn O(1) lookup

2. **Không bị duplicate/missing** 🔒
   - Vì luôn query theo key (id)
   - Dù data có thay đổi, vẫn an toàn

3. **Phù hợp với real-time data**
   - Infinite scroll (Twitter, Instagram)
   - Timeline, news feed
   - Chat messages

**Nhược điểm** ❌
- ❌ Không jump page: Không thể `page=100`
- ❌ Không biết total: Không biết có bao nhiêu pages
- ❌ Implementation phức tạp hơn

**Khi nào dùng**: Social media feeds, infinite scroll, real-time data, mobile apps

---

## 3️⃣ SO SÁNH 3 CHIẾN LƯỢC

| Tiêu chí | Offset/Limit | Page-Based | Cursor-Based |
|----------|-------------|----------|------------|
| **Độ phức tạp** | Đơn giản | Trung bình | Phức tạp |
| **Jump to page** | ✅ Có | ✅ Có | ❌ Không |
| **Biết total** | ✅ Có | ✅ Có | ❌ Không |
| **Performance** | 🐢 Slow | 🐢 Slow | ⚡ Fast |
| **Stable** | ❌ No | ❌ No | ✅ Yes |
| **Duplicates** | ⚠️ Có thể | ⚠️ Có thể | ✅ Không |

---

## 4️⃣ BEST PRACTICES

### Response Format

```python
# Always include pagination metadata
{
    "data": [...items...],
    "pagination": {
        // Strategy-specific fields
        "has_more": true,  // Always include this
        "total": 500       // If available
    }
}
```

### Input Validation

```python
# Validate ALL parameters
offset = max(0, int(request.args.get('offset', 0)))
limit = max(1, min(int(request.args.get('limit', 10)), 100))  # Max 100

# Always validate in Flask
try:
    offset, limit = validate_pagination_params(offset, limit)
except ValueError:
    return jsonify({'error': 'Invalid parameters'}), 400
```

### Defaults

- Default limit/page_size: 10-20 items (not too many!)
- Max limit: 100 items (prevent abuse)
- Default page: 1 (not 0)
- Default offset: 0

---

## 5️⃣ COMPLETE FLASK EXAMPLE (with Ontology)

```python
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Data
users_db = [{'id': i, 'name': f'User{i}'} for i in range(1, 51)]
products_db = [{'id': i, 'name': f'Product{i}', 'price': i*10} for i in range(1, 101)]
current_user = {'id': 1, 'name': 'Alice'}  # For /user endpoint

# ===== SINGULAR RESOURCES (avoid one-off URLs) =====
# Instead of: /users/current, /users/me
# Use: /user (singular) for current logged-in user
@app.route('/user', methods=['GET'])
def get_current_user():
    return jsonify(current_user)

# ===== COLLECTION + OFFSET/LIMIT =====
@app.route('/users', methods=['GET'])
def list_users():
    offset = max(0, int(request.args.get('offset', 0)))
    limit = max(1, min(int(request.args.get('limit', 10)), 100))
    total = len(users_db)
    data = users_db[offset:offset + limit]
    return jsonify({
        'data': data,
        'pagination': {'offset': offset, 'limit': limit, 'total': total, 'has_more': offset + limit < total}
    })

# ===== SINGLE RESOURCE with ID =====
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users_db if u['id'] == user_id), None)
    return jsonify(user) if user else jsonify({'error': 'Not Found'}), 404 if not user else 200

# ===== NESTED RESOURCES (show relationships) =====
@app.route('/users/<int:user_id>/orders', methods=['GET'])
def list_user_orders(user_id):
    offset = max(0, int(request.args.get('offset', 0)))
    limit = max(1, min(int(request.args.get('limit', 10)), 100))
    # Simulate user's orders
    orders = [{'id': i, 'user_id': user_id, 'total': 100+i*10} for i in range(1, 11)]
    data = orders[offset:offset + limit]
    return jsonify({
        'data': data,
        'pagination': {'offset': offset, 'limit': limit, 'total': len(orders)}
    })

# Collection: /products
@app.route('/products', methods=['GET'])
def list_products():
    page = max(1, int(request.args.get('page', 1)))
    page_size = max(1, min(int(request.args.get('page_size', 10)), 100))
    total = len(products_db)
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    data = products_db[offset:offset + page_size]
    return jsonify({
        'data': data,
        'pagination': {'page': page, 'page_size': page_size, 'total_pages': total_pages}
    })

# Single: /products/{id}
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products_db if p['id'] == product_id), None)
    return jsonify(product) if product else jsonify({'error': 'Not Found'}), 404 if not product else 200

if __name__ == '__main__':
    app.run(debug=True)
```

**Test Ontology Endpoints**:
```bash
# Singular resource (current user)
curl "http://localhost:5000/user"

# Collection
curl "http://localhost:5000/users?offset=0&limit=5"

# Single resource with ID
curl "http://localhost:5000/users/5"

# Nested resource (user's orders)
curl "http://localhost:5000/users/1/orders"
```

---

## 6️⃣ QUICK DECISION GUIDE

| Scenario | Strategy | Ontology Pattern | Lý do |
|----------|----------|-------|-------|
| List all users | Offset/Limit | `GET /users` | Simple, flexible |
| Current user | - | `GET /user` (singular!) | Not `/users/current` |
| Get user by ID | - | `GET /users/{id}` | Specific resource |
| User's orders | Offset/Limit | `GET /users/{id}/orders` | Nested/relationship |
| Blog articles | Page-based | `GET /posts` | Familiar pagination |
| Twitter feed | Cursor-based | `GET /feed` | Real-time, efficient |
| Product search | Offset/Limit | `GET /products?category=...` | Flexible filters |
| Mobile app | Cursor-based | `GET /timeline` | Infinite scroll |

---

## 7️⃣ COMMON ONTOLOGY MISTAKES

| ❌ Wrong Pattern | ✅ Correct Pattern | Why |
|-------|--------|------|
| `/users/current` | `GET /user` | Singular for single resource, avoids one-off URLs |
| `/users/me` | `GET /user` (with auth context) | Same - singular |
| `GET /get_all_users` | `GET /users` | Use HTTP verb, not in URL |
| `GET /users/42/delete` | `DELETE /users/42` | Use HTTP method for action |
| `/api/user/orders/all` | `GET /users/42/orders` | Use IDs, not keywords |
| `/products_featured` | `GET /products?featured=true` | Use query params for filtering |
| `/orders/active` | `GET /orders?status=active` | Same - query params for state |
| `GET /users?get_orders=true` | `GET /users/42/orders` | Use nesting for relationships |

---

## 📌 KEY TAKEAWAYS

✅ **Resource Ontology**: Define consistent naming & structure
✅ **Plural Collections**: `/users`, `/products`, `/orders`
✅ **Singular Single**: `/user`, `/cart` (not `/users/current`)
✅ **Nested Resources**: `/users/{id}/orders` (relationships)
✅ **HTTP Verbs**: GET (read), POST (create), PUT (update), DELETE (delete)
✅ **Pagination**: Choose based on use case
✅ **Offset/Limit**: Simple but slow for large offset
✅ **Page-based**: User-friendly, familiar
✅ **Cursor-based**: Fast & stable, no duplicates
✅ **Always validate input** & include pagination metadata
✅ **Limit max page_size** to prevent abuse
