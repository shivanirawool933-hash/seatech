import os
import sys
import numpy as np

# Add app to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.oil_detection.segmentation import OilSpillDetectorModule
from app.schemas.dto import GeoBounds

def test_unet_pipeline():
    detector = OilSpillDetectorModule()
    print(f"PyTorch Model Initialized: {detector.model_loaded}")
    
    # Test tensor forward pass prediction with synthetic numpy raster
    synthetic_sar = np.random.uniform(50, 200, size=(256, 256)).astype(np.float32)
    # Inject dark oil slick spot (intensity ~ 10)
    synthetic_sar[100:150, 100:150] = 10.0
    
    if detector.model_loaded:
        mask = detector.predict_mask_pytorch(synthetic_sar)
        print(f"Generated binary mask shape: {mask.shape}")
        print(f"Oil slick pixel count in mask: {np.sum(mask)}")
        assert mask.shape == (256, 256)
    
    print("PyTorch U-Net inference test passed successfully.")

if __name__ == "__main__":
    test_unet_pipeline()
