from datasets import load_dataset
import pandas as pd
import os
from embedder import embed_chunks
from processor import process_dataset
from vector_store import save_vector_store, load_vector_store
from assistant import ask

# load dataset
ds = load_dataset("iblai/ibl-khanacademy-transcripts")
df = pd.DataFrame(ds['train'])
print(f"Dataset loaded: {len(df)} videos")

# process all videos into chunks
all_chunks = process_dataset(df)
print(f"Total chunks: {len(all_chunks)}")

# embed and save or load from disk
if os.path.exists("vector_store.index") and os.path.exists("metadata.json"):
    print("Vector store already exists, loading from disk...")
    index, metadata = load_vector_store()
else:
    print("Embedding all chunks... this will take a few minutes")
    all_embedded = embed_chunks(all_chunks)
    save_vector_store(all_embedded)
    index, metadata = load_vector_store()

print(f"FAISS index total vectors: {index.ntotal}")

# ask a question
response = ask("what is a catalyst?", index, metadata)
response = ask("who is Virat Kohli?", index, metadata)
print(f"\nAnswer:\n{response['answer']}")
print(f"\nSources:")
for source in response['sources']:
    print(f"- {source['title']}: {source['url']}")