from html import entities
from transformers import AutoModel, AutoTokenizer
import os
import ollama
import psycopg2
from psycopg2 import sql
from extract_text_from_pdf import extract_text_from_pdf
from metadata_extraction import extract_metadata
from entitites_from_ner import entitites_from_ner
from insert_to_mongodb import insert_to_mongodb

#pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verbindung zur PostgreSQL-Datenbank herstellen
conn = psycopg2.connect(
    dbname="normendbvector",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)
cursor = conn.cursor()

cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

# Tabelle "documents" erstellen, falls sie nicht existiert
cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding VECTOR(1024)
    );
""")
conn.commit()

folder = r"./pdfs"
# For-Schleife, die alle Dateinamen im Ordner durchläuft
for filename in os.listdir(folder):
    # Nur Dateien zurückgeben (keine Unterordner)
    if os.path.isfile(os.path.join(folder, filename)):
        doc = extract_text_from_pdf(f'./{folder}/{filename}', lang='deu')
        
        for chunk in doc:
            # Embedding des Dokuments generieren
            try:
                response = ollama.embeddings(model="mxbai-embed-large", prompt=chunk)
                embedding = response["embedding"]
            except Exception as e:
                print(f"Fehler beim Abrufen des Embeddings: {e}")
                continue
            
            # Überprüfen, ob das Embedding bereits in der Datenbank vorhanden ist
            cursor.execute("""
                SELECT COUNT(*) FROM documents WHERE embedding = %s::vector;
            """, (embedding,))
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Embedding des Dokuments in die Datenbank einfügen
                cursor.execute(
                    sql.SQL("INSERT INTO documents (content, embedding) VALUES (%s, %s) RETURNING id"),
                    [chunk, embedding]
                )
                last_id = cursor.fetchone()[0]
                conn.commit()
                print(last_id)
                
                # TODO: MongoDB - last_id als indentifier - metadaten - entitites durch NER - Chunk-Text - Tags
                metadata = extract_metadata(f'./{folder}/{filename}')
                ner_entities, tags = entitites_from_ner(chunk) # sind immer leer
                insert_to_mongodb(last_id, metadata, chunk, ner_entities, tags)
                
                print(f'Dokument {filename} wurde in die Datenbank eingefügt.', last_id)
            else:
                print(f'Dokument {filename} ist bereits in der Datenbank vorhanden.')

cursor.close()
conn.close()