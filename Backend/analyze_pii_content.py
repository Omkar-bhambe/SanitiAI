import re
import spacy
from typing import List, Dict, Any, Tuple
import logging

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

def extract_text_from_image(*args, **kwargs):
    """
    Placeholder function for OCR text extraction
    Replace this with actual OCR implementation using tesseract, easyocr, etc.
    """
    return ""

def load_dummy_data(file_path: str = "results/dummy_data.json") -> Dict:
    """Loads the dummy data dictionary from the specified JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("dummy_data", {})
    except FileNotFoundError:
        print(f"⚠️ Warning: Dummy data file not found at '{file_path}'.")
        return {}
    except json.JSONDecodeError:
        print(f"⚠️ Warning: Could not decode JSON from '{file_path}'.")
        return {}
    
def replace_numerical_pii(text: str, dummy_data: Dict) -> str:
    """Finds and replaces numerical PII with dummy values."""
    if not dummy_data:
        return text
    sanitized_text = text
    # MODIFIED: Added more patterns for replacement
    pii_patterns = {
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b',
        'account_number': r'\b\d{9,18}\b' # Generic bank account number
    }
    for pii_type, pattern in pii_patterns.items():
        if pii_type in dummy_data:
            dummy_value = dummy_data[pii_type]
            sanitized_text = re.sub(pattern, dummy_value, sanitized_text)
    return sanitized_text

def detect_pii_regex(text: str) -> List[Dict[str, Any]]:
    """
    Detect PII using regular expressions
    """
    pii_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'url': r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
    }
    
    detected_pii = []
    
    for pii_type, pattern in pii_patterns.items():
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            detected_pii.append({
                'type': pii_type,
                'text': match.group(),
                'start': match.start(),
                'end': match.end(),
                'confidence': 0.9
            })
    
    return detected_pii

class YoloSignatureDetector:
    """
    Placeholder class for YOLO signature detection
    Replace with actual YOLO model implementation
    """
    def __init__(self):
        self.model = None
    
    def detect(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Detect signatures in image
        Returns list of bounding boxes with confidence scores
        """
        # Placeholder implementation
        return []

class SpacyNer:
    """
    spaCy Named Entity Recognition for PII detection
    """
    def __init__(self):
        self.nlp = nlp
    
    def detect_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect named entities that could be PII
        """
        if not self.nlp:
            return []
        
        doc = self.nlp(text)
        entities = []
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY', 'CARDINAL']:
                entities.append({
                    'type': ent.label_.lower(),
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.8
                })
        
        return entities

def redact_boxes(image_path: str, boxes: List[Dict[str, Any]], output_path: str = None) -> str:
    """
    Redact regions in image given bounding boxes
    """
    try:
        from PIL import Image, ImageDraw
        
        # Open image
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)
        
        # Draw black rectangles over detected regions
        for box in boxes:
            if 'bbox' in box:
                x1, y1, x2, y2 = box['bbox']
                draw.rectangle([x1, y1, x2, y2], fill='black')
        
        # Save redacted image
        if not output_path:
            output_path = image_path.replace('.', '_redacted.')
        
        image.save(output_path)
        return output_path
        
    except ImportError:
        print("PIL/Pillow not installed. Install with: pip install Pillow")
        return image_path
    except Exception as e:
        print(f"Error redacting image: {e}")
        return image_path

def log_redaction(event_type: str, details: Dict[str, Any] = None) -> None:
    """
    Log redaction events
    """
    logging.info(f"Redaction event: {event_type}, Details: {details}")