# 🔐 Authentication & Authorization Flow Documentation

**Week 6 - JWT + OAuth 2.0 Implementation**

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [JWT Authentication Flow](#jwt-authentication-flow)
3. [OAuth 2.0 Flow](#oauth-20-flow)
4. [Scopes & Permissions](#scopes--permissions)
5. [Roles & Authorizations](#roles--authorizations)
6. [Usage Guide](#usage-guide)
7. [Error Handling](#error-handling)

---

## 🎯 System Overview

This system implements a comprehensive authentication and authorization solution using two complementary mechanisms:

- **JWT (JSON Web Tokens)**: Direct authentication for users with username/password
- **OAuth 2.0**: Delegated authorization for third-party applications

### Key Components

```
┌─────────────────────────────────────────────────────┐
│              Authentication System                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         JWT Authentication (Direct)          │  │
│  ├──────────────────────────────────────────────┤  │
│  │ • User Login (username/password)             │  │
│  │ • Access Token Generation                    │  │
│  │ • Refresh Token Management                   │  │
│  │ • Token Blacklisting on Logout               │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │      OAuth 2.0 Authorization (Delegated)     │  │
│  ├──────────────────────────────────────────────┤  │
│  │ • Authorization Code Flow (Web Apps)         │  │
│  │ • Implicit Flow (SPAs, Mobile Apps)          │  │
│  │ • Client Credentials Flow (Services)         │  │
│  │ • Scope-based Permission Control             │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 🔐 JWT Authentication Flow

### Flow Diagram

```
┌─────────┐                                    ┌──────────┐
│  User   │                                    │  Server  │
└────┬────┘                                    └────┬─────┘
     │                                              │
     │  1. POST /auth/login                        │
     │  {username, password}                       │
     ├─────────────────────────────────────────>  │
     │                                              │
     │                                  2. Verify credentials
     │                                     Generate tokens
     │                                              │
     │  3. Response: {access_token,                │
     │              refresh_token}                 │
     │  <─────────────────────────────────────────┤
     │                                              │
     │  4. Store tokens in client                  │
     │                                              │
     │  5. Include access_token in                 │
     │     Authorization header                    │
     │  Authorization: Bearer <token>              │
     ├─────────────────────────────────────────>  │
     │                                              │
     │                          6. Verify token signature
     │                             Check expiration
     │                             Validate scopes
     │                                              │
     │  7. Response: Protected resource            │
     │  <─────────────────────────────────────────┤
```

### Login Process

```bash
POST /auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "alice123"
}

# Response (200 OK)
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "roles": ["admin"]
  }
}
```

### Token Structure

#### Access Token
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": 1,
  "username": "alice",
  "roles": ["admin"],
  "scopes": ["read:products", "write:products", "admin:full"],
  "exp": 1640000000,        // Expiration time
  "iat": 1639996400,        // Issued at
  "type": "access"
}

Signature: HMAC-SHA256(header + payload + secret)
```

#### Refresh Token
```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Payload:
{
  "user_id": 1,
  "username": "alice",
  "exp": 1640086800,        // Longer expiration
  "iat": 1639996400,
  "type": "refresh"
}

Signature: HMAC-SHA256(header + payload + refresh_secret)
```

### Refresh Token Flow

```
┌─────────┐                                    ┌──────────┐
│  User   │                                    │  Server  │
└────┬────┘                                    └────┬─────┘
     │                                              │
     │  Access Token Expired                       │
     │                                              │
     │  POST /auth/refresh                         │
     │  {refresh_token}                            │
     ├────────────────────────────────────────>   │
     │                                              │
     │                      Verify refresh token
     │                      Generate new access token
     │                                              │
     │  Response: {new_access_token}               │
     │  <────────────────────────────────────────┤
     │                                              │
     │  Continue using new access_token            │
```

### Logout Process

```bash
POST /auth/logout
Authorization: Bearer <access_token>

# Response (200 OK)
{
  "message": "Logged out successfully"
}

# Token is added to blacklist and cannot be used anymore
```

---

## 🔑 OAuth 2.0 Flow

### Grant Types Supported

#### 1. Authorization Code Flow (Most Common)
**Best for:** Web applications, traditional server-side apps

```
┌──────────┐                                     ┌──────────┐
│  Browser │                                     │  Server  │
└────┬─────┘                                     └────┬─────┘
     │                                                │
     │  1. User clicks "Login with OAuth"            │
     │                                                │
     │  2. Redirect to /oauth/authorize              │
     │  https://localhost:5000/oauth/authorize      │
     │  ?response_type=code                         │
     │  &client_id=web-app-client                   │
     │  &redirect_uri=http://localhost:3000/callback│
     │  &scope=read:products write:products         │
     │  &state=random123                            │
     ├──────────────────────────────────────────>  │
     │                                                │
     │                        User login & authorize
     │                        app permissions
     │                                                │
     │  3. Redirect to redirect_uri with code        │
     │  http://localhost:3000/callback              │
     │  ?code=AUTH_CODE_xyz                         │
     │  &state=random123                            │
     │  <──────────────────────────────────────────┤
     │
     │  4. Backend: Exchange code for token
     │  POST /oauth/token
     │  {
     │    grant_type: "authorization_code",
     │    code: "AUTH_CODE_xyz",
     │    client_id: "web-app-client",
     │    client_secret: "web-app-secret-12345"
     │  }
     │                                                │
     │                        5. Validate code
     │                           Generate access token
     │                                                │
     │  6. Return access token                       │
     │  {access_token, expires_in, scope}           │
     │  <──────────────────────────────────────────┤
     │                                                │
     │  7. Use access_token to access resources
```

**Example:**

```bash
# Step 1: Authorization Request (URL in browser)
GET /oauth/authorize?response_type=code&client_id=web-app-client&redirect_uri=http://localhost:3000/callback&scope=read:products%20write:products&state=random_state_123

# User logs in and authorizes

# Step 2: Backend receives auth code
GET http://localhost:3000/callback?code=AUTH_CODE_xyz&state=random_state_123

# Step 3: Backend exchanges code for token
POST /oauth/token
{
  "grant_type": "authorization_code",
  "code": "AUTH_CODE_xyz",
  "client_id": "web-app-client",
  "client_secret": "web-app-secret-12345",
  "redirect_uri": "http://localhost:3000/callback"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read:products write:products"
}
```

#### 2. Implicit Flow
**Best for:** Single Page Applications (SPAs), mobile apps

⚠️ **Note:** Deprecated in OAuth 2.0 Security Best Practices

```bash
GET /oauth/authorize?response_type=token&client_id=spa-app&redirect_uri=https://app.example.com/callback&scope=read:products&state=abc123

# User authorizes

# Redirect with token in URL fragment
https://app.example.com/callback#access_token=TOKEN&state=abc123&expires_in=3600
```

#### 3. Client Credentials Flow
**Best for:** Service-to-service authentication, backend integrations

```
┌─────────────────┐                      ┌──────────────┐
│  Backend Service│                      │ OAuth Server │
└────┬────────────┘                      └────┬─────────┘
     │                                        │
     │  POST /oauth/token                    │
     │  {                                     │
     │    grant_type: "client_credentials",  │
     │    client_id: "backend-service",      │
     │    client_secret: "secret",           │
     │    scope: "backend:full"              │
     │  }                                     │
     ├───────────────────────────────────>  │
     │                                        │
     │                  Validate credentials
     │                  Generate token
     │                                        │
     │  {access_token, expires_in}           │
     │  <───────────────────────────────────┤
     │                                        │
     │  Use token to access APIs             │
```

**Example:**

```bash
POST /oauth/token
{
  "grant_type": "client_credentials",
  "client_id": "backend-service",
  "client_secret": "backend-service-secret-99999",
  "scope": "backend:full"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "backend:full"
}
```

---

## 🔓 Scopes & Permissions

Scopes define what actions an OAuth client can perform on behalf of a user.

### Available Scopes

| Scope | Description | Examples |
|-------|-------------|----------|
| `read:products` | Read product information | GET /products |
| `write:products` | Create/modify products | POST /products |
| `read:orders` | Read user orders | GET /orders |
| `write:orders` | Create orders | POST /orders |
| `admin:users` | Manage users (admin only) | GET/DELETE /admin/users |
| `admin:full` | Full admin access | All admin endpoints |
| `backend:full` | Backend service access | Service-to-service |

### Scope Request

```bash
# Request specific scopes
GET /oauth/authorize?...&scope=read:products%20write:products

# Authorization Server validates if client can request these scopes
# Scopes listed in client's allowed_scopes configuration
```

### Demo Users & Their Scopes

```python
{
  "alice": {
    "username": "alice",
    "email": "alice@example.com",
    "roles": ["admin"],
    "scopes": ["read:products", "write:products", "admin:full"],
    "password": "alice123"
  },
  "bob": {
    "username": "bob",
    "email": "bob@example.com",
    "roles": ["user"],
    "scopes": ["read:products", "read:orders"],
    "password": "bob456"
  },
  "charlie": {
    "username": "charlie",
    "email": "charlie@example.com",
    "roles": ["moderator"],
    "scopes": ["read:products", "read:orders"],
    "password": "charlie789"
  }
}
```

---

## 👥 Roles & Authorizations

### Role-Based Access Control (RBAC)

```
┌─────────────────────────────────────┐
│      Roles & Permissions Matrix     │
├─────────────────────────────────────┤
│                                     │
│  ADMIN                              │
│  ├── GET /products (read:products)  │
│  ├── POST /products (write:products)│
│  ├── GET /orders (read:orders)      │
│  ├── GET /admin/users               │
│  └── DELETE /admin/users/<id>       │
│                                     │
│  USER                               │
│  ├── GET /products (read:products)  │
│  └── GET /orders (read:orders)      │
│                                     │
│  MODERATOR                          │
│  ├── GET /products (read:products)  │
│  └── GET /orders (read:orders)      │
│                                     │
└─────────────────────────────────────┘
```

### Authorization Decorators

```python
@require_auth              # Requires valid JWT/OAuth token
@require_scope('read:products')  # Requires specific scope
@require_role('admin')     # Requires specific role
```

### Example Authorization Check

```python
@protected_bp.route('/products', methods=['GET'])
@require_auth                      # Token required
@require_scope('read:products')    # Scope check
def get_products():
    return jsonify({...})

# Decorator stack validation order:
# 1. Check if token exists
# 2. Validate token signature & expiration
# 3. Extract user info from token
# 4. Check required scope
# 5. Check user role (if needed)
```

---

## 📖 Usage Guide

### Demo OAuth 2.0 Clients

```python
OAUTH_CLIENTS = {
  "web-app-client": {
    "client_secret": "web-app-secret-12345",
    "redirect_uris": ["http://localhost:3000/callback"],
    "grant_types": ["authorization_code"],
    "allowed_scopes": ["read:products", "write:products"]
  },
  "mobile-app-client": {
    "client_secret": "mobile-app-secret-67890",
    "redirect_uris": ["app://callback"],
    "grant_types": ["implicit"],
    "allowed_scopes": ["read:products"]
  },
  "backend-service": {
    "client_secret": "backend-service-secret-99999",
    "grant_types": ["client_credentials"],
    "allowed_scopes": ["backend:full"]
  }
}
```

### Step-by-Step: Web App OAuth Flow

#### 1. User Clicks Login Button
```html
<a href="http://localhost:5000/oauth/authorize?response_type=code&client_id=web-app-client&redirect_uri=http://localhost:3000/callback&scope=read:products%20write:products&state=random123">
  Login with OAuth
</a>
```

#### 2. Server Redirects to Authorization Page
User logs in with username/password and approves scopes

#### 3. Redirect with Authorization Code
```
http://localhost:3000/callback?code=AUTH_CODE_xyz&state=random123
```

#### 4. Backend Exchanges Code for Token
```python
response = requests.post('http://localhost:5000/oauth/token', json={
    'grant_type': 'authorization_code',
    'code': 'AUTH_CODE_xyz',
    'client_id': 'web-app-client',
    'client_secret': 'web-app-secret-12345',
    'redirect_uri': 'http://localhost:3000/callback'
})
```

#### 5. Store and Use Access Token
```javascript
const {access_token} = response.json();
localStorage.setItem('access_token', access_token);

// Use in subsequent requests
fetch('http://localhost:5000/products', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
})
```

---

## ❌ Error Handling

### JWT Authentication Errors

| Status | Error | Description |
|--------|-------|-------------|
| 400 | Missing username or password | Invalid login request |
| 401 | Invalid credentials | Wrong username/password |
| 401 | Token has expired | Access token expired |
| 401 | Invalid token | Malformed or invalid token |
| 401 | Refresh token has expired | Refresh token expired |

### OAuth 2.0 Errors

| Error Code | Description | Solution |
|-----------|-------------|----------|
| `invalid_request` | Missing required parameters | Check all required params |
| `invalid_client` | Client_id/secret invalid | Verify client credentials |
| `invalid_grant` | Authorization code invalid/expired | Request new code |
| `invalid_scope` | Requested scope not allowed | Check allowed_scopes |
| `unauthorized_client` | Client not allowed this grant type | Use correct grant type |
| `server_error` | Internal server error | Contact server admin |

### Authorization Errors

| Status | Error | Reason |
|--------|-------|--------|
| 403 | Insufficient permissions | Missing required scope |
| 403 | Admin role required | User is not admin |
| 403 | Forbidden | Permission denied |

### Error Response Examples

```json
// Missing token
{
  "error": "Authorization header missing"
}

// Invalid scope
{
  "error": "Insufficient permissions",
  "required_scope": "write:products",
  "user_scopes": ["read:products"]
}

// Invalid OAuth client
{
  "error": "invalid_client",
  "error_description": "Invalid client_id"
}
```

---

## 🔒 Security Best Practices Implemented

✅ **Token Validation:**
- JWT signature verification using secret key
- Token expiration checking
- Token type validation (access vs refresh)

✅ **Token Blacklisting:**
- Logout invalidates tokens
- Prevents token reuse after logout

✅ **Scope-based Authorization:**
- Fine-grained permission control
- Principle of least privilege

✅ **Role-based Access Control:**
- Role-based endpoint protection
- Admin-only operations

✅ **HTTPS Headers:**
- X-Content-Type-Options: nosniff
- X-Frame-Options: DENY
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security (when HTTPS enabled)

✅ **OAuth 2.0 Security:**
- Client secret verification
- Redirect URI validation
- State parameter for CSRF protection
- Authorization code expiration

✅ **Password Security:**
- Bcrypt hashing with salt
- Case-insensitive usernames

---

## 📊 Token Lifetime Configuration

```python
ACCESS_TOKEN_EXPIRATION = timedelta(hours=1)      # 1 hour
REFRESH_TOKEN_EXPIRATION = timedelta(days=7)      # 7 days
OAUTH_AUTH_CODE_EXPIRATION = timedelta(minutes=5) # 5 minutes
OAUTH_ACCESS_TOKEN_EXPIRATION = timedelta(hours=2)# 2 hours
```

---

## 🧪 Testing with Postman

Import the provided `Auth_OAuth_API.postman_collection.json` for quick testing:

1. **Set Variables:**
   - Login with a demo user (alice:alice123)
   - Copy `access_token` and `refresh_token` from response
   - Use in subsequent requests

2. **Test Protected Endpoints:**
   - Use the token in Authorization header
   - Check scope requirements

3. **Test OAuth Flows:**
   - Authorization Code: Request auth code, exchange for token
   - Client Credentials: Get token directly

---

**Created: April 2026 | Week 6 - Authentication & Authorization**
