"""
AquaGuard AI - YOLOv11 Training Script
Trains the YOLOv11 object detection model on the side scan sonar dataset.
"""

import os
import sys

def train_yolov11(dataset_yaml="datasets/dataset.yaml", epochs=25, img_size=640, batch_size=8):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[Error] Ultralytics package not found. Install via: pip install ultralytics")
        sys.exit(1)

    abs_yaml = os.path.abspath(dataset_yaml)
    if not os.path.exists(abs_yaml):
        print(f"[AquaGuard Train] Dataset configuration file not found at {abs_yaml}")
        print("[AquaGuard Train] Generating synthetic training dataset first...")
        from ml.synthetic_generator import generate_dataset_split
        generate_dataset_split()
        
    print(f"[AquaGuard Train] Initializing YOLOv11n architecture for Sonar Debris Detection...")
    model = YOLO("yolo11n.pt") # Loads pretrained YOLOv11 nano backbone
    
    print(f"[AquaGuard Train] Starting model training for {epochs} epochs...")
    results = model.train(
        data=abs_yaml,
        epochs=epochs,
        imgsz=img_size,
        batch=batch_size,
        name="aquaguard_yolov11_sonar",
        project="runs/detect",
        plots=True
    )
    
    saved_model_path = os.path.join("runs", "detect", "aquaguard_yolov11_sonar", "weights", "best.pt")
    print(f"[AquaGuard Train] Training completed successfully!")
    print(f"[AquaGuard Train] Best weights saved to: {os.path.abspath(saved_model_path)}")
    return saved_model_path

if __name__ == "__main__":
    train_yolov11()
