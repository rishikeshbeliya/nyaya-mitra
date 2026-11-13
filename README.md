# Nyaya Mitra

Nyaya Mitra is an Indian legal information retrieval system powered by Retrieval-Augmented Generation (RAG). It matches legal queries and factual scenarios against statutory legal provisions from major Indian codes and acts, returning relevant citations, statutory context, and explanatory legal summaries.

## Covered Acts & Codes

- **Constitution of India** (Fundamental Rights, DPSP, Constitutional Remedies)
- **Bharatiya Nyaya Sanhita, 2023 (BNS)**
- **Bharatiya Nagrik Suraksha Sanhita, 2023 (BNSS)**
- **Bharatiya Sakshya Adhiniyam, 2023 (BSA)**
- **Motor Vehicles Act, 1988**
- **Information Technology Act, 2000**
- **Sexual Harassment of Women at Workplace (POSH) Act, 2013**
- **Income Tax Act, 1961**

## Tech Stack & Architecture

- **Interface:** Streamlit
- **Orchestration:** LangChain
- **Embeddings:** `AdamLucek/ModernBERT-embed-base-legal-MRL`
- **Vector Store:** Qdrant Cloud
- **Inference:** Llama 3.3 70B via Groq

Raw act documents are chunked by chapter/section and indexed into Qdrant. At query time, input queries are contextualized, matched via dense retrieval against indexed provisions, and passed to the LLM to synthesize cited explanations with exact section and chapter references.

---

## Getting Started

### Prerequisites

- Python 3.11+
- Qdrant Cloud cluster and API key
- Groq API key

### 1. Installation

```bash
git clone https://github.com/rishikeshbeliya/nyaya-mitra.git
cd nyaya-mitra

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Configuration

Create `.streamlit/secrets.toml`:

```toml
qdrant_url = "https://your-cluster-id.qdrant.io"
qdrant_api_key = "your_qdrant_api_key"
groq_api_key = "gsk_your_groq_api_key"
```

Environment variables (`QDRANT_URL`, `QDRANT_API_KEY`, `GROQ_API_KEY`) can also be used if deploying via container or cloud host.

### 3. Data Ingestion (One-time)

If populating a fresh collection, place the statutory source PDFs in the `data/` folder and run:

```bash
python ingest.py
```

### 4. Running the Web App

```bash
streamlit run app.py
```

---

## Deployment (Docker)

The included `Dockerfile` builds a production container exposing port `7860`:

```bash
docker build -t nyaya-mitra .
docker run -p 7860:7860 \
  -e QDRANT_URL="https://your-cluster-id.qdrant.io" \
  -e QDRANT_API_KEY="your_key" \
  -e GROQ_API_KEY="your_groq_key" \
  nyaya-mitra
```

---

## Legal Disclaimer

Nyaya Mitra is intended for informational and academic purposes only. It is not an alternative to formal legal counsel from an advocate or attorney.
