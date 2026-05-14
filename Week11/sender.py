import requests
import hmac
import hashlib
import json
import uuid
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] - %(message)s'
)
logger = logging.getLogger(__name__)

SECRET_KEY = b'my_super_secret_webhook_key'
WEBHOOK_URL = 'http://127.0.0.1:5001/webhook/notifications'

def trigger_webhook(event_type, payload_dict):
    """
    Dong goi du lieu, tao chu ky dien tu va gui request den he thong nhan.
    """
    payload_bytes = json.dumps(payload_dict).encode('utf-8')
    signature = hmac.new(SECRET_KEY, payload_bytes, hashlib.sha256).hexdigest()
    delivery_id = str(uuid.uuid4())
    
    headers = {
        'Content-Type': 'application/json',
        'X-MySystem-Event': event_type,
        'X-MySystem-Signature': f"sha256={signature}",
        'X-MySystem-Delivery': delivery_id
    }
    
    logger.info("Khoi tao gui webhook. Su kien: %s, Delivery ID: %s, URL: %s", event_type, delivery_id, WEBHOOK_URL)
    
    try:
        response = requests.post(WEBHOOK_URL, data=payload_bytes, headers=headers, timeout=5)
        logger.info("He thong nhan phan hoi ma trang thai: %s", response.status_code)
    except requests.exceptions.RequestException as error:
        logger.error("Loi ket noi den he thong nhan. Chi tiet: %s", error)

if __name__ == '__main__':
    mock_payment_data = {
        "transaction_id": "txn_987654321",
        "user_id": "u_001",
        "amount": 1500000,
        "currency": "VND",
        "status": "succeeded"
    }
    trigger_webhook('payment.success', mock_payment_data)