"""
AquaGuard AI - Dataset Pipeline & Acquisition Utility
Documentation and helper functions for acquiring real-world side-scan sonar datasets
and converting annotations from PascalVOC/COCO XML/JSON formats to YOLO format.

DATASET SOURCES:
1. Marine Debris Sonar Dataset (Kaggle / GitHub marine-debris-sonar)
2. Seabed Object Detection Side-Scan Sonar Dataset (Roboflow Universe)
3. Seabed Object Sonar Dataset (Shipwrecks, Drowning, Debris)
"""

import os
import json
import xml.etree.ElementTree as ET

def convert_voc_xml_to_yolo(xml_path: str, classes_list: list) -> str:
    """Converts a PascalVOC XML annotation file to YOLO format string."""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    size = root.find('size')
    w = float(size.find('width').text)
    h = float(size.find('height').text)
    
    yolo_lines = []
    for obj in root.findall('object'):
        cls_name = obj.find('name').text
        if cls_name not in classes_list:
            continue
        cls_id = classes_list.index(cls_name)
        
        xmlbox = obj.find('bndbox')
        xmin = float(xmlbox.find('xmin').text)
        xmax = float(xmlbox.find('xmax').text)
        ymin = float(xmlbox.find('ymin').text)
        ymax = float(xmlbox.find('ymax').text)
        
        x_center = (xmin + xmax) / (2.0 * w)
        y_center = (ymin + ymax) / (2.0 * h)
        bw = (xmax - xmin) / w
        bh = (ymax - ymin) / h
        
        yolo_lines.append(f"{cls_id} {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f}")
        
    return "\n".join(yolo_lines)

def print_dataset_acquisition_instructions():
    """Prints acquisition commands and guidance for downloading real sonar datasets."""
    instructions = """
=====================================================================
AquaGuard AI - Side Scan Sonar Dataset Acquisition Guide
=====================================================================

1. Roboflow Side-Scan Sonar Datasets:
   Install Roboflow CLI:
   $ pip install roboflow
   
   Download side scan sonar marine debris dataset in YOLOv8 format:
   python -c "
   from roboflow import Roboflow
   rf = Roboflow(api_key='YOUR_API_KEY')
   project = rf.workspace('marine-debris').project('side-scan-sonar-debris')
   dataset = project.version(1).download('yolov8')
   "

2. Kaggle Marine Debris Sonar Datasets:
   $ kaggle datasets download -d acoustic-sonar/marine-debris-sss
   $ unzip marine-debris-sss.zip -d datasets/

3. Directory Structure Expectation:
   datasets/
    ├── dataset.yaml
    ├── images/
    │    ├── train/
    │    └── val/
    └── labels/
         ├── train/
         └── val/
=====================================================================
"""
    print(instructions)

if __name__ == "__main__":
    print_dataset_acquisition_instructions()
