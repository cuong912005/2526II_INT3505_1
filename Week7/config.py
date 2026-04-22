import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    JSON_SORT_KEYS = False

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://username:password@cluster.mongodb.net/product_db?retryWrites=true&w=majority'
    )
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'product_db')

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb+srv://username:password@cluster.mongodb.net/product_db?retryWrites=true&w=majority'
    )
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'product_db')

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    MONGO_URI = os.getenv(
        'MONGO_URI',
        'mongodb://localhost:27017/product_db_test'
    )
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'product_db_test')

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()

# MongoDB Configuration
MONGO_CONFIG = {
    'host': os.getenv('MONGO_HOST', 'mongodb+srv'),
    'username': os.getenv('MONGO_USERNAME', 'username'),
    'password': os.getenv('MONGO_PASSWORD', 'password'),
    'cluster': os.getenv('MONGO_CLUSTER', 'cluster.mongodb.net'),
    'database': os.getenv('MONGO_DB_NAME', 'product_db'),
    'uri': os.getenv(
        'MONGO_URI',
        'mongodb+srv://cuong:<db_password>@cluster0.1os2cjc.mongodb.net/?appName=Cluster0'
    ),
    'connection_timeout': int(os.getenv('MONGO_CONNECTION_TIMEOUT', '5000')),
    'server_selection_timeout': int(os.getenv('MONGO_SERVER_SELECTION_TIMEOUT', '5000')),
}

# Application Configuration
APP_CONFIG = {
    'host': os.getenv('APP_HOST', '0.0.0.0'),
    'port': int(os.getenv('APP_PORT', '5000')),
    'debug': os.getenv('DEBUG', 'False').lower() == 'true',
    'environment': os.getenv('FLASK_ENV', 'development'),
}

# Pagination Configuration
PAGINATION_CONFIG = {
    'default_page_size': int(os.getenv('DEFAULT_PAGE_SIZE', '10')),
    'max_page_size': int(os.getenv('MAX_PAGE_SIZE', '100')),
}
