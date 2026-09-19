"""
AquaGuard AI - ONNX Model Exporter for NVIDIA Jetson & Edge Deployments
Exports PyTorch YOLOv11 weights to ONNX format optimized for TensorRT / DeepStream pipelines.
"""

import os
import sys

def export_to_onnx(weights_path="runs/detect/aquaguard_yolov11_sonar/weights/best.pt"):
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[Error] Ultralytics package not found. Install via: pip install ultralytics")
        sys.exit(1)
        
    if not os.path.exists(weights_path):
        weights_path = "yolo11n.pt"
        
    print(f"[AquaGuard ONNX Exporter] Loading model weights from {weights_path}...")
    model = YOLO(weights_path)
    
    print("[AquaGuard ONNX Exporter] Exporting model to ONNX format...")
    onnx_path = model.export(format="onnx", opset=12, dynamic=True, simplify=True)
    
    print(f"[AquaGuard ONNX Exporter] Export successful! ONNX model ready at: {onnx_path}")
    print("[NVIDIA Jetson Optimization Note]: Run 'trtexec --onnx=best.onnx --saveEngine=best.engine --fp16' on Jetson for max FPS performance.")
    return onnx_path

if __name__ == "__main__":
    export_to_onnx()
