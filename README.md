# ⚖️ Nyaya Mitra — AI Legal Advisor for Indian Law

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-red?style=flat-square&logo=streamlit)
![LangChain](https://img.shields.io/badge/LangChain-1.3-green?style=flat-square)
![Groq](https://img.shields.io/badge/LLM-Llama%203.3%2070B%20via%20Groq-orange?style=flat-square)
![Qdrant](https://img.shields.io/badge/VectorDB-Qdrant%20Cloud-purple?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)

**A Retrieval-Augmented Generation (RAG) application that provides AI-powered legal guidance across major Indian laws.**

[🚀 Live Demo on HuggingFace](#) · [📖 Documentation](#-local-setup) · [🐛 Report Issue](https://github.com/rishikeshbeliya/nyaya-mitra/issues)

</div>

---

## 📸 Overview

Nyaya Mitra ("Friend of Justice") is an intelligent legal assistant built on a RAG pipeline. It retrieves the most relevant legal provisions from a Qdrant vector database, then uses **Llama 3.3 70B** (via Groq API) to generate accurate, cited, reader-friendly legal advice — all within seconds.

**Ask scenario-based questions** like:
> *"A police officer snatched my phone during a traffic check. What are my rights?"*  
> *"My employer didn't act on my POSH complaint for 3 months. What can I do?"*  
> *"I lent ₹50,000 to a friend who now refuses to return it. What legal action can I take?"*

---

## 📚 Covered Laws

| Act | Description |
|-----|-------------|
| 🏛️ **Constitution of India** | Fundamental Rights, Duties, Directive Principles |
| ⚔️ **Bhartiya Nyaya Sanhita (BNS)** | Replacement of IPC — criminal offences & punishments |
| 🔏 **Bhartiya Nagrik Suraksha Sanhita (BNSS)** | Replacement of CrPC — criminal procedure |
| 📜 **Bharatiya Sakshya Adhiniyam (BSA)** | Replacement of Indian Evidence Act |
| 🚗 **Motor Vehicles Act** | Traffic laws, accidents, licensing |
| 💻 **Information Technology Act** | Cybercrime, digital signatures, data protection |
| 👩 **POSH Act** | Prevention of Sexual Harassment at Workplace |
| 💰 **Income Tax Act** | Tax obligations, deductions, assessments |

---

## 🏗️ Architecture

```
User Query
    │
    ▼
Query Optimizer (Groq/Llama 3.3 70B)     ← Fix grammar, enhance semantics
    │
    ▼
Qdrant Vector DB                          ← ModernBERT-legal embeddings
(Top-5 relevant legal provisions)
    │
    ▼
RAG Prompt Construction
    │
    ▼
Llama 3.3 70B via Groq API               ← Generate cited legal advice
    │
    ▼
Streamlit UI                              ← Display advice + source citations
```

**Tech Stack:**
- **LLM:** `meta-llama/llama-3.3-70b-versatile` via Groq API (free tier)
- **Embeddings:** `AdamLucek/ModernBERT-embed-base-legal-MRL` (domain-specific legal embeddings)
- **Vector DB:** Qdrant Cloud (free tier)
- **Framework:** LangChain 1.x + Streamlit
- **Deployment:** Docker → HuggingFace Spaces

---

## 🚀 Local Setup

### Prerequisites
- Python 3.11+
- Free accounts: [Qdrant Cloud](https://cloud.qdrant.io), [Groq](https://console.groq.com)

### 1. Clone & Install
```bash
git clone https://github.com/rishikeshbeliya/nyaya-mitra.git
cd nyaya-mitra
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### 2. Configure Secrets
Create `.streamlit/secrets.toml` (this file is gitignored — never committed):
```toml
qdrant_url     = "https://YOUR-CLUSTER.qdrant.io"
qdrant_api_key = "YOUR_QDRANT_API_KEY"
groq_api_key   = "gsk_YOUR_GROQ_KEY"
```

### 3. Add PDFs & Ingest (one-time)
Place the following PDFs in the `data/` directory:
```
data/
├── constituition.pdf
├── bns.pdf
├── bnss.pdf
├── bsa.pdf
├── motor.pdf
├── info_tech.pdf
├── posh.pdf
└── income.pdf
```
Then run:
```bash
.venv\Scripts\python.exe -u ingest.py    # Windows
# python -u ingest.py                    # Linux/macOS
```

### 4. Launch App
```bash
streamlit run app.py
```
Open `http://localhost:8501`

---

## 🐳 HuggingFace Spaces Deployment (Docker)

### Step 1: Create a Space
1. Go to [huggingface.co/new-space](https://huggingface.co/new-space)
2. Set **SDK** → `Docker`
3. Set **Hardware** → `CPU Basic` (free)
4. Name it `nyaya-mitra`

### Step 2: Add Repository Secrets
In your Space → **Settings → Repository secrets**, add:

| Name | Value |
|------|-------|
| `QDRANT_URL` | Your Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | Your Qdrant API key |
| `GROQ_API_KEY` | Your Groq API key (`gsk_...`) |

### Step 3: Push to HuggingFace
```bash
# Copy the HF README header first
copy SPACES_README.md README.md   # This becomes the HF Space card

git remote add hf https://huggingface.co/spaces/rishikeshbeliya/nyaya-mitra
git push hf main
```
HuggingFace will auto-build via Docker and deploy. First build takes ~5 minutes.

> **Note:** The embedding model (`ModernBERT-legal`) is downloaded automatically on first startup (~400MB). Subsequent starts are instant.

---

## 📁 Project Structure

```
nyaya-mitra/
├── app.py                  # Streamlit UI (dark/light theme, citations, RAG pipeline)
├── ingest.py               # One-time ingestion script (parse PDFs → Qdrant)
├── requirements.txt        # Pinned Python dependencies
├── Dockerfile              # Multi-stage Docker build for HF Spaces
├── .dockerignore           # Excludes data/, venv, secrets from image
├── .gitignore              # Excludes secrets, data, model cache
├── README.md               # This file
├── SPACES_README.md        # HuggingFace Space card header
├── data/                   # (gitignored) Local PDF source files
└── src/
    ├── __init__.py
    ├── parsers.py          # Custom PDF parsers per act (regex-based)
    ├── database.py         # Qdrant client + ModernBERT embeddings
    └── llm.py              # Groq LLM + query optimizer + RAG chain
```

---

## ⚙️ Environment Variables

The app reads secrets from `.streamlit/secrets.toml` locally, or from environment variables in Docker/HF Spaces:

| Variable | Description |
|----------|-------------|
| `QDRANT_URL` | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | Qdrant REST API key |
| `GROQ_API_KEY` | Groq API key for Llama 3.3 70B inference |

---

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only** and does not constitute professional legal advice. Always consult a qualified legal professional for specific legal matters.

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Made with ❤️ for Indian citizens seeking accessible legal information
</div>
