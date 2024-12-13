from PyPDF2 import PdfReader
from datetime import datetime

def extract_metadata(pdf_path:str) -> dict:
    # PDF einlesen
    reader = PdfReader(pdf_path)
    metadata = reader.metadata

    # Metadaten sammeln
    extracted_metadata = {
        "title": metadata.title if metadata.title else "Unknown",
        "author": metadata.author if metadata.author else "Unknown",
        "creator": metadata.creator if metadata.creator else "Unknown",
        "producer": metadata.producer if metadata.producer else "Unknown",
        "created_at": metadata.get("/CreationDate", "Unknown"),
        "modified_at": metadata.get("/ModDate", "Unknown"),
        "total_pages": len(reader.pages)
    }
    return extracted_metadata