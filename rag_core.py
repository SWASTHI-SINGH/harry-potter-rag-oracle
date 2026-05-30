"""
rag_core.py — Harry Potter RAG Backend
Bridge between the notebook pipeline and the Streamlit UI (app.py)

Place this file in the SAME folder as:
  - harry_potter_rag_v3.ipynb
  - app.py
  - .env
  - data/         (contains chunks.pkl and vector_store/)
  - models/       (contains embedding_model/)
"""

import os, re, pickle, warnings
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import chromadb
from groq import Groq

warnings.filterwarnings('ignore')
load_dotenv()

# ── Paths (same as notebook) ──────────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.resolve()
PDF_DIR     = BASE_DIR / "pdf"
VECTOR_DIR  = BASE_DIR / "data" / "vector_store"
MODEL_DIR   = BASE_DIR / "models"
CHUNKS_FILE = BASE_DIR / "data" / "chunks.pkl"

# ── Book metadata ─────────────────────────────────────────────────────────────
BOOK_NAMES = {
    1: "HP1: Sorcerer's Stone",
    2: "HP2: Chamber of Secrets",
    3: "HP3: Prisoner of Azkaban",
    4: "HP4: Goblet of Fire",
    5: "HP5: Order of the Phoenix",
    6: "HP6: Half-Blood Prince",
    7: "HP7: Deathly Hallows",
}

# ── LLM config ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a knowledgeable Harry Potter expert assistant.
Answer questions using ONLY the provided book passages.
If the passages do not contain enough information, say so honestly.
Always cite which book and page the information comes from."""

# ── Lazy-loaded globals (loaded once on first call) ───────────────────────────
_embedding_model = None
_cross_encoder   = None
_vector_store    = None
_groq_client     = None
_chunks          = None


def _load_resources():
    """Load all models and data once, then cache in module globals."""
    global _embedding_model, _cross_encoder, _vector_store, _groq_client, _chunks

    if _embedding_model is not None:
        return  # already loaded

    print("🔄 Loading RAG resources (first call only)...")

    # 1. Embedding model
    model_path = MODEL_DIR / "embedding_model"
    if model_path.exists():
        _embedding_model = SentenceTransformer(str(model_path))
    else:
        _embedding_model = SentenceTransformer("all-mpnet-base-v2")
    print("   ✅ Embedding model loaded")

    # 2. Cross-encoder reranker
    _cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2', max_length=512)
    print("   ✅ Cross-encoder loaded")

    # 3. ChromaDB vector store
    client = chromadb.PersistentClient(path=str(VECTOR_DIR))
    _vector_store = client.get_collection("harry_potter_rag")
    print(f"   ✅ Vector store loaded ({_vector_store.count():,} docs)")

    # 4. Groq client
    if not GROQ_API_KEY:
        raise EnvironmentError("❌ GROQ_API_KEY not found in .env")
    _groq_client = Groq(api_key=GROQ_API_KEY)
    print("   ✅ Groq client ready")

    # 5. Chunks (for metadata)
    if CHUNKS_FILE.exists():
        with open(CHUNKS_FILE, "rb") as f:
            _chunks = pickle.load(f)
        print(f"   ✅ Chunks loaded ({len(_chunks):,})")

    print("🎉 All resources ready!\n")


# ── Core retrieval functions ──────────────────────────────────────────────────

def _embed(text: str) -> np.ndarray:
    vec = _embedding_model.encode([text], convert_to_numpy=True, normalize_embeddings=True)
    return vec[0]


def _retrieve(query: str, top_k: int = 40, book_filter: Optional[int] = None) -> List[Dict]:
    query_vec = _embed(query)
    kwargs = dict(
        query_embeddings=[query_vec.tolist()],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )
    if book_filter:
        kwargs["where"] = {"book_num": str(book_filter)}

    res = _vector_store.query(**kwargs)
    return [
        {
            "text"    : doc,
            "metadata": meta,
            "score"   : round(1 - dist, 4),
        }
        for doc, meta, dist in zip(
            res['documents'][0],
            res['metadatas'][0],
            res['distances'][0],
        )
    ]


def _rerank(query: str, candidates: List[Dict], top_k: int = 5) -> List[Dict]:
    scores = _cross_encoder.predict([(query, c['text']) for c in candidates])
    for c, s in zip(candidates, scores):
        c['rerank_score'] = float(s)
    return sorted(candidates, key=lambda x: x['rerank_score'], reverse=True)[:top_k]


def _build_context(chunks_list: List[Dict]) -> str:
    return "\n\n".join(
        f"[Passage {i} — {c['metadata'].get('book_name','?')}, "
        f"Page {c['metadata'].get('page','?')}]\n{c['text']}"
        for i, c in enumerate(chunks_list, 1)
    )


# ── Public API — called by app.py ─────────────────────────────────────────────

def ask(question: str, retrieve_k: int = 40, final_k: int = 5,
        book: Optional[int] = None) -> Dict:
    """
    Main entry point for the Streamlit UI.

    Args:
        question   : Natural language question about Harry Potter
        retrieve_k : Candidates to pull from ChromaDB (default 40)
        final_k    : Passages to send to LLM after reranking (default 5)
        book       : Restrict search to a specific book 1–7 (None = all books)

    Returns:
        {
            "answer" : str,
            "sources": [{"book": str, "page": str, "rerank_score": float}, ...]
        }
    """
    _load_resources()   # no-op after first call

    candidates = _retrieve(question, top_k=retrieve_k, book_filter=book)
    reranked   = _rerank(question, candidates, top_k=final_k)
    context    = _build_context(reranked)

    response = _groq_client.chat.completions.create(
        model      = GROQ_MODEL,
        messages   = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user',   'content': f'Book passages:\n{context}\n\nQuestion: {question}'},
        ],
        max_tokens  = 1024,
        temperature = 0.2,
    )

    return {
        'answer' : response.choices[0].message.content,
        'sources': [
            {
                'book'        : c['metadata'].get('book_name', '?'),
                'page'        : c['metadata'].get('page', '?'),
                'rerank_score': round(c['rerank_score'], 4),
            }
            for c in reranked
        ],
    }


# ── Quick test (run this file directly to verify) ─────────────────────────────
if __name__ == "__main__":
    print("🧪 Testing rag_core.py...\n")
    result = ask("Who gave Harry the invisibility cloak?")
    print("Answer:", result['answer'][:300], "...")
    print("\nSources:")
    for s in result['sources']:
        print(f"  {s['book']}, p.{s['page']}  (score: {s['rerank_score']})")
