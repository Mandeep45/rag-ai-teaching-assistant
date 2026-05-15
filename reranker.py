try:
    from sentence_transformers import CrossEncoder

    # load reranker model
    reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

    RERANKER_AVAILABLE = True

except ImportError:
    print("sentence-transformers not installed. Reranker disabled.")

    RERANKER_AVAILABLE = False


def rerank(query, chunks, top_k=5):
    """
    Rerank chunks based on relevance to query.
    """

    if not chunks:
        return chunks

    # fallback if reranker not available
    if not RERANKER_AVAILABLE:
        return chunks[:top_k]

    # create pairs of (query, chunk_text)
    pairs = [[query, chunk['text']] for chunk in chunks]

    # score each pair
    scores = reranker.predict(pairs)

    # attach scores to chunks
    for i, chunk in enumerate(chunks):
        chunk['rerank_score'] = float(scores[i])

    # sort by rerank score
    reranked = sorted(
        chunks,
        key=lambda x: x['rerank_score'],
        reverse=True
    )

    return reranked[:top_k]