import os
from datetime import timedelta
import secrets


class Config:
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_ENV') == 'development'

    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
    if not SECRET_KEY:
        if FLASK_ENV == 'production':
            raise ValueError("SECRET_KEY must be set in production!")
        SECRET_KEY = secrets.token_hex(32)  # 32 bytes = 64 character hex string

    # VM-specific settings
    VM_DEFAULT_MEMORY = 2048
    VM_DEFAULT_OS = 'Ubuntu'

    # Monitoring settings
    MONITORING_INTERVAL = timedelta(minutes=5)
    ALERT_THRESHOLD = 90  # CPU/Memory threshold for alerts

