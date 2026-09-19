"""
AquaGuard AI - Side Scan Sonar Detection Engine (YOLOv11 Architecture Integration)
Handles model loading, sonar preprocessing, YOLO object detection inference,
false positive anomaly scoring, and geospatial coordinate translation.
"""

import os
import json
import numpy as np
import cv2

try:
    import torch
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

try:
    from ml.preprocessor import SonarPreprocessor
    from ml.false_positive_filter import FalsePositiveFilter
    from ml.geo_converter import SonarGeoConverter
except ImportError:
    from preprocessor import SonarPreprocessor
    from false_positive_filter import FalsePositiveFilter
    from geo_converter import SonarGeoConverter

CLASSES = ["ghost_net", "shipwreck", "pipe", "cylinder", "underwater_debris"]

class AquaGuardDetector:
    def __init__(self, model_path: str = None, confidence_threshold=0.35):
        self.confidence_threshold = confidence_threshold
        self.preprocessor = SonarPreprocessor()
        self.fp_filter = FalsePositiveFilter()
        self.geo_converter = SonarGeoConverter()
        
        self.model = None
        if ULTRALYTICS_AVAILABLE:
            candidate_paths = [
                model_path,
                os.path.join("runs", "detect", "aquaguard_yolov11_sonar", "weights", "best.pt"),
                os.path.join("ml", "weights", "best.pt"),
            ]
            for cp in candidate_paths:
                if cp and os.path.exists(cp):
                    try:
                        self.model = YOLO(cp)
                        print(f"[AquaGuard Detector] Loaded trained YOLOv11 model from {cp}")
                        break
                    except Exception as e:
                        print(f"[AquaGuard Detector] Failed loading model {cp}: {e}")
                
    def fallback_acoustic_detector(self, gray_img: np.ndarray, telemetry: dict) -> list:
        """
        Robust high-reflectivity acoustic highlight detector.
        Ensures prototype produces immediate bounding boxes on synthetic or real side-scan images
        even before custom GPU training is executed.
        """
        h, w = gray_img.shape
        detections = []
        
        # Threshold top acoustic reflectivity highlights
        _, thresh = cv2.threshold(gray_img, 185, 255, cv2.THRESH_BINARY)
        
        # Morphological close to bridge acoustic gaps
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        det_id = 1
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 80 or area > (w * h * 0.4):
                continue
                
            bx, by, bw, bh = cv2.boundingRect(cnt)
            
            # Avoid direct Nadir central vessel track
            nadir_center = w // 2
            if abs((bx + bw/2.0) - nadir_center) < (w * 0.07):
                continue
                
            # Class heuristic based on aspect ratio and geometry
            aspect = bw / (bh + 1e-5)
            if aspect > 2.5 or aspect < 0.4:
                class_id = 2 # Pipe
            elif area > 1200:
                class_id = 1 # Shipwreck
            elif area < 300:
                class_id = 3 # Cylinder
            elif aspect > 1.2 and area < 800:
                class_id = 0 # Ghost Net
            else:
                class_id = 4 # Underwater Debris
                
            class_name = CLASSES[class_id]
            conf = min(0.96, max(0.45, 0.55 + (area / 3000.0)))
            
            norm_bbox = [
                round((bx + bw / 2.0) / w, 6),
                round((by + bh / 2.0) / h, 6),
                round(bw / w, 6),
                round(bh / h, 6)
            ]
            
            # Run False Positive Anomaly Verification
            fp_result = self.fp_filter.compute_anomaly_score(gray_img, norm_bbox, conf, class_id)
            
            if not fp_result["is_verified"]:
                continue
                
            # Georeference detection
            geo_info = self.geo_converter.convert_bbox_to_georeference(norm_bbox, telemetry, w, h)
            
            detections.append({
                "detection_id": f"DET-{det_id:03d}",
                "object_class": class_name,
                "class_id": class_id,
                "confidence_percentage": round(conf * 100, 2),
                "anomaly_score_pct": fp_result["anomaly_score_pct"],
                "bounding_box_coordinates": {
                    "x_center": norm_bbox[0],
                    "y_center": norm_bbox[1],
                    "width": norm_bbox[2],
                    "height": norm_bbox[3],
                    "pixel_x": bx,
                    "pixel_y": by,
                    "pixel_width": bw,
                    "pixel_height": bh
                },
                "geospatial": geo_info
            })
            det_id += 1
            
        return detections

    def detect(self, image_input, telemetry: dict = None) -> dict:
        """
        Executes end-to-end detection pipeline on input image.
        Returns detailed JSON payload with preprocessing status, detections, and metrics.
        """
        if telemetry is None:
            telemetry = {
                "latitude": 15.4989,
                "longitude": 73.8278,
                "depth_meters": 20.0,
                "sonar_heading_deg": 45.0,
                "timestamp": "2026-09-06T00:00:00Z"
            }
            
        # 1. Preprocess Sonar Image
        prep_results = self.preprocessor.preprocess_sonar_image(image_input)
        enhanced_bgr = prep_results["enhanced_bgr"]
        gray_img = prep_results["enhanced"]
        
        detections = []
        
        # 2. Run Trained YOLOv11 if loaded
        if self.model is not None:
            try:
                results = self.model.predict(enhanced_bgr, conf=self.confidence_threshold, verbose=False)
                det_id = 1
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        cls_id = int(box.cls[0].cpu().numpy())
                        conf = float(box.conf[0].cpu().numpy())
                        xywh_norm = box.xywhn[0].cpu().numpy().tolist()
                        
                        class_name = CLASSES[cls_id] if cls_id < len(CLASSES) else "underwater_debris"
                        
                        # False positive filter
                        fp_result = self.fp_filter.compute_anomaly_score(gray_img, xywh_norm, conf, cls_id)
                        if not fp_result["is_verified"]:
                            continue
                            
                        # Georeferencing
                        geo_info = self.geo_converter.convert_bbox_to_georeference(xywh_norm, telemetry, 640, 640)
                        
                        detections.append({
                            "detection_id": f"YOLO-{det_id:03d}",
                            "object_class": class_name,
                            "class_id": cls_id,
                            "confidence_percentage": round(conf * 100, 2),
                            "anomaly_score_pct": fp_result["anomaly_score_pct"],
                            "bounding_box_coordinates": {
                                "x_center": round(xywh_norm[0], 6),
                                "y_center": round(xywh_norm[1], 6),
                                "width": round(xywh_norm[2], 6),
                                "height": round(xywh_norm[3], 6)
                            },
                            "geospatial": geo_info
                        })
                        det_id += 1
            except Exception as e:
                print(f"[AquaGuard Detector] YOLO inference error: {e}. Falling back to acoustic analysis.")
                detections = self.fallback_acoustic_detector(gray_img, telemetry)
        else:
            # Fallback heuristic detector
            detections = self.fallback_acoustic_detector(gray_img, telemetry)
            
        return {
            "total_objects_detected": len(detections),
            "detections": detections,
            "preprocessing_status": "Success",
            "telemetry_used": telemetry
        }


# Quick test interface
if __name__ == "__main__":
    detector = AquaGuardDetector()
    sample_img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    res = detector.detect(sample_img)
    print(f"[AquaGuard Detector] Detection finished. Found {res['total_objects_detected']} objects.")
