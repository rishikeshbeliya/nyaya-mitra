---
title: Nyaya Mitra - AI Legal Advisor
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
license: mit
short_description: RAG-powered AI legal advisor for Indian law powered by Llama 3.3 70B & Qdrant
tags:
  - legal
  - india
  - rag
  - langchain
  - streamlit
  - llama
  - groq
---

# ⚖️ Nyaya Mitra — AI Legal Advisor

**Nyaya Mitra** ("Friend of Justice") is a RAG-powered AI legal assistant covering 8 major Indian laws. Ask scenario-based legal questions in plain language and receive accurate, cited legal guidance.

## 🔑 Required Secrets
Add these in **Space Settings → Repository Secrets**:
- `QDRANT_URL` — your Qdrant Cloud cluster URL
- `QDRANT_API_KEY` — your Qdrant API key
- `GROQ_API_KEY` — your Groq API key (free at console.groq.com)

## 📚 Covered Laws
Constitution of India · BNS · BNSS · BSA · Motor Vehicles Act · IT Act · POSH Act · Income Tax Act

## 🏗️ Stack
Llama 3.3 70B (Groq) · ModernBERT-legal embeddings · Qdrant Cloud · LangChain · Streamlit · Docker

---
*For educational purposes only. Not a substitute for professional legal advice.*
