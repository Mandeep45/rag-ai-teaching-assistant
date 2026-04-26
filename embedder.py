from fastembed import TextEmbedding

# load the model
model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

def embed_chunks(chunks, batch_size=100):
    """
    Convert list of chunks into embeddings in batches.
    """
    all_embedded = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [chunk['text'] for chunk in batch]
        embeddings = list(model.embed(texts))
        
        for j, chunk in enumerate(batch):
            chunk['embedding'] = embeddings[j].tolist()
            all_embedded.append(chunk)
        
        print(f"Embedded {min(i+batch_size, len(chunks))}/{len(chunks)} chunks")
    
    return all_embedded