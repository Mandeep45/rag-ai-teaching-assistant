from flask import Flask, render_template, request, jsonify
import os
import numpy as np
from huggingface_hub import hf_hub_download
from embedder import embed_chunks
from vector_store import load_vector_store
from assistant import ask
from document_processor import process_document
from spell_corrector import build_vocabulary
from dotenv import load_dotenv
from database import init_db, save_message, get_history, get_all_sessions
import uuid

load_dotenv()
init_db()

app = Flask(__name__)

def download_vector_store():
    if not os.path.exists("vector_store.index"):
        print("Downloading vector_store.index from Hugging Face...")
        hf_hub_download(
            repo_id="Mandeep6345/khan-academy-vector-store",
            filename="vector_store.index",
            repo_type="dataset",
            local_dir="."
        )
    if not os.path.exists("metadata.json"):
        print("Downloading metadata.json from Hugging Face...")
        hf_hub_download(
            repo_id="Mandeep6345/khan-academy-vector-store",
            filename="metadata.json",
            repo_type="dataset",
            local_dir="."
        )
    print("Vector store ready!")

download_vector_store()

index, metadata = load_vector_store()
vocabulary = build_vocabulary(metadata)
print(f"Ready! {len(metadata)} chunks loaded.")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    question = data.get("question", "")
    chat_history = data.get("chat_history", [])
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not question:
        return jsonify({"error": "No question provided"}), 400

    response = ask(question, index, metadata, chat_history, vocabulary)

    # save to database
    save_message(session_id, question, response["answer"], response["sources"])

    response["session_id"] = session_id
    return jsonify(response)

@app.route("/history/<session_id>", methods=["GET"])
def get_session_history(session_id):
    history = get_history(session_id)
    return jsonify(history)

@app.route("/sessions", methods=["GET"])
def get_sessions():
    sessions = get_all_sessions()
    return jsonify(sessions)

@app.route("/upload", methods=["POST"])
def upload_document():
    global index, metadata, vocabulary

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    filename = file.filename

    if not filename.endswith((".pdf", ".txt")):
        return jsonify({"error": "Only PDF and TXT files are supported"}), 400

    new_chunks = process_document(file, filename)

    if not new_chunks:
        return jsonify({"error": "Could not process document"}), 400

    new_embedded = embed_chunks(new_chunks)
    new_embeddings = np.array([chunk['embedding'] for chunk in new_embedded]).astype('float32')
    index.add(new_embeddings)

    for chunk in new_embedded:
        metadata.append({"text": chunk['text'], "title": chunk['title'], "video_url": chunk['video_url'], "chunk_index": chunk['chunk_index']})

    vocabulary = build_vocabulary(metadata)

    return jsonify({"message": f"Successfully added {len(new_chunks)} chunks from {filename}"})

if __name__ == "__main__":
    app.run(debug=True)