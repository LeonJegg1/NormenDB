from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader
from metadata_extraction import extract_metadata
from chunks import chunks as ch

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path:str, lang:str='deu') -> list:
    try:
        # Get the number of pages in the PDF
        reader = PdfReader(pdf_path)
        page_limit = len(reader.pages)

        # Convert PDF to images
        pages = convert_from_path(pdf_path, first_page=1, last_page=page_limit)
        ocr_text = ""

        # Perform OCR on each page
        for i, page in enumerate(pages):
            print(f"Processing page {i + 1}")
            text = pytesseract.image_to_string(page, lang=lang)
            ocr_text += text + "\n"

        chunks = ch(ocr_text)

        return chunks
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
