"""
pdf_extractor.py — Extracts raw text from Form 16 PDFs.

Strategy:
  1. Try PyMuPDF (fast, works on digital / text-based PDFs)
  2. Fall back to pytesseract OCR (for scanned / image-based PDFs)
"""

import os
import sys
import tempfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ── PyMuPDF extraction ──────────────────────────────────────────────────────

def extract_text_pymupdf_bytes(pdf_bytes: bytes, file_ext: str = "pdf") -> str:
    """
    Extract all text from a file using PyMuPDF (fitz) directly from RAM.
    Works best on digitally-created PDFs (not scanned).
    Returns empty string if PyMuPDF is unavailable or extraction fails.
    """
    try:
        import fitz  # PyMuPDF
    except ImportError:
        logger.warning("PyMuPDF not installed. Run: pip install PyMuPDF")
        return ""

    text_parts = []
    try:
        with fitz.open(stream=pdf_bytes, filetype=file_ext) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
    except Exception as exc:
        logger.error("PyMuPDF RAM extraction failed: %s", exc)
        return ""

    return "\n".join(text_parts)


# ── Groq Vision AI Extraction (LLaMA 3.2 11B Vision) ─────────────────────────

def extract_text_vision_llm(pdf_bytes: bytes, file_ext: str = "pdf") -> str:
    """
    Convert each PDF page to an image natively in RAM using PyMuPDF,
    encode to base64, and use Groq Vision (llama-3.2-11b-vision-preview)
    to intelligently read the text without needing native Tesseract OCR installed!
    """
    import base64
    import io
    try:
        import fitz
        from PIL import Image
        from groq import Groq
    except ImportError as exc:
        logger.warning("Vision dependencies missing (%s).", exc)
        return ""

    # Lazy-import auditor configs inside the function exactly like form16_agent does
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
    from auditor_agent.config import settings

    if not settings.GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is missing. Cannot run Vision Extraction.")
        return ""

    client = Groq(api_key=settings.GROQ_API_KEY)
    
    text_parts = []
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page_num, page in enumerate(doc, start=1):
                # Render page natively into visual RAM memory (100 DPI is optimal for LLaMA Vision to prevent payload overflow)
                pix = page.get_pixmap(dpi=100)
                
                # Translate fitz pixmap to PIL JPEG image perfectly
                mode = "RGBA" if pix.alpha else "RGB"
                img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
                
                buffer = io.BytesIO()
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(buffer, format="JPEG", quality=80)
                base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
                
                # Deploy Base64 logic to Groq Unified LLaMA-3.2 Vision Model
                logger.info(f"Shooting Page {page_num} memory buffer natively to Groq Vision AI...")
                response = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text", 
                                    "text": "Identify and extract all the text visible in this financial document. Output ONLY the raw financial text perfectly. Do not include markdown or explanations."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}",
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=2048,
                    temperature=0.0
                )
                
                page_text = response.choices[0].message.content.strip()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                    
    except Exception as exc:
        logger.error("Groq Native Vision memory extraction completely failed: %s", exc)
        return ""

    return "\n".join(text_parts)


# ── Primary entry point ─────────────────────────────────────────────────────

def extract_form16_text(file_bytes: bytes, file_ext: str = "pdf") -> str:
    """
    Master extraction function.
    Tries digital RAM extraction first; if the result is too sparse,
    safely provisions a temporary file for fallback Groq Vision parsing.

    Args:
        file_bytes: Raw binary string of the file.
        file_ext: File extension (pdf, png, jpg, jpeg)

    Returns:
        Raw extracted text as a single string.

    Raises:
        ValueError: If no text could be extracted by any method.
    """
    if not isinstance(file_bytes, bytes):
        raise TypeError("Expected raw bytes for memory stream.")

    logger.info("Extracting Form16 text natively from RAM... (%d bytes) [ext: %s]", len(file_bytes), file_ext)

    # Clean the extension
    ext = file_ext.lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"

    # Step 1 — PyMuPDF directly from RAM (Bypasses Windows TempFile Locks entirely)
    text = extract_text_pymupdf_bytes(file_bytes, ext)

    # If fewer than 200 characters, automatically try Vision LLM via RAM-buffered fitz pixmap rendering
    if len(text.strip()) < 200:
        logger.info("RAM extraction yielded sparse text. Initiating Groq LLaMA Vision memory extraction...")
        ocr_text = extract_text_vision_llm(file_bytes, ext)
        # Only overwrite if Vision actually successfully extracted something!
        if len(ocr_text.strip()) > len(text.strip()):
            text = ocr_text

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the document. "
            "Ensure the file is a valid Form 16 and that Groq API is reachable."
        )

    logger.info("Extraction complete. Characters extracted: %d", len(text))
    return text


# ── Quick CLI test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_form16.pdf>")
        sys.exit(1)

    pdf = sys.argv[1]
    with open(pdf, "rb") as f:
        pdf_bytes = f.read()

    result = extract_form16_text(pdf_bytes)
    print("\n" + "=" * 60)
    print("EXTRACTED TEXT PREVIEW (first 1500 chars):")
    print("=" * 60)
    print(result[:1500])
