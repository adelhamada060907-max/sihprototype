"""
AquaGuard AI - Side Scan Sonar (SSS) Image Preprocessing Pipeline
Provides noise suppression (speckle reduction via median/Gaussian/bilateral filters),
acoustic contrast enhancement (CLAHE, histogram equalization), and normalization.
"""

import cv2
import numpy as np

class SonarPreprocessor:
    def __init__(self, target_size=(640, 640), clip_limit=3.0, tile_grid_size=(8, 8)):
        self.target_size = target_size
        self.clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        
    def reduce_speckle_noise(self, image: np.ndarray, method="adaptive") -> np.ndarray:
        """Removes speckle noise characteristic of side-scan acoustic returns."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        if method == "median":
            # 5x5 Median Filter
            denoised = cv2.medianBlur(gray, 5)
        elif method == "gaussian":
            # Gaussian blur preserving background trends
            denoised = cv2.GaussianBlur(gray, (5, 5), 1.2)
        elif method == "adaptive":
            # Edge-preserving Bilateral Filter to maintain target highlights and shadows
            denoised = cv2.bilateralFilter(gray, d=7, sigmaColor=75, sigmaSpace=75)
        else:
            denoised = gray
            
        return denoised

    def enhance_contrast(self, image: np.ndarray, method="clahe") -> np.ndarray:
        """Enhances acoustic highlights and shadow boundaries against low-contrast seabed background."""
        if method == "clahe":
            enhanced = self.clahe.apply(image)
        elif method == "hist_eq":
            enhanced = cv2.equalizeHist(image)
        else:
            enhanced = image
            
        return enhanced

    def normalize_dynamic_range(self, image: np.ndarray) -> np.ndarray:
        """Min-Max normalizes pixel values to [0, 255]."""
        normalized = cv2.normalize(image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        return normalized.astype(np.uint8)

    def preprocess_sonar_image(self, image_input) -> dict:
        """
        Executes full preprocessing pipeline on input image (filepath or numpy array).
        Returns dictionary containing intermediate and final enhanced images.
        """
        if isinstance(image_input, str):
            raw = cv2.imread(image_input)
            if raw is None:
                raise ValueError(f"Could not read image from path: {image_input}")
        elif isinstance(image_input, np.ndarray):
            raw = image_input
        else:
            raise TypeError("Image input must be a file path string or numpy array.")

        # Ensure 3-channel standard RGB output for model input and 1-channel for processing
        if len(raw.shape) == 3:
            gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
        else:
            gray = raw.copy()
            raw = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

        # 1. Noise Reduction
        denoised = self.reduce_speckle_noise(gray, method="adaptive")
        
        # 2. Contrast Enhancement
        enhanced = self.enhance_contrast(denoised, method="clahe")
        
        # 3. Dynamic Range Normalization
        normalized = self.normalize_dynamic_range(enhanced)
        
        # 4. Resizing & RGB formatting for Deep Learning model
        resized_enhanced = cv2.resize(normalized, self.target_size, interpolation=cv2.INTER_LINEAR)
        rgb_enhanced = cv2.cvtColor(resized_enhanced, cv2.COLOR_GRAY2BGR)
        
        # 5. Tensor float32 normalized [0.0, 1.0]
        tensor = resized_enhanced.astype(np.float32) / 255.0
        tensor = np.expand_dims(tensor, axis=0) # Shape: (1, H, W)
        tensor = np.repeat(tensor, 3, axis=0)   # Shape: (3, H, W)
        tensor = np.expand_dims(tensor, axis=0) # Shape: (1, 3, H, W)

        return {
            "raw_original": raw,
            "gray": gray,
            "denoised": denoised,
            "enhanced": resized_enhanced,
            "enhanced_bgr": cv2.cvtColor(resized_enhanced, cv2.COLOR_GRAY2BGR),
            "rgb_tensor": tensor
        }


# Quick test interface
if __name__ == "__main__":
    preprocessor = SonarPreprocessor()
    test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    res = preprocessor.preprocess_sonar_image(test_img)
    print(f"[AquaGuard Preprocessor] Preprocessing successful! Tensor shape: {res['rgb_tensor'].shape}")
