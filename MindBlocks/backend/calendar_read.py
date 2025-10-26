import pdfplumber
import pytesseract
from PIL import Image
import tempfile
import os

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF. Falls back to OCR if pages contain images only.
    """
    text_parts = []
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmpf:
        tmpf.write(pdf_bytes)
        tmpf.flush()
        tmp_path = tmpf.name

    try:
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    # OCR fallback
                    try:
                        pil_image = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        text_parts.append(ocr_text)
                    except Exception:
                        pass
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return "\n\n".join(text_parts)
