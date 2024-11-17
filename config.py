import os
from datetime import timedelta


class Config:
    # SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # VM-specific settings
    VM_DEFAULT_MEMORY = 2048
    VM_DEFAULT_OS = 'Ubuntu'

    # Monitoring settings
    MONITORING_INTERVAL = timedelta(minutes=5)
    ALERT_THRESHOLD = 90  # CPU/Memory threshold for alerts
