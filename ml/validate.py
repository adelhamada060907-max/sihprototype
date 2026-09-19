"""
AquaGuard AI - Model Validation & Performance Metrics Evaluation Script
Evaluates trained YOLOv11 detector on sonar test set:
- Precision
- Recall
- mAP@50
- mAP@50-95
"""

import os
import sys

def validate_model(weights_path="runs/detect/aquaguard_yolov11_sonar/weights/best.pt", dataset_yaml="datasets/dataset.yaml"):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[Error] Ultralytics package not found. Install via: pip install ultralytics")
        sys.exit(1)
        
    if not os.path.exists(weights_path):
        print(f"[AquaGuard Validate] Custom weights not found at {weights_path}, using base yolo11n.pt")
        weights_path = "yolo11n.pt"
        
    model = YOLO(weights_path)
    metrics = model.val(data=dataset_yaml, split="val")
    
    print("\n==================================================")
    print("      AquaGuard AI - Detection Validation Results")
    print("==================================================")
    print(f" Precision (P)    : {metrics.box.mp:.4f} ({metrics.box.mp*100:.2f}%)")
    print(f" Recall (R)       : {metrics.box.mr:.4f} ({metrics.box.mr*100:.2f}%)")
    print(f" mAP@50           : {metrics.box.map50:.4f} ({metrics.box.map50*100:.2f}%)")
    print(f" mAP@50-95        : {metrics.box.map:.4f} ({metrics.box.map*100:.2f}%)")
    print("==================================================\n")
    
    return {
        "precision": metrics.box.mp,
        "recall": metrics.box.mr,
        "mAP50": metrics.box.map50,
        "mAP50_95": metrics.box.map
    }

if __name__ == "__main__":
    validate_model()
