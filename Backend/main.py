import os
import sys
from io import BytesIO
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# --- Setup Python Path for relative imports ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import your project's custom modules ---
try:
    # MODIFIED: Import the single orchestrator function
    from pii_analyzer import analyze_and_sanitize_document
except ImportError as e:
    print(f"❌ Critical Import Error: {e}")
    print("👉 Please ensure 'pii_analyzer.py' with the 'analyze_and_sanitize_document' function exists.")
    sys.exit(1)

# --- Initialize FastAPI App ---
app = FastAPI(
    title="SanitiAI - PII Detection Pipeline",
    description="A synchronous API to analyze and sanitize documents for PII.",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Endpoints ---

@app.get("/", summary="API Health Check")
async def root():
    """Provides a simple status check to confirm the API is running."""
    return {"message": "SanitiAI API is running!", "status": "healthy"}

# MODIFIED: Replaced the background task endpoint with the new synchronous version
@app.post("/analyze/", summary="Analyze and Sanitize a Document")
async def start_analysis(file: UploadFile = File(...)):
    """
    Accepts a document, performs analysis and sanitization, 
    and returns the complete results in a single response.
    """
    try:
        file_content = await file.read()

        # Call the single pipeline function from pii_analyzer.py
        analysis_results = analyze_and_sanitize_document(file_content, file.content_type)
        
        # Add the filename and return the final results
        analysis_results["filename"] = file.filename
        return analysis_results
        
    except Exception as e:
        # Catch any errors during the process
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")