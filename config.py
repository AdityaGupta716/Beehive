import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-this")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24

    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'beehive-secret-key')
    UPLOAD_FOLDER = 'static/uploads'
    PDF_THUMBNAIL_FOLDER = 'static/uploads/thumbnails/'
    
    # Database Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'beehive')
    
    # CORS Configuration
    _cors_origins_env = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
    )
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present"""
        if not Config.JWT_SECRET or Config.JWT_SECRET == "dev-secret-change-this":
            raise ValueError("Missing or insecure JWT_SECRET environment variable. Set JWT_SECRET in your .env for production.")
        return True
