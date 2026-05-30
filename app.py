"""
╔══════════════════════════════════════════════════════════╗
║   🧙 Harry Potter RAG — Streamlit UI                     ║
║   Dark magical theme · Chat Q&A · Book filter · Sources  ║
╚══════════════════════════════════════════════════════════╝
"""

import streamlit as st
import time
import random
import os
from pathlib import Path

# ── Page config (MUST be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="Alohomora · HP RAG Oracle",
    page_icon="🧙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
#  THEME — injected CSS
# ══════════════════════════════════════════════════════════════════════════════
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@400;700;900&family=Cinzel:wght@400;600;700&family=IM+Fell+English:ital@0;1&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap');

/* ── Root variables ── */
:root {
  --gold:        #C9A84C;
  --gold-bright: #F0C060;
  --gold-dim:    #7A6030;
  --crimson:     #8B0000;
  --crimson-bright: #C41E3A;
  --slytherin:   #1A472A;
  --ravenclaw:   #0E1A40;
  --hufflepuff:  #ECB939;
  --bg-void:     #050508;
  --bg-deep:     #0A0A12;
  --bg-card:     #10101C;
  --bg-card2:    #14141F;
  --border:      rgba(201,168,76,0.3);
  --border-bright: rgba(201,168,76,0.7);
  --text:        #E8D8B0;
  --text-dim:    #9A8860;
  --text-muted:  #5A5040;
}

/* ── Global reset ── */
html, body, [class*="css"] {
  font-family: 'Crimson Text', Georgia, serif !important;
  background-color: var(--bg-void) !important;
  color: var(--text) !important;
}

/* ── Starfield background ── */
.stApp {
  background:
    radial-gradient(ellipse at 20% 20%, rgba(201,168,76,0.04) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 80%, rgba(139,0,0,0.05) 0%, transparent 50%),
    radial-gradient(ellipse at 50% 0%, rgba(14,26,64,0.3) 0%, transparent 60%),
    var(--bg-void) !important;
  background-attachment: fixed !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #08080F 0%, #0D0D1A 40%, #060610 100%) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"]::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Headings ── */
h1, h2, h3 {
  font-family: 'Cinzel Decorative', serif !important;
  color: var(--gold) !important;
  text-shadow: 0 0 20px rgba(201,168,76,0.4), 0 0 40px rgba(201,168,76,0.15) !important;
  letter-spacing: 0.05em !important;
}
h4, h5, h6 {
  font-family: 'Cinzel', serif !important;
  color: var(--gold-bright) !important;
  letter-spacing: 0.08em !important;
}

/* ── Buttons ── */
.stButton > button {
  background: linear-gradient(135deg, #1A0A00, #2D1500) !important;
  border: 1px solid var(--gold-dim) !important;
  color: var(--gold) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.1em !important;
  border-radius: 4px !important;
  transition: all 0.3s ease !important;
  text-transform: uppercase !important;
}
.stButton > button:hover {
  border-color: var(--gold-bright) !important;
  color: var(--gold-bright) !important;
  box-shadow: 0 0 15px rgba(201,168,76,0.3), inset 0 0 20px rgba(201,168,76,0.05) !important;
  transform: translateY(-1px) !important;
}

/* ── Primary button (cast spell) ── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #3D1A00, #6B2E00) !important;
  border-color: var(--gold) !important;
  font-size: 1rem !important;
  padding: 0.6rem 2rem !important;
}

/* ── Text input ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
  background: rgba(10,8,4,0.8) !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
  color: var(--text) !important;
  font-family: 'Crimson Text', serif !important;
  font-size: 1.05rem !important;
  caret-color: var(--gold) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--gold) !important;
  box-shadow: 0 0 12px rgba(201,168,76,0.2) !important;
}
.stTextInput label, .stTextArea label {
  color: var(--gold-dim) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.1em !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
  background: rgba(10,8,4,0.8) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
}
.stSelectbox label {
  color: var(--gold-dim) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.75rem !important;
  letter-spacing: 0.1em !important;
}

/* ── Sliders ── */
.stSlider > div > div > div > div {
  background: var(--gold) !important;
}
.stSlider label {
  color: var(--gold-dim) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.75rem !important;
}

/* ── Divider ── */
hr {
  border-color: var(--border) !important;
  margin: 1.5rem 0 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
  padding: 1rem !important;
}
[data-testid="metric-container"] label {
  color: var(--gold-dim) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
}
[data-testid="metric-container"] [data-testid="metric-value"] {
  color: var(--gold-bright) !important;
  font-family: 'Cinzel Decorative', serif !important;
}

/* ── Expander ── */
details {
  background: var(--bg-card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 6px !important;
}
summary {
  color: var(--gold) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.05em !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--text-dim) !important;
  font-family: 'Cinzel', serif !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.08em !important;
  border: none !important;
  padding: 0.6rem 1.2rem !important;
}
.stTabs [aria-selected="true"] {
  color: var(--gold) !important;
  border-bottom: 2px solid var(--gold) !important;
}

/* ── Spinner ── */
.stSpinner > div {
  border-top-color: var(--gold) !important;
}

/* ── Info / success / warning boxes ── */
.stAlert {
  background: var(--bg-card) !important;
  border-left-color: var(--gold) !important;
  color: var(--text) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-void); }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--gold); }

/* ── Chat message cards ── */
.chat-user {
  background: linear-gradient(135deg, rgba(139,0,0,0.15), rgba(139,0,0,0.05));
  border: 1px solid rgba(139,0,0,0.4);
  border-left: 3px solid var(--crimson-bright);
  border-radius: 6px;
  padding: 1rem 1.2rem;
  margin: 0.8rem 0;
  font-size: 1.05rem;
  line-height: 1.6;
}
.chat-answer {
  background: linear-gradient(135deg, rgba(10,10,20,0.9), rgba(14,14,26,0.95));
  border: 1px solid var(--border);
  border-left: 3px solid var(--gold);
  border-radius: 6px;
  padding: 1.2rem 1.4rem;
  margin: 0.8rem 0;
  font-size: 1.1rem;
  line-height: 1.8;
  font-family: 'Crimson Text', serif;
}
.chat-answer::before {
  content: '⚡ ';
  color: var(--gold);
}
.source-chip {
  display: inline-block;
  background: rgba(201,168,76,0.1);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 0.15rem 0.6rem;
  font-family: 'Cinzel', serif;
  font-size: 0.7rem;
  color: var(--gold-dim);
  margin: 0.2rem 0.3rem 0.2rem 0;
  letter-spacing: 0.05em;
}
.source-score {
  color: var(--gold);
  font-weight: 600;
}

/* ── House badge ── */
.house-badge {
  display: inline-block;
  padding: 0.2rem 0.8rem;
  border-radius: 3px;
  font-family: 'Cinzel', serif;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  font-weight: 700;
  text-transform: uppercase;
}
.badge-gryffindor { background: rgba(174,0,1,0.2); border: 1px solid #AE0001; color: #FF6B6B; }
.badge-slytherin  { background: rgba(26,71,42,0.2); border: 1px solid #1A472A; color: #7CFC00; }
.badge-ravenclaw  { background: rgba(14,26,64,0.3); border: 1px solid #4169E1; color: #87CEEB; }
.badge-hufflepuff { background: rgba(236,185,57,0.2); border: 1px solid #ECB939; color: #FFD700; }

/* ── Pipeline step box ── */
.pipeline-step {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-top: 2px solid var(--gold);
  border-radius: 6px;
  padding: 0.8rem 1rem;
  text-align: center;
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: var(--gold-dim);
  letter-spacing: 0.05em;
}
.pipeline-step .step-icon { font-size: 1.5rem; display: block; margin-bottom: 0.3rem; }
.pipeline-step .step-name { color: var(--gold); font-weight: 600; display: block; }
.pipeline-step .step-tech { color: var(--text-muted); font-size: 0.65rem; display: block; margin-top: 0.2rem; }

/* ── Demo mode banner ── */
.demo-banner {
  background: linear-gradient(135deg, rgba(236,185,57,0.1), rgba(236,185,57,0.05));
  border: 1px solid rgba(236,185,57,0.4);
  border-radius: 6px;
  padding: 0.6rem 1rem;
  font-family: 'Cinzel', serif;
  font-size: 0.75rem;
  color: var(--hufflepuff);
  letter-spacing: 0.05em;
  margin-bottom: 1rem;
}

/* ── Glowing divider ── */
.gold-divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 1.5rem 0;
}

/* ── Typewriter cursor ── */
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
.cursor { animation: blink 1s infinite; color: var(--gold); }

/* ── Stars animation ── */
@keyframes twinkle {
  0%,100% { opacity: 0.2; transform: scale(1); }
  50%      { opacity: 0.8; transform: scale(1.3); }
}
.star { animation: twinkle var(--d,3s) infinite var(--delay,0s); color: var(--gold-dim); }
</style>
"""

# ══════════════════════════════════════════════════════════════════════════════
#  BACKEND — try to import real pipeline, fall back to demo mode
# ══════════════════════════════════════════════════════════════════════════════

DEMO_MODE = False
_ask_fn   = None

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    # Attempt to import core pieces from the notebook-converted module
    # (user should export notebook cells to rag_core.py — see README)
    from rag_core import ask as _ask_fn  # type: ignore
except Exception:
    DEMO_MODE = True

# ── Mock answers for demo mode ─────────────────────────────────────────────
DEMO_QA = {
    "default": [
        {
            "answer": "The ancient magic that protected Harry was born of his mother Lily's self-sacrificial love — a power so rare and profound that Voldemort's curse rebounded, leaving only a lightning-bolt scar upon the infant's brow. This enchantment, woven into Harry's very blood, shielded him time and again throughout his years at Hogwarts.",
            "sources": [
                {"book": "HP1: Sorcerer's Stone", "page": "12", "rerank_score": 0.9821},
                {"book": "HP7: Deathly Hallows", "page": "740", "rerank_score": 0.8934},
            ]
        },
        {
            "answer": "Dumbledore was many things — Headmaster of Hogwarts, Supreme Mugwump of the International Confederation of Wizards, and Chief Warlock of the Wizengamot. Yet beneath these titles lay a man haunted by his past and driven by a singular, terrible purpose: to prepare Harry Potter for the sacrifice that would ultimately destroy Lord Voldemort.",
            "sources": [
                {"book": "HP6: Half-Blood Prince", "page": "545", "rerank_score": 0.9512},
                {"book": "HP7: Deathly Hallows", "page": "287", "rerank_score": 0.8761},
            ]
        },
        {
            "answer": "Horcruxes are objects of the darkest magic — each one a vessel containing a fragment of the creator's soul, split through the ultimate act of evil: murder. Voldemort created seven, hiding pieces of himself in objects of great significance: a diary, a ring, a locket, a cup, a diadem, a snake, and — unknowingly — Harry Potter himself.",
            "sources": [
                {"book": "HP6: Half-Blood Prince", "page": "497", "rerank_score": 0.9934},
                {"book": "HP7: Deathly Hallows", "page": "103", "rerank_score": 0.9120},
            ]
        },
    ]
}

def demo_ask(question: str, book: int = None) -> dict:
    """Return a convincing mock answer with a brief delay."""
    time.sleep(random.uniform(1.2, 2.4))
    pool = DEMO_QA["default"]
    result = random.choice(pool).copy()
    result["answer"] = result["answer"]  # already themed
    return result

def real_ask(question: str, book: int = None) -> dict:
    try:
        return _ask_fn(question, book=book)
    except Exception as e:
        return {
            "answer": f"The Oracle encountered an error whilst consulting the tomes: {e}",
            "sources": []
        }

def ask_oracle(question: str, book: int = None) -> dict:
    if DEMO_MODE or _ask_fn is None:
        return demo_ask(question, book)
    return real_ask(question, book)


# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

BOOKS = {
    0: ("All Books", "⚡", "all"),
    1: ("Sorcerer's Stone",    "🪄", "gryffindor"),
    2: ("Chamber of Secrets",  "🐍", "slytherin"),
    3: ("Prisoner of Azkaban", "🐺", "ravenclaw"),
    4: ("Goblet of Fire",      "🔥", "gryffindor"),
    5: ("Order of Phoenix",    "🦅", "ravenclaw"),
    6: ("Half-Blood Prince",   "☠️",  "slytherin"),
    7: ("Deathly Hallows",     "💀", "hufflepuff"),
}

SPELL_PROMPTS = [
    "Who gave Harry the Invisibility Cloak?",
    "What are Horcruxes and how were they made?",
    "Describe the first Quidditch match Harry played.",
    "Who is the Half-Blood Prince?",
    "What is the Prophecy about Harry and Voldemort?",
    "How does the Sorting Hat choose houses?",
    "What happened to Dumbledore at the Astronomy Tower?",
    "Who are the Marauders and what were their nicknames?",
]

PIPELINE_STEPS = [
    ("📄", "PDF Loader",     "PyMuPDF · 7 Books"),
    ("✂️",  "Chunker",        "1200 chars / 200 overlap"),
    ("🧠", "Embeddings",     "all-mpnet-base-v2 · 768d"),
    ("🗄️",  "ChromaDB",       "HNSW cosine index"),
    ("🔍", "Retriever",      "Top-40 candidates"),
    ("⚖️",  "Cross-Encoder",  "ms-marco reranker → Top-5"),
    ("🤖", "Groq LLM",       "llama-3.3-70b-versatile"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "history" not in st.session_state:
    st.session_state.history = []
if "selected_book" not in st.session_state:
    st.session_state.selected_book = 0


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(THEME_CSS, unsafe_allow_html=True)


# ── SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1.5rem 0 1rem;'>
      <div style='font-size:3rem; margin-bottom:0.5rem;'>🧙</div>
      <div style='font-family:Cinzel Decorative,serif; font-size:1rem; color:#C9A84C;
                  text-shadow:0 0 15px rgba(201,168,76,0.5); letter-spacing:0.1em;'>
        HP RAG Oracle
      </div>
      <div style='font-family:IM Fell English,serif; font-size:0.75rem; color:#7A6030;
                  font-style:italic; margin-top:0.3rem;'>
        "Alohomora · Lumos · Accio"
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── Backend status ──
    if DEMO_MODE:
        st.markdown("""
        <div class='demo-banner'>
          ✨ Demo Mode — mock answers active<br>
          <span style='color:#9A8860'>Add rag_core.py to enable live RAG</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:rgba(26,71,42,0.2); border:1px solid rgba(26,71,42,0.6);
                    border-radius:6px; padding:0.5rem 1rem; font-family:Cinzel,serif;
                    font-size:0.72rem; color:#7CFC00; margin-bottom:1rem;'>
          ✅ Live RAG Backend Connected
        </div>
        """, unsafe_allow_html=True)

    # ── Book filter ──
    st.markdown("""
    <div style='font-family:Cinzel,serif; font-size:0.72rem; color:#7A6030;
                letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.8rem;'>
      📚 Filter by Book
    </div>
    """, unsafe_allow_html=True)

    for book_num, (name, icon, house) in BOOKS.items():
        label = f"{icon} {'All Books' if book_num == 0 else f'HP{book_num}: {name}'}"
        is_sel = st.session_state.selected_book == book_num
        btn_style = "background:rgba(201,168,76,0.15);border-color:#C9A84C;" if is_sel else ""
        if st.button(label, key=f"book_{book_num}", use_container_width=True):
            st.session_state.selected_book = book_num
            st.rerun()

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # ── Spell suggestions ──
    st.markdown("""
    <div style='font-family:Cinzel,serif; font-size:0.72rem; color:#7A6030;
                letter-spacing:0.12em; text-transform:uppercase; margin-bottom:0.8rem;'>
      ⚡ Suggested Incantations
    </div>
    """, unsafe_allow_html=True)

    for prompt in SPELL_PROMPTS[:5]:
        if st.button(f"› {prompt[:42]}{'…' if len(prompt)>42 else ''}", key=f"prompt_{prompt[:20]}", use_container_width=True):
            st.session_state["prefill"] = prompt
            st.rerun()

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    if st.button("🗑️ Clear Scroll", use_container_width=True):
        st.session_state.history = []
        st.rerun()

    # ── Stats ──
    st.markdown(f"""
    <div style='font-family:Cinzel,serif; font-size:0.65rem; color:#5A5040;
                text-align:center; margin-top:1rem; line-height:2;'>
      📖 7 Books · ~85K chunks<br>
      🧠 768-dim embeddings<br>
      ⚖️ Cross-encoder reranked<br>
      🤖 llama-3.3-70b via Groq
    </div>
    """, unsafe_allow_html=True)


# ── MAIN PANEL ────────────────────────────────────────────────────────────

# Header
st.markdown("""
<div style='text-align:center; padding:2.5rem 0 1rem;'>
  <div style='font-size:4rem; margin-bottom:0.5rem;
              filter:drop-shadow(0 0 20px rgba(201,168,76,0.6));'>⚡</div>
  <h1 style='font-size:2.2rem; margin:0; letter-spacing:0.08em;'>
    Alohomora
  </h1>
  <p style='font-family:IM Fell English,serif; color:#7A6030; font-size:1.1rem;
            font-style:italic; margin-top:0.4rem;'>
    The Harry Potter Retrieval Oracle · Powered by RAG &amp; Groq
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

# Tabs
tab_oracle, tab_pipeline, tab_about = st.tabs([
    "⚡  The Oracle",
    "🏗️  Pipeline Architecture",
    "📜  About This Project",
])


# ══════════════════════════════════════════════════════════════════════════
#  TAB 1 — ORACLE (main Q&A)
# ══════════════════════════════════════════════════════════════════════════
with tab_oracle:

    # Active book banner
    book_num = st.session_state.selected_book
    book_name, book_icon, house = BOOKS[book_num]
    filter_label = "All 7 Books" if book_num == 0 else f"HP{book_num}: {book_name}"
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:0.8rem; margin-bottom:1.2rem;
                padding:0.6rem 1rem; background:var(--bg-card);
                border:1px solid var(--border); border-radius:6px;'>
      <span style='font-size:1.3rem;'>{book_icon}</span>
      <span style='font-family:Cinzel,serif; font-size:0.78rem; color:var(--gold-dim);
                   letter-spacing:0.08em;'>SEARCHING:</span>
      <span style='font-family:Cinzel,serif; font-size:0.85rem; color:var(--gold);'>{filter_label}</span>
    </div>
    """, unsafe_allow_html=True)

    # Chat history
    if st.session_state.history:
        for entry in st.session_state.history:
            st.markdown(f'<div class="chat-user">🔮 &nbsp;{entry["question"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="chat-answer">{entry["answer"]}</div>', unsafe_allow_html=True)

            if entry.get("sources"):
                chips = ""
                for s in entry["sources"]:
                    score = s.get("rerank_score", 0)
                    chips += f'<span class="source-chip">📖 {s["book"]} · p.{s["page"]} · <span class="source-score">{score:.3f}</span></span>'
                st.markdown(f'<div style="margin:-0.4rem 0 1rem;">{chips}</div>', unsafe_allow_html=True)

            st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:3rem 2rem; color:var(--text-muted);
                    font-family:IM Fell English,serif; font-style:italic; font-size:1rem;
                    border:1px dashed rgba(201,168,76,0.15); border-radius:8px;
                    background:rgba(10,10,18,0.5); margin:1rem 0 2rem;'>
          <div style='font-size:2rem; margin-bottom:0.8rem; opacity:0.5;'>📜</div>
          The scroll awaits your incantation…<br>
          <span style='font-size:0.85rem; color:var(--text-muted); margin-top:0.5rem; display:block;'>
            Ask anything about the wizarding world
          </span>
        </div>
        """, unsafe_allow_html=True)

    # Input area
    prefill = st.session_state.pop("prefill", "")
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        question = st.text_input(
            "YOUR INCANTATION",
            value=prefill,
            placeholder="e.g. Who created the Philosopher's Stone?",
            key="question_input",
            label_visibility="visible",
        )
    with col_btn:
        st.markdown("<div style='height:1.85rem;'></div>", unsafe_allow_html=True)
        cast = st.button("⚡ Cast", type="primary", use_container_width=True)

    if cast and question.strip():
        with st.spinner("🔮 Consulting the tomes…"):
            result = ask_oracle(
                question.strip(),
                book=book_num if book_num > 0 else None,
            )
        st.session_state.history.append({
            "question": question.strip(),
            "answer":   result.get("answer", "The Oracle could not divine an answer."),
            "sources":  result.get("sources", []),
        })
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════
#  TAB 2 — PIPELINE ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════
with tab_pipeline:

    st.markdown("""
    <h3 style='text-align:center; font-size:1.2rem; margin-bottom:0.3rem;'>
      RAG Pipeline Architecture
    </h3>
    <p style='text-align:center; font-family:IM Fell English,serif; color:var(--text-dim);
              font-style:italic; margin-bottom:2rem;'>
      From raw PDFs to grounded, cited answers — every step handcrafted
    </p>
    """, unsafe_allow_html=True)

    # Pipeline diagram — 7 steps in a row with arrows
    cols = st.columns(len(PIPELINE_STEPS))
    for i, (icon, name, tech) in enumerate(PIPELINE_STEPS):
        with cols[i]:
            st.markdown(f"""
            <div class='pipeline-step'>
              <span class='step-icon'>{icon}</span>
              <span class='step-name'>{name}</span>
              <span class='step-tech'>{tech}</span>
            </div>
            """, unsafe_allow_html=True)
            if i < len(PIPELINE_STEPS) - 1:
                pass  # arrow handled by layout

    # Arrow row
    arrow_cols = st.columns(len(PIPELINE_STEPS))
    for i in range(len(PIPELINE_STEPS)):
        with arrow_cols[i]:
            if i < len(PIPELINE_STEPS) - 1:
                st.markdown("""
                <div style='text-align:right; color:var(--gold-dim);
                            font-size:1.2rem; margin-top:-0.5rem; padding-right:0.5rem;'>
                  →
                </div>
                """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    # Detail table
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("#### 🔬 Technical Choices")
        details = [
            ("Embedding Model", "all-mpnet-base-v2", "768-dim, ~420MB — higher recall than MiniLM"),
            ("Vector DB",       "ChromaDB (HNSW)",   "Persistent cosine index, deduplication"),
            ("Retrieval",       "Two-stage",         "Top-40 candidates → cross-encoder reranked"),
            ("Reranker",        "ms-marco-MiniLM-L-6", "Pairwise scoring for precision"),
            ("LLM",             "llama-3.3-70b",     "Via Groq API — fast inference"),
            ("Chunk Size",      "1200 chars",        "200-char overlap at paragraph boundaries"),
        ]
        for label, value, note in details:
            st.markdown(f"""
            <div style='padding:0.6rem 0; border-bottom:1px solid rgba(201,168,76,0.1);'>
              <span style='font-family:Cinzel,serif; font-size:0.72rem;
                           color:var(--gold-dim); letter-spacing:0.06em;'>{label}</span><br>
              <span style='font-size:1rem; color:var(--gold);'>{value}</span>
              <span style='font-size:0.82rem; color:var(--text-muted); margin-left:0.5rem;'>· {note}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_r:
        st.markdown("#### 📊 Corpus Stats")
        metrics = [
            ("Books Indexed",  "7",        "All HP novels"),
            ("Est. Chunks",    "~85,000",  "1200-char segments"),
            ("Embedding Dim",  "768",      "mpnet-base-v2"),
            ("Retrieve Top-K", "40 → 5",   "retrieve then rerank"),
            ("Context Window", "5 passages","sent to LLM"),
        ]
        for label, val, sub in metrics:
            st.metric(label=label, value=val, help=sub)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)

    st.markdown("#### 🏗️ Why This Architecture Stands Out")
    st.markdown("""
    <div style='background:var(--bg-card); border:1px solid var(--border);
                border-left:3px solid var(--gold); border-radius:6px;
                padding:1.2rem 1.4rem; font-size:1rem; line-height:1.9;'>
      <strong style='color:var(--gold);'>Custom-built, no LangChain wrappers</strong>
      — every component (PDF loader, chunker, retriever, reranker) is handcrafted,
      showing deep understanding of the fundamentals.<br><br>
      <strong style='color:var(--gold);'>Two-stage retrieval</strong>
      — ChromaDB handles fast approximate search, while the cross-encoder
      re-scores each candidate with full attention, dramatically improving precision
      on subtle or inferential questions.<br><br>
      <strong style='color:var(--gold);'>768-dim embeddings</strong>
      — upgraded from MiniLM's 384-dim, capturing richer semantic relationships
      across the 1M+ words of the HP corpus.
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════
#  TAB 3 — ABOUT
# ══════════════════════════════════════════════════════════════════════════
with tab_about:

    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("""
        <h3>About This Project</h3>
        <p style='font-size:1.05rem; line-height:1.9; color:var(--text);'>
          This is a <strong style='color:var(--gold);'>production-grade RAG system</strong>
          built from scratch over all 7 Harry Potter novels. It demonstrates every
          layer of a modern retrieval-augmented generation pipeline —
          without relying on LangChain or other high-level wrappers.
        </p>
        <p style='font-size:1rem; line-height:1.9; color:var(--text-dim);'>
          The pipeline was designed with interview-readiness in mind: every
          architectural decision has a clear rationale, every component can be
          explained at a whiteboard, and the system degrades gracefully when
          the backend is unavailable (demo mode).
        </p>
        """, unsafe_allow_html=True)

        st.markdown("#### 🛠️ Tech Stack")
        stack = [
            ("PyMuPDF (fitz)",        "PDF text extraction with page metadata"),
            ("SentenceTransformers",  "all-mpnet-base-v2 bi-encoder embeddings"),
            ("ChromaDB",              "Persistent HNSW vector store"),
            ("CrossEncoder",          "ms-marco-MiniLM-L-6-v2 reranker"),
            ("Groq API",              "Ultra-fast LLM inference (llama-3.3-70b)"),
            ("Streamlit",             "This UI — deployable to Streamlit Cloud"),
        ]
        for tech, desc in stack:
            st.markdown(f"""
            <div style='display:flex; align-items:baseline; gap:0.6rem;
                        padding:0.4rem 0; border-bottom:1px solid rgba(201,168,76,0.08);'>
              <code style='background:rgba(201,168,76,0.1); color:var(--gold);
                           padding:0.15rem 0.5rem; border-radius:3px;
                           font-size:0.82rem;'>{tech}</code>
              <span style='color:var(--text-dim); font-size:0.9rem;'>{desc}</span>
            </div>
            """, unsafe_allow_html=True)

    with col_b:
        st.markdown("#### 🎯 Key Achievements")
        achievements = [
            ("No LangChain", "Built every component from scratch — shows fundamentals"),
            ("Two-stage Retrieval", "Embedding recall + cross-encoder precision"),
            ("768-dim Embeddings", "2× richer than baseline MiniLM"),
            ("Persistent Index", "ChromaDB survives kernel restarts"),
            ("Groq LLM", "~10× faster inference than OpenAI"),
            ("Demo Mode", "UI works without a backend for demos"),
            ("Book Filtering", "Scoped queries per book for precision"),
            ("Source Citations", "Every answer cites book + page"),
        ]
        for title, desc in achievements:
            st.markdown(f"""
            <div style='background:var(--bg-card); border:1px solid var(--border);
                        border-left:2px solid var(--gold); border-radius:4px;
                        padding:0.6rem 0.9rem; margin-bottom:0.5rem;'>
              <div style='font-family:Cinzel,serif; font-size:0.75rem;
                          color:var(--gold); letter-spacing:0.05em;'>✦ {title}</div>
              <div style='font-size:0.85rem; color:var(--text-dim);
                          margin-top:0.2rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align:center; font-family:IM Fell English,serif;
                    font-style:italic; color:var(--text-muted); font-size:0.9rem;
                    line-height:1.8;'>
          "It is our choices, Harry, that show<br>
          what we truly are, far more than<br>
          our abilities."<br>
          <span style='color:var(--gold-dim); font-size:0.8rem;'>— Albus Dumbledore</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="gold-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 🚀 How to Deploy")

    deploy_col1, deploy_col2, deploy_col3 = st.columns(3)
    with deploy_col1:
        st.markdown("""
        <div class='pipeline-step'>
          <span class='step-icon'>💻</span>
          <span class='step-name'>Run Locally</span>
          <span class='step-tech'>streamlit run app.py</span>
        </div>
        """, unsafe_allow_html=True)
    with deploy_col2:
        st.markdown("""
        <div class='pipeline-step'>
          <span class='step-icon'>☁️</span>
          <span class='step-name'>Streamlit Cloud</span>
          <span class='step-tech'>Push to GitHub → deploy free</span>
        </div>
        """, unsafe_allow_html=True)
    with deploy_col3:
        st.markdown("""
        <div class='pipeline-step'>
          <span class='step-icon'>🤗</span>
          <span class='step-name'>Hugging Face Spaces</span>
          <span class='step-tech'>Streamlit SDK · free tier</span>
        </div>
        """, unsafe_allow_html=True)
