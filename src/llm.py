import re
import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

# Global for lazy loading
_llm = None

SYSTEM_PROMPT = """You are Nyaya Mitra — an Official AI Legal Advisor for the following Indian laws:
- Constitution of India
- Bhartiya Nyaya Sanhita (BNS)
- Bhartiya Nagrik Suraksha Sanhita (BNSS)
- Bharatiya Sakshya Adhiniyam (BSA)
- Motor Vehicles Act
- Information Technology Act
- Prevention of Sexual Harassment at Workplace Act (POSH)
- Income Tax Act

Answer the question using ONLY the provided context. If the context does not contain the answer, say so clearly.
Always cite the specific Chapter Number and Article/Section number from the metadata.
If Article or Section is Unknown, omit it.
Answer in a reader-friendly, structured manner.
Use any Illustrations in the context to explain scenarios more clearly.

For scenario-based questions (e.g., "My friend refuses to return my 100 rupees"), rephrase the scenario formally before giving legal advice."""


def get_groq_api_key():
    """Retrieves Groq API key from environment, secrets.toml directly, or Streamlit secrets."""
    key = os.environ.get("GROQ_API_KEY")
    if key:
        return key
    # Try reading from secrets.toml directly (for scripts run outside Streamlit)
    try:
        secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".streamlit", "secrets.toml")
        if os.path.exists(secrets_path):
            with open(secrets_path, "r") as f:
                content = f.read()
                match = re.search(r'groq_api_key\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception:
        pass
    # Fallback to Streamlit runtime secrets
    try:
        return st.secrets["groq_api_key"]
    except Exception:
        pass
    return None


def load_llm():
    """Lazy-loads the Groq LLM client."""
    global _llm
    if _llm is not None:
        return _llm
    api_key = get_groq_api_key()
    if not api_key:
        raise ValueError("Groq API key not found. Add `groq_api_key` to .streamlit/secrets.toml")
    _llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.1,
        max_tokens=1024,
    )
    return _llm


def optimise_query(text: str) -> str:
    """Corrects grammar and optimizes the user query for vector search via Groq."""
    llm = load_llm()
    messages = [
        SystemMessage(content="You are a precise query rewriter. Fix grammar and typos in the user's legal question. Output ONLY the corrected text. Do not explain or add anything."),
        HumanMessage(content=f"Text: {text}"),
    ]
    result = llm.invoke(messages)
    return result.content.strip()


def full_context(docs) -> str:
    """Formats retrieved documents into a structured context string."""
    if not docs:
        return "No relevant legal provisions found."
    formatted = []
    for doc in docs:
        meta = doc.metadata
        doc_source = meta.get("document", "Unknown").upper()
        chapter = meta.get("chapter", "Unknown")
        article = meta.get("article")
        section = meta.get("section")

        cite = f"Source: {doc_source}, Chapter: {chapter}"
        if article and str(article) not in ("None", ""):
            cite += f", Article: {article}"
        if section and str(section) not in ("None", ""):
            cite += f", Section: {section}"

        formatted.append(f"[{cite}]:\n{doc.page_content}")
    return "\n\n---\n\n".join(formatted)


def get_legal_answer(context: str, question: str) -> str:
    """Generates a legal answer given context and question using Groq LLM."""
    llm = load_llm()
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
    ]
    result = llm.invoke(messages)
    return result.content.strip()


def get_legal_chain(retriever):
    """
    Assembles and returns the full LangChain RAG processing chain.
    """
    llm = load_llm()

    def format_for_llm(inputs):
        context = inputs["context"]
        question = inputs["question"]
        return [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}"),
        ]

    parallel_chain = RunnableParallel(
        {
            "question": RunnablePassthrough(),
            "context": RunnableLambda(optimise_query) | retriever | RunnableLambda(full_context),
        }
    )
    parser = StrOutputParser()
    final_chain = parallel_chain | RunnableLambda(format_for_llm) | llm | parser
    return final_chain
