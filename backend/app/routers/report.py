"""
AquaGuard AI Router - Report Export API Endpoints
Provides direct JSON & CSV downloads for SIH reporting and geospatial analytics.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.report_service import generate_json_report, generate_csv_report

router = APIRouter(tags=["Reports"])

@router.get("/report/json")
def download_json_report(db: Session = Depends(get_db)):
    json_path = generate_json_report(db)
    return FileResponse(
        path=json_path,
        filename="aquaguard_marine_debris_report.json",
        media_type="application/json"
    )

@router.get("/report/csv")
def download_csv_report(db: Session = Depends(get_db)):
    csv_path = generate_csv_report(db)
    return FileResponse(
        path=csv_path,
        filename="aquaguard_marine_debris_report.csv",
        media_type="text/csv"
    )
