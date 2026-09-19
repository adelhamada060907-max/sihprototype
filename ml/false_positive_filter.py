"""
AquaGuard AI - False Positive Reduction & Anomaly Verification System
Eliminates false positive detections (rocks, sand ridges, noise spikes) by analyzing:
1. Highlight intensity gradient & contrast.
2. Trailing acoustic shadow presence (shadow-to-bright highlight ratio).
3. Bounding box aspect ratio and surface area constraints.
4. Composite Anomaly Score (0 - 100%).
"""

import numpy as np
import cv2

CLASSES = ["ghost_net", "shipwreck", "pipe", "cylinder", "underwater_debris"]

class FalsePositiveFilter:
    def __init__(self, min_anomaly_threshold=40.0, max_aspect_ratio=6.0):
        self.min_anomaly_threshold = min_anomaly_threshold
        self.max_aspect_ratio = max_aspect_ratio

    def evaluate_shadow_ratio(self, gray_img: np.ndarray, bbox_xywh_pixel: tuple) -> float:
        """
        Analyzes the acoustic shadow region trailing the bright highlight return.
        Sonar physics dictating man-made objects project an acoustic shadow behind them away from nadir.
        Returns shadow score between 0.0 and 1.0.
        """
        h, w = gray_img.shape
        x, y, bw, bh = bbox_xywh_pixel
        
        # Define shadow sampling zone adjacent to the bounding box (extending horizontally)
        shadow_w = int(bw * 1.5)
        
        # Check port side vs starboard side relative position
        if x > w // 2:
            # Starboard: shadow extends rightward
            sx1 = min(w - 1, x + bw)
            sx2 = min(w, x + bw + shadow_w)
        else:
            # Port: shadow extends leftward
            sx1 = max(0, x - shadow_w)
            sx2 = max(0, x)
            
        sy1 = max(0, y)
        sy2 = min(h, y + bh)
        
        if sx2 <= sx1 or sy2 <= sy1:
            return 0.5 # Default moderate score if near boundary
            
        shadow_region = gray_img[sy1:sy2, sx1:sx2]
        bbox_region = gray_img[max(0, y):min(h, y+bh), max(0, x):min(w, x+bw)]
        
        if shadow_region.size == 0 or bbox_region.size == 0:
            return 0.5
            
        mean_shadow = float(np.mean(shadow_region))
        mean_highlight = float(np.mean(bbox_region))
        
        # High contrast between bright highlight return and dark shadow region indicates genuine physical object
        if mean_highlight + 1e-5 > 0:
            contrast_ratio = max(0.0, (mean_highlight - mean_shadow) / mean_highlight)
        else:
            contrast_ratio = 0.0
            
        return min(1.0, contrast_ratio * 1.2)

    def compute_anomaly_score(self, gray_img: np.ndarray, bbox_norm: list, raw_confidence: float, class_id: int) -> dict:
        """
        Computes composite Anomaly Score (0 - 100%) and decides whether to keep or filter detection.
        bbox_norm: [x_center, y_center, width, height] normalized to [0, 1].
        """
        h, w = gray_img.shape
        bx_c, by_c, bw_n, bh_n = bbox_norm
        
        px_w = int(bw_n * w)
        px_h = int(bh_n * h)
        px_x = int((bx_c - bw_n / 2.0) * w)
        px_y = int((by_c - bh_n / 2.0) * h)
        
        px_x = max(0, min(w - 1, px_x))
        px_y = max(0, min(h - 1, px_y))
        px_w = max(5, min(w - px_x, px_w))
        px_h = max(5, min(h - px_y, px_h))
        
        # 1. Aspect Ratio check
        aspect_ratio = max(px_w, px_h) / (min(px_w, px_h) + 1e-5)
        aspect_score = 1.0 if aspect_ratio <= self.max_aspect_ratio else max(0.2, 1.0 - (aspect_ratio - self.max_aspect_ratio)*0.15)
        
        # 2. Size check (filter out tiny single-pixel noise spikes or giant background gradients)
        area_pct = (px_w * px_h) / (w * h)
        if area_pct < 0.0005 or area_pct > 0.6:
            size_score = 0.2
        else:
            size_score = 1.0
            
        # 3. Acoustic shadow analysis
        shadow_score = self.evaluate_shadow_ratio(gray_img, (px_x, px_y, px_w, px_h))
        
        # 4. Highlight Intensity Variance (artificial man-made debris has distinct geometric boundaries)
        roi = gray_img[px_y:px_y+px_h, px_x:px_x+px_w]
        std_dev = float(np.std(roi)) if roi.size > 0 else 10.0
        texture_score = min(1.0, std_dev / 40.0)
        
        # Weighted Anomaly Score formula
        composite_score = (
            (raw_confidence * 0.35) +
            (shadow_score * 0.30) +
            (aspect_score * 0.15) +
            (size_score * 0.10) +
            (texture_score * 0.10)
        ) * 100.0
        
        anomaly_score = round(max(0.0, min(100.0, composite_score)), 2)
        is_verified = anomaly_score >= self.min_anomaly_threshold
        
        return {
            "anomaly_score_pct": anomaly_score,
            "is_verified": is_verified,
            "metrics": {
                "shadow_score": round(shadow_score, 3),
                "aspect_ratio": round(aspect_ratio, 2),
                "area_pct": round(area_pct * 100, 3),
                "raw_confidence": round(raw_confidence, 3)
            }
        }
