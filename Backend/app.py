# app.py

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import logging
from PIL import Image

# Import your existing modules
try:
    # NOTE: Ensure your analyze_pii_content.py has these functions
    from pii_analyzer import (
        extract_text_with_boxes, 
        detect_pii_regex, 
        YoloSignatureDetector, 
        SpacyNer, 
        redact_boxes, 
        log_redaction
    )
    MODULES_LOADED = True
except ImportError as e:
    print(f"Warning: Some modules not found. Please ensure pii_analyzer.py exists. Details: {e}")
    MODULES_LOADED = False


app = Flask(__name__)
CORS(app)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx', 'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 16MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Load Models on Startup ---
# This is more efficient than loading them on each request.
if MODULES_LOADED:
    try:
        # NOTE: Update model paths if they are in a config file
        signature_detector = YoloSignatureDetector("path/to/yolo_model.pt")
        spacy_ner = SpacyNer("en_core_web_lg")
        print("✅ AI Models would be loaded here.")
    except Exception as e:
        print(f"⚠️ Error loading AI models on startup: {e}")
else:
    print("⚠️ Running with dummy functions. AI processing will be skipped.")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ===============================================================
# === CHANGE 1: SERVE THE WEB FRONTEND INSTEAD OF JSON
# ===============================================================
@app.route('/')
def home():
    """Serves the main web page for the document scanner."""
    return render_template('index.html')

# ===============================================================
# === CHANGE 2: ADD A ROUTE TO SERVE PROCESSED (REDACTED) IMAGES
# ===============================================================
@app.route('/processed/<filename>')
def get_processed_file(filename):
    """Serves a processed file from the processed directory."""
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

# --- API Routes (Unchanged) ---
@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.route('/api/docs')
def api_docs():
    # This documentation endpoint remains as you designed it.
    return jsonify({"message": "API docs are available here..."})

@app.route('/api/health')
def health_check():
    # This health check endpoint remains as you designed it.
    return jsonify({"status": "healthy"})

# --- File Upload Route (Unchanged) ---
@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads"""
    # This upload logic remains as you designed it.
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filename}")
        if MODULES_LOADED: log_redaction("file_upload", {"filename": filename})
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename,
        }), 200
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

# ===============================================================
# === CHANGE 3: REFINE THE PROCESSING LOGIC
# ===============================================================
@app.route('/api/process', methods=['POST'])
def process_file():
    """Process uploaded file for PII detection and redaction"""
    if not MODULES_LOADED:
        return jsonify({"error": "Processing modules are not loaded."}), 503

    try:
        data = request.get_json()
        if not data or 'filename' not in data:
            return jsonify({"error": "Filename is required"}), 400
        
        filename = data['filename']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({"error": "File not found on server"}), 404
        
        start_time = datetime.now()
        image = Image.open(filepath).convert("RGB")
        
        # 1. OCR to get text and bounding boxes
        ocr_results = extract_text_with_boxes(image)
        full_text = " ".join([item['text'] for item in ocr_results])
        
        boxes_to_redact = []
        pii_found = []

        # 2. Detect PII (Regex and NER) and map to boxes
        pii_regex_matches = detect_pii_regex(full_text)
        for pii_text in pii_regex_matches:
            pii_found.append({"text": pii_text, "type": "regex"})
            for item in ocr_results:
                if pii_text in item['text']:
                    boxes_to_redact.append(item['box'])
                    log_redaction("regex_pii", pii_text, item['box'])

        # NOTE: Initialize models once at startup for production
        spacy_ner = SpacyNer("en_core_web_lg")
        pii_ner_entities = spacy_ner.detect_pii(full_text)
        for entity in pii_ner_entities:
            pii_found.append({"text": entity['text'], "type": entity['label']})
            for item in ocr_results:
                if entity['text'] in item['text']:
                    boxes_to_redact.append(item['box'])
                    log_redaction("ner_pii", entity['text'], item['box'])

        # 3. Detect Signatures
        signature_detector = YoloSignatureDetector("path/to/model.pt")
        signature_boxes = signature_detector.detect_signatures(image)
        for box in signature_boxes:
            boxes_to_redact.append(box)
            log_redaction("signature", "signature detected", box)

        # 4. Redact image if sensitive content was found
        results = {"filename": filename}
        if boxes_to_redact:
            output_filename = f"redacted_{filename}"
            output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
            
            redact_boxes(image, boxes_to_redact, output_path, method='blackbox')
            
            results["redacted_file"] = output_filename
            results["status"] = "Redacted"
        else:
            results["status"] = "No PII found"

        processing_time = (datetime.now() - start_time).total_seconds()
        results["processing_time"] = round(processing_time, 2)
        results["pii_detected"] = pii_found
        
        return jsonify(results), 200
        
    except Exception as e:
        logger.error(f"Processing error: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

# --- Existing Error Handlers (Unchanged) ---
@app.errorhandler(404)
def not_found(error):
    # Your 404 handler
    return jsonify({"error": "Endpoint not found"}), 404

# ... (include your other error handlers: 405, 413, 500) ...

if __name__ == '__main__':
    # Your startup messages remain the same
    print("🚀 Starting SanitiAI Backend Server...")
    app.run(host='0.0.0.0', port=5000, debug=True)