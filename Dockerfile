# ── Stage 1: Builder ─────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ── Stage 2: Runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code and streamlit config
COPY src/ ./src/
COPY app.py .
COPY .streamlit/config.toml .streamlit/config.toml

# HF Spaces runtime env vars
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME=/tmp/hf_cache \
    TRANSFORMERS_CACHE=/tmp/hf_cache

# HF Spaces MUST use port 7860
EXPOSE 7860

# Create non-root user (HuggingFace requirement)
RUN useradd -m -u 1000 appuser && \
    mkdir -p /tmp/hf_cache && \
    chown -R appuser /app /tmp/hf_cache

USER appuser

# Secrets (QDRANT_URL, QDRANT_API_KEY, GROQ_API_KEY) injected at runtime
# via HF Space Settings → Repository Secrets → available as env vars
CMD ["streamlit", "run", "app.py", \
     "--server.port=7860", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--browser.gatherUsageStats=false"]
