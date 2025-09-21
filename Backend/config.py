

YOLO_SIGNATURE_MODEL_PATH = "backend/vision/signature_yolov5.pt"  # Path to your YOLOv5 signature model weights
SPACY_MODEL = "en_core_web_sm"  # spaCy model for NER
import os
from pathlib import Path

import pytesseract

# Get the base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Model paths
YOLO_SIGNATURE_MODEL_PATH = os.path.join(BASE_DIR, 'backend', 'vision', 'signature_yolov5.pt')


# Tesseract configuration
#TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  
pytesseract.pytesseract.tesseract_cmd = r"C:/Users/bhamb/Downloads/tesseract-ocr-w64-setup-5.5.0.20241111.exe"
# Other configurations
DEBUG = True
HOST = "0.0.0.0"
PORT = 8000

# Logging
LOG_LEVEL = "INFO"

# File upload settings
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}

print(f"Model path set to: {YOLO_SIGNATURE_MODEL_PATH}")
print(f"Model file exists: {os.path.exists(YOLO_SIGNATURE_MODEL_PATH)}")