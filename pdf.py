import os
from pdf2image import convert_from_path

# Pfad zum Verzeichnis mit den PDF-Dateien und Basis-Ausgabeordner definieren
pdf_directory = './pdfs'
base_output_folder = './imageOut'

# Erstellen des Basis-Ausgabeordners, falls dieser noch nicht existiert
if not os.path.exists(base_output_folder):
    os.makedirs(base_output_folder)

# Durchlaufe alle Dateien im PDF-Verzeichnis
for pdf_filename in os.listdir(pdf_directory):
    if pdf_filename.endswith('.pdf'):
        pdf_path = os.path.join(pdf_directory, pdf_filename)
        
        # Extrahiere den Namen der PDF-Datei ohne Erweiterung
        pdf_name = os.path.splitext(pdf_filename)[0]
        
        # Konvertiere jede Seite des PDFs in ein Bild
        images = convert_from_path(pdf_path)
        
        # Jede Seite speichern
        for i, image in enumerate(images):
            image_path = os.path.join(base_output_folder, f'seite_{i + 1}_{pdf_name}.png')
            image.save(image_path, 'PNG')
        
        print(f'Alle Seiten von {pdf_filename} wurden erfolgreich in {base_output_folder} gespeichert.')
        
        # Lösche die PDF-Datei nach der Verarbeitung
        os.remove(pdf_path)
        print(f'{pdf_filename} wurde aus dem Verzeichnis gelöscht.')
