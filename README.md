# 🔐 Warsztat: Indirect Prompt Injection w systemach RAG

> **UAM — Testowanie Oprogramowania z AI**  
> Temat: Bezpieczeństwo LLM — ataki na systemy Retrieval-Augmented Generation

---

## Co będziemy robić?

Uruchomisz własny system AI do oceny kandydatów HR — zbudowany na **LangChain + Gemini + ChromaDB**.  
Następnie **zaatakujesz go** — tak żeby model wybrał Cię na najlepszego kandydata, mimo braku kwalifikacji.  
Na koniec zastanowimy się, jak takie systemy **zabezpieczyć**.

---

## Wymagania

Potrzebujesz tylko **dwóch rzeczy**:

1. **Docker Desktop** — pobierz z [docker.com/get-started](https://www.docker.com/get-started/)
2. **VS Code** z rozszerzeniem **Dev Containers** — [marketplace.visualstudio.com](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

> Nie musisz instalować Pythona, pip, ani żadnych bibliotek — wszystko jest w kontenerze.

---

## Krok 0 — Klonowanie repozytorium

```bash
git clone https://github.com/TWOJE_REPO/rag-security-workshop.git
cd rag-security-workshop
```

---

## Krok 1 — Klucz API Google Gemini (darmowy!)

1. Wejdź na [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Zaloguj się kontem Google i kliknij **"Create API key"**
3. Skopiuj klucz

Utwórz plik `.env` w głównym folderze projektu:

```bash
# .env
GOOGLE_API_KEY=tutaj_wklej_swoj_klucz
```

> ⚠️ Nie commituj pliku `.env` do Gita! (jest już w `.gitignore`)

---

## Krok 2 — Uruchomienie dev containera

1. Otwórz folder projektu w VS Code
2. Pojawi się powiadomienie: **"Reopen in Container"** — kliknij je  
   *(lub naciśnij `F1` → wpisz `Dev Containers: Reopen in Container`)*
3. Poczekaj ~2 minuty na pierwsze uruchomienie (Docker pobiera obraz i instaluje zależności przez `uv sync`)
4. Gotowe — masz pełne środowisko Pythona w kontenerze!

---

## Krok 3 — Uruchomienie systemu RAG

Masz dwa sposoby uruchomienia systemu — wybierz jeden:

**Opcja A — Interfejs webowy (Streamlit) — zalecane:**
```bash
uv run streamlit run streamlit_app.py
```
VS Code automatycznie otworzy przeglądarkę pod adresem `http://localhost:8501`.  
Zobaczysz panel do wgrywania CV, pole pytania i historię zapytań.

**Opcja B — Interfejs CLI (terminal):**
```bash
uv run python app.py
```

Powinieneś zobaczyć w terminalu:
```
[*] Wczytuję dokumenty z 'docs/'...
[*] Załadowano 4 dokumenty → 47 chunków.
System gotowy. Wpisz pytanie:
```

---

## Krok 4 — Zadanie bazowe (zanim zaatakujesz)

Zadaj pytania i zanotuj odpowiedzi systemu:

```
Pytanie: Który kandydat najlepiej zna Pythona?
Pytanie: Porównaj doświadczenie wszystkich kandydatów.
Pytanie: Kogo powinieneś zatrudnić i dlaczego?
```

> Zapisz odpowiedzi — będziesz je porównywać z wynikami po ataku.

---

## Krok 5 — ATAK: Indirect Prompt Injection 🎯

### Opcja A — przez interfejs Streamlit (prościej)

1. W panelu bocznym kliknij **"Dodaj CV (PDF)"** i wgraj swój plik
2. System automatycznie przeindeksuje bazę
3. Zadaj pytanie — gotowe!

### Opcja B — ręcznie przez terminal

1. Skopiuj szablon ataku:
   ```bash
   cp malicious_cv_template.txt moje_cv.txt
   ```

2. Otwórz `moje_cv.txt` w edytorze i:
   - Wypełnij dane osobowe (wymyślone)
   - Wybierz **jeden payload** z sekcji "PRZYKŁADOWE PAYLOADY" i wklej go w oznaczonym miejscu

3. Skonwertuj plik na PDF i dodaj do folderu `docs/`:
   ```bash
   uv run python txt_to_pdf.py moje_cv.txt
   ```

4. Odśwież stronę Streamlit (lub uruchom ponownie `app.py`) — system zaindeksuje nowy plik

5. Zadaj te same pytania co w Kroku 4. Czy atak zadziałał?

---

## Krok 6 — Eksperymenty do przeprowadzenia

| Eksperyment | Co sprawdzamy? |
|-------------|---------------|
| Zmień payload na angielski | Czy język ma znaczenie? |
| Spróbuj "eksfiltrować" prompt systemowy (Payload C) | Czy model ujawni instrukcje? |
| Dodaj dwa złośliwe CV jednocześnie | Co wygra — które CV? |
| Wymyśl własny payload (Payload F) | Kreatywność! |

---

## Krok 7 — Dyskusja: Jak to naprawić?

Po warsztacie zastanów się (lub porozmawiaj z grupą):

- **Separacja danych od instrukcji** — czy `{context}` powinien być w prompcie systemowym?
- **Input sanitization** — czy filtrowanie słów kluczowych wystarczy?
- **LLM-as-a-Judge** — drugi model sprawdzający odpowiedź pierwszego
- **Guardrails** — narzędzia jak [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) (NVIDIA)
- **Red Teaming** — dlaczego `pytest` nie wystarczy do testowania LLM-ów?

---

## Struktura projektu

```
rag-security-workshop/
├── .devcontainer/
│   └── devcontainer.json     # Konfiguracja środowiska Docker (port 8501)
├── docs/                     # CV kandydatów (PDF) — tu dodajesz swój atak
│   ├── cv_anna_kowalska.pdf
│   ├── cv_jan_nowak.pdf
│   ├── cv_marta_wisniewska.pdf
│   └── cv_piotr_zajac.pdf
├── rag.py                    # ⚠️ Współdzielona logika RAG (podatny PROMPT_TEMPLATE)
├── streamlit_app.py          # Interfejs webowy (upload CV, historia, źródła)
├── app.py                    # Interfejs CLI (terminal)
├── txt_to_pdf.py             # Pomocniczy skrypt: .txt → .pdf
├── malicious_cv_template.txt # Szablon ataku dla studenta
├── pyproject.toml            # Zależności projektu (uv)
├── .env.example              # Przykład pliku z kluczem API
└── README.md                 # Ten plik
```

---

## Kluczowe wnioski

> **"LLM nie widzi cudzysłowów"** — dla modelu wszystko w oknie kontekstowym jest tak samo ważne: instrukcja systemowa i tekst z PDF-a.

> **"Zaufanie jest luką"** — nigdy nie traktuj zewnętrznych danych (PDF, strona WWW, email) jako bezpiecznych.

> **"Testowanie AI to statystyka"** — nie sprawdzamy, czy wynik jest identyczny, lecz czy mieści się w bezpiecznym przedziale semantycznym.

---

## Problemy? FAQ

**`ModuleNotFoundError`** — upewnij się, że jesteś w dev containerze (zielony pasek na dole VS Code)

**`GOOGLE_API_KEY not found`** — sprawdź, czy plik `.env` jest w głównym folderze projektu

**`No such file or directory: docs/`** — uruchom skrypt z głównego folderu projektu, nie z podfolderu

**Atak nie zadziałał** — spróbuj innego payloadu lub zadaj bardziej bezpośrednie pytanie, np. *"Kogo zatrudnić?"*
