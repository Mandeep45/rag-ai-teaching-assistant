from groq import Groq
from retriever import retrieve
from spell_corrector import correct_spelling
from reranker import rerank
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
USE_RERANKER = os.getenv("USE_RERANKER", "false").lower() == "true"

def ask(question, index, metadata, chat_history=[], vocabulary=[]):
    # correct spelling mistakes
    question = correct_spelling(question, vocabulary)

    # build enriched query using chat history
    if chat_history:
        last_question = chat_history[-1]["question"]
        enriched_query = f"{last_question} {question}"
    else:
        enriched_query = question

    # retrieve chunks — more if reranker enabled
    top_k = 20 if USE_RERANKER else 5
    results = retrieve(enriched_query, index, metadata, top_k=top_k)

    if not results:
        return {
            "answer": "I don't have enough information in my knowledge base to answer this question.",
            "sources": []
        }

    # rerank if enabled
    if USE_RERANKER:
        results = rerank(question, results, top_k=5)

    # build context from chunks
    context = ""
    for i, result in enumerate(results):
        context += f"Source {i+1}: {result['title']}\n"
        context += f"{result['text']}\n\n"

    # build prompt
    prompt = f"""You are a helpful AI teaching assistant. Use the following context from Khan Academy videos to answer the student's question.
If the answer is not in the context, say "I don't have enough information to answer this question."

Context:
{context}

Student's Question: {question}

Answer:"""

    # build messages with history
    messages = []
    for chat in chat_history:
        messages.append({"role": "user", "content": chat["question"]})
        messages.append({"role": "assistant", "content": chat["answer"]})

    messages.append({"role": "user", "content": prompt})

    # call Groq API
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1000
    )

    # remove duplicate sources
    seen = set()
    unique_sources = []
    for r in results:
        if r['video_url'] not in seen:
            seen.add(r['video_url'])
            unique_sources.append({"title": r['title'], "url": r['video_url']})

    return {
        "answer": response.choices[0].message.content,
        "sources": unique_sources
    }