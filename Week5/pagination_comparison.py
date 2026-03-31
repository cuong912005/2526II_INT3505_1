from datetime import datetime

# ========== DATA MODELS ==========
class User:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email

class Product:
    def __init__(self, id, name, price, stock):
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock
    
    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'price': self.price, 'stock': self.stock}

class Order:
    def __init__(self, id, user_id, total, created_at):
        self.id = id
        self.user_id = user_id
        self.total = total
        self.created_at = created_at
    
    def to_dict(self):
        return {'id': self.id, 'user_id': self.user_id, 'total': self.total, 'created_at': self.created_at.isoformat()}

# Sample data
products_db = [Product(i, f"Product{i}", 10 * i, 100 - i * 5) for i in range(1, 101)]
orders_db = [Order(i, (i % 5) + 1, 100 + i * 10, datetime(2025, 1, (i % 28) + 1)) for i in range(1, 101)]

# ========== PAGINATION IMPLEMENTATION 1: OFFSET/LIMIT ==========
def paginate_offset_limit(data, offset=0, limit=10):
    # Example: offset=0, limit=10 -> lấy 0-9
    # Example: offset=10, limit=10 -> lấy 10-19
    total = len(data)
    paginated = data[offset:offset + limit]
    
    return {
        'data': paginated,
        'pagination': {
            'offset': offset,
            'limit': limit,
            'total': total,
            'has_more': offset + limit < total
        }
    }

# Test offset/limit
print("=" * 60)
print("OFFSET/LIMIT PAGINATION")
print("=" * 60)
result = paginate_offset_limit(products_db, offset=0, limit=5)
print(f"Request: offset=0, limit=5")
print(f"Result: Got {len(result['data'])} items, total={result['pagination']['total']}, has_more={result['pagination']['has_more']}")
for p in result['data']:
    print(f"  - {p.name} (${p.price})")

# ========== PAGINATION IMPLEMENTATION 2: PAGE-BASED ==========
def paginate_page_based(data, page=1, page_size=10):
    # Example: page=1, page_size=10 -> lấy  0-9 (trang đầu)
    # Example: page=2, page_size=10 -> lấy 10-19 (trang thứ 2)
    total = len(data)
    total_pages = (total + page_size - 1) // page_size
    offset = (page - 1) * page_size
    paginated = data[offset:offset + page_size]
    
    return {
        'data': paginated,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_pages': total_pages,
            'total_items': total
        }
    }

# Test page-based
print("\n" + "=" * 60)
print("PAGE-BASED PAGINATION")
print("=" * 60)
result = paginate_page_based(products_db, page=2, page_size=5)
print(f"Request: page=2, page_size=5")
print(f"Result: Page {result['pagination']['page']} of {result['pagination']['total_pages']}, got {len(result['data'])} items")
for p in result['data']:
    print(f"  - {p.name} (${p.price})")

# ========== PAGINATION IMPLEMENTATION 3: CURSOR-BASED ==========
def paginate_cursor_based(data, cursor=None, limit=10, cursor_field='id'):
    # cursor format: cursor="next_12" -> bắt đầu với item có id=12
    if cursor:
        prefix, cursor_value = cursor.split('_')
        cursor_id = int(cursor_value)
        # tìm kiếm vị trí bắt đầu dựa trên cursor_id
        start_index = next((i for i, item in enumerate(data) if item.id > cursor_id), len(data))
    else:
        start_index = 0
    
    paginated = data[start_index:start_index + limit]
    next_cursor = f"next_{paginated[-1].id}" if len(paginated) == limit else None
    
    return {
        'data': paginated,
        'pagination': {
            'next_cursor': next_cursor,
            'has_more': next_cursor is not None,
            'count': len(paginated)
        }
    }

# Test cursor-based
print("\n" + "=" * 60)
print("CURSOR-BASED PAGINATION")
print("=" * 60)
result = paginate_cursor_based(products_db, cursor=None, limit=5)
print(f"Request: cursor=None, limit=5 (first batch)")
print(f"Result: Got {result['pagination']['count']} items, next_cursor={result['pagination']['next_cursor']}")
for p in result['data']:
    print(f"  - {p.name}")

result2 = paginate_cursor_based(products_db, cursor=result['pagination']['next_cursor'], limit=5)
print(f"\nRequest: cursor={result['pagination']['next_cursor']}, limit=5 (second batch)")
print(f"Result: Got {result2['pagination']['count']} items, next_cursor={result2['pagination']['next_cursor']}")
for p in result2['data']:
    print(f"  - {p.name}")

# ========== COMPARISON TABLE ==========
print("\n" + "=" * 60)
print("PAGINATION STRATEGY COMPARISON")
print("=" * 60)
comparison = {
    'Feature': ['Simplicity', 'Jump to page', 'Performance large dataset', 'Real-time data', 'Duplicate/Miss', 'Mobile friendly', 'SEO friendly', 'SQL efficiency'],
    'Offset/Limit': ['High', 'Yes', 'Low', 'Risky', 'Possible', 'Medium', 'No', 'Medium'],
    'Page-Based': ['High', 'Yes', 'Low', 'Risky', 'Possible', 'High', 'Yes', 'Medium'],
    'Cursor-Based': ['Medium', 'No', 'High', 'Safe', 'No', 'Medium', 'No', 'High']
}

for key in comparison['Feature']:
    print(f"{key:25} | {comparison['Offset/Limit'][comparison['Feature'].index(key)]:20} | {comparison['Page-Based'][comparison['Feature'].index(key)]:20} | {comparison['Cursor-Based'][comparison['Feature'].index(key)]:15}")

# ========== BEST PRACTICES ==========
print("\n" + "=" * 60)
print("BEST PRACTICES")
print("=" * 60)
print("""
1. CHOOSE BASED ON USE CASE:
   - offset/limit: Small datasets, admin panels, general APIs
   - page-based: User-facing, SEO-important, web apps
   - cursor-based: Real-time feeds, large datasets, mobile apps

2. RESPONSE FORMAT:
   - Always include pagination metadata
   - Indicate if more data exists (has_more)
   - Return total count only if cheap to compute

3. DEFAULTS:
   - limit/page_size: 10-20 items (not too many)
   - max limit: 100 items (prevent abuse)
   - default offset: 0, default page: 1

4. EFFICIENCY:
   - Use database LIMIT/OFFSET or SEEK
   - Index frequently filtered/sorted columns
   - Avoid SELECT COUNT(*) if possible

5. CONSISTENCY:
   - Document pagination method clearly
   - Keep cursor format stable
   - Consistent parameter naming
""")
