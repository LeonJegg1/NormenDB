import ollama
import psycopg2
from psycopg2 import sql

conn = psycopg2.connect(
    dbname="ragdb",
    user="postgres",
    password="password",
    host="localhost",
    port="5433"
)
cur = conn.cursor()

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
    LIMIT 25;
    """, (response["embedding"], ))

    results = cur.fetchall()
    if results:
        # Berechnung der minimalen Distanz (Top-Ergebnis)
        min_distance = results[0][2]
        # Liste für relevante Ergebnisse initialisieren
        relevant_results = []
        for result in results:
            id, content, distance = result
            # Berechnung der prozentualen Abweichung vom Top-Ergebnis
            deviation = ((distance - min_distance) / min_distance) * 100 if min_distance != 0 else 0
            if deviation <= 10:
                relevant_results.append(content)
        if relevant_results:
            # Übergabe aller relevanten Ergebnisse an das Modell
            output = ollama.generate(
                model="llama3.1:8b",
                prompt=f"Using this data: {relevant_results}. Respond to this prompt: {prompt}"
            )
            print(output['response'])
        else:
            print("Keine relevanten Ergebnisse gefunden.")
    else:
        print("Keine Ergebnisse gefunden.")
    
if __name__ == "__main__":
    while True:
        retrieve_embeddings()