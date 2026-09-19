"""
AquaGuard AI - FastAPI Backend Configuration
"""

import os

class Settings:
    PROJECT_NAME: str = "AquaGuard AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    REPORTS_DIR: str = os.path.join(BASE_DIR, "reports")
    SAMPLE_DATA_DIR: str = os.path.join(BASE_DIR, "sample_data")
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'aquaguard.db')}"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_DATA_DIR, exist_ok=True)
