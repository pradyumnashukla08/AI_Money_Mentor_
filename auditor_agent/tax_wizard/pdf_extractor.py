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

def extract_text_pymupdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF using PyMuPDF (fitz).
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
        with fitz.open(pdf_path) as doc:
            for page_num, page in enumerate(doc, start=1):
                page_text = page.get_text("text")
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
    except Exception as exc:
        logger.error("PyMuPDF extraction failed: %s", exc)
        return ""

    return "\n".join(text_parts)


# ── OCR extraction (pytesseract) ────────────────────────────────────────────

def extract_text_ocr(pdf_path: str) -> str:
    """
    Convert each PDF page to an image, then run Tesseract OCR.
    Used as a fallback for scanned / image-based PDFs.
    Returns empty string if dependencies are unavailable.
    """
    try:
        from pdf2image import convert_from_path
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        logger.warning("OCR dependencies missing (%s). Run: pip install pdf2image pytesseract Pillow", exc)
        return ""

    text_parts = []
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            images = convert_from_path(pdf_path, dpi=300, output_folder=tmp_dir)
            for page_num, img in enumerate(images, start=1):
                page_text = pytesseract.image_to_string(img, lang="eng")
                if page_text.strip():
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
    except Exception as exc:
        logger.error("OCR extraction failed: %s", exc)
        return ""

    return "\n".join(text_parts)


# ── Primary entry point ─────────────────────────────────────────────────────

def extract_form16_text(pdf_path: str) -> str:
    """
    Master extraction function.
    Tries digital extraction first; if the result is too sparse (likely
    a scanned PDF), automatically retries with OCR.

    Args:
        pdf_path: Absolute or relative path to the Form 16 PDF file.

    Returns:
        Raw extracted text as a single string.

    Raises:
        FileNotFoundError: If the PDF file does not exist.
        ValueError: If no text could be extracted by any method.
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    logger.info("Extracting text from: %s", path.name)

    # Step 1 — PyMuPDF (fast, accurate for digital PDFs)
    text = extract_text_pymupdf(str(path))

    # If fewer than 200 characters extracted, likely scanned — try OCR
    if len(text.strip()) < 200:
        logger.info("Digital extraction yielded sparse text. Switching to OCR...")
        text = extract_text_ocr(str(path))

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the PDF. "
            "Ensure the file is a valid Form 16 and Tesseract is installed for scanned PDFs."
        )

    logger.info("Extraction complete. Characters extracted: %d", len(text))
    return text


# ── Quick CLI test ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_extractor.py <path_to_form16.pdf>")
        sys.exit(1)

    pdf = sys.argv[1]
    result = extract_form16_text(pdf)
    print("\n" + "=" * 60)
    print("EXTRACTED TEXT PREVIEW (first 1500 chars):")
    print("=" * 60)
    print(result[:1500])
