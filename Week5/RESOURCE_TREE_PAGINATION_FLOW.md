# 📚 Resource Tree Design & Pagination Strategies Flow

**Week 5 - REST API Design Patterns**

---

## 📋 Table of Contents

1. [Resource Tree Design Principles](#resource-tree-design-principles)
2. [Domain Modeling](#domain-modeling)
3. [Pagination Strategies](#pagination-strategies)
4. [Nested Resources](#nested-resources)
5. [API Flow Examples](#api-flow-examples)
6. [Best Practices](#best-practices)

---

## 🎯 Resource Tree Design Principles

### What is a Resource Tree?

A **Resource Tree** is a hierarchical organization of API endpoints that reflects the relationships between business entities (resources) in your domain.

```
Resource Tree Structure:
┌─────────────────────────────────────┐
│         /users                      │
│       ├─ /users/{id}                │
│       └─ /users/{id}/orders         │
│          └─ /users/{id}/orders/{id} │
│                                     │
│         /products                   │
│       ├─ /products/{id}             │
│       └─ /products/{id}/reviews     │
│                                     │
│         /orders                     │
│       ├─ /orders/{id}               │
│       └─ /orders/{id}/items         │
└─────────────────────────────────────┘
```

### Design Principles

#### 1. **Use Plural Resource Names**
```
✅ CORRECT:
GET    /users              # Collection
GET    /users/1            # Specific resource
GET    /products           # Collection

❌ WRONG:
GET    /user               # Should be /users
GET    /product/5          # Should be /products/5
```

#### 2. **Use IDs for Specific Resources**
```
✅ CORRECT:
GET    /users/123          # Get user with ID 123
PUT    /products/456       # Update product with ID 456

❌ WRONG:
GET    /users/name=alice   # Use ID instead
GET    /products/name=Laptop
```

#### 3. **Nested Resources for Relationships**
```
✅ CORRECT:
GET    /users/1/orders     # All orders of user 1
GET    /users/1/orders/5   # Order 5 of user 1

❌ WRONG (too deep):
GET    /users/1/orders/5/items/10/details
✅ BETTER (flatten when needed):
GET    /orders/5/items
GET    /items/10
```

#### 4. **Use HTTP Methods Correctly (CRUD)**
```
CREATE:
POST   /users              # Create new user
POST   /users/1/orders     # Create order for user 1

READ:
GET    /users              # List all users
GET    /users/1            # Get specific user
GET    /users/1/orders     # List user's orders

UPDATE:
PUT    /users/1            # Replace entire user
PATCH  /users/1            # Update specific fields

DELETE:
DELETE /users/1            # Delete user
DELETE /users/1/orders/5   # Delete user's order
```

---

## 📊 Domain Modeling

### E-commerce Domain Example

```
┌────────────────────────────────────────────────┐
│          E-Commerce Data Model                 │
├────────────────────────────────────────────────┤
│                                                │
│  User                                          │
│  ├─ id (PK)                                    │
│  ├─ name                                       │
│  ├─ email                                      │
│  └─ created_at                                 │
│       │                                        │
│       └─ 1:N relationship with Order           │
│                                                │
│  Order                                         │
│  ├─ id (PK)                                    │
│  ├─ user_id (FK → User)                       │
│  ├─ total_price                                │
│  ├─ status                                     │
│  ├─ created_at                                 │
│       │                                        │
│       └─ 1:N relationship with OrderItem       │
│                                                │
│  OrderItem                                     │
│  ├─ id (PK)                                    │
│  ├─ order_id (FK → Order)                     │
│  ├─ product_id (FK → Product)                 │
│  ├─ quantity                                   │
│  └─ price                                      │
│                                                │
│  Product                                       │
│  ├─ id (PK)                                    │
│  ├─ name                                       │
│  ├─ price                                      │
│  ├─ stock                                      │
│  └─ category                                   │
│                                                │
└────────────────────────────────────────────────┘
```

### Resource Tree for E-commerce

```python
# Users Resource Tree
/users                          # List users
/users/{id}                     # Get/Update/Delete user
/users/{id}/orders              # User's orders
/users/{id}/orders/{order_id}   # Specific order
/users/{id}/addresses           # User's addresses

# Orders Resource Tree
/orders                         # List all orders
/orders/{id}                    # Get/Update/Delete order
/orders/{id}/items              # Order items

# Products Resource Tree
/products                       # List products
/products/{id}                  # Get product
/products/{id}/reviews          # Product reviews
/products/{id}/images           # Product images
```

---

## 📖 Pagination Strategies

### Why Pagination?

Pagination allows clients to retrieve large datasets in manageable chunks:
- **Reduces response size** and network bandwidth
- **Improves API performance** (database queries faster)
- **Better user experience** (mobile-friendly)
- **Scalability** for large datasets

### Strategy 1: Offset/Limit Pagination

**How it works:**
- `offset`: Number of items to skip
- `limit`: Number of items to return
- Example: `?offset=10&limit=5` → Skip 10 items, get next 5

**Request/Response Example:**

```bash
# Request: Get 5 users starting from position 0
GET /users?offset=0&limit=5

# Response:
{
  "data": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie", "email": "charlie@example.com"},
    {"id": 4, "name": "Diana", "email": "diana@example.com"},
    {"id": 5, "name": "Eve", "email": "eve@example.com"}
  ],
  "pagination": {
    "offset": 0,
    "limit": 5,
    "total": 20,
    "has_more": true
  }
}

# Request: Next page
GET /users?offset=5&limit=5

# Response: Next 5 users (IDs 6-10)
```

**Pros:**
- ✅ Easy to understand and implement
- ✅ Can jump to any page easily: `?offset=100&limit=10`
- ✅ Works well for small-medium datasets
- ✅ SEO friendly for pagination

**Cons:**
- ❌ Performance degrades with large offsets (database scans from beginning)
- ❌ Duplicate/missing items if data changes during pagination
- ❌ Not ideal for real-time data

```
Offset/Limit Flow Diagram:

User requests page 1:
GET /users?offset=0&limit=5
           ↓
┌─────────────────────┐
│ User 1, 2, 3, 4, 5  │  ← Returned
└─────────────────────┘

User requests page 2:
GET /users?offset=5&limit=5
           ↓
┌─────────────────────┐
│ User 6, 7, 8, 9, 10 │  ← Returned
└─────────────────────┘
```

### Strategy 2: Page-Based Pagination

**How it works:**
- `page`: Page number (1-indexed)
- `page_size`: Items per page
- Example: `?page=2&page_size=10` → Get page 2 with 10 items per page

**Request/Response Example:**

```bash
# Request: Get page 1 with 5 items per page
GET /products?page=1&page_size=5

# Response:
{
  "data": [
    {"id": 1, "name": "Product1", "price": 10},
    {"id": 2, "name": "Product2", "price": 20},
    {"id": 3, "name": "Product3", "price": 30},
    {"id": 4, "name": "Product4", "price": 40},
    {"id": 5, "name": "Product5", "price": 50}
  ],
  "pagination": {
    "page": 1,
    "page_size": 5,
    "total_pages": 4,
    "total_items": 20
  }
}

# Request: Next page
GET /products?page=2&page_size=5

# Response: Items 6-10
```

**Pros:**
- ✅ User-friendly (people think in pages)
- ✅ Easy to display page numbers in UI
- ✅ SEO friendly (easily indexable: /products?page=1)
- ✅ Good for general web applications

**Cons:**
- ❌ Still suffers from performance issues with large pages
- ❌ Not ideal for real-time data (items can shift between pages)
- ❌ Less efficient than cursor-based for mobile apps

```
Page-Based Flow Diagram:

Page 1: ?page=1&page_size=5
    ↓
┌─────────────┐
│ Item 1-5    │
└─────────────┘

Page 2: ?page=2&page_size=5
    ↓
┌─────────────┐
│ Item 6-10   │
└─────────────┘

Page 3: ?page=3&page_size=5
    ↓
┌─────────────┐
│ Item 11-15  │
└─────────────┘
```

### Strategy 3: Cursor-Based Pagination

**How it works:**
- `cursor`: Position pointer to a specific item
- `limit`: Number of items to return after cursor
- The cursor tells server exactly where to start
- Great for real-time data (infinite scroll)

**Request/Response Example:**

```bash
# Request: Get first batch (no cursor)
GET /orders?limit=5

# Response:
{
  "data": [
    {"id": 1, "user_id": 1, "total": 100},
    {"id": 2, "user_id": 2, "total": 150},
    {"id": 3, "user_id": 1, "total": 200},
    {"id": 4, "user_id": 3, "total": 250},
    {"id": 5, "user_id": 2, "total": 300}
  ],
  "pagination": {
    "next_cursor": "next_5",      ← Use this for next request
    "has_more": true
  }
}

# Request: Next batch (using cursor)
GET /orders?cursor=next_5&limit=5

# Response: Items 6-10, cursor=next_10
{
  "data": [
    {"id": 6, "user_id": 1, "total": 350},
    {"id": 7, "user_id": 4, "total": 400},
    ...
  ],
  "pagination": {
    "next_cursor": "next_10",     ← Use for next request
    "has_more": true
  }
}

# Request: Final batch
GET /orders?cursor=next_10&limit=5

# Response: Last 5 items, cursor=null
{
  "data": [...],
  "pagination": {
    "next_cursor": null,          ← No more items
    "has_more": false
  }
}
```

**Pros:**
- ✅ **Best performance** (stateless position, no counting)
- ✅ **Real-time safe** (no duplicate/missing items even if data changes)
- ✅ **Ideal for infinite scroll** (mobile apps, social media)
- ✅ **Consistent results** (always sorted by creation order)

**Cons:**
- ❌ Can't jump to specific page directly
- ❌ More complex to implement
- ❌ Requires maintaining sort order
- ❌ Not SEO friendly (non-bookmarkable URLs)

```
Cursor-Based Flow Diagram:

1. First Request (no cursor):
   GET /orders?limit=5
   ↓
   [Order 1, 2, 3, 4, 5]
   next_cursor: "next_5"

2. Second Request (with cursor):
   GET /orders?cursor=next_5&limit=5
   ↓
   [Order 6, 7, 8, 9, 10]
   next_cursor: "next_10"

3. Third Request (with new cursor):
   GET /orders?cursor=next_10&limit=5
   ↓
   [Order 11, 12, 13, 14, 15]
   next_cursor: null (end of data)
```

### Pagination Strategies Comparison

| Feature | Offset/Limit | Page-Based | Cursor-Based |
|---------|-------------|-----------|-------------|
| **Simplicity** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Jump to page** | ✅ Yes | ✅ Yes | ❌ No |
| **Performance (large datasets)** | ❌ Low | ❌ Low | ✅ High |
| **Real-time data** | ⚠️ Risky (duplicates) | ⚠️ Risky (duplicates) | ✅ Safe |
| **Duplicate/Miss items** | Possible | Possible | Never |
| **Mobile friendly** | ⭐⭐⭐ Medium | ⭐⭐⭐ Medium | ⭐⭐⭐⭐ Excellent |
| **SEO friendly** | ✅ Yes | ✅ Yes | ❌ No |
| **SQL efficiency** | ⭐⭐ Medium | ⭐⭐ Medium | ⭐⭐⭐⭐ Excellent |

---

## 🔗 Nested Resources

### Types of Relationships

#### 1. **One-to-Many Relationships**

```
User → Orders (1 user has many orders)

GET /users/1/orders          # Get all orders for user 1
GET /users/1/orders/5        # Get order 5 of user 1
POST /users/1/orders         # Create order for user 1
DELETE /users/1/orders/5     # Delete order 5 of user 1
```

#### 2. **Query Resource Instead of Nesting Too Deep**

```
❌ TOO DEEP (avoid):
GET /users/1/orders/5/items/10/comments/3

✅ BETTER (flatten):
GET /users/1/orders         # Orders for user 1
GET /orders/5               # Specific order
GET /orders/5/items         # Items in order
GET /items/10               # Item details
GET /items/10/comments      # Comments on item
```

### Nested Resource Best Practices

**1. Limit nesting depth to 2 levels:**
```
✅ Good:  /users/1/orders
❌ Bad:   /users/1/orders/5/items/10
```

**2. Consider flattening for direct access:**
```
✅ Better to provide both:
GET /users/1/orders         # Through parent
GET /orders/5                # Direct access (priority)
```

**3. Apply filtering in nested resources:**
```bash
# Filter user's orders by status
GET /users/1/orders?status=completed&offset=0&limit=10

# Filter user's orders by date range
GET /users/1/orders?date_from=2024-01-01&date_to=2024-12-31
```

---

## 📊 API Flow Examples

### Complete E-commerce Flow

```
┌──────────────────────────────────────────────────────────┐
│           E-commerce API Complete Flow                   │
└──────────────────────────────────────────────────────────┘

1. BROWSE PRODUCTS (page-based pagination)
   GET /products?page=1&page_size=10
   ↓
   ┌────────────────────────────────┐
   │ Products 1-10 (page 1)         │
   │ - Product1: $10                │
   │ - Product2: $20                │
   │ - ...                          │
   │ total_pages: 5                 │
   └────────────────────────────────┘

2. GET PRODUCT DETAILS
   GET /products/5
   ↓
   ┌────────────────────────────────┐
   │ Product5: "Laptop"             │
   │ Price: $50                     │
   │ Stock: 100                     │
   └────────────────────────────────┘

3. LOGIN/GET USER (implicit or token-based)
   GET /users/1
   ↓
   ┌────────────────────────────────┐
   │ User1: Alice                   │
   │ Email: alice@example.com       │
   └────────────────────────────────┘

4. VIEW ORDER HISTORY (offset/limit pagination)
   GET /users/1/orders?offset=0&limit=5
   ↓
   ┌────────────────────────────────┐
   │ Order1: Total $100 (Jan 1)     │
   │ Order2: Total $150 (Jan 5)     │
   │ Order3: Total $200 (Jan 10)    │
   │ ...                            │
   │ has_more: true                 │
   └────────────────────────────────┘

5. VIEW SPECIFIC ORDER DETAILS
   GET /users/1/orders/2
   ↓
   ┌────────────────────────────────┐
   │ Order2: User1                  │
   │ Total: $150                    │
   │ Status: Shipped                │
   │ Created: Jan 5                 │
   └────────────────────────────────┘

6. VIEW ORDER ITEMS
   GET /orders/2/items
   ↓
   ┌────────────────────────────────┐
   │ Item1: Product5 × 2 = $100     │
   │ Item2: Product3 × 1 = $50      │
   │ Total: $150                    │
   └────────────────────────────────┘

7. CREATE NEW ORDER
   POST /users/1/orders
   {
     "items": [
       {"product_id": 5, "quantity": 1},
       {"product_id": 3, "quantity": 2}
     ]
   }
   ↓
   ┌────────────────────────────────┐
   │ ✅ Order Created Successfully   │
   │ Order ID: 15                   │
   │ Total: $210                    │
   └────────────────────────────────┘
```

### Pagination Flow Example

```
USER BROWSING PRODUCTS (INFINITE SCROLL - Cursor-based)

1. Page Load
   GET /products?limit=20
   ↓
   ┌─────────────────────────┐
   │ Products 1-20           │
   │ next_cursor: "next_20"  │
   │ has_more: true          │
   └─────────────────────────┘
   
   User sees products, scrolls down

2. User Reaches End of Page
   GET /products?cursor=next_20&limit=20
   ↓
   ┌─────────────────────────┐
   │ Products 21-40          │
   │ next_cursor: "next_40"  │
   │ has_more: true          │
   └─────────────────────────┘
   
   More products loaded automatically

3. User Continues Scrolling
   GET /products?cursor=next_40&limit=20
   ↓
   ┌─────────────────────────┐
   │ Products 41-60          │
   │ next_cursor: null       │
   │ has_more: false         │
   └─────────────────────────┘
   
   No more products (reached end)
```

---

## ✅ Best Practices

### 1. **Consistent Response Structure**

```json
{
  "data": [...],
  "pagination": {
    "offset": 0,
    "limit": 10,
    "total": 100,
    "has_more": true
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "v1"
  }
}
```

### 2. **Choose Right Strategy for Use Case**

| Use Case | Best Strategy |
|----------|--------------|
| Admin panels | Offset/Limit (can jump to page) |
| Web products listing | Page-based (SEO friendly) |
| Mobile infinite scroll | Cursor-based (best performance) |
| Real-time feeds | Cursor-based (no duplicates) |
| API documentation | Offset/Limit (simplest) |

### 3. **Set Reasonable Limits**

```python
# Example: reasonable limit constraints
MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 20

# Validate in API
if limit > MAX_LIMIT:
    limit = MAX_LIMIT
if limit < MIN_LIMIT:
    limit = MIN_LIMIT
```

### 4. **Provide Metadata**

```json
{
  "data": [...],
  "pagination": {
    "current_count": 10,      # Items in this response
    "total_count": 1000000,   # Total items available
    "has_more": true,
    "page": 1,
    "total_pages": 100000
  }
}
```

### 5. **Error Handling**

```python
# Invalid page number
GET /products?page=999999
{
  "error": "invalid_page",
  "message": "Page 999999 does not exist. Total pages: 50"
}

# Invalid limit
GET /users?offset=0&limit=1000
{
  "error": "limit_too_large",
  "message": "Maximum limit is 100. Set limit=100"
}
```

### 6. **Document Pagination in API**

```markdown
## GET /users

### Pagination Parameters

- **offset** (integer, default=0): Number of items to skip
- **limit** (integer, default=10, max=100): Items to return

### Example
```
GET /users?offset=10&limit=5
```

### Response
```json
{
  "data": [...],
  "pagination": {
    "offset": 10,
    "limit": 5,
    "total": 100,
    "has_more": true
  }
}
```
```

---

## 🧪 Testing Pagination

### Test Matrix

| Strategy | Test Case | Expected Behavior |
|----------|-----------|-------------------|
| Offset/Limit | `?offset=0&limit=5` | Return items 1-5 |
| Offset/Limit | `?offset=5&limit=5` | Return items 6-10 |
| Page-based | `?page=1&page_size=5` | Return items 1-5 |
| Page-based | `?page=2&page_size=5` | Return items 6-10 |
| Cursor-based | `?limit=5` (no cursor) | Return first 5, with cursor |
| Cursor-based | `?cursor=next_5&limit=5` | Return items after position 5 |

### Using Postman

1. Import `ResourceTree_Pagination.postman_collection.json`
2. Test each strategy with different parameters
3. Verify response structure and metadata
4. Check pagination calculation

---

**Created: April 2026 | Week 5 - Resource Tree Design & Pagination Strategies**
