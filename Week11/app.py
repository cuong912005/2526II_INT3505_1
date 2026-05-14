from flask import Flask, request, jsonify, url_for
import requests
import threading

app = Flask(__name__)

# Mock Database
orders_db = [
    {"id": 1, "item": "Sách C++ nâng cao", "status": "pending", "price": 150},
    {"id": 2, "item": "Bàn phím cơ", "status": "shipped", "price": 1200}
]

# Danh sách URL Webhook mà client đăng ký để nhận thông báo
registered_webhooks = []


# --- HELPER FUNCTIONS ---

def simulate_publish_to_kafka(event_type, payload):
    """Mô phỏng Event-driven pattern: Đẩy event vào Message Broker (như Kafka)"""
    print(f"[EVENT-DRIVEN] Đang đẩy sự kiện '{event_type}' tới Broker...")
    print(f"[EVENT-DRIVEN] Payload: {payload}")
    # Trong thực tế, đây là nơi bạn dùng confluent_kafka producer.produce()

def trigger_webhooks(payload):
    """Mô phỏng Webhook pattern: Bắn request đến các URL đã đăng ký"""
    for url in registered_webhooks:
        print(f"[WEBHOOK] Đang gửi POST request tới {url}...")
        try:
            # Gửi không đồng bộ (bỏ qua lỗi trong demo này)
            requests.post(url, json=payload, timeout=2)
        except Exception as e:
            print(f"[WEBHOOK] Gửi thất bại tới {url}: {e}")

# --- API ENDPOINTS ---

@app.route('/webhooks', methods=['POST'])
def register_webhook():
    """Client đăng ký Webhook URL"""
    data = request.json
    url = data.get("url")
    if url and url not in registered_webhooks:
        registered_webhooks.append(url)
        return jsonify({"message": "Webhook registered successfully", "url": url}), 201
    return jsonify({"error": "Invalid URL"}), 400


@app.route('/orders', methods=['GET'])
def get_orders():
    """
    CRUD (Read) + Query Pattern
    Ví dụ Query: /orders?status=pending
    """
    status_query = request.args.get('status')
    
    # Logic lọc (Query)
    result = orders_db
    if status_query:
        result = [order for order in orders_db if order['status'] == status_query]
        
    return jsonify({"count": len(result), "data": result}), 200


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    CRUD (Read) + HATEOAS Pattern
    """
    order = next((o for o in orders_db if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Áp dụng HATEOAS: Cung cấp _links để Client tự biết điều hướng tiếp theo
    response = {
        "data": order,
        "_links": {
            "self": url_for('get_order', order_id=order['id'], _external=True),
            "update_status": url_for('update_order_status', order_id=order['id'], _external=True),
            "all_orders": url_for('get_orders', _external=True)
        }
    }
    return jsonify(response), 200


@app.route('/orders', methods=['POST'])
def create_order():
    """
    CRUD (Create) + Event-driven + Webhook
    """
    data = request.json
    new_order = {
        "id": len(orders_db) + 1,
        "item": data.get("item"),
        "status": "pending",
        "price": data.get("price")
    }
    orders_db.append(new_order)

    # 1. Áp dụng Event-Driven: Bắn event (ví dụ để Service Kho hàng cập nhật số lượng)
    # Dùng thread để không block API response
    threading.Thread(
        target=simulate_publish_to_kafka, 
        args=("OrderCreated", new_order)
    ).start()

    # 2. Áp dụng Webhook: Thông báo cho Client biết đơn hàng đã tạo thành công
    threading.Thread(
        target=trigger_webhooks, 
        args=({"event": "order.created", "data": new_order},)
    ).start()

    return jsonify({"message": "Order created", "data": new_order}), 201


@app.route('/orders/<int:order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """Cập nhật trạng thái đơn hàng"""
    order = next((o for o in orders_db if o['id'] == order_id), None)
    if not order:
        return jsonify({"error": "Order not found"}), 404
        
    data = request.json
    new_status = data.get("status")
    order['status'] = new_status
    
    return jsonify({"message": "Status updated", "data": order}), 200

if __name__ == '__main__':
    print("🚀 Server đang chạy tại http://127.0.0.1:5000")
    app.run(debug=True, port=5000)