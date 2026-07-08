import os
import re
import torch
import streamlit as st
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_core.documents import Document

def get_qdrant_credentials():
    """
    Retrieves Qdrant URL and API Key from environment variables, secrets.toml directly, or Streamlit secrets.
    """
    qdrant_url = os.environ.get("QDRANT_URL")
    qdrant_api_key = os.environ.get("QDRANT_API_KEY")
    
    # Try reading from streamlit secrets file directly (for scripts run outside streamlit context)
    if not qdrant_url or not qdrant_api_key:
        try:
            secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
            if os.path.exists(secrets_path):
                with open(secrets_path, "r") as f:
                    content = f.read()
                    url_match = re.search(r'qdrant_url\s*=\s*["\']([^"\']+)["\']', content)
                    key_match = re.search(r'qdrant_api_key\s*=\s*["\']([^"\']+)["\']', content)
                    if url_match:
                        qdrant_url = url_match.group(1)
                    if key_match:
                        qdrant_api_key = key_match.group(1)
        except Exception:
            pass

    # Fallback to Streamlit secrets context if available
    if not qdrant_url or not qdrant_api_key:
        try:
            qdrant_url = st.secrets["qdrant_url"]
            qdrant_api_key = st.secrets["qdrant_api_key"]
        except Exception:
            pass
            
    return qdrant_url, qdrant_api_key

def get_embeddings():
    """
    Initializes Hugging Face embedding model.
    Checks if CUDA is available and runs on GPU, else falls back to CPU.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    if device == "cuda":
        torch.cuda.empty_cache()
        
    # ModernBERT embedding model optimized for legal contexts
    embedding = HuggingFaceEmbeddings(
        model_name="AdamLucek/ModernBERT-embed-base-legal-MRL",
        model_kwargs={'device': device},
        encode_kwargs={'batch_size': 16}
    )
    return embedding

def document_dtype(chunks):
    """
    Converts list of chunk dictionaries into LangChain Document format.
    """
    return [
        Document(
            page_content=chunk['text'],
            metadata=chunk['metadata']
        )
        for chunk in chunks
    ]

def get_vectorstore(documents=None, force_recreate=False):
    """
    Returns a QdrantVectorStore connection.
    If documents is provided, it indexes/uploads them in chunks to prevent timeouts.
    Otherwise, it connects to the existing collection.
    """
    qdrant_url, qdrant_api_key = get_qdrant_credentials()
    if not qdrant_url or not qdrant_api_key:
        raise ValueError("Qdrant credentials not found. Set QDRANT_URL and QDRANT_API_KEY in environment variables or streamlit secrets.")
        
    embeddings = get_embeddings()
    
    if documents is not None:
        chunk_size = 500
        first_chunk = documents[:chunk_size]
        print(f"Initializing collection 'legal_system' with first {len(first_chunk)} documents...")
        
        vectorstore = QdrantVectorStore.from_documents(
            collection_name="legal_system",
            documents=first_chunk,
            embedding=embeddings,
            url=qdrant_url,
            api_key=qdrant_api_key,
            force_recreate=force_recreate,
            batch_size=32,
            timeout=180.0,
        )
        
        # Upload remaining chunks
        for i in range(chunk_size, len(documents), chunk_size):
            sub_chunk = documents[i:i+chunk_size]
            print(f"Uploading next batch of documents: {i} to {min(i+chunk_size, len(documents))}...")
            vectorstore.add_documents(sub_chunk, batch_size=32, timeout=180.0)
            
    else:
        client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key, timeout=180.0)
        vectorstore = QdrantVectorStore(
            client=client,
            collection_name="legal_system",
            embedding=embeddings
        )
    return vectorstore

def get_retriever():
    """
    Helper to get the similarity search retriever.
    """
    vectorstore = get_vectorstore()
    return vectorstore.as_retriever(search_kwargs={"k": 5}, search_type='similarity')
