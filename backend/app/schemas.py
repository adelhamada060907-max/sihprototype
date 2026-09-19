"""
AquaGuard AI - Pydantic Request/Response Schemas
"""

from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

class TelemetrySchema(BaseModel):
    latitude: Optional[float] = 15.4989
    longitude: Optional[float] = 73.8278
    depth_meters: Optional[float] = 20.0
    sonar_heading_deg: Optional[float] = 45.0
    timestamp: Optional[str] = None

class DetectionBase(BaseModel):
    detection_id: str
    object_class: str
    confidence_percentage: float
    anomaly_score_pct: float
    bounding_box_coordinates: Any
    geospatial: Any

class DetectionResponse(BaseModel):
    id: int
    detection_code: str
    object_class: str
    confidence: float
    anomaly_score: float
    latitude: float
    longitude: float
    depth_meters: float
    bounding_box: Any
    created_at: datetime

    class Config:
        from_attributes = True

class DetectionPipelineResult(BaseModel):
    image_id: int
    filename: str
    file_url: str
    total_objects_detected: int
    detections: List[DetectionBase]
    preprocessing_status: str

class SonarImageResponse(BaseModel):
    id: int
    filename: str
    file_url: str
    uploaded_at: datetime
    latitude: float
    longitude: float
    depth_meters: float
    sonar_heading_deg: float
    detections_count: int

    class Config:
        from_attributes = True
