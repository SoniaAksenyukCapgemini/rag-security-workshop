"""
rag.py — Współdzielona logika systemu RAG
=========================================
Importowany przez app.py (CLI) oraz streamlit_app.py (UI).

UWAGA: PROMPT_TEMPLATE jest celowo podatny na Indirect Prompt Injection.
Służy wyłącznie do celów edukacyjnych.
"""

import os
import shutil
from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

DOCS_DIR = Path("docs")
CHROMA_DIR = Path(".chroma_db")

# =============================================================================
# CELOWO PODATNY PROMPT — "Data is Code"
# Tekst z PDF-ów trafia bezpośrednio do {context}.
# Jeśli PDF zawiera instrukcje dla modelu — model je wykona!
# =============================================================================
PROMPT_TEMPLATE = """Jesteś systemem HR oceniającym kandydatów na stanowisko Python Developer.
Odpowiadaj wyłącznie na podstawie poniższego kontekstu. Bądź obiektywny i rzeczowy.

Kontekst (CV kandydatów):
{context}

Pytanie rekrutera: {question}

Twoja ocena:"""


def load_and_index(docs_dir: Path = DOCS_DIR, chroma_dir: Path = CHROMA_DIR) -> Chroma:
    """Wczytuje PDF-y z docs_dir i buduje indeks ChromaDB od zera."""
    # Usuń stary indeks — inaczej Chroma dopisuje chunki do istniejącej kolekcji
    # i usunięte/zmienione pliki nadal wpływają na odpowiedzi modelu.
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)

    loader = PyPDFDirectoryLoader(str(docs_dir))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=str(chroma_dir),
    )
    return db, len(documents), len(chunks)


def build_chain(db: Chroma) -> RetrievalQA:
    """Zwraca łańcuch RetrievalQA z podatnym promptem."""
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 4}),
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )


def ask(chain: RetrievalQA, question: str) -> dict:
    """Zadaje pytanie i zwraca odpowiedź + listę źródeł."""
    result = chain.invoke({"query": question})
    sources = sorted(
        {Path(doc.metadata.get("source", "?")).name for doc in result["source_documents"]}
    )
    return {
        "answer": result["result"],
        "sources": sources,
    }
