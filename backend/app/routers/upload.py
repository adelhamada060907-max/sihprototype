"""
AquaGuard AI Router - Upload API Endpoint
Handles side-scan sonar image uploads and telemetry metadata ingestion.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import SonarImage
from backend.app.config import settings
from backend.app.schemas import SonarImageResponse

router = APIRouter(tags=["Upload"])

@router.post("/upload", response_model=SonarImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_sonar_image(
    file: UploadFile = File(...),
    latitude: float = Form(15.4989),
    longitude: float = Form(73.8278),
    depth_meters: float = Form(20.0),
    sonar_heading_deg: float = Form(45.0),
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files (PNG, JPG, TIFF) are accepted.")
        
    ext = os.path.splitext(file.filename)[1] or ".png"
    unique_filename = f"sonar_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    with open(filepath, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    file_url = f"/uploads/{unique_filename}"
    
    image_record = SonarImage(
        filename=unique_filename,
        filepath=filepath,
        file_url=file_url,
        latitude=latitude,
        longitude=longitude,
        depth_meters=depth_meters,
        sonar_heading_deg=sonar_heading_deg
    )
    
    db.add(image_record)
    db.commit()
    db.refresh(image_record)
    
    return SonarImageResponse(
        id=image_record.id,
        filename=image_record.filename,
        file_url=image_record.file_url,
        uploaded_at=image_record.uploaded_at,
        latitude=image_record.latitude,
        longitude=image_record.longitude,
        depth_meters=image_record.depth_meters,
        sonar_heading_deg=image_record.sonar_heading_deg,
        detections_count=0
    )
