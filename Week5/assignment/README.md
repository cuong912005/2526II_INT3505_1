# Book Management REST API (Flask)

API quản lý sách với 5 endpoints REST chuẩn và 3 phương thức phân trang.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cấu hình Database

Đảm bảo MySQL đang chạy tại `localhost:3306`. Cập nhật thông tin kết nối trong `app.py`:

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',  # Thay đổi password nếu cần
    'database': 'book_management'
}
```

## Chạy ứng dụng

```bash
python app.py
```

Server chạy tại: `http://localhost:5000`

## Cấu trúc code

```
app.py
├── CONFIG          # Cấu hình kết nối MySQL
├── REPOSITORY      # BookRepository - thao tác với database
├── CONTROLLER      # BookController - xử lý request/response  
└── ROUTES          # Flask routes - 5 REST endpoints
```

## API Endpoints

### 1. GET /api/books - Lấy danh sách sách (có phân trang)

**Phân trang Limit/Offset:**
```
GET /api/books?paginationType=limit-offset&limit=10&offset=0
```

**Phân trang Page-based:**
```
GET /api/books?paginationType=page-based&page=1&pageSize=10
```

**Phân trang Cursor-based:**
```
GET /api/books?paginationType=cursor-based&cursor=5&limit=10
```

### 2. GET /api/books/<id> - Lấy sách theo ID

```
GET /api/books/1
```

### 3. POST /api/books - Tạo sách mới

```json
POST /api/books
Content-Type: application/json

{
    "title": "Clean Code",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "published_year": 2008,
    "genre": "Programming",
    "price": 45.99
}
```

### 4. PUT /api/books/<id> - Cập nhật sách

```json
PUT /api/books/1
Content-Type: application/json

{
    "title": "Clean Code (Updated)",
    "author": "Robert C. Martin",
    "isbn": "978-0132350884",
    "published_year": 2008,
    "genre": "Programming",
    "price": 49.99
}
```

### 5. DELETE /api/books/<id> - Xóa sách

```
DELETE /api/books/1
```

## Ví dụ Response

### Limit/Offset Pagination
```json
{
    "success": true,
    "pagination_type": "limit-offset",
    "data": [...],
    "total": 100,
    "limit": 10,
    "offset": 0
}
```

### Page-based Pagination
```json
{
    "success": true,
    "pagination_type": "page-based",
    "data": [...],
    "pagination": {
        "current_page": 1,
        "page_size": 10,
        "total_items": 100,
        "total_pages": 10,
        "has_next_page": true,
        "has_prev_page": false
    }
}
```

### Cursor-based Pagination
```json
{
    "success": true,
    "pagination_type": "cursor-based",
    "data": [...],
    "pagination": {
        "next_cursor": 15,
        "has_more": true,
        "limit": 10
    }
}
```
