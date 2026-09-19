"""
AquaGuard AI - Report Generation Service
Exports detected debris records to standardized JSON and CSV formats.
"""

import os
import json
import csv
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.models import Detection
from backend.app.config import settings

def generate_json_report(db: Session) -> str:
    """Generates JSON report file and returns absolute file path."""
    detections = db.query(Detection).all()
    
    report_data = {
        "system": "AquaGuard AI - Autonomous Side Scan Sonar Marine Debris Detection",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_detections": len(detections),
        "records": []
    }
    
    for d in detections:
        report_data["records"].append({
            "detection_id": d.id,
            "detection_code": d.detection_code,
            "image_id": d.image_id,
            "object_type": d.object_class,
            "confidence_percentage": d.confidence,
            "anomaly_score_pct": d.anomaly_score,
            "latitude": d.latitude,
            "longitude": d.longitude,
            "depth_meters": d.depth_meters,
            "bounding_box": d.bounding_box,
            "timestamp": d.created_at.isoformat() + "Z"
        })
        
    filename = f"aquaguard_debris_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = os.path.join(settings.REPORTS_DIR, filename)
    
    with open(filepath, "w") as f:
        json.dump(report_data, f, indent=2)
        
    return filepath


def generate_csv_report(db: Session) -> str:
    """Generates CSV report file and returns absolute file path."""
    detections = db.query(Detection).all()
    
    filename = f"aquaguard_debris_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(settings.REPORTS_DIR, filename)
    
    fieldnames = [
        "detection_id", "detection_code", "image_id", "object_type",
        "confidence_pct", "anomaly_score_pct", "latitude", "longitude",
        "depth_meters", "bbox_x_center", "bbox_y_center", "bbox_width",
        "bbox_height", "timestamp"
    ]
    
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for d in detections:
            bbox = d.bounding_box or {}
            writer.writerow({
                "detection_id": d.id,
                "detection_code": d.detection_code,
                "image_id": d.image_id,
                "object_type": d.object_class,
                "confidence_pct": d.confidence,
                "anomaly_score_pct": d.anomaly_score,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "depth_meters": d.depth_meters,
                "bbox_x_center": bbox.get("x_center", 0.0),
                "bbox_y_center": bbox.get("y_center", 0.0),
                "bbox_width": bbox.get("width", 0.0),
                "bbox_height": bbox.get("height", 0.0),
                "timestamp": d.created_at.isoformat() + "Z"
            })
            
    return filepath
