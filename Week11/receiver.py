# notification_receiver.py
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
SECRET_KEY = b'my_super_secret_webhook_key'

def verify_signature(payload_bytes, signature_header):
    """Áp dụng Security Pattern của GitHub (HMAC SHA-256)"""
    if not signature_header:
        return False
    # Băm payload nhận được với secret key
    expected_mac = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
    expected_signature = f"sha256={expected_mac}"
    # So sánh chuỗi an toàn để chống Timing Attacks
    return hmac.compare_digest(expected_signature, signature_header)

@app.route('/webhook/notifications', methods=['POST'])
def handle_webhook():
    # 1. Lấy Headers đặc trưng (Pattern)
    signature = request.headers.get('X-MySystem-Signature')
    event_type = request.headers.get('X-MySystem-Event')
    delivery_id = request.headers.get('X-MySystem-Delivery')

    # 2. Xác thực (Security)
    if not verify_signature(request.data, signature):
        print(" [CẢNH BÁO] Chữ ký không hợp lệ! Từ chối request.")
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    print(f"[NHẬN WEBHOOK] Sự kiện: {event_type} | ID: {delivery_id}")
    
    # 3. Logic thông báo (Nên đẩy vào Celery/Queue trong thực tế)
    if event_type == 'payment.success':
        print(f" Đang gửi Email & SMS xác nhận cho User: {data['user_id']} số tiền {data['amount']}...")
    elif event_type == 'repo.push':
        print(f" Đang bắn thông báo lên Slack: Có code mới!")

    # 4. Trả về 200 OK NGAY LẬP TỨC (Async Pattern)
    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(port=5001)