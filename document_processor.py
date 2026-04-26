import PyPDF2
from chunker import chunk_text

def process_document(file, filename):
    """
    Process an uploaded document and return chunks.
    Supports PDF and TXT files.
    """
    if filename.endswith(".pdf"):
        return process_pdf(file, filename)
    elif filename.endswith(".txt"):
        return process_txt(file, filename)
    else:
        return []

def process_pdf(file, filename):
    """Extract text from PDF file."""
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        chunks = chunk_text(text, filename, "uploaded_document")
        return chunks
    except Exception as e:
        print(f"PDF processing failed: {e}")
        return []

def process_txt(file, filename):
    """Extract text from TXT file."""
    try:
        text = file.read().decode("utf-8")
        chunks = chunk_text(text, filename, "uploaded_document")
        return chunks
    except Exception as e:
        print(f"TXT processing failed: {e}")
        return []

