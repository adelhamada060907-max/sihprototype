"""
AquaGuard AI Router - Detect API Endpoint
Runs AI preprocessing, object detection, false positive filter, and GIS mapping.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import SonarImage
from backend.app.services.detection_service import run_detection_on_image_record

router = APIRouter(tags=["Detection"])

@router.post("/detect")
def run_detection(
    image_id: int = Query(..., description="Database ID of the uploaded sonar image"),
    db: Session = Depends(get_db)
):
    image_record = db.query(SonarImage).filter(SonarImage.id == image_id).first()
    if not image_record:
        raise HTTPException(status_code=404, detail=f"Sonar image with ID {image_id} not found.")
        
    result = run_detection_on_image_record(db, image_record)
    return result
