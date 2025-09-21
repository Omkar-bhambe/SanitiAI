import pytesseract
from PIL import Image

def extract_text_with_boxes(image: Image.Image):
    """
    Extract text and bounding boxes from image using Tesseract OCR.
    Returns list of dicts: [{'text': str, 'box': (x, y, w, h)}]
    """
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    results = []
    n_boxes = len(data['level'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if text:
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            results.append({'text': text, 'box': (x, y, w, h)})
    return results
