# Nyaya Mitra — AI Legal Advisor

**Nyaya Mitra** is a Retrieval-Augmented Generation (RAG) application that provides AI-powered legal guidance across major Indian laws. It uses **Llama 3.3 70B** (via Groq API) for generation and **ModernBERT-legal** embeddings stored in **Qdrant Cloud** for retrieval.

## 📚 Covered Laws
- Constitution of India
- Bhartiya Nyaya Sanhita (BNS)
- Bhartiya Nagrik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)
- Motor Vehicles Act
- Information Technology Act
- Prevention of Sexual Harassment at Workplace Act (POSH)
- Income Tax Act

---

## 🏗️ Project Structure
```
rag-legal-advisor/
├── app.py                  # Streamlit application
├── ingest.py               # One-time DB ingestion script
├── requirements.txt        # Python dependencies
├── Dockerfile              # HuggingFace Spaces Docker config
├── .dockerignore
├── .gitignore
├── data/                   # (local only, gitignored) PDF source files
│   ├── constituition.pdf
│   ├── bns.pdf  bnss.pdf  bsa.pdf
│   ├── motor.pdf  info_tech.pdf  posh.pdf  income.pdf
└── src/
    ├── __init__.py
    ├── parsers.py           # Custom PDF parsers per act
    ├── database.py          # Qdrant + embeddings
    └── llm.py               # Groq LLM + RAG chain
```

---

## 🚀 Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/YOUR_USERNAME/nyaya-mitra.git
cd nyaya-mitra
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 2. Set Secrets
Create `.streamlit/secrets.toml`:
```toml
qdrant_url     = "https://YOUR-CLUSTER.qdrant.io"
qdrant_api_key = "YOUR_QDRANT_API_KEY"
groq_api_key   = "gsk_YOUR_GROQ_KEY"
```
Get a free Groq key at [console.groq.com](https://console.groq.com).

### 3. Ingest Documents (one-time)
Place your PDFs in `data/` then run:
```bash
.venv\Scripts\python.exe -u ingest.py
```

### 4. Run App
```bash
streamlit run app.py
```

---

## 🐳 HuggingFace Spaces Deployment

### Step 1: Create a Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Choose **Docker** as the SDK
3. Set Space hardware to **CPU Basic** (free)

### Step 2: Add Secrets in HF Space Settings
In your Space → **Settings → Repository secrets**, add:
| Name | Value |
|------|-------|
| `QDRANT_URL` | Your Qdrant Cloud URL |
| `QDRANT_API_KEY` | Your Qdrant API Key |
| `GROQ_API_KEY` | Your Groq API Key |

### Step 3: Push to HuggingFace
```bash
git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/nyaya-mitra
git push hf main
```
HuggingFace will automatically build and deploy via Docker.

---

## 🔑 Environment Variables (Docker / HF Spaces)

| Variable | Description |
|----------|-------------|
| `QDRANT_URL` | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | Qdrant API key |
| `GROQ_API_KEY` | Groq API key for Llama 3.3 70B |

---

## ⚠️ Disclaimer
This tool is for **educational purposes only** and does not constitute professional legal advice. Always consult a qualified legal professional for specific legal matters.
