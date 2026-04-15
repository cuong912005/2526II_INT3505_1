from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage
books = [
    {"id": 1, "title": "Python 101", "author": "John Doe", "year": 2020, "price": 29.99}
]

# 1. GET - Lấy danh sách sách
@app.route('/api/books', methods=['GET'])
def get_books():
    search = request.args.get('search', '').lower()
    if search:
        filtered = [b for b in books if search in b['title'].lower() or search in b['author'].lower()]
        return jsonify(filtered), 200
    return jsonify(books), 200

# 2. GET - Lấy sách theo ID
@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book), 200

# 3. POST - Tạo sách mới
@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author'):
        return jsonify({"error": "Title and author are required"}), 400
    
    new_id = max([b['id'] for b in books], default=0) + 1
    book = {
        "id": new_id,
        "title": data['title'],
        "author": data['author'],
        "year": data.get('year', 2024),
        "price": data.get('price', 0)
    }
    books.append(book)
    return jsonify(book), 201

# 4. PUT - Cập nhật sách
@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    data = request.get_json()
    book.update(data)
    return jsonify(book), 200

# 5. DELETE - Xóa sách
@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    global books
    book = next((b for b in books if b['id'] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    books = [b for b in books if b['id'] != book_id]
    return jsonify({"message": "Book deleted"}), 200

# Health check
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
