import os
from pdf2image import convert_from_path

# Pfad zur PDF-Datei und Ausgabeordner definieren
pdf_path = './DIN EN 998-1.pdf'
output_folder = './imageOut'

# Erstellen des Ausgabeordners, falls dieser noch nicht existiert
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Konvertiere jede Seite des PDFs in ein Bild
images = convert_from_path(pdf_path)

# Jede Seite speichern
for i, image in enumerate(images):
    image_path = os.path.join(output_folder, f'seite_{i + 1}.png')
    image.save(image_path, 'PNG')

print(f'Alle Seiten wurden erfolgreich in {output_folder} gespeichert.')
