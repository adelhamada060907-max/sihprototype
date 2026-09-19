"""
AquaGuard AI - Synthetic Side Scan Sonar (SSS) Generator
Generates realistic acoustic side-scan sonar waterfall images with speckle noise,
seabed texture ripples, acoustic shadows behind underwater targets, and bounding box labels.
"""

import os
import random
import math
import json
import numpy as np
import cv2

CLASSES = ["ghost_net", "shipwreck", "pipe", "cylinder", "underwater_debris"]

def generate_seabed_background(width=640, height=640):
    """Generates acoustic seabed texture with nadir gap and sandy/rocky ripples."""
    # Base dark acoustic background
    background = np.zeros((height, width), dtype=np.float32)
    
    # 1. Acoustic propagation gradient (attenuation towards outer edges)
    x = np.linspace(-1, 1, width)
    y = np.linspace(-1, 1, height)
    xx, yy = np.meshgrid(x, y)
    
    # Central nadir zone (dark stripe down the middle of side-scan waterfall)
    nadir_width = int(width * 0.08)
    nadir_center = width // 2
    
    dist_from_nadir = np.abs(np.arange(width) - nadir_center).astype(np.float32)
    attenuation = np.exp(-dist_from_nadir / (width * 0.4))
    
    # Seabed micro-ripple simulation via sine waves and Perlin-like noise
    ripple_freq = random.uniform(0.05, 0.12)
    ripple_angle = random.uniform(-0.3, 0.3)
    
    ripples = np.sin(xx * 50 * ripple_freq + yy * 20 * ripple_angle) * 15.0
    
    # Rayleigh speckle noise (characteristic of acoustic sonar returns)
    rayleigh_noise = np.random.rayleigh(scale=18.0, size=(height, width)).astype(np.float32)
    
    sonar_img = (60.0 + ripples + rayleigh_noise) * attenuation[np.newaxis, :]
    
    # Render nadir gap (water column underneath vessel)
    sonar_img[:, nadir_center - nadir_width:nadir_center + nadir_width] *= 0.15
    
    # Add nadir acoustic return boundaries (bright highlight line at sea floor contact)
    sonar_img[:, nadir_center - nadir_width] += 40.0
    sonar_img[:, nadir_center + nadir_width] += 40.0
    
    return np.clip(sonar_img, 0, 255).astype(np.uint8)


def render_ghost_net(img, x, y, size):
    """Renders irregular tangled acoustic highlight of a ghost fishing net."""
    h, w = img.shape
    net_mask = np.zeros((h, w), dtype=np.uint8)
    
    # Draw tangled polyline filaments
    num_strands = random.randint(6, 12)
    points = []
    for _ in range(num_strands):
        px = int(x + random.uniform(-size*0.4, size*0.4))
        py = int(y + random.uniform(-size*0.4, size*0.4))
        points.append((px, py))
        
    for i in range(len(points) - 1):
        cv2.line(net_mask, points[i], points[i+1], 220, thickness=random.randint(2, 4))
        
    # Dilate slightly for mesh look
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    net_mask = cv2.dilate(net_mask, kernel, iterations=1)
    return net_mask


def render_shipwreck(img, x, y, size):
    """Renders high-reflectivity acoustic hull structure of a sunken ship."""
    h, w = img.shape
    wreck_mask = np.zeros((h, w), dtype=np.uint8)
    
    length = int(size * 1.2)
    width = int(size * 0.5)
    angle = random.randint(0, 180)
    
    rect = ((float(x), float(y)), (float(length), float(width)), float(angle))
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    
    cv2.fillPoly(wreck_mask, [box], 235)
    cv2.drawContours(wreck_mask, [box], 0, 255, 3)
    return wreck_mask


def render_pipe(img, x, y, size):
    """Renders linear underwater pipeline acoustic highlight."""
    h, w = img.shape
    pipe_mask = np.zeros((h, w), dtype=np.uint8)
    
    length = int(size * 1.5)
    thickness = random.randint(4, 8)
    angle = random.choice([15, 30, 45, 135, 160])
    
    rad = math.radians(angle)
    dx = int((length / 2) * math.cos(rad))
    dy = int((length / 2) * math.sin(rad))
    
    pt1 = (max(0, min(w-1, x - dx)), max(0, min(h-1, y - dy)))
    pt2 = (max(0, min(w-1, x + dx)), max(0, min(h-1, y + dy)))
    
    cv2.line(pipe_mask, pt1, pt2, 240, thickness=thickness)
    return pipe_mask


def render_cylinder(img, x, y, size):
    """Renders acoustic reflection of an underwater tank/cylinder."""
    h, w = img.shape
    cyl_mask = np.zeros((h, w), dtype=np.uint8)
    r = int(size * 0.35)
    cv2.circle(cyl_mask, (x, y), r, 230, -1)
    cv2.circle(cyl_mask, (x, y), r, 255, 2)
    return cyl_mask


def render_debris(img, x, y, size):
    """Renders arbitrary anthropogenic debris."""
    h, w = img.shape
    deb_mask = np.zeros((h, w), dtype=np.uint8)
    pts = np.array([
        [x - int(size*0.3), y - int(size*0.2)],
        [x + int(size*0.3), y - int(size*0.4)],
        [x + int(size*0.4), y + int(size*0.3)],
        [x - int(size*0.2), y + int(size*0.4)]
    ], np.int32)
    cv2.fillPoly(deb_mask, [pts], 215)
    return deb_mask


def generate_synthetic_sonar_sample(img_id, output_img_dir, output_label_dir, width=640, height=640):
    """Generates a synthetic sonar image along with YOLO annotations and telemetry metadata."""
    sonar_img = generate_seabed_background(width, height)
    
    # Choose 1 to 3 objects to embed
    num_objects = random.randint(1, 3)
    labels = []
    
    for _ in range(num_objects):
        class_id = random.randint(0, len(CLASSES) - 1)
        class_name = CLASSES[class_id]
        
        # Position object away from direct center nadir gap
        if random.random() > 0.5:
            cx = random.randint(40, width // 2 - 50)
            shadow_dir = -1  # Acoustic shadow projects towards port edge
        else:
            cx = random.randint(width // 2 + 50, width - 40)
            shadow_dir = 1   # Acoustic shadow projects towards starboard edge
            
        cy = random.randint(80, height - 80)
        obj_size = random.randint(35, 75)
        
        # Render highlight mask
        if class_id == 0:
            target_mask = render_ghost_net(sonar_img, cx, cy, obj_size)
        elif class_id == 1:
            target_mask = render_shipwreck(sonar_img, cx, cy, obj_size)
        elif class_id == 2:
            target_mask = render_pipe(sonar_img, cx, cy, obj_size)
        elif class_id == 3:
            target_mask = render_cylinder(sonar_img, cx, cy, obj_size)
        else:
            target_mask = render_debris(sonar_img, cx, cy, obj_size)
            
        # Render acoustic shadow behind target (extending away from vessel track)
        shadow_length = int(obj_size * random.uniform(1.2, 2.5))
        shadow_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Acoustic rays cast shadows behind bright returns
        for sy in range(max(0, cy - obj_size//2), min(height, cy + obj_size//2)):
            sx_start = cx
            sx_end = max(0, min(width - 1, cx + shadow_dir * shadow_length))
            cv2.line(shadow_mask, (sx_start, sy), (sx_end, sy), 255, thickness=2)
            
        # Apply shadow (darkening sonar returns behind target)
        sonar_img[shadow_mask > 0] = (sonar_img[shadow_mask > 0] * 0.15).astype(np.uint8)
        
        # Add target bright acoustic return
        sonar_img = np.maximum(sonar_img, target_mask)
        
        # Calculate bounding box (including target and immediate highlight zone)
        nonzero_y, nonzero_x = np.nonzero(target_mask)
        if len(nonzero_x) > 0 and len(nonzero_y) > 0:
            min_x, max_x = np.min(nonzero_x), np.max(nonzero_x)
            min_y, max_y = np.min(nonzero_y), np.max(nonzero_y)
            
            # Normalize to YOLO format (x_center, y_center, width, height)
            bbox_w = (max_x - min_x + 10) / width
            bbox_h = (max_y - min_y + 10) / height
            bbox_x = (min_x + max_x) / (2.0 * width)
            bbox_y = (min_y + max_y) / (2.0 * height)
            
            # Clamp to [0, 1]
            bbox_x = max(0.01, min(0.99, bbox_x))
            bbox_y = max(0.01, min(0.99, bbox_y))
            bbox_w = max(0.02, min(0.95, bbox_w))
            bbox_h = max(0.02, min(0.95, bbox_h))
            
            labels.append(f"{class_id} {bbox_x:.6f} {bbox_y:.6f} {bbox_w:.6f} {bbox_h:.6f}")
            
    # Save Image
    img_filename = f"sonar_{img_id:04d}.png"
    img_path = os.path.join(output_img_dir, img_filename)
    cv2.imwrite(img_path, sonar_img)
    
    # Save Label TXT
    label_filename = f"sonar_{img_id:04d}.txt"
    label_path = os.path.join(output_label_dir, label_filename)
    with open(label_path, "w") as f:
        f.write("\n".join(labels))
        
    # Generate metadata file (telemetry for GIS conversion testing)
    meta = {
        "image_id": img_filename,
        "latitude": 15.4989 + random.uniform(-0.05, 0.05),
        "longitude": 73.8278 + random.uniform(-0.05, 0.05),
        "depth_meters": round(random.uniform(12.5, 45.0), 2),
        "sonar_heading_deg": round(random.uniform(0.0, 360.0), 1),
        "range_resolution_m": 0.1
    }
    meta_path = os.path.join(output_img_dir, f"sonar_{img_id:04d}.json")
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
        
    return img_path, label_path


def generate_dataset_split(base_dir="datasets", count_train=30, count_val=10):
    """Creates directory tree and generates synthetic side scan sonar dataset."""
    train_img_dir = os.path.join(base_dir, "images", "train")
    val_img_dir = os.path.join(base_dir, "images", "val")
    train_lbl_dir = os.path.join(base_dir, "labels", "train")
    val_lbl_dir = os.path.join(base_dir, "labels", "val")
    
    for d in [train_img_dir, val_img_dir, train_lbl_dir, val_lbl_dir]:
        os.makedirs(d, exist_ok=True)
        
    print(f"[AquaGuard ML] Generating {count_train} synthetic training samples...")
    for i in range(1, count_train + 1):
        generate_synthetic_sonar_sample(i, train_img_dir, train_lbl_dir)
        
    print(f"[AquaGuard ML] Generating {count_val} synthetic validation samples...")
    for i in range(count_train + 1, count_train + count_val + 1):
        generate_synthetic_sonar_sample(i, val_img_dir, val_lbl_dir)
        
    # Write dataset.yaml configuration file for YOLOv11
    dataset_yaml = f"""# AquaGuard AI - Side Scan Sonar Dataset Config
path: {os.path.abspath(base_dir)}
train: images/train
val: images/val

names:
  0: ghost_net
  1: shipwreck
  2: pipe
  3: cylinder
  4: underwater_debris
"""
    yaml_path = os.path.join(base_dir, "dataset.yaml")
    with open(yaml_path, "w") as f:
        f.write(dataset_yaml)
        
    print(f"[AquaGuard ML] Dataset generation complete. Config saved to {yaml_path}")


if __name__ == "__main__":
    generate_dataset_split()
