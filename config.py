import os
from datetime import timedelta

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-for-chandrakanta-crm'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///chandrakanta.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Authentication configuration
    USERNAME = os.environ.get('USERNAME') or 'admin'
    PASSWORD = os.environ.get('PASSWORD') or 'password'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Upload configuration
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'images', 'items')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    
    # Store information
    STORE_NAME = "Chandrakanta Store"
    STORE_ADDRESS = "Hewitt Road, Lucknow, UP"
    STORE_PHONE = "+91 00000 00000"
    STORE_EMAIL = "contact@chandrakantastore.com"
    
    # Allowed users
    ALLOWED_USERS = [USERNAME]  # Add more usernames if needed
