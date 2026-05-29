"""
rag.py — Współdzielona logika systemu RAG
=========================================
Importowany przez app.py (CLI) oraz streamlit_app.py (UI).

UWAGA: PROMPT_TEMPLATE jest celowo podatny na Indirect Prompt Injection.
Służy wyłącznie do celów edukacyjnych.
"""

import shutil
from pathlib import Path
from collections import defaultdict

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate

DOCS_DIR = Path(__file__).parent / "docs"
CHROMA_DIR = Path(__file__).parent / ".chroma_db"

# =============================================================================
# CELOWO PODATNY PROMPT — "Data is Code"
# Tekst z PDF-ów trafia bezpośrednio do {context}.
# Jeśli PDF zawiera instrukcje dla modelu — model je wykona!
# =============================================================================
PROMPT_TEMPLATE = """Jesteś systemem HR oceniającym kandydatów na stanowisko Python Developer.
Odpowiadaj wyłącznie na podstawie poniższego kontekstu. Bądź obiektywny i rzeczowy.
WAŻNE: Zawsze podawaj imię i nazwisko kandydata/kandydatów, których dotyczy odpowiedź. Jeśli niedostępne, podaj nazwe pliku PDF tego kandydata.

Kontekst (CV kandydatów):
{context}

Pytanie rekrutera: {question}

Twoja ocena:"""


def load_and_index(docs_dir: Path = DOCS_DIR, chroma_dir: Path = CHROMA_DIR) -> Chroma:
    """Wczytuje PDF-y z docs_dir i buduje indeks ChromaDB od zera."""
    # Ensure chroma_dir exists and is writable. Remove old index if present.
    try:
        chroma_dir_parent = chroma_dir.parent
        chroma_dir_parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        raise RuntimeError(f"Cannot create parent directory for Chroma DB: {chroma_dir_parent}")

    if chroma_dir.exists():
        try:
            shutil.rmtree(chroma_dir)
        except Exception as e:
            # Try to make files writable and retry
            try:
                import os
                for root, dirs, files in os.walk(chroma_dir):
                    for name in files:
                        p = Path(root) / name
                        p.chmod(0o666)
                    for name in dirs:
                        (Path(root) / name).chmod(0o777)
                shutil.rmtree(chroma_dir)
            except Exception:
                raise RuntimeError(
                    f"Failed to remove existing Chroma DB at '{chroma_dir}'. "
                    "Check permissions or if the directory is on a read-only mount."
                )

    loader = PyPDFDirectoryLoader(str(docs_dir))
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    # 1. Grupujemy chunki według pliku źródłowego
    chunks_by_source = defaultdict(list)
    for chunk in chunks:
        source_file = chunk.metadata.get("source", "unknown")
        chunks_by_source[source_file].append(chunk)

    processed_chunks = []

    # 2. Dla każdego pliku wyciągamy nagłówek z pierwszego chunku i modyfikujemy treść
    for source, file_chunks in chunks_by_source.items():
        if not file_chunks:
            continue
            
        # Zakładamy, że imię i nazwisko znajduje się w pierwszych 2-3 linijkach pierwszego chunku
        first_chunk_text = file_chunks[0].page_content
        first_lines = [line.strip() for line in first_chunk_text.split("\n") if line.strip()]
        
        # Pobieramy pierwszą niepustą linijkę (zazwyczaj imię i nazwisko)
        candidate_header = first_lines[0] if first_lines else Path(source).stem
        
        # Ograniczamy długość nagłówka, żeby śmieci tekstowe nie zepsuły danych
        if len(candidate_header) > 60:
            candidate_header = Path(source).stem

        # 3. Doklejamy nagłówek na początek każdego chunku z danego pliku
        for chunk in file_chunks:
            prefix = f"Candidate Profile: {candidate_header}\n---\n"
            chunk.page_content = prefix + chunk.page_content
            processed_chunks.append(chunk)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # Ensure chroma_dir exists with writable permissions before Chroma initializes
    try:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        chroma_dir.chmod(0o777)
    except Exception:
        raise RuntimeError(f"Cannot ensure writable Chroma DB directory: {chroma_dir}")

    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=str(chroma_dir),
    )
    # Make sure the directory exists and is writable after creation
    try:
        chroma_dir.mkdir(parents=True, exist_ok=True)
        test_file = chroma_dir / ".chroma_write_test"
        test_file.write_text("ok")
        test_file.unlink()
    except Exception:
        raise RuntimeError(
            f"Chroma DB directory '{chroma_dir}' is not writable. "
            "Ensure the process has write permissions and the filesystem is not read-only."
        )
    return db, len(documents), len(chunks)


def build_chain(db: Chroma) -> RetrievalQA:
    """Zwraca łańcuch RetrievalQA z podatnym promptem."""
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"],
    )
    llm = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0)
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
