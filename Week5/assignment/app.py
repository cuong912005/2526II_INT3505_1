from flask import Flask, request, jsonify
import pymysql

# ============== CONFIG ==============
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'cuong912005',
    'database': 'book_management',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection():
    return pymysql.connect(**DB_CONFIG)

def init_database():
    """Initialize database and create books table"""
    try:
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                author VARCHAR(255) NOT NULL,
                published_year INT,
                genre VARCHAR(100),
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print('✅ Database and table initialized')
        cursor.close()
        conn.close()
    except Exception as e:
        print(f'❌ Database initialization failed: {e}')


# ============== REPOSITORY ==============
class BookRepository:
    
    def get_all_limit_offset(self, limit=10, offset=0):
        """Get all books with limit/offset pagination"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books ORDER BY id LIMIT %s OFFSET %s', (int(limit), int(offset)))
        rows = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) as total FROM books')
        total = cursor.fetchone()['total']
        cursor.close()
        conn.close()
        return {
            'data': rows,
            'total': total,
            'limit': int(limit),
            'offset': int(offset)
        }
    
    def get_all_page_based(self, page=1, page_size=10):
        """Get all books with page-based pagination"""
        page = int(page)
        page_size = int(page_size)
        offset = (page - 1) * page_size
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books ORDER BY id LIMIT %s OFFSET %s', (page_size, offset))
        rows = cursor.fetchall()
        cursor.execute('SELECT COUNT(*) as total FROM books')
        total = cursor.fetchone()['total']
        cursor.close()
        conn.close()
        total_pages = (total + page_size - 1) // page_size
        return {
            'data': rows,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_items': total,
                'total_pages': total_pages,
                'has_next_page': page < total_pages,
                'has_prev_page': page > 1
            }
        }
    
    def get_all_cursor_based(self, cursor_id=None, limit=10):
        """Get all books with cursor-based pagination (using id as cursor)"""
        limit = int(limit)
        conn = get_connection()
        db_cursor = conn.cursor()
        if cursor_id:
            db_cursor.execute('SELECT * FROM books WHERE id > %s ORDER BY id LIMIT %s', (int(cursor_id), limit))
        else:
            db_cursor.execute('SELECT * FROM books ORDER BY id LIMIT %s', (limit,))
        rows = db_cursor.fetchall()
        next_cursor = rows[-1]['id'] if rows else None
        has_more = len(rows) == limit
        db_cursor.close()
        conn.close()
        return {
            'data': rows,
            'pagination': {
                'next_cursor': next_cursor if has_more else None,
                'has_more': has_more,
                'limit': limit
            }
        }
    
    def get_by_id(self, id):
        """Get book by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM books WHERE id = %s', (id,))
        book = cursor.fetchone()
        cursor.close()
        conn.close()
        return book
    
    def create(self, book):
        """Create new book"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO books (title, author, published_year, genre, price)
            VALUES (%s, %s, %s, %s, %s)
        ''', (book.get('title'), book.get('author'),
              book.get('published_year'), book.get('genre'), book.get('price')))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return {'id': new_id, **book}
    
    def update(self, id, book):
        """Update book"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE books SET title = %s, author = %s, 
            published_year = %s, genre = %s, price = %s WHERE id = %s
        ''', (book.get('title'), book.get('author'),
              book.get('published_year'), book.get('genre'), book.get('price'), id))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        if affected == 0:
            return None
        return self.get_by_id(id)
    
    def delete(self, id):
        """Delete book"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM books WHERE id = %s', (id,))
        conn.commit()
        affected = cursor.rowcount
        cursor.close()
        conn.close()
        return affected > 0


book_repository = BookRepository()


# ============== CONTROLLER ==============
class BookController:
    
    def get_all(self):
        """GET /api/books - Get all books with pagination"""
        try:
            pagination_type = request.args.get('paginationType', 'page-based')
            
            if pagination_type == 'limit-offset':
                limit = request.args.get('limit', 10)
                offset = request.args.get('offset', 0)
                result = book_repository.get_all_limit_offset(limit, offset)
            elif pagination_type == 'cursor-based':
                cursor_id = request.args.get('cursor')
                limit = request.args.get('limit', 10)
                result = book_repository.get_all_cursor_based(cursor_id, limit)
            else:  # page-based (default)
                page = request.args.get('page', 1)
                page_size = request.args.get('pageSize', 10)
                result = book_repository.get_all_page_based(page, page_size)
            
            return jsonify({
                'success': True,
                'pagination_type': pagination_type,
                **result
            })
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error fetching books', 'error': str(e)}), 500
    
    def get_by_id(self, id):
        """GET /api/books/:id - Get book by ID"""
        try:
            book = book_repository.get_by_id(id)
            if not book:
                return jsonify({'success': False, 'message': 'Book not found'}), 404
            return jsonify({'success': True, 'data': book})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error fetching book', 'error': str(e)}), 500
    
    def create(self):
        """POST /api/books - Create new book"""
        try:
            data = request.get_json()
            if not data.get('title') or not data.get('author'):
                return jsonify({'success': False, 'message': 'Title and author are required'}), 400
            new_book = book_repository.create(data)
            return jsonify({'success': True, 'message': 'Book created successfully', 'data': new_book}), 201
        except pymysql.err.IntegrityError:
            return jsonify({'success': False, 'message': 'ISBN already exists'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error creating book', 'error': str(e)}), 500
    
    def update(self, id):
        """PUT /api/books/:id - Update book"""
        try:
            data = request.get_json()
            if not data.get('title') or not data.get('author'):
                return jsonify({'success': False, 'message': 'Title and author are required'}), 400
            updated_book = book_repository.update(id, data)
            if not updated_book:
                return jsonify({'success': False, 'message': 'Book not found'}), 404
            return jsonify({'success': True, 'message': 'Book updated successfully', 'data': updated_book})
        except pymysql.err.IntegrityError:
            return jsonify({'success': False, 'message': 'ISBN already exists'}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error updating book', 'error': str(e)}), 500
    
    def delete(self, id):
        """DELETE /api/books/:id - Delete book"""
        try:
            deleted = book_repository.delete(id)
            if not deleted:
                return jsonify({'success': False, 'message': 'Book not found'}), 404
            return jsonify({'success': True, 'message': 'Book deleted successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error deleting book', 'error': str(e)}), 500


book_controller = BookController()


# ============== APP & ROUTES ==============
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'Book Management API',
        'version': '1.0.0',
        'endpoints': {
            'GET /api/books': 'Get all books with pagination',
            'GET /api/books/<id>': 'Get book by ID',
            'POST /api/books': 'Create new book',
            'PUT /api/books/<id>': 'Update book',
            'DELETE /api/books/<id>': 'Delete book'
        },
        'pagination': {
            'limit-offset': 'GET /api/books?paginationType=limit-offset&limit=10&offset=0',
            'page-based': 'GET /api/books?paginationType=page-based&page=1&pageSize=10',
            'cursor-based': 'GET /api/books?paginationType=cursor-based&cursor=5&limit=10'
        }
    })

@app.route('/api/books', methods=['GET'])
def get_all_books():
    return book_controller.get_all()

@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    return book_controller.get_by_id(id)

@app.route('/api/books', methods=['POST'])
def create_book():
    return book_controller.create()

@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    return book_controller.update(id)

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    return book_controller.delete(id)


if __name__ == '__main__':
    init_database()
    print('🚀 Server running on http://localhost:5000')
    print('📚 API endpoints available at http://localhost:5000/api/books')
    app.run(debug=True, port=5000)
