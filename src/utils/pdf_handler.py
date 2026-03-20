import pdfplumber
import pytesseract

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file. 
    Uses pdfplumber for text-based PDFs and pytesseract for scanned ones.
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text and page_text.strip():
                    text += page_text + "\n"
                else:
                    # Possibly a scanned page, try OCR
                    print(f"DEBUG: No text on page {page.page_number}, attempting OCR...")
                    try:
                        # Convert page to image
                        im = page.to_image(resolution=200).original
                        ocr_text = pytesseract.image_to_string(im)
                        if ocr_text:
                            text += ocr_text + "\n"
                    except Exception as ocr_err:
                        print(f"OCR Error on page {page.page_number}: {ocr_err}")
                        
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text
