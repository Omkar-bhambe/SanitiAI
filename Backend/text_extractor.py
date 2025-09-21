import io
import docx
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

def extract_text(content_type: str, file_content: bytes) -> str:
    """
    Extracts text from a file's content based on its MIME type.
    """
    try:
        if "image" in content_type:
            image = Image.open(io.BytesIO(file_content)).convert("RGB")
            return pytesseract.image_to_string(image)
        
        elif "pdf" in content_type:
            text = ""
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
            return text
            
        elif "text" in content_type or "csv" in content_type or "json" in content_type:
            return file_content.decode('utf-8', errors='ignore')

        elif "openxmlformats-officedocument.wordprocessingml" in content_type: # .docx
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join([para.text for para in doc.paragraphs])
            
        else:
            return "Unsupported file type for text extraction."

    except Exception as e:
        print(f"❌ Error extracting text from {content_type}: {e}")
        return f"Could not extract text from the document. Error: {e}"