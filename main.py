from transformers import AutoModel, AutoTokenizer
import os
import ollama
import psycopg2
from psycopg2 import sql

# Verbindung zur PostgreSQL-Datenbank herstellen
conn = psycopg2.connect(
    dbname="ragdb",
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

tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id)
model = model.eval().cuda()

# Pfad zum Ausgabeordner
output_folder = './imageOut'

# For-Schleife, die alle Dateinamen im Ordner durchläuft
for filename in os.listdir(output_folder):
    # Nur Dateien zurückgeben (keine Unterordner)
    if os.path.isfile(os.path.join(output_folder, filename)):
        doc = model.chat(tokenizer, f'./{output_folder}/{filename}', ocr_type='ocr')
        #print(doc)
        
        # Embedding des Dokuments generieren
        try:
            response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
            embedding = response["embedding"]
        except Exception as e:
            print(f"Fehler beim Abrufen des Embeddings: {e}")
            continue
        print(len(embedding))
        
        # Überprüfen, ob das Embedding bereits in der Datenbank vorhanden ist
        cursor.execute("""
            SELECT COUNT(*) FROM documents WHERE embedding = %s::vector;
        """, (embedding,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Embedding des Dokuments in die Datenbank einfügen
            cursor.execute(
                sql.SQL("INSERT INTO documents (content, embedding) VALUES (%s, %s)"),
                [doc, embedding]
            )
            print(f'Dokument {filename} wurde in die Datenbank eingefügt.')
        else:
            print(f'Dokument {filename} ist bereits in der Datenbank vorhanden.')

conn.commit()
cursor.close()
conn.close()