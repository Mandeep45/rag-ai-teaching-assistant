from embedder import model
import numpy as np

def retrieve(query, index, metadata, top_k=5, threshold=0.8):
    # embed the query
    query_embedding = list(model.embed([query]))[0].astype('float32').reshape(1, -1)
    
    # search FAISS for top_k similar chunks
    distances, indices = index.search(query_embedding, top_k)
    
    # get the matching chunks from metadata
    results = []
    for i, idx in enumerate(indices[0]):
        if distances[0][i] < threshold:
            chunk = metadata[idx]
            chunk['score'] = float(distances[0][i])
            results.append(chunk)
    
    return results
 