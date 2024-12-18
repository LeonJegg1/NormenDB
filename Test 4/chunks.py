from langchain.text_splitter import TokenTextSplitter
from langchain.schema import Document
from typing import List

def chunks(text:str, chunk_size:int = 300, chunk_overlap:int = 50) -> List[str]:
    splitter = TokenTextSplitter(
        encoding_name="gpt2",
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    documents = splitter.create_documents([text])
    return [doc.page_content for doc in documents]