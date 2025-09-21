import re
import spacy
from typing import List, Dict, Any
import logging
from PIL import Image, ImageDraw, ImageFilter
import json
import os

# --- Setup & Model Loading ---

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("spaCy English model not found. Install with: python -m spacy download en_core_web_sm")
    nlp = None

# --- Core PII and Redaction Functions ---

def extract_text_with_boxes(image: Image.Image) -> List[Dict[str, Any]]:
    """
    Performs OCR on a PIL Image and returns a list of dictionaries,
    each containing text and its bounding box.
    """
    try:
        import pytesseract
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        results = []
        n_boxes = len(data['level'])
        for i in range(n_boxes):
            if int(data['conf'][i]) > 60 and data['text'][i].strip():
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                results.append({
                    'text': data['text'][i],
                    'box': (x, y, x + w, y + h)
                })
        return results
    except Exception as e:
        print(f"❌ OCR Error in extract_text_with_boxes: {e}")
        return []

def detect_pii_patterns(text: str) -> Dict[str, List[str]]:
    """Detects various PII patterns and returns them organized in a dictionary."""
    pii_patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'phone': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b',
        'account_number': r'\b\d{9,18}\b'
    }
    detected_pii = {}
    for pii_type, pattern in pii_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            detected_pii[pii_type] = matches
    return detected_pii

class YoloSignatureDetector:
    """Placeholder class for YOLO signature detection."""
    def __init__(self, model_path: str):
        self.model = None
        self.model_path = model_path
    def detect_signatures(self, image: Image.Image) -> List[List[int]]:
        return []

class SpacyNer:
    """spaCy Named Entity Recognition for PII detection."""
    def __init__(self, model_name: str):
        self.nlp = nlp
    def detect_pii(self, text: str) -> List[Dict[str, Any]]:
        if not self.nlp: return []
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'MONEY']:
                entities.append({'type': ent.label_.lower(), 'text': ent.text})
        return entities

def redact_boxes(image: Image.Image, boxes: List[tuple], output_path: str = None, method: str = 'blackbox') -> None:
    """Redacts regions on an in-memory PIL Image object given bounding boxes."""
    try:
        draw = ImageDraw.Draw(image)
        for box in boxes:
            if method == 'blackbox':
                draw.rectangle(box, fill='black')
            elif method == 'blur':
                cropped = image.crop(box)
                blurred = cropped.filter(ImageFilter.GaussianBlur(radius=10))
                image.paste(blurred, box)
    except Exception as e:
        print(f"Error redacting image: {e}")

def log_redaction(event_type: str, details: Any = None, box: tuple = None) -> None:
    """Log redaction events."""
    logging.info(f"Redaction Event: {event_type}, Details: {details}, Box: {box}")

# --- Dummy Data and Replacement Functions ---

def load_dummy_data(file_path: str = "backend/results/dummy_data.json") -> Dict:
    """
    Loads the first dummy profile from the JSON file and flattens it
    into the simple key-value structure needed for replacement.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        profiles = data.get("dummy_profiles")
        if not profiles or not isinstance(profiles, list):
            print("⚠️ Warning: 'dummy_profiles' key not found or is not a list in the JSON file.")
            return {}
            
        first_profile = profiles[0]
        
        dummy_values = {
            "phone": first_profile.get("contact", {}).get("phone_number"),
            "aadhaar": first_profile.get("identity", {}).get("aadhaar_number"),
            "credit_card": first_profile.get("financial", {}).get("credit_card_number")
        }
        
        return {k: v for k, v in dummy_values.items() if v is not None}
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"⚠️ Warning: Could not load dummy data from '{file_path}'.")
        return {}

def replace_numerical_pii(text: str, dummy_data: Dict) -> str:
    """
    Finds and replaces numerical PII in a text with corresponding values
    from the flattened dummy_data dictionary.
    """
    if not dummy_data:
        return text

    sanitized_text = text

    pii_patterns_to_replace = {
        'phone': r'\b(?:\+?91[-\s]?)?(?:\d{3}[-\s]?\d{3}[-\s]?\d{4}|\d{5}[-\s]?\d{5}|\d{10})\b',
        'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
        'aadhaar': r'\b\d{4}\s\d{4}\s\d{4}\b',
        'ssn': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'account_number': r'\b\d{9,18}\b'
    }

    for pii_type, pattern in pii_patterns_to_replace.items():
        if pii_type in dummy_data:
            dummy_value = dummy_data[pii_type]
            sanitized_text = re.sub(pattern, dummy_value, sanitized_text)
            
    return sanitized_text

# --- Main Orchestrator Function ---

def analyze_and_sanitize_document(file_content: bytes, content_type: str) -> Dict[str, Any]:
    """
    This is the main pipeline function that orchestrates the entire process.
    It takes a file's content, processes it, and returns a structured dictionary.
    """
    # Note: Requires text_extractor.py to be in the same project directory
    from text_extractor import extract_text
    original_text = extract_text(content_type, file_content)

    if not original_text.strip():
        return {
            "pii_count": 0,
            "pii_found": {},
            "original_text": original_text,
            "sanitized_text": "No text could be extracted from the document."
        }

    pii_data = detect_pii_patterns(original_text)
    pii_count = sum(len(items) for items in pii_data.values())

    dummy_values = load_dummy_data()
    sanitized_text = replace_numerical_pii(original_text, dummy_values)
    
    return {
        "pii_count": pii_count,
        "pii_found": pii_data,
        "original_text": original_text,
        "sanitized_text": sanitized_text
    }