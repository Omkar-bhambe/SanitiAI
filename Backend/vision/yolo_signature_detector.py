import torch
import os
from typing import Optional

class YoloSignatureDetector:
    def __init__(self, model_path: str):
        self.model_path = model_path
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLOv5 model with fallback options"""
        try:
            # Check if custom model file exists
            if os.path.exists(self.model_path):
                print(f"Loading custom model from: {self.model_path}")
                self.model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                          path=self.model_path, force_reload=False)
                print("Custom signature detection model loaded successfully!")
            else:
                print(f"Custom model not found at: {self.model_path}")
                print("Using default YOLOv5s model...")
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', 
                                          force_reload=False)
                print("Default YOLOv5s model loaded successfully!")
                
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to YOLOv5s model...")
            try:
                self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', 
                                          force_reload=False)
                print("Fallback model loaded successfully!")
            except Exception as fallback_error:
                print(f"Failed to load fallback model: {fallback_error}")
                raise Exception("Could not load any YOLOv5 model")
    
    def detect_signatures(self, image):
        """Detect signatures in the image"""
        if self.model is None:
            raise Exception("Model not loaded")
        
        try:
            # Run inference
            results = self.model(image)
            return results
        except Exception as e:
            print(f"Error during detection: {e}")
            return None
    
    def is_model_loaded(self) -> bool:
        """Check if model is successfully loaded"""
        return self.model is not None