import os
from datetime import timedelta

class Config:
    # Security
    SECRET_KEY = 'your-super-secret-key-here'
    SESSION_TYPE = 'filesystem'
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///locksmith.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # External APIs
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    print(f"Loaded Google Maps API Key: {GOOGLE_MAPS_API_KEY}")
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # File Upload
    UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 