import streamlit as st
import os
from qdrant_client import QdrantClient
from src.database import get_retriever, get_qdrant_credentials
from src.llm import optimise_query, full_context, get_legal_answer, load_llm

# ─── 1. Page Config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Nyaya Mitra — AI Legal Advisor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── 2. Theme ─────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

def toggle_theme():
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"

IS_DARK = st.session_state.theme == "dark"

# ─── 3. CSS Design System ─────────────────────────────────────────────────────
css = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

:root {{
    --bg:           {"#09090b" if IS_DARK else "#ffffff"};
    --bg-subtle:    {"#0c0c0f" if IS_DARK else "#f9fafb"};
    --card:         {"#111115" if IS_DARK else "#ffffff"};
    --card-hover:   {"#16161b" if IS_DARK else "#f4f4f5"};
    --border:       {"#1e1e28" if IS_DARK else "#e4e4e7"};
    --text:         {"#f2f2f5" if IS_DARK else "#09090b"};
    --text-muted:   {"#8b8b99" if IS_DARK else "#6b6b80"};
    --text-dim:     {"#44445a" if IS_DARK else "#b0b0c0"};
    --accent:       #3b82f6;
    --accent-deep:  #1d4ed8;
    --gold:         {"#f59e0b" if IS_DARK else "#d97706"};
    --gold-bg:      {"rgba(245,158,11,0.10)" if IS_DARK else "rgba(217,119,6,0.07)"};
    --green:        {"#22c55e" if IS_DARK else "#16a34a"};
    --green-bg:     {"rgba(34,197,94,0.10)" if IS_DARK else "rgba(22,163,74,0.07)"};
    --red:          {"#ef4444" if IS_DARK else "#dc2626"};
    --red-bg:       {"rgba(239,68,68,0.10)" if IS_DARK else "rgba(220,38,38,0.07)"};
    --radius:       14px;
    --shadow:       {"0 0 0 1px rgba(255,255,255,0.03), 0 4px 24px rgba(0,0,0,0.45)" if IS_DARK else "0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.05)"};
}}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"],
.main, .block-container, section[data-testid="stMain"] {{
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', -apple-system, sans-serif !important;
}}

header[data-testid="stHeader"], footer {{ display: none !important; }}

.block-container {{
    padding: 1.75rem 2.25rem 2.5rem !important;
    max-width: 1500px !important;
}}

section[data-testid="stSidebar"] {{
    background-color: var(--bg-subtle) !important;
    border-right: 1px solid var(--border) !important;
}}

/* ── Brand ── */
.brand-wrap {{ margin-bottom: 1.25rem; }}
.brand-logo {{
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 45%, #1d4ed8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.04em;
    line-height: 1.1;
}}
.brand-sub {{
    font-size: 0.82rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
    letter-spacing: 0.01em;
}}

/* ── Cards ── */
.card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
    transition: border-color 0.2s, background 0.2s;
}}
.card:hover {{ border-color: var(--text-dim); background: var(--card-hover); }}
.card-head {{ font-size: 0.92rem; font-weight: 700; color: var(--text); margin-bottom: 0.3rem; }}
.card-meta {{ font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.8rem; }}
.card-body {{ font-size: 0.85rem; color: var(--text-muted); line-height: 1.65; font-family: 'JetBrains Mono', monospace; }}

/* ── Hero card ── */
.hero-card {{
    background: {"linear-gradient(135deg, #0f1729 0%, #0a1020 100%)" if IS_DARK else "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)"};
    border: 1px solid {"#1e2d4a" if IS_DARK else "#bfdbfe"};
    border-radius: var(--radius);
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.5rem;
}}
.hero-title {{
    font-size: 1.9rem;
    font-weight: 800;
    background: linear-gradient(135deg, #93c5fd 0%, #3b82f6 50%, #1d4ed8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.03em;
    margin-bottom: 0.3rem;
}}
.hero-sub {{
    font-size: 0.88rem;
    color: var(--text-muted);
    line-height: 1.5;
}}

/* ── Answer card ── */
.answer-card {{
    background: var(--card);
    border: 1px solid {"#1e3a6e" if IS_DARK else "#bfdbfe"};
    border-left: 4px solid var(--accent);
    border-radius: var(--radius);
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.2rem;
    box-shadow: var(--shadow);
}}
.answer-head {{
    font-size: 1rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}
.answer-meta {{ font-size: 0.78rem; color: var(--text-muted); margin-bottom: 1rem; }}
.answer-body {{ font-size: 0.92rem; line-height: 1.75; color: var(--text); }}

/* ── Badges ── */
.badge {{
    display: inline-block;
    padding: 2px 9px;
    border-radius: 5px;
    font-size: 0.70rem;
    font-weight: 600;
    margin-right: 5px;
    margin-bottom: 5px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    border: 1px solid transparent;
}}
.b-blue  {{ color: var(--accent); background: rgba(59,130,246,0.12); border-color: rgba(59,130,246,0.25); }}
.b-gold  {{ color: var(--gold);   background: var(--gold-bg);          border-color: rgba(245,158,11,0.25); }}
.b-green {{ color: var(--green);  background: var(--green-bg);         border-color: rgba(34,197,94,0.25); }}
.b-red   {{ color: var(--red);    background: var(--red-bg);           border-color: rgba(239,68,68,0.25); }}
.b-gray  {{ color: var(--text-muted); background: rgba(255,255,255,0.03); border-color: var(--border); }}

/* ── Query box ── */
.query-card {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 0.6rem 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.84rem;
    color: var(--accent);
    word-break: break-word;
}}

/* ── Streamlit overrides ── */
[data-testid="stHorizontalBlock"] {{ gap: 1.5rem !important; }}
div[data-baseweb="textarea"] {{
    background-color: var(--bg-subtle) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}}
textarea {{ color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }}

.stButton > button {{
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}}
.stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    border: none !important;
    color: white !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity: 0.9 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(59,130,246,0.4) !important;
}}

div[data-testid="stStatusWidget"] {{
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}}
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# ─── 4. Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="brand-wrap">
        <div class="brand-logo">⚖️ Nyaya Mitra</div>
        <div class="brand-sub">AI Legal Advisor · Indian Law</div>
    </div>
    """, unsafe_allow_html=True)

    theme_label = "☀️ Switch to Light" if IS_DARK else "🌙 Switch to Dark"
    st.button(theme_label, on_click=toggle_theme, use_container_width=True)
    st.markdown("---")

    # ── DB Status ──
    st.markdown("**📡 Database**")
    qdrant_url, qdrant_api_key = get_qdrant_credentials()
    if qdrant_url and qdrant_api_key:
        try:
            client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=10)
            info = client.get_collection("legal_system")
            count = info.points_count
            st.markdown(f'<span class="badge b-green">● Connected</span>', unsafe_allow_html=True)
            st.markdown(f"Collection: `legal_system`  \nIndexed: **{count:,} records**")
        except Exception as e:
            st.markdown(f'<span class="badge b-red">● Error</span>', unsafe_allow_html=True)
            st.caption(str(e)[:80])
    else:
        st.markdown('<span class="badge b-red">● No Credentials</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── LLM Status ──
    st.markdown("**🤖 Model Info**")
    st.markdown("""
    - **LLM:** `Llama 3.3 70B` via Groq
    - **Embeddings:** `ModernBERT-legal`
    - **Vector DB:** Qdrant Cloud
    """)

    st.markdown("---")

    # ── Acts covered ──
    st.markdown("**📚 Covered Laws**")
    acts = ["Constitution of India", "BNS", "BNSS", "BSA",
            "Motor Vehicles Act", "IT Act", "POSH Act", "Income Tax Act"]
    for act in acts:
        st.markdown(f'<span class="badge b-blue">{act}</span>', unsafe_allow_html=True)

    st.markdown("---")

    # ── Sample Queries ──
    st.markdown("**💡 Try a Scenario**")
    samples = [
        ("🚗 Traffic Stop & Rights",
         "An RTO officer stopped me, snatched my bike keys, and insulted me in front of a crowd. My PUC certificate was wet due to rain. People gathered and beat us. What are my legal rights?"),
        ("💰 Unpaid Debt Recovery",
         "I lent my friend ₹50,000 six months ago and he refuses to return it. What legal action can I take under Indian law?"),
        ("👩 POSH Act Protection",
         "My male colleague repeatedly makes uncomfortable jokes about my appearance in team meetings and on WhatsApp groups. How does the POSH Act protect me?"),
        ("💻 Cybercrime & IT Act",
         "Someone hacked my Instagram account and is sending fraudulent messages to my contacts asking for money. What sections of the IT Act apply?"),
    ]
    for label, text in samples:
        if st.button(label, key=f"sample_{label[:15]}", use_container_width=True):
            st.session_state.user_query = text

    st.markdown("---")
    st.caption("⚠️ For educational purposes only. Not a substitute for professional legal counsel.")


# ─── 5. Main Content ──────────────────────────────────────────────────────────

# Hero header
st.markdown("""
<div class="hero-card">
    <div class="hero-title">⚖️ Nyaya Mitra AI</div>
    <div class="hero-sub">
        Your expert AI legal guide across the Constitution of India, BNS, BNSS, BSA,
        Motor Vehicles Act, Information Technology Act, POSH Act, and Income Tax Act.
        Powered by Llama 3.3 70B &amp; Qdrant vector retrieval.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Query Input ──
if "user_query" not in st.session_state:
    st.session_state.user_query = ""

user_input = st.text_area(
    "Describe your legal scenario or question:",
    value=st.session_state.user_query,
    height=140,
    placeholder="e.g., A police officer confiscated my phone during a routine traffic check. What are my rights under BNSS?",
    key="query_input",
)

col_btn1, col_btn2 = st.columns([5, 1])
with col_btn1:
    submit = st.button("⚖️ Get Legal Advice", type="primary", use_container_width=True)
with col_btn2:
    clear = st.button("🗑️ Clear", use_container_width=True)

if clear:
    st.session_state.user_query = ""
    st.rerun()

# ─── 6. Inference Pipeline ────────────────────────────────────────────────────
if submit and user_input.strip():
    if not qdrant_url or not qdrant_api_key:
        st.error("❌ Qdrant credentials missing. Add them to `.streamlit/secrets.toml`.")
        st.stop()

    with st.status("🔄 Processing your legal query...", expanded=True) as status:
        # Step 1: Load retriever
        status.write("Connecting to vector database...")
        try:
            retriever = get_retriever()
        except Exception as e:
            status.update(label="❌ Database connection failed", state="error")
            st.error(f"Could not connect to Qdrant: {e}")
            st.stop()

        # Step 2: Optimise query
        status.write("Optimizing query for legal retrieval...")
        try:
            optimized = optimise_query(user_input)
        except Exception as e:
            optimized = user_input  # fallback gracefully
            status.write(f"⚠️ Query optimization skipped: {e}")

        # Step 3: Retrieve docs
        status.write("Retrieving relevant legal provisions...")
        retrieved_docs = retriever.invoke(optimized)

        # Step 4: Generate answer
        status.write("Generating legal analysis with Llama 3.3 70B...")
        try:
            context_str = full_context(retrieved_docs)
            advice = get_legal_answer(context_str, user_input)
        except Exception as e:
            status.update(label="❌ LLM generation failed", state="error")
            st.error(f"Could not generate answer: {e}")
            st.stop()

        status.update(label="✅ Legal advice ready!", state="complete")

    # ── Results Layout ──
    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Optimized query
        st.markdown(f"""
        <div class="card">
            <div class="card-head">🔍 Optimized Search Query</div>
            <div class="card-meta">Grammar-corrected &amp; semantically enhanced for retrieval</div>
            <div class="query-card">{optimized}</div>
        </div>
        """, unsafe_allow_html=True)

        # Legal advice
        st.markdown(f"""
        <div class="answer-card">
            <div class="answer-head">⚖️ Official Legal Analysis</div>
            <div class="answer-meta">Generated strictly from retrieved Indian legal provisions · Llama 3.3 70B · Qdrant RAG</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(advice)

    with col_right:
        st.markdown("### 📚 Retrieved Legal Provisions")
        if not retrieved_docs:
            st.info("No explicit provisions matched. Try rephrasing your query.")
        else:
            for idx, doc in enumerate(retrieved_docs, 1):
                meta = doc.metadata
                doc_name  = meta.get("document", "Unknown").upper()
                chapter   = meta.get("chapter", "")
                section   = meta.get("section", "")
                article   = meta.get("article", "")
                part      = meta.get("part", "")

                badges = f'<span class="badge b-blue">{doc_name}</span>'
                if part and str(part) not in ("None", ""):
                    badges += f'<span class="badge b-gray">{part}</span>'
                if chapter and str(chapter) not in ("None", ""):
                    badges += f'<span class="badge b-gray">{chapter}</span>'
                if section and str(section) not in ("None", ""):
                    badges += f'<span class="badge b-gold">§ {section}</span>'
                if article and str(article) not in ("None", ""):
                    badges += f'<span class="badge b-gold">Art. {article}</span>'

                preview = doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else "")
                st.markdown(f"""
                <div class="card">
                    <div style="margin-bottom:0.5rem;">{badges}</div>
                    <div class="card-body">{preview}</div>
                </div>
                """, unsafe_allow_html=True)

elif submit and not user_input.strip():
    st.warning("⚠️ Please enter a legal question or scenario first.")
