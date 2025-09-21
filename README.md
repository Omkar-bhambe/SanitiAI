# SanitiAI - Secure PII Sanitization Pipeline 🔒

**SanitiAI is a comprehensive, full-stack application designed to detect and sanitize Personally Identifiable Information (PII) from various document types. It features a modern web interface, a powerful backend, and an extensible plugin architecture for different analysis engines.**

![SanitiAI Application Interface]

---

## 🚀 Key Features

* **Multi-Document Support:** Analyze a wide range of file types, including images (`PNG`, `JPG`), documents (`PDF`, `DOCX`), and plain text (`TXT`, `CSV`, `JSON`).
* **Advanced PII Detection:** Utilizes a custom regex engine to identify common PII patterns like phone numbers, emails, Aadhaar numbers, credit card numbers, and bank account numbers.
* **Text Sanitization:** Automatically replaces detected numerical PII with dummy data loaded from a secure profile, providing clean, shareable text.
* **Asynchronous Processing:** Employs a robust background task queue to handle slow document analysis (like OCR) without freezing the user interface, ensuring a smooth user experience.
* **Interactive Frontend:** A modern, responsive user interface built with HTML, CSS, and vanilla JavaScript that provides a clear side-by-side comparison of original and sanitized text.
* **Extensible Plugin Architecture:** Easily switch between different PII analysis engines. The system is pre-configured with a powerful internal regex engine and includes placeholders for integrating external APIs like **Google Cloud DLP** and **Microsoft Azure AI**.
* **Ready for Integration:** The backend exposes a clean REST API, making SanitiAI a powerful pipeline that can be easily integrated into other systems and data workflows.

---

## 🛠️ Technology Stack

* **Backend:** **Python** with **FastAPI** for a high-performance, asynchronous API. An alternative **Flask** server is also provided.
* **Frontend:** **HTML5**, **CSS3**, and modern **JavaScript (ES6+)**.
* **PII Analysis & Text Extraction:**
    * **Tesseract OCR** for text extraction from images.
    * **PyMuPDF** (`fitz`) for text extraction from PDFs.
    * **python-docx** for text extraction from DOCX files.
    * **spaCy** (placeholder) for future NLP-based entity recognition.
* **Core Libraries:** `uvicorn`, `python-multipart`, `Pillow`.

---

## ⚙️ Setup and Installation

Follow these steps to get the SanitiAI application running on your local machine.

### Prerequisites

* **Python 3.10+**
* **Tesseract OCR Engine:** You must have Tesseract installed on your system.
    * **Windows:** Download from the [UB Mannheim Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki) and ensure its installation path is either added to your system's PATH or updated directly in the `pii_analyzer.py` script.
    * **macOS:** `brew install tesseract`
    * **Linux (Ubuntu):** `sudo apt install tesseract-ocr`

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/sanitiai.git](https://github.com/your-username/sanitiai.git)
    cd sanitiai
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install the required Python packages:**
    Create a `requirements.txt` file with the content from the previous response and run:
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run the Application

SanitiAI runs as two separate processes: the backend API and the frontend server. You will need **two terminals** open.

### 1. Start the Backend Server

In your first terminal, from the project's root directory, run the FastAPI server:

```bash
# Ensure you are in the main project directory
uvicorn backend.main:app --reload
```
### 2. Start the Frontend Server
```bash
Navigate into the frontend directory
cd frontend
# For Python 3
python -m http.server 8080
```
### 3. Access the Application
```bash
Open your web browser and navigate to:
http://localhost:8080/templates/index.html

You should now see the SanitiAI user interface and be ready to upload documents.
```
##  How to Use
1.Select a File: Click the upload area or drag and drop a file (.png, .pdf, .docx, etc.).

2. Choose an Engine (Optional): Use the "Select Analysis Engine" dropdown to choose which PII service to use. The default is the powerful internal engine.

3. Submit for Sanitization: Click the "Sanitize Document" button.

4. View Results: The application will show a "Processing" status. Once complete, the results panel will display the full extracted text on the left and the sanitized text (with PII replaced by dummy data) on the right.
