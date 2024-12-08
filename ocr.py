from PIL import Image
import pytesseract
import cv2
import numpy as np

# Set the Tesseract OCR path if necessary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_table_as_markdown(image_path):
    """
    Extrahiert den Inhalt einer Tabelle aus einem Bild und gibt diesen als Markdown zurück.
    Wiederholt den OCR-Prozess zweimal, um die Ergebnisse zu validieren.
    """
    # Lade das Bild
    image = Image.open(image_path)
    
    # Erste OCR-Durchführung
    ocr_result_1 = pytesseract.image_to_string(image, lang='deu')
    
    # Konvertiere das Bild in OpenCV-Format und wende Bildverarbeitung an
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Zweite OCR-Durchführung auf dem verbesserten Bild
    ocr_result_2 = pytesseract.image_to_string(thresh, lang='deu')
    
    # Ergebnisse kombinieren
    combined_result = f"### OCR Ergebnis 1:\n{ocr_result_1}\n\n### OCR Ergebnis 2:\n{ocr_result_2}"
    
    # Markdown-Rückgabe
    return combined_result

# Pfad zum Bild
image_path = './imageOut/seite_17.png'

# Tabelle extrahieren und als Markdown ausgeben
markdown_output = extract_table_as_markdown(image_path)
print(markdown_output)
