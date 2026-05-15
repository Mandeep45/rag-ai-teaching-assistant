from sentence_transformers import CrossEncoder

# load reranker model
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query, chunks, top_k=5):
    """
    Rerank chunks based on relevance to query.
    query: student's question
    chunks: list of retrieved chunks from FAISS
    top_k: number of top chunks to return after reranking
    """
    if not chunks:
        return chunks

    # create pairs of (query, chunk_text)
    pairs = [[query, chunk['text']] for chunk in chunks]

    # score each pair
    scores = reranker.predict(pairs)

    # attach scores to chunks
    for i, chunk in enumerate(chunks):
        chunk['rerank_score'] = float(scores[i])

    # sort by rerank score (higher is better)
    reranked = sorted(chunks, key=lambda x: x['rerank_score'], reverse=True)

    return reranked[:top_k]