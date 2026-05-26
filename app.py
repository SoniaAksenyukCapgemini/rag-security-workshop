"""
app.py - Interfejs CLI podatnego systemu RAG
Uruchomienie: uv run python app.py
Alternatywnie z UI: uv run streamlit run streamlit_app.py
"""

import os
import sys

from dotenv import load_dotenv
from rag import DOCS_DIR, ask, build_chain, load_and_index

load_dotenv()


def main():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[BLAD] Brak zmiennej GOOGLE_API_KEY.")
        print("Utworz plik .env z zawartoscia: GOOGLE_API_KEY=twoj_klucz")
        print("Klucz mozesz wygenerowac na: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    if not DOCS_DIR.exists() or not any(DOCS_DIR.glob("*.pdf")):
        print(f"[BLAD] Folder '{DOCS_DIR}' jest pusty lub nie istnieje.")
        sys.exit(1)

    print(f"[*] Wczytuje dokumenty z '{DOCS_DIR}/'...")
    db, n_docs, n_chunks = load_and_index()
    print(f"[*] Zaladowano {n_docs} dokumentow -> {n_chunks} chunkow.")
    print("[*] Buduje lancuch RAG...")
    chain = build_chain(db)

    print("\n" + "=" * 55)
    print("  System oceny kandydatow HR  (powered by Gemini RAG)")
    print("=" * 55)
    print("Wpisz pytanie lub 'quit' aby wyjsc.\n")
    print("Przykladowe pytania:")
    print("  > Ktory kandydat najlepiej zna Pythona?")
    print("  > Porownaj doswiadczenie wszystkich kandydatow.")
    print("  > Kogo powinienes zatrudnic i dlaczego?\n")

    while True:
        try:
            question = input("Pytanie: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nDo widzenia!")
            break

        if not question:
            continue
        if question.lower() in ("quit", "exit", "q", "koniec"):
            print("Do widzenia!")
            break

        result = ask(chain, question)
        print(f"\n{'─' * 55}")
        print(f"Odpowiedz:\n{result['answer']}")
        print(f"\nZrodla: {', '.join(result['sources'])}")
        print(f"{'─' * 55}\n")


if __name__ == "__main__":
    main()
