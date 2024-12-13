# Verwendung nur möglich mit Python-Version < 3.10.0

from pdf2image import convert_from_path
import pytesseract
from PyPDF2 import PdfReader

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path, lang='eng'):
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

        return ocr_text
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Path to the PDF file
pdf_file_path = r".\pdfs\DINtest-rotated.pdf"

# Extract text (use 'deu' for German, 'eng' for English)
extracted_text = extract_text_from_pdf(pdf_file_path, lang='deu')

# Save the extracted text to a file or print it
if extracted_text:
    with open("output.txt", "w", encoding="utf-8") as text_file:
        text_file.write(extracted_text)
    print("Text extraction completed. Saved to output.txt.")
else:
    print("Failed to extract text.")