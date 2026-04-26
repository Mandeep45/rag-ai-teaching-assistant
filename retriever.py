from embedder import model
import numpy as np

def retrieve(query, index, metadata, top_k=5):
    """
    Find the most relevant chunks for a given query.
    query: student's question
    index: FAISS index
    metadata: list of chunk metadata
    top_k: number of top results to return
    """
    # embed the query
    query_embedding = list(model.embed([query]))[0].astype('float32').reshape(1, -1)
    
    # search FAISS for top_k similar chunks
    distances, indices = index.search(query_embedding, top_k)
    
    # get the matching chunks from metadata
    results = []
    for i, idx in enumerate(indices[0]):
        chunk = metadata[idx]
        chunk['score'] = float(distances[0][i])
        results.append(chunk)
    
    return results
 