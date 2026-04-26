import faiss
import numpy as np
import json
import os

def save_vector_store(chunks, index_path="vector_store.index", metadata_path="metadata.json"):
    """
    Save embeddings to FAISS index and metadata to JSON.
    chunks: list of chunks with embeddings
    """
    # extract embeddings into a numpy array
    embeddings = np.array([chunk['embedding'] for chunk in chunks]).astype('float32')
    
    # create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    # save FAISS index to disk
    faiss.write_index(index, index_path)
    
    # save metadata (text, title, video_url) to JSON
    metadata = [{"text": chunk['text'], "title": chunk['title'], "video_url": chunk['video_url'], "chunk_index": chunk['chunk_index']} for chunk in chunks]
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    print(f"Saved {len(chunks)} chunks to vector store")

def load_vector_store(index_path="vector_store.index", metadata_path="metadata.json"):
    """
    Load FAISS index and metadata from disk.
    """
    index = faiss.read_index(index_path)
    
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    
    print(f"Loaded {len(metadata)} chunks from vector store")
    return index, metadata