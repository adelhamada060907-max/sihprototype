"""
AquaGuard AI - SQLAlchemy Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class SonarImage(Base):
    __tablename__ = "sonar_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String)
    file_url = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Telemetry
    latitude = Column(Float, default=15.4989)
    longitude = Column(Float, default=73.8278)
    depth_meters = Column(Float, default=20.0)
    sonar_heading_deg = Column(Float, default=45.0)

    detections = relationship("Detection", back_populates="image", cascade="all, delete-orphan")


class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    detection_code = Column(String, index=True)
    image_id = Column(Integer, ForeignKey("sonar_images.id"))
    
    object_class = Column(String, index=True)
    confidence = Column(Float)
    anomaly_score = Column(Float)
    
    # Geospatial
    latitude = Column(Float)
    longitude = Column(Float)
    depth_meters = Column(Float)
    
    # Bounding Box JSON
    bounding_box = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("SonarImage", back_populates="detections")
