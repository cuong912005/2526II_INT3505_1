from flask import Flask
from datetime import datetime
from config import SECRET_KEY, REQUIRE_HTTPS
from routes import auth_bp, oauth_bp, protected_bp, public_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(oauth_bp)
app.register_blueprint(protected_bp)
app.register_blueprint(public_bp)


@app.before_request
def security_headers():
    pass


@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    if REQUIRE_HTTPS:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    return response


if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║  JWT Authentication + OAuth 2.0 Authorization Server Demo     ║
    ║                                                                ║
    ║  Week 6: Authentication & Authorization                       ║
    ╚════════════════════════════════════════════════════════════════╝
    
    Demo users:
    - alice:alice123 (admin, all scopes)
    - bob:bob456 (user, read-only scopes)
    - charlie:charlie789 (moderator, read scopes)
    
    Demo OAuth 2.0 Clients:
    - web-app-client / web-app-secret-12345
    - mobile-app-client / mobile-app-secret-67890
    - backend-service / backend-service-secret-99999
    """)
    
    print("\n🚀 Starting Flask server on http://localhost:5000\n")
    app.run(debug=True, host='localhost', port=5000)
