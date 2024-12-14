import ollama
import psycopg2
from psycopg2 import sql
from pymongo import MongoClient

conn = psycopg2.connect(
    dbname="normendbvector",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

client = MongoClient("mongodb://root:example@localhost:27017/")
db = client["pdf_database"]
collection = db["documents"]

def retrieve_embeddings():
    # Beispiel-Prompt
    prompt = input("Enter a prompt: ")
    # Generieren eines Embeddings für den Prompt und Abrufen des relevantesten Dokuments
    response = ollama.embeddings(
        prompt=prompt,
        model="mxbai-embed-large"
    )
    #print(response)
    cur.execute("""
    SELECT id, content, embedding <-> %s::vector AS distance
    FROM documents
    ORDER BY distance
    LIMIT 1;
    """, (response["embedding"], ))
    
    results = cur.fetchall()[0] # (id, content, distance)
    
    mongo_result = collection.find_one({"id": results[0]})
    
    if results:
        # Dynamischer Prompt
        prompt = f"""
        Im Folgenden findest Du Informationen aus einer MongoDB-Datenbank:

        ID: {mongo_result.get('id', 'Unknown')}
        Metadata:
        - Titel: {mongo_result.get('title', 'Unknown')}
        - Autor: {mongo_result.get('author', 'Unknown')}
        - Creator: {mongo_result.get('creator', 'Unknown')}
        - Producer: {mongo_result.get('producer', 'Unknown')}
        - Erstellt am: {mongo_result.get('created_at', 'Unknown')}
        - Modifiziert am: {mongo_result.get('modified_at', 'Unknown')}
        - Gesamtseiten: {mongo_result.get('total_pages', 'Unknown')}

        Content-Auszug:
        "{mongo_result.get('content_excerpt', 'Unknown')}"

        Entitäten:
        Personen: {mongo_result.get('entities_persons', [])}
        Organisationen: {mongo_result.get('entities_organizations', [])}
        Daten: {mongo_result.get('entities_dates', [])}
        Technische Begriffe: {mongo_result.get('entities_technical_terms', [])}
        Produkte: {mongo_result.get('entities_products', [])}
        Orte: {mongo_result.get('entities_places', [])}
        Kunstwerke: {mongo_result.get('entities_artworks', [])}
        Veranstaltungen: {mongo_result.get('entities_events', [])}
        Sprachen: {mongo_result.get('entities_languages', [])}
        Gesetze: {mongo_result.get('entities_laws', [])}
        Sonstiges: {mongo_result.get('entities_misc', [])}

        Tags: 
        {mongo_result.get('tags', [])}

        Basierend auf diesen Informationen:

        {prompt}
        """

        # Übergabe des dynamischen Prompts an das Modell
        output = ollama.generate(
            model="llama3.1:8b",
            prompt=prompt
        )
        print(output['response'])
    else:
        print("Keine relevanten Ergebnisse gefunden.")
        
if __name__ == "__main__":
    while True:
        retrieve_embeddings()