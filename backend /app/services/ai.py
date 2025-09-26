from typing import List
import random
import os
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL_SUMMARY, OPENAI_MODEL_RAG, OPENAI_EMBED_MODEL

# Check if we have valid API credentials
HAS_REAL_API_KEY = OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-") and len(OPENAI_API_KEY) > 20

if HAS_REAL_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None
    print("⚠️  Using mock AI services - no valid OpenAI API key detected")

def embed(texts: List[str]) -> List[List[float]]:
    if HAS_REAL_API_KEY and client:
        r = client.embeddings.create(model=OPENAI_EMBED_MODEL, input=texts)
        return [d.embedding for d in r.data]
    else:
        # Mock embeddings for testing - generate consistent random vectors
        random.seed(42)  # Consistent seed for reproducible results
        return [[random.random() for _ in range(1536)] for _ in texts]

def gen_title(page_text: str) -> str:
    if HAS_REAL_API_KEY and client:
        sys = "Return only a concise factual title (<= 12 words). No extra text."
        r = client.chat.completions.create(
            model=OPENAI_MODEL_SUMMARY,
            messages=[{"role":"system","content":sys},{"role":"user","content":page_text[:6000]}],
            temperature=0.2
        )
        return (r.choices[0].message.content or "Untitled").strip().split("\n")[0]
    else:
        # Mock title generation based on first words
        words = page_text.strip().split()[:8]
        if not words:
            return "Untitled Document"
        title = " ".join(words).replace('\n', ' ')[:50]
        return f"{title}..." if len(title) == 50 else title

def page_summary(title: str, text: str, target_words: int = 140) -> str:
    if HAS_REAL_API_KEY and client:
        sys = (f"Summarize the page factually in {target_words-30}–{target_words+30} words. "
               "Do not invent content; only use provided text.")
        user = f"Title: {title or 'Untitled'}\n\nText:\n{text[:8000]}"
        r = client.chat.completions.create(
            model=OPENAI_MODEL_SUMMARY,
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0.2
        )
        return r.choices[0].message.content.strip()
    else:
        # Mock summary generation
        words = text.strip().split()
        if len(words) <= target_words:
            return text.strip()
        summary_text = " ".join(words[:target_words])
        return f"{summary_text}... [Mock summary - add real OpenAI API key for full functionality]"

def rag_answer(query: str, context_chunks: List[str]) -> str:
    if HAS_REAL_API_KEY and client:
        sys = ("Answer using only the provided context. Cite with [p1], [p2] in order. "
               "If information is insufficient, say you don't know.")
        ctx = "".join(f"[p{i}] {t}\n\n" for i, t in enumerate(context_chunks, 1))
        r = client.chat.completions.create(
            model=OPENAI_MODEL_RAG,
            messages=[{"role":"system","content":sys},
                      {"role":"user","content":f"Question: {query}\n\nContext:\n{ctx}"}],
            temperature=0.0
        )
        return r.choices[0].message.content.strip()
    else:
        # Mock RAG answer
        if not context_chunks:
            return f"I don't have enough context to answer: {query} [Mock mode - add real OpenAI API key]"
        
        # Return first chunk with citation as mock answer
        first_chunk = context_chunks[0][:200]
        return f"Based on the available context: {first_chunk}... [p1] [Mock mode - add real OpenAI API key for full functionality]"

