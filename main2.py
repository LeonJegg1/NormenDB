import os
import boto3
import redis
import psycopg2
from neo4j import GraphDatabase
from pymongo import MongoClient
from minio import Minio
from typing import List
from psycopg2.extras import Json
from transformers import AutoModel, AutoTokenizer
import ollama
from keybert import KeyBERT

# 1. MinIO Setup (für Speicherung der PDFs)
minio_client = Minio(
    "localhost:9000",  # MinIO-Host
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Ensure the bucket exists
def create_minio_bucket(bucket_name: str):
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print(f"Bucket {bucket_name} created.")
    else:
        print(f"Bucket {bucket_name} already exists.")

# Upload all files in a directory to MinIO
def upload_directory_to_minio(bucket_name: str, directory_path: str):
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            file_name = os.path.relpath(file_path, directory_path)
            minio_client.fput_object(bucket_name, file_name, file_path)
            print(f"Uploaded {file_name} to {bucket_name}.")

# 2. Redis Setup (für Embeddings und Cache)
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Store embeddings in Redis
def store_embedding(key: str, embedding: List[float]):
    redis_client.set(key, str(embedding))

# Retrieve embeddings from Redis
def get_embedding(key: str):
    return eval(redis_client.get(key))

# 3. PostgreSQL Setup (für Metadaten)
pg_connection = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="user",
    password="password"
)

# Create a table for storing metadata and embeddings
def create_metadata_table():
    with pg_connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id SERIAL PRIMARY KEY,
            file_name TEXT,
            metadata JSONB,
            embedding VECTOR(1024),
            tags JSONB
        );
        """)
        pg_connection.commit()

# Insert metadata, embeddings, and tags into PostgreSQL
def insert_metadata_with_embedding_and_tags(file_name: str, metadata: dict, embedding: List[float], tags: List[str]):
    with pg_connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO metadata (file_name, metadata, embedding, tags) VALUES (%s, %s, %s, %s)",
            (file_name, Json(metadata), embedding, Json(tags))
        )
        pg_connection.commit()

# 4. Neo4j Setup (für Beziehungen zwischen Normen)
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))

# Create relationships between norms
def create_relationships_from_data(metadata: dict):
    relationships = []
    with neo4j_driver.session() as session:
        title = metadata.get("title", "Unknown")
        tags = metadata.get("tags", [])

        # Add tags as nodes and connect them to the document node
        session.run("MERGE (doc:Document {title: $title})", title=title)
        for tag in tags:
            session.run("MERGE (tag:Tag {name: $tag})", tag=tag)
            session.run(
                "MATCH (doc:Document {title: $title}), (tag:Tag {name: $tag}) "
                "MERGE (doc)-[:HAS_TAG]->(tag)",
                title=title, tag=tag
            )

        # Add relationships based on inferred context
        for related_tag in tags:
            if related_tag != tag:
                session.run(
                    "MATCH (tag1:Tag {name: $tag1}), (tag2:Tag {name: $tag2}) "
                    "MERGE (tag1)-[:RELATED_TO]->(tag2)",
                    tag1=tag, tag2=related_tag
                )

# 5. MongoDB Setup (für vollständige Dokumentenspeicherung)
mongo_client = MongoClient("mongodb://root:example@localhost:27017")
mongo_db = mongo_client["norms_db"]
mongo_collection = mongo_db["documents"]

# Store data in MongoDB
def store_in_mongodb(file_name: str, metadata: dict, embedding: List[float], tags: List[str]):
    document = {
        "file_name": file_name,
        "metadata": metadata,
        "embedding": embedding,
        "tags": tags
    }
    mongo_collection.insert_one(document)

# Generate embeddings using Transformer model
def generate_embedding(model, tokenizer, file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    doc = model.chat(tokenizer, content, ocr_type='ocr')
    try:
        response = ollama.embeddings(model="mxbai-embed-large", prompt=doc)
        embedding = response["embedding"]
        return embedding, doc
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None, None

# Generate tags using KeyBERT
def generate_tags(text: str):
    kw_model = KeyBERT()
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english")
    return [kw[0] for kw in keywords]

# Retrieve and process queries using Ollama, PostgreSQL, and MongoDB
def retrieve_embeddings():
    prompt = input("Enter a prompt: ")
    # Generate embedding for the prompt
    response = ollama.embeddings(prompt=prompt, model="mxbai-embed-large")
    embedding = response.get("embedding")
    if not embedding:
        print("Failed to generate embedding for the prompt.")
        return

    # Query PostgreSQL for relevant content
    with pg_connection.cursor() as cursor:
        cursor.execute("""
        SELECT file_name, metadata, embedding <-> %s::vector AS distance
        FROM metadata
        ORDER BY distance
        LIMIT 25;
        """, (embedding,))
        results_pg = cursor.fetchall()

    # Query MongoDB for additional matches
    results_mongo = mongo_collection.find({"embedding": {"$exists": True}})

    # Combine results from both sources
    relevant_results = []
    for result in results_pg:
        relevant_results.append(result[1])

    for doc in results_mongo:
        relevant_results.append(doc["metadata"])

    if relevant_results:
        response = ollama.generate(
            model="llama3.1:8b",
            prompt=f"Using this data: {relevant_results}. Respond to this prompt: {prompt}"
        )
        print(response['response'])
    else:
        print("No relevant results found.")

# Example Integration Steps
if __name__ == "__main__":
    # 1. MinIO: Create bucket and upload directory
    BUCKET_NAME = "norms-bucket"
    DIRECTORY_PATH = ".pdfs"
    create_minio_bucket(BUCKET_NAME)
    upload_directory_to_minio(BUCKET_NAME, DIRECTORY_PATH)

    # Initialize Transformer model and tokenizer
    tokenizer = AutoTokenizer.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True)
    model = AutoModel.from_pretrained('ucaslcl/GOT-OCR2_0', trust_remote_code=True, low_cpu_mem_usage=True, device_map='cuda', use_safetensors=True, pad_token_id=tokenizer.eos_token_id).eval().cuda()

    # 3. PostgreSQL: Store metadata, embeddings, and tags
    create_metadata_table()
    for root, _, files in os.walk(DIRECTORY_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            embedding, content = generate_embedding(model, tokenizer, file_path)
            if embedding and content:
                tags = generate_tags(content)
                metadata = {"title": file, "path": file_path, "tags": tags}
                insert_metadata_with_embedding_and_tags(file, metadata, embedding, tags)
                create_relationships_from_data(metadata)
                store_in_mongodb(file, metadata, embedding, tags)

    while True:
        retrieve_embeddings()
