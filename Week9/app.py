from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================
# Mock Data
# ==========================================
payments_db = [
    {"id": 1, "user_id": 101, "amount_usd": 50.0, "status": "completed"},
    {"id": 2, "user_id": 102, "amount_usd": 150.0, "status": "pending"}
]

# ==========================================
# 1. URL Versioning (Phổ biến nhất)
# Ưu điểm: Dễ dàng cache, dễ nhìn thấy trong logs và trình duyệt
# Khuyết điểm: Làm bẩn URL với thông tin thay đổi
# ==========================================

@app.route('/api/v1/payments', methods=['GET'])
def get_payments_v1():
    """
    API v1: Trả về số tiền dưới dạng số thực `amount_usd`
    """
    return jsonify({
        "version": "v1",
        "data": payments_db
    })

@app.route('/api/v2/payments', methods=['GET'])
def get_payments_v2():
    """
    API v2 (Breaking Change): Trả về số tiền dưới dạng object `amount` chứa `value` và `currency`
    """
    v2_data = []
    for p in payments_db:
        p_v2 = {
            "id": p["id"],
            "user_id": p["user_id"],
            "amount": {
                "value": p["amount_usd"],
                "currency": "USD"
            },
            "status": p["status"].upper() # Chuyển status thành UPPERCASE trong v2
        }
        v2_data.append(p_v2)
        
    return jsonify({
        "version": "v2",
        "data": v2_data
    })

# ==========================================
# 2. Header / Accept-Version Versioning (Custom Header)
# Ưu điểm: Giữ URL sạch
# Khuyết điểm: Khó test trực tiếp trên trình duyệt, có thể bị sót khi cache
# ==========================================

@app.route('/api/payments', methods=['GET'])
def get_payments_by_header():
    # Kiểm tra custom header 'X-API-Version'
    version = request.headers.get('X-API-Version', '1.0')
    
    if version == '2.0':
        return jsonify({"message": "Phản hồi theo cấu trúc v2.0 (Header)"})
    
    # Mặc định gọi logic hàm v1
    return jsonify({"message": "Phản hồi theo cấu trúc v1.0 (Header)"})

# ==========================================
# 3. Query Parameter Versioning
# Ưu điểm: Thay đổi URL dễ dàng từ phía client
# Khuyết điểm: Tham số query thường dùng cho filtering, dùng cho versioning có thể gây nhầm lẫn
# ==========================================

@app.route('/api/payments_query', methods=['GET'])
def get_payments_by_query():
    version = request.args.get('version', 'v1')
    
    if version == 'v2':
        return jsonify({"message": "Phản hồi theo cấu trúc v2 (Query)"})
        
    return jsonify({"message": "Phản hồi theo cấu trúc v1 (Query)"})

if __name__ == '__main__':
    print("Khởi chạy server tại: http://localhost:5000")
    print("Test URL Versioning:")
    print(" - v1: http://localhost:5000/api/v1/payments")
    print(" - v2: http://localhost:5000/api/v2/payments")
    app.run(debug=True, port=5000)
