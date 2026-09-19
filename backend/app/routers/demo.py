"""
AquaGuard AI Router - SIH Hackathon Demo Seed API
Pre-generates realistic side scan sonar samples and populates database for instant 1-click demonstration.
"""

import os
import random
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import SonarImage, Detection
from backend.app.config import settings
from ml.synthetic_generator import generate_synthetic_sonar_sample
from backend.app.services.detection_service import run_detection_on_image_record

router = APIRouter(tags=["Demo"])

@router.post("/demo/seed")
def seed_demo_data(db: Session = Depends(get_db)):
    """Pre-generates 5 sample side-scan sonar images and populates AI detections."""
    # Clear existing demo data
    db.query(Detection).delete()
    db.query(SonarImage).delete()
    db.commit()
    
    locations = [
        {"name": "Goa Coast Offshore", "lat": 15.4989, "lon": 73.8278, "depth": 22.5, "heading": 45.0},
        {"name": "Mumbai Harbour Trench", "lat": 18.9438, "lon": 72.8358, "depth": 35.0, "heading": 120.0},
        {"name": "Kochi Port Channel", "lat": 9.9674, "lon": 76.2428, "depth": 18.0, "heading": 210.0},
        {"name": "Visakhapatnam Shelf", "lat": 17.6868, "lon": 83.2185, "depth": 42.0, "heading": 90.0},
        {"name": "Chennai Outer Anchorage", "lat": 13.0827, "lon": 80.2707, "depth": 28.5, "heading": 180.0}
    ]
    
    created_records = []
    
    for i, loc in enumerate(locations, 1):
        lbl_dir = os.path.join(settings.SAMPLE_DATA_DIR, "labels")
        os.makedirs(lbl_dir, exist_ok=True)
        
        # Generate synthetic sonar image
        img_path, _ = generate_synthetic_sonar_sample(i, settings.SAMPLE_DATA_DIR, lbl_dir)
        img_filename = os.path.basename(img_path)
        
        # Also copy image to upload directory for static web serving
        upload_path = os.path.join(settings.UPLOAD_DIR, img_filename)
        with open(img_path, "rb") as src, open(upload_path, "wb") as dst:
            dst.write(src.read())
            
        file_url = f"/uploads/{img_filename}"
        
        image_record = SonarImage(
            filename=img_filename,
            filepath=upload_path,
            file_url=file_url,
            latitude=loc["lat"],
            longitude=loc["lon"],
            depth_meters=loc["depth"],
            sonar_heading_deg=loc["heading"]
        )
        db.add(image_record)
        db.commit()
        db.refresh(image_record)
        
        # Run detection pipeline
        det_res = run_detection_on_image_record(db, image_record)
        created_records.append(det_res)
        
    return {
        "status": "Success",
        "message": f"Successfully seeded {len(created_records)} side scan sonar demo datasets with live AI detections.",
        "samples": created_records
    }
