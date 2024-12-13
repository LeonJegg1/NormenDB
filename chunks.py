def chunks(ocr:str, chunk_size:int=500) -> list:
    tokens = ocr.split()
    token_chunks = [' '.join(tokens[i:i + chunk_size]) for i in range(0, len(tokens), chunk_size)]
    return token_chunks