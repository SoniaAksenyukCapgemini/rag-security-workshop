"""
streamlit_app.py — Webowy interfejs podatnego systemu RAG
=========================================================
UWAGA: Ten skrypt jest CELOWO niezabezpieczony.
Służy wyłącznie do celów edukacyjnych na warsztatach z bezpieczeństwa LLM.

Uruchomienie: uv run streamlit run streamlit_app.py
"""

import os
import shutil
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from rag import DOCS_DIR, ask, build_chain, load_and_index
import traceback
import os

load_dotenv(override=True)

# ── Konfiguracja strony ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HR Candidate Evaluator",
    page_icon="🔍",
    layout="centered",
)

# ── Inicjalizacja session state ───────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []   # lista {"question": ..., "answer": ..., "sources": [...]}
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()


# ── Cache RAG chain — przebuduj tylko gdy zmienią się pliki w docs/ ───────────
@st.cache_resource(show_spinner=False)
def get_chain(file_snapshot: frozenset):
    """Buduje i cachuje łańcuch RAG. Przebudowywany gdy zmieni się file_snapshot."""
    db, n_docs, n_chunks = load_and_index()
    chain = build_chain(db, n_docs)
    return chain, n_docs, n_chunks


def current_snapshot() -> frozenset:
    """Zwraca frozenset nazw + rozmiarów plików w docs/ — używany jako klucz cache."""
    if not DOCS_DIR.exists():
        return frozenset()
    return frozenset(
        (p.name, p.stat().st_size) for p in DOCS_DIR.glob("*.pdf")
    )


# ── Nagłówek ──────────────────────────────────────────────────────────────────
st.title("🔍 HR Candidate Evaluator")

with st.expander("ℹ️ O tym systemie"):
    st.warning(
        "**System demonstracyjny** — celowo podatny na **Indirect Prompt Injection**. "
        "Tylko do celów edukacyjnych. NIE wdrażaj tego kodu na produkcji."
    )
    st.markdown(
        "System używa architektury **RAG** (Retrieval-Augmented Generation): "
        "wczytuje CV kandydatów z folderu `docs/`, indeksuje je w bazie wektorowej "
        "i odpowiada na pytania rekrutera na ich podstawie.\n\n"
        "**Podatność:** tekst z PDF-ów trafia bezpośrednio do promptu modelu — "
        "jeśli CV zawiera instrukcje dla LLM, model je wykona."
    )

st.divider()

# ── Sprawdzenie klucza API ────────────────────────────────────────────────────
if not os.getenv("GOOGLE_API_KEY"):
    st.error(
        "**Brak klucza API.** Utwórz plik `.env` z zawartością:\n\n"
        "```\nGOOGLE_API_KEY=twoj_klucz\n```\n\n"
        "Klucz wygenerujesz na [aistudio.google.com](https://aistudio.google.com/app/apikey)."
    )
    st.stop()

# ── Sidebar: upload CV + lista plików ─────────────────────────────────────────
with st.sidebar:
    st.header("📂 Baza CV")

    uploaded = st.file_uploader(
        "Dodaj CV (PDF)",
        type=["pdf"],
        accept_multiple_files=True,
        help="Wgraj normalne CV lub swoje złośliwe CV z payloadem injection.",
    )

    if uploaded:
        DOCS_DIR.mkdir(exist_ok=True)
        new_files = []
        for f in uploaded:
            dest = DOCS_DIR / f.name
            dest.write_bytes(f.read())
            new_files.append(f.name)
        if new_files:
            st.success(f"Dodano: {', '.join(new_files)}")
            get_chain.clear()
            st.session_state.history = []

    st.subheader("Zaindeksowane pliki")
    if DOCS_DIR.exists():
        pdfs = sorted(DOCS_DIR.glob("*.pdf"))
        if pdfs:
            for pdf in pdfs:
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"📄 `{pdf.name}`")
                if col2.button("🗑", key=f"del_{pdf.name}", help=f"Usuń {pdf.name}"):
                    pdf.unlink()
                    get_chain.clear()
                    st.session_state.history = []
                    st.rerun()
        else:
            st.info("Brak plików PDF w folderze `docs/`.")
    else:
        st.info("Folder `docs/` nie istnieje.")

    st.divider()
    st.caption("Zmiana plików automatycznie przebudowuje indeks.")

# ── Ładowanie chain ────────────────────────────────────────────────────────────
snapshot = current_snapshot()

if not snapshot:
    st.warning("Brak CV w bazie. Wgraj pliki PDF przez panel po lewej stronie.")
    st.stop()

with st.spinner("⏳ Indeksuję dokumenty i buduję bazę wektorową..."):
    try:
        chain, n_docs, n_chunks = get_chain(snapshot)
    except Exception as e:
        # Show full traceback to help debugging
        tb = traceback.format_exc()
        st.error(f"Błąd podczas indeksowania: {e}")
        st.code(tb)
        st.stop()

st.success(f"✅ Zaindeksowano **{n_docs}** CV ({n_chunks} chunków). System gotowy.")

# ── Formularz zapytania ────────────────────────────────────────────────────────
st.subheader("💬 Zadaj pytanie rekrutera")

with st.form("question_form", clear_on_submit=True):
    question = st.text_area(
        "Pytanie",
        placeholder="Np. Który kandydat najlepiej zna Pythona? / Kogo powinieneś zatrudnić?",
        height=80,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("🔎 Oceń kandydatów", use_container_width=True)

if submitted and question.strip():
    with st.spinner("Analizuję CV..."):
        result = ask(chain, question.strip())

    st.session_state.history.insert(0, {
        "question": question.strip(),
        "answer": result["answer"],
        "sources": result["sources"],
    })

# ── Historia zapytań ───────────────────────────────────────────────────────────
if st.session_state.history:
    st.divider()
    st.subheader("📋 Historia zapytań")

    for i, entry in enumerate(st.session_state.history):
        with st.expander(
            f"{'🟢' if i == 0 else '⚪'} {entry['question']}",
            expanded=(i == 0),
        ):
            st.markdown(entry["answer"])

            if entry["sources"]:
                st.markdown("**Źródła użyte przez model:**")
                for src in entry["sources"]:
                    # Podświetl złośliwe pliki (nie zaczynają się od "cv_")
                    icon = "📄" if src.startswith("cv_") else "⚠️"
                    st.markdown(f"{icon} `{src}`")

    if st.button("🧹 Wyczyść historię"):
        st.session_state.history = []
        st.rerun()
