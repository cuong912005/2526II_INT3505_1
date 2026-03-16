# ═══════════════════════════════════════════════════════════════
# Week4 - OpenAPI & Swagger UI Demo
# API quản lý sách (5 endpoints) với tài liệu tự động
# ═══════════════════════════════════════════════════════════════

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import yaml
import os

app = Flask(__name__)
CORS(app)

# ─── Swagger UI Configuration ────────────────────────────────
# /api/docs      → Swagger UI (giao diện tài liệu tương tác)
# /api/spec      → OpenAPI YAML spec dạng JSON để Swagger UI đọc
SWAGGER_URL = "/api/docs"
API_URL = "/api/spec"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Book Management API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# ─── Serve OpenAPI spec file ─────────────────────────────────
# Đọc file openapi.yaml và trả về dạng JSON cho Swagger UI render
@app.route("/api/spec")
def get_spec():
    spec_path = os.path.join(os.path.dirname(__file__), "openapi.yaml")
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    return jsonify(spec)


# ─── In-memory data store ────────────────────────────────────
# Dữ liệu mẫu, lưu trong bộ nhớ (reset khi restart server)
books = [
    {"id": 1, "title": "Tôi Thấy Hoa Vàng Trên Cỏ Xanh", "author": "Nguyen Nhat Anh", "year": 2010},
    {"id": 2, "title": "Dế Mèn Phiêu Lưu Ký", "author": "Tô Hoài", "year": 1941},
    {"id": 3, "title": "Số Đỏ", "author": "Vũ Trọng Phụng", "year": 1936},
]
next_id = 4  # auto-increment counter


# ─── Helper: tìm sách theo id ────────────────────────────────
def find_book(book_id):
    return next((b for b in books if b["id"] == book_id), None)


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 1: GET /api/v1/books
# Lấy danh sách sách, hỗ trợ filter theo author và search theo title
# ═══════════════════════════════════════════════════════════════
@app.route("/api/v1/books", methods=["GET"])
def list_books():
    result = books[:]

    # Filter theo author (exact match, case-insensitive)
    author = request.args.get("author")
    if author:
        result = [b for b in result if b["author"].lower() == author.lower()]

    # Search theo title (substring, case-insensitive)
    search = request.args.get("search")
    if search:
        result = [b for b in result if search.lower() in b["title"].lower()]

    return jsonify({"success": True, "data": result, "total": len(result)})


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 2: GET /api/v1/books/<id>
# Lấy chi tiết một cuốn sách theo id
# ═══════════════════════════════════════════════════════════════
@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"success": False, "message": "Book not found"}), 404
    return jsonify({"success": True, "data": book})


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 3: POST /api/v1/books
# Thêm sách mới — yêu cầu title, author, year trong request body
# ═══════════════════════════════════════════════════════════════
@app.route("/api/v1/books", methods=["POST"])
def create_book():
    global next_id
    data = request.get_json()

    # Validate: kiểm tra các trường bắt buộc
    for field in ["title", "author", "year"]:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing required field: {field}"}), 400

    new_book = {
        "id": next_id,
        "title": data["title"],
        "author": data["author"],
        "year": data["year"],
    }
    books.append(new_book)
    next_id += 1

    return jsonify({"success": True, "message": "Book created successfully", "data": new_book}), 201


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 4: PUT /api/v1/books/<id>
# Cập nhật thông tin sách — cho phép cập nhật title, author, year
# ═══════════════════════════════════════════════════════════════
@app.route("/api/v1/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"success": False, "message": "Book not found"}), 404

    data = request.get_json()

    # Chỉ cập nhật các trường được gửi lên
    if "title" in data:
        book["title"] = data["title"]
    if "author" in data:
        book["author"] = data["author"]
    if "year" in data:
        book["year"] = data["year"]

    return jsonify({"success": True, "message": "Book updated successfully", "data": book})


# ═══════════════════════════════════════════════════════════════
# ENDPOINT 5: DELETE /api/v1/books/<id>
# Xoá sách theo id
# ═══════════════════════════════════════════════════════════════
@app.route("/api/v1/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = find_book(book_id)
    if not book:
        return jsonify({"success": False, "message": "Book not found"}), 404

    books.remove(book)
    return jsonify({"success": True, "message": "Book deleted successfully"})


# ─── Custom error handlers ───────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "message": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "message": "Method not allowed"}), 405


# ─── Entry point ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Book Management API")
    print("  API endpoints : http://localhost:5000/api/v1/books")
    print("  Swagger UI    : http://localhost:5000/api/docs")
    print("  OpenAPI spec  : http://localhost:5000/api/spec")
    print("=" * 55)
    app.run(debug=True, port=5000)
