from flask import Flask
from config import get_config
from controllers.product_controller import product_bp

app = Flask(__name__)
# Nạp configuration environment
app.config.from_object(get_config())

# Đăng ký Blueprint cho endpoint /api/products
app.register_blueprint(product_bp, url_prefix='/api/products')

if __name__ == '__main__':
    # Tham khảo APP_CONFIG từ config.py nếu cần (mặc định Port 5000)
    app.run(host='0.0.0.0', port=5000, debug=True)