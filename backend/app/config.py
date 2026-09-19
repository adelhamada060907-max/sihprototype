"""
AquaGuard AI - FastAPI Backend Configuration
"""

import os
import shutil

class Settings:
    PROJECT_NAME: str = "AquaGuard AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    IS_VERCEL: bool = os.environ.get("VERCEL") == "1"
    WRITABLE_DIR: str = "/tmp" if IS_VERCEL else BASE_DIR

    UPLOAD_DIR: str = os.path.join(WRITABLE_DIR, "uploads")
    REPORTS_DIR: str = os.path.join(WRITABLE_DIR, "reports")
    SAMPLE_DATA_DIR: str = os.path.join(BASE_DIR, "sample_data")
    DATABASE_URL: str = f"sqlite:///{os.path.join(WRITABLE_DIR, 'aquaguard.db')}"

settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.SAMPLE_DATA_DIR, exist_ok=True)

if settings.IS_VERCEL:
    db_source = os.path.join(settings.BASE_DIR, "aquaguard.db")
    db_dest = os.path.join(settings.WRITABLE_DIR, "aquaguard.db")
    if os.path.exists(db_source) and not os.path.exists(db_dest):
        try:
            shutil.copyfile(db_source, db_dest)
        except Exception:
            pass

