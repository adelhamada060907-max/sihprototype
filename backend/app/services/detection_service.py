"""
AquaGuard AI - Detection Service
Bridge connecting FastAPI endpoints with ML preprocessing, inference, false positive reduction,
georeferencing, and SQLite persistence.
"""

import os
from sqlalchemy.orm import Session
from ml.detector import AquaGuardDetector
from backend.app.models import SonarImage, Detection

# Global instance of detection engine
detector_engine = AquaGuardDetector()

def run_detection_on_image_record(db: Session, image_record: SonarImage) -> dict:
    """Executes AI detection pipeline on an uploaded SonarImage database record."""
    telemetry = {
        "latitude": image_record.latitude,
        "longitude": image_record.longitude,
        "depth_meters": image_record.depth_meters,
        "sonar_heading_deg": image_record.sonar_heading_deg
    }
    
    # Run full ML pipeline
    ml_result = detector_engine.detect(image_record.filepath, telemetry)
    
    # Save detections to database
    db_detections = []
    for d in ml_result["detections"]:
        det_obj = Detection(
            detection_code=d["detection_id"],
            image_id=image_record.id,
            object_class=d["object_class"],
            confidence=d["confidence_percentage"],
            anomaly_score=d["anomaly_score_pct"],
            latitude=d["geospatial"]["latitude"],
            longitude=d["geospatial"]["longitude"],
            depth_meters=d["geospatial"]["depth_meters"],
            bounding_box=d["bounding_box_coordinates"]
        )
        db.add(det_obj)
        db_detections.append(det_obj)
        
    db.commit()
    
    return {
        "image_id": image_record.id,
        "filename": image_record.filename,
        "file_url": image_record.file_url,
        "total_objects_detected": len(ml_result["detections"]),
        "detections": ml_result["detections"],
        "preprocessing_status": ml_result["preprocessing_status"]
    }
