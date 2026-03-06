# STATELESS - Server không lưu trạng thái client

## Kịch bản
Server không lưu session hay state của client. Mỗi request phải chứa đủ thông tin (token) để xác thực.

## Test
```bash
# Bước 1: Login lấy token
POST http://localhost:5001/login
{"username": "admin", "password": "123"}
# Response: {"token": "token_admin_abc123"}

# Bước 2: Dùng token để truy cập profile
GET http://localhost:5001/profile
Header: Authorization: Bearer token_admin_abc123

# Bước 3: Mỗi request đều phải gửi token
GET http://localhost:5001/data
Header: Authorization: Bearer token_admin_abc123
```

## Chạy
```bash
python app.py
```
