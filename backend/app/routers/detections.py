"""
AquaGuard AI Router - Detections Query API Endpoint
Retrieves stored debris detection records and analytics.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models import Detection
from backend.app.schemas import DetectionResponse

router = APIRouter(tags=["Detections"])

@router.get("/detections", response_model=List[DetectionResponse])
def get_all_detections(db: Session = Depends(get_db)):
    detections = db.query(Detection).order_by(Detection.created_at.desc()).all()
    return detections

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db)):
    detections = db.query(Detection).all()
    
    category_counts = {}
    confidence_distribution = {"high": 0, "medium": 0, "low": 0}
    
    for d in detections:
        category_counts[d.object_class] = category_counts.get(d.object_class, 0) + 1
        
        if d.confidence >= 80.0:
            confidence_distribution["high"] += 1
        elif d.confidence >= 55.0:
            confidence_distribution["medium"] += 1
        else:
            confidence_distribution["low"] += 1
            
    return {
        "total_detections": len(detections),
        "category_counts": category_counts,
        "confidence_distribution": confidence_distribution
    }
