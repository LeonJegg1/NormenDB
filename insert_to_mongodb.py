from pymongo import MongoClient

def insert_to_mongodb(id:int, metadata:dict, content:str, entities:dict, tags:list):
    # Verbindung zur MongoDB herstellen
    client = MongoClient("mongodb://root:example@localhost:27017/")
    db = client["pdf_database"]
    collection = db["documents"]
    
    # Dokument in die MongoDB einfügen
    document = {
        "id": id,
        "metadata": metadata,
        "content": content,
        "entities": entities,
        "tags": tags
    }
    collection.insert_one(document)
    
    print(f'Dokument {id} wurde in die MongoDB eingefügt.')
    
    client.close()