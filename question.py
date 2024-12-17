from typing import final
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
    
    best_result = cur.fetchone() # (id, content, distance)
    
    if best_result:
        best_distance = best_result[2]
        threshold = best_distance * 1.1  # 10% mehr als die beste Distanz

        cur.execute("""
        SELECT id, content, embedding <-> %s::vector AS distance
        FROM documents
        WHERE embedding <-> %s::vector <= %s
        ORDER BY distance
        LIMIT 5;
        """, (response["embedding"], response["embedding"], threshold))
        
        results = cur.fetchall()
        
        all_personen = []
        all_organisationen = []
        all_daten = []
        all_technische_begriffe = []
        all_produkte = []
        all_orte = []
        all_kunstwerke = []
        all_veranstaltungen = []
        all_sprachen = []
        all_gesetze = []
        all_sonstiges = []
        all_tags = []

        all_titles = []
        all_authors = []
        all_creators = []
        all_producers = []
        all_created_at = []
        all_modified_at = []
        all_total_pages = []
        all_contents = []

        for result in results:
            mongo_result = collection.find_one({"id": result[0]})
            if mongo_result:
                all_personen.extend(mongo_result.get('entities', {}).get('personen', []))
                all_organisationen.extend(mongo_result.get('entities', {}).get('organisationen', []))
                all_daten.extend(mongo_result.get('entities', {}).get('daten', []))
                all_technische_begriffe.extend(mongo_result.get('entities', {}).get('technische_begriffe', []))
                all_produkte.extend(mongo_result.get('entities', {}).get('produkte', []))
                all_orte.extend(mongo_result.get('entities', {}).get('orte', []))
                all_kunstwerke.extend(mongo_result.get('entities', {}).get('kunstwerke', []))
                all_veranstaltungen.extend(mongo_result.get('entities', {}).get('veranstaltungen', []))
                all_sprachen.extend(mongo_result.get('entities', {}).get('sprachen', []))
                all_gesetze.extend(mongo_result.get('entities', {}).get('gesetze', []))
                all_sonstiges.extend(mongo_result.get('entities', {}).get('sonstiges', []))
                all_tags.extend(mongo_result.get('tags', []))

                all_titles.append(mongo_result.get('metadata', {}).get('title', 'Unknown'))
                all_authors.append(mongo_result.get('metadata', {}).get('author', 'Unknown'))
                all_creators.append(mongo_result.get('metadata', {}).get('creator', 'Unknown'))
                all_producers.append(mongo_result.get('metadata', {}).get('producer', 'Unknown'))
                all_created_at.append(mongo_result.get('metadata', {}).get('created_at', 'Unknown'))
                all_modified_at.append(mongo_result.get('metadata', {}).get('modified_at', 'Unknown'))
                all_total_pages.append(mongo_result.get('metadata', {}).get('total_pages', 'Unknown'))
                all_contents.append(mongo_result.get('content', 'Unknown'))

        final_prompt = f"""
        Im Folgenden findest Du Informationen aus einer MongoDB-Datenbank:

        Metadata:
        - Titel: {all_titles}
        - Autor: {all_authors}
        - Creator: {all_creators}
        - Producer: {all_producers}
        - Erstellt am: {all_created_at}
        - Modifiziert am: {all_modified_at}
        - Gesamtseiten: {all_total_pages}

        Content-Auszug:
        {all_contents}

        Entitäten:
        Personen: {all_personen}
        Organisationen: {all_organisationen}
        Daten: {all_daten}
        Technische Begriffe: {all_technische_begriffe}
        Produkte: {all_produkte}
        Orte: {all_orte}
        Kunstwerke: {all_kunstwerke}
        Veranstaltungen: {all_veranstaltungen}
        Sprachen: {all_sprachen}
        Gesetze: {all_gesetze}
        Sonstiges: {all_sonstiges}

        Tags: 
        {all_tags}

        Basierend auf diesen Informationen, antworte auf die folgende Frage. 
        Halte dich dabei strikt an die Informationen aus der MongoDB-Datenbank.
        Halluziniere keine Informationen, die nicht in der Datenbank vorhanden sind.
        Halte dich an die Fakten.
        Halte dich möglichst kurz und präzise.

        {prompt}
        """

        # Übergabe des dynamischen Prompts an das Modell
        output = ollama.generate(
            model="llama3.1:8b",
            prompt=final_prompt
        )
        print(final_prompt)
        print(output['response'], "\n")
    else:
        print("Keine relevanten Ergebnisse gefunden.")

if __name__ == "__main__":
    while True:
        retrieve_embeddings()