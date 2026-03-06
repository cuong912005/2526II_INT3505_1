# LAYERED SYSTEM - Hệ thống phân lớp

## Kịch bản
Request đi qua nhiều layer middleware (logging, auth, rate-limit) trước khi đến endpoint.

## Test
```bash
# 1. Public endpoint - Chỉ qua logging layer
GET http://localhost:5005/api/public

# 2. Protected endpoint - Qua logging -> auth -> rate-limit
GET http://localhost:5005/api/protected
Header: Authorization: Bearer mytoken123

# 3. Admin endpoint - Qua logging -> auth
GET http://localhost:5005/api/admin
Header: Authorization: Bearer admintoken
```

## Chạy
```bash
python app.py
```

## Các Layer
1. Logging Layer: Ghi log mọi request
2. Authentication Layer: Kiểm tra token
3. Rate Limit Layer: Giới hạn tốc độ request

Client không biết có bao nhiêu layer ở giữa.
