from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
from datasets import load_dataset
from embedder import embed_chunks
from processor import process_dataset
from vector_store import save_vector_store, load_vector_store
from assistant import ask
from document_processor import process_document
from spell_corrector import build_vocabulary

app = Flask(__name__)

# load dataset and vector store on startup
ds = load_dataset("iblai/ibl-khanacademy-transcripts")
df = pd.DataFrame(ds['train'])
all_chunks = process_dataset(df)

if os.path.exists("vector_store.index") and os.path.exists("metadata.json"):
    print("Vector store already exists, loading from disk...")
    index, metadata = load_vector_store()
else:
    print("Embedding all chunks... this will take a few minutes")
    all_embedded = embed_chunks(all_chunks)
    save_vector_store(all_embedded)
    index, metadata = load_vector_store()

# build vocabulary from metadata
vocabulary = build_vocabulary(metadata)
print(f"Vocabulary built: {len(vocabulary)} words")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    question = data.get("question", "")
    chat_history = data.get("chat_history", [])
    
    if not question:
        return jsonify({"error": "No question provided"}), 400
    
    response = ask(question, index, metadata, chat_history, vocabulary)
    return jsonify(response)

@app.route("/upload", methods=["POST"])
def upload_document():
    global index, metadata, vocabulary
    
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files["file"]
    filename = file.filename
    
    if not filename.endswith((".pdf", ".txt")):
        return jsonify({"error": "Only PDF and TXT files are supported"}), 400
    
    # process document into chunks
    new_chunks = process_document(file, filename)
    
    if not new_chunks:
        return jsonify({"error": "Could not process document"}), 400
    
    # embed new chunks
    new_embedded = embed_chunks(new_chunks)
    
    # add to existing FAISS index
    import numpy as np
    new_embeddings = np.array([chunk['embedding'] for chunk in new_embedded]).astype('float32')
    index.add(new_embeddings)
    
    # add to metadata
    for chunk in new_embedded:
        metadata.append({"text": chunk['text'], "title": chunk['title'], "video_url": chunk['video_url'], "chunk_index": chunk['chunk_index']})
    
    # rebuild vocabulary with new content
    vocabulary = build_vocabulary(metadata)
    
    return jsonify({"message": f"Successfully added {len(new_chunks)} chunks from {filename}"})

if __name__ == "__main__":
    app.run(debug=True)