# UNIFORM INTERFACE - Giao diện thống nhất

## Kịch bản
Sử dụng HTTP methods chuẩn: GET, POST, PUT, DELETE cho CRUD operations.

## Test
```bash
# 1. GET - Lấy tất cả
GET http://localhost:5004/api/books

# 2. GET - Lấy 1 item
GET http://localhost:5004/api/books/1

# 3. POST - Tạo mới
POST http://localhost:5004/api/books
{"title": "New Book", "author": "Author C"}

# 4. PUT - Cập nhật
PUT http://localhost:5004/api/books/1
{"title": "Updated Title", "author": "Author A"}

# 5. DELETE - Xóa
DELETE http://localhost:5004/api/books/1
```

## Chạy
```bash
python app.py
```

## Nguyên tắc
- GET: Đọc dữ liệu (safe, idempotent)
- POST: Tạo mới (not idempotent)
- PUT: Cập nhật (idempotent)
- DELETE: Xóa (idempotent)
