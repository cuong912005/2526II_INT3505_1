# JWT + OAuth 2.0 Authentication System

## Structure

```
Week6/
├── main.py                 # Flask app + entry point
├── config.py               # Configuration, secrets, users DB
├── models.py               # TokenManager, OAuth2Manager
├── decorators.py           # require_auth, require_role, etc.
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py      # /auth/* endpoints
│   ├── oauth_routes.py     # /oauth/* endpoints
│   ├── protected_routes.py # Protected resources
│   └── public_routes.py    # Public endpoints
├── requirements.txt
└── jwt_auth_system.py      # Old (keep for reference)
```

## Quick Start

```bash
pip install -r requirements.txt
python main.py
```

## Demo Users

- **alice:alice123** (admin) - All scopes
- **bob:bob456** (user) - Read-only
- **charlie:charlie789** (moderator) - Read scopes

## OAuth 2.0 Clients

- **web-app-client** / web-app-secret-12345
- **mobile-app-client** / mobile-app-secret-67890
- **backend-service** / backend-service-secret-99999

## API Endpoints

### Authentication
- `POST /auth/login` - Get JWT tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout
- `GET /auth/info` - Get token info

### OAuth 2.0
- `GET /oauth/authorize` - Authorization endpoint
- `POST /oauth/token` - Token endpoint
- `POST /oauth/introspect` - Check token validity
- `POST /oauth/revoke` - Revoke token
- `GET /oauth/clients` - List registered clients
- `POST /oauth/login` - OAuth login
- `GET /oauth/login-page` - OAuth login page

### Protected Resources
- `GET /products` - List products (scope: read:products)
- `POST /products` - Create product (scope: write:products)
- `GET /admin/users` - List users (role: admin)
- `DELETE /admin/users/<id>` - Delete user (role: admin)
- `GET /orders` - Get orders (role: user)

### Public
- `GET /health` - Health check
