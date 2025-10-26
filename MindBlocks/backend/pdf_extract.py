import pdfplumber
import pytesseract
from PIL import Image
import tempfile
import os

def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract text from PDF bytes. 
    Falls back to OCR for image-based pages.
    
    Args:
        pdf_bytes: PDF file content in bytes
    
    Returns:
        Full extracted text as a string
    """
    text_parts = []

    # save to temp file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmpf:
        tmpf.write(pdf_bytes)
        tmpf.flush()
        tmp_path = tmpf.name

    try:
        #pdfplumber documentation code
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
                else:
                    #  fallback for pages with images
                    try:
                        pil_image = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        text_parts.append(ocr_text)
                    except Exception:
                        pass
    finally:
        # cleanup temporary file
        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    return "\n\n".join(text_parts)
