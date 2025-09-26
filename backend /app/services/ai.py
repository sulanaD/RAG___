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
        # Keep the prompt small to reduce token usage: take the first 1200 chars
        sys = "Return only a concise factual title (<= 10 words). No extra text. Reply with the title only."
        prompt_text = page_text.strip()[:1200]
        try:
            r = client.chat.completions.create(
                model=OPENAI_MODEL_SUMMARY,
                messages=[{"role":"system","content":sys},{"role":"user","content":prompt_text}],
                temperature=0.0,
                max_tokens=24,
            )
            content = None
            # new OpenAI client shapes may vary; be defensive
            if hasattr(r, "choices") and r.choices:
                content = getattr(r.choices[0].message, "content", None) or getattr(r.choices[0], "text", None)
            if content:
                return content.strip().split("\n")[0]
        except Exception as e:
            # Log the error and fall back to mock title to avoid crashing and to limit retries
            print(f"⚠️ OpenAI title generation failed: {e}")
            # Fall through to mock below
    else:
        # Mock title generation based on first words
        words = page_text.strip().split()[:8]
        if not words:
            return "Untitled Document"
        title = " ".join(words).replace('\n', ' ')[:50]
        return f"{title}..." if len(title) == 50 else title

def page_summary(title: str, text: str, target_words: int = 140) -> str:
    if HAS_REAL_API_KEY and client:
        # Limit the input text to the first ~4000 chars to reduce tokens
        sys = (f"Summarize the page factually in {max(60, target_words-30)}–{target_words+30} words. "
               "Do not invent content; only use provided text.")
        user = f"Title: {title or 'Untitled'}\n\nText:\n{text.strip()[:4000]}"
        try:
            r = client.chat.completions.create(
                model=OPENAI_MODEL_SUMMARY,
                messages=[{"role":"system","content":sys},{"role":"user","content":user}],
                temperature=0.2,
                max_tokens=min(300, int(target_words * 2)),
            )
            # Defensive parsing of the response
            if hasattr(r, "choices") and r.choices:
                return getattr(r.choices[0].message, "content", None) or getattr(r.choices[0], "text", "").strip()
        except Exception as e:
            print(f"⚠️ OpenAI page_summary failed: {e}")
            # fall back to mock summary
            pass
    else:
        # Mock summary generation
        words = text.strip().split()
        if len(words) <= target_words:
            return text.strip()
        summary_text = " ".join(words[:target_words])
        return f"{summary_text}... [Mock summary - add real OpenAI API key for full functionality]"

def rag_answer(query: str, context_chunks: List[str], citations: List[dict] | None = None) -> str:
    """
    Generate a RAG-style answer from context_chunks. Optionally append a short mapping of
    citation markers [p1], [p2], ... to page numbers / chunk ids supplied in `citations`.

    citations: optional list of dicts with keys: page_number (int or None), chunk_id (str or None)
    """
    answer_text = None
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
        # Defensive parsing
        try:
            answer_text = getattr(r.choices[0].message, "content", None) or getattr(r.choices[0], "text", None)
        except Exception:
            answer_text = None

    # Mock or fallback
    if not answer_text:
        if not context_chunks:
            answer_text = f"I don't have enough context to answer: {query} [Mock mode - add real OpenAI API key]"
        else:
            first_chunk = context_chunks[0][:200]
            answer_text = f"Based on the available context: {first_chunk}... [p1] [Mock mode - add real OpenAI API key for full functionality]"

    answer_text = answer_text.strip()

    # Append a short, explicit mapping of citation markers to page numbers/chunk ids when provided.
    if citations:
        lines = ["\n\nSources:"]
        for i, c in enumerate(citations, 1):
            parts = []
            page = c.get("page_number") if isinstance(c, dict) else None
            cid = c.get("chunk_id") if isinstance(c, dict) else None
            if page:
                parts.append(f"page {page}")
            if cid and not page:
                # if page not available, at least include a short chunk id hint (first 8 chars)
                parts.append(f"chunk {str(cid)[:8]}")
            if not parts:
                parts.append("unknown location")
            lines.append(f"[p{i}] {', '.join(parts)}")
        answer_text = answer_text + "\n" + "\n".join(lines)

    return answer_text

