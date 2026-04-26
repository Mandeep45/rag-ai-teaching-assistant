def chunk_text(text, title, video_url, chunk_size=500, overlap=50):
    """
    Split clean text into overlapping chunks with metadata.
    text: clean text from transcript_parser
    title: video title
    video_url: original youtube url
    chunk_size: number of words per chunk
    overlap: number of overlapping words between chunks
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "text": chunk_text,
            "title": title,
            "video_url": video_url,
            "chunk_index": len(chunks)
        })

        start = end - overlap

    return chunks