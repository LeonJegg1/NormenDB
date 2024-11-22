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
    LIMIT 1;
    """, (response["embedding"], ))

    results = cur.fetchone()
    if results:
        # data = results[1]
        # print(data)
        
        output = ollama.generate(
        model="llama3.1:8b",
        prompt=f"Using this data: {results[1]}. Respond to this prompt: {prompt}"
        )

        print(output['response'])
    else:
        print("No results found.")
    
if __name__ == "__main__":
    retrieve_embeddings()