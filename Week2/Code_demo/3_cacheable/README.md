# CACHEABLE - Dữ liệu có thể cache

## Kịch bản
Server chỉ định response nào có thể cache, bao lâu thông qua HTTP headers.

## Test
```bash
# 1. News - Cache 1 giờ
GET http://localhost:5003/api/news
# Check header: Cache-Control: public, max-age=3600

# 2. Time - Không cache (luôn mới)
GET http://localhost:5003/api/time
# Check header: Cache-Control: no-cache, no-store

# 3. Static data - Cache 24 giờ
GET http://localhost:5003/api/static-data
# Check header: Cache-Control: public, max-age=86400
```

## Chạy
```bash
python app.py
```

## Giải thích
- max-age=3600: Cache 1 giờ
- no-cache: Không cache
- public: Cho phép cache ở proxy/CDN
