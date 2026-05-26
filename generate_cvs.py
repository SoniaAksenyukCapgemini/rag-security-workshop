"""Skrypt generujący przykładowe CV jako PDF do folderu docs/."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path

OUTPUT_DIR = Path("/sessions/sweet-kind-thompson/mnt/outputs/docs")
OUTPUT_DIR.mkdir(exist_ok=True)

styles = getSampleStyleSheet()

def make_styles():
    name_style = ParagraphStyle("Name", parent=styles["Title"], fontSize=20, textColor=colors.HexColor("#1a1a2e"), spaceAfter=2)
    role_style = ParagraphStyle("Role", parent=styles["Normal"], fontSize=11, textColor=colors.HexColor("#4a4e69"), spaceAfter=6)
    section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#1a1a2e"),
                                    spaceBefore=12, spaceAfter=4, borderPad=2)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, leading=14, spaceAfter=4)
    bullet_style = ParagraphStyle("Bullet", parent=styles["Normal"], fontSize=10, leading=14, leftIndent=12, spaceAfter=2)
    return name_style, role_style, section_style, body_style, bullet_style

def divider():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#4a4e69"), spaceAfter=6)

def build_cv(filename, name, role, contact, summary, experience, education, skills_text, languages):
    n, r, s, b, bl = make_styles()
    doc = SimpleDocTemplate(str(OUTPUT_DIR / filename), pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    story.append(Paragraph(name, n))
    story.append(Paragraph(role, r))
    story.append(Paragraph(contact, b))
    story.append(divider())

    story.append(Paragraph("Profil zawodowy", s))
    story.append(Paragraph(summary, b))
    story.append(divider())

    story.append(Paragraph("Doświadczenie zawodowe", s))
    for exp in experience:
        story.append(Paragraph(f"<b>{exp['title']}</b> · {exp['company']} ({exp['period']})", b))
        for bullet in exp["bullets"]:
            story.append(Paragraph(f"• {bullet}", bl))
        story.append(Spacer(1, 4))
    story.append(divider())

    story.append(Paragraph("Wykształcenie", s))
    for edu in education:
        story.append(Paragraph(f"<b>{edu['degree']}</b> · {edu['school']} ({edu['year']})", b))
    story.append(divider())

    story.append(Paragraph("Umiejętności techniczne", s))
    story.append(Paragraph(skills_text, b))
    story.append(divider())

    story.append(Paragraph("Języki", s))
    story.append(Paragraph(languages, b))

    doc.build(story)
    print(f"  [+] Wygenerowano: {filename}")


# ── CV 1: Anna Kowalska — Senior Python Developer ────────────────────────────
build_cv(
    filename="cv_anna_kowalska.pdf",
    name="Anna Kowalska",
    role="Senior Python Developer",
    contact="anna.kowalska@email.pl  |  +48 600 123 456  |  linkedin.com/in/anna-kowalska-dev  |  Warszawa",
    summary=(
        "Doświadczona inżynierka oprogramowania z 7-letnim stażem w Pythonie. "
        "Specjalizuje się w budowaniu skalowalnych API, automatyzacji procesów oraz systemach ML. "
        "Liderka techniczna w dwóch projektach fin-tech. Autorka artykułów na blogu o architekturze mikroserwisów."
    ),
    experience=[
        {"title": "Senior Python Developer", "company": "FinTech Innovations S.A.", "period": "2021–obecnie",
         "bullets": [
             "Projektowanie i wdrożenie API REST w FastAPI obsługującego 2 mln zapytań dziennie.",
             "Migracja monolitu Django do architektury mikroserwisów (Docker, Kubernetes).",
             "Mentorig 4 juniorów, prowadzenie code review i warsztatów wewnętrznych.",
             "Wdrożenie pipeline'ów MLflow do zarządzania cyklem życia modeli ML.",
         ]},
        {"title": "Python Developer", "company": "DataSoft Sp. z o.o.", "period": "2018–2021",
         "bullets": [
             "Budowanie ETL pipeline'ów w Pythonie (pandas, SQLAlchemy, Airflow).",
             "Integracja z zewnętrznymi API (REST, GraphQL) dla klientów z sektora e-commerce.",
             "Pisanie testów jednostkowych i integracyjnych (pytest, coverage >90%).",
         ]},
        {"title": "Junior Python Developer", "company": "StartupXYZ", "period": "2017–2018",
         "bullets": [
             "Tworzenie scrapperów danych w Beautiful Soup i Scrapy.",
             "Wsparcie w utrzymaniu aplikacji Django.",
         ]},
    ],
    education=[
        {"degree": "Magister Informatyki", "school": "Politechnika Warszawska", "year": "2017"},
        {"degree": "Kurs ML Specialization", "school": "Coursera (Andrew Ng)", "year": "2020"},
    ],
    skills_text=(
        "Python (zaawansowany: FastAPI, Django, Flask, pandas, NumPy, SQLAlchemy, pytest) · "
        "Docker · Kubernetes · PostgreSQL · Redis · Git · CI/CD (GitHub Actions) · "
        "Machine Learning (scikit-learn, MLflow) · AWS (EC2, S3, Lambda)"
    ),
    languages="Polski (ojczysty) · Angielski (C1) · Niemiecki (A2)"
)

# ── CV 2: Jan Nowak — Junior Python Developer ────────────────────────────────
build_cv(
    filename="cv_jan_nowak.pdf",
    name="Jan Nowak",
    role="Junior Python Developer",
    contact="jan.nowak95@gmail.com  |  +48 512 987 654  |  Poznań",
    summary=(
        "Absolwent informatyki poszukujący pierwszej pracy jako Python developer. "
        "Ukończyłem kilka kursów online z Pythona i zrealizowałem własne projekty hobbystyczne. "
        "Chętny do nauki, zmotywowany, otwarty na mentoring."
    ),
    experience=[
        {"title": "Stażysta Python", "company": "WebAgency Poznań", "period": "lato 2023 (3 miesiące)",
         "bullets": [
             "Pomoc w utrzymaniu aplikacji Flask (poprawki bugów, pisanie testów).",
             "Tworzenie prostych skryptów automatyzujących raportowanie w Excelu.",
             "Zapoznanie się z Gitem i code review.",
         ]},
        {"title": "Projekt własny: BudgetTracker", "company": "GitHub", "period": "2023",
         "bullets": [
             "Aplikacja webowa w Flask + SQLite do śledzenia wydatków.",
             "Podstawowe testy jednostkowe w pytest.",
             "Wdrożenie na Heroku.",
         ]},
    ],
    education=[
        {"degree": "Licencjat Informatyki", "school": "Uniwersytet im. Adama Mickiewicza w Poznaniu", "year": "2023"},
    ],
    skills_text=(
        "Python (podstawowy/średnio zaawansowany: Flask, pandas, pytest) · "
        "SQL (SQLite, podstawy PostgreSQL) · HTML/CSS · Git · Linux (podstawy)"
    ),
    languages="Polski (ojczysty) · Angielski (B1)"
)

# ── CV 3: Marta Wiśniewska — Mid Java/Python Developer ───────────────────────
build_cv(
    filename="cv_marta_wisniewska.pdf",
    name="Marta Wiśniewska",
    role="Software Developer (Java / Python)",
    contact="marta.wisniewska@devmail.pl  |  +48 728 345 678  |  Kraków",
    summary=(
        "Programistka z 4-letnim doświadczeniem, głównie w Java i Spring Boot. "
        "Python znam na poziomie skryptowym — używałam go do automatyzacji testów i małych narzędzi CLI. "
        "Aktywnie rozwijam umiejętności Pythona i chcę przestawić się na backend Python."
    ),
    experience=[
        {"title": "Java Developer", "company": "Enterprise Solutions Kraków", "period": "2020–2024",
         "bullets": [
             "Rozbudowa systemu ERP w Java 17 / Spring Boot / Hibernate.",
             "Pisanie testów w JUnit i Mockito (coverage ~85%).",
             "Skrypty pomocnicze w Pythonie do parsowania logów i raportowania.",
             "Uczestnictwo w migracji bazy danych Oracle → PostgreSQL.",
         ]},
        {"title": "Intern Java Developer", "company": "Comarch S.A.", "period": "2019–2020",
         "bullets": [
             "Wsparcie zespołu przy development mikroserwisów Java.",
             "Pisanie dokumentacji technicznej.",
         ]},
    ],
    education=[
        {"degree": "Inżynier Informatyki", "school": "AGH Kraków", "year": "2019"},
    ],
    skills_text=(
        "Java (zaawansowany: Spring Boot, Hibernate, JUnit) · "
        "Python (średni: skrypty, automatyzacja, podstawy Django) · "
        "SQL (PostgreSQL, Oracle) · Maven · Git · Docker (podstawy)"
    ),
    languages="Polski (ojczysty) · Angielski (B2)"
)

# ── CV 4: Piotr Zając — Mid Python Developer ─────────────────────────────────
build_cv(
    filename="cv_piotr_zajac.pdf",
    name="Piotr Zając",
    role="Python Developer / Data Engineer",
    contact="pzajac.dev@proton.me  |  +48 661 234 567  |  Wrocław  |  github.com/pzajac-dev",
    summary=(
        "Python developer z 4 letnim doświadczeniem, specjalizujący się w data engineering i automatyzacji. "
        "Pracowałem przy budowaniu pipeline'ów danych dla klientów z sektora logistycznego. "
        "Dobra znajomość SQLa, Apacha Airflow i podstaw chmury."
    ),
    experience=[
        {"title": "Python Data Engineer", "company": "LogiFlow Sp. z o.o.", "period": "2021–2024",
         "bullets": [
             "Projektowanie i utrzymanie pipeline'ów ETL w Pythonie i Apache Airflow.",
             "Przetwarzanie dużych zbiorów danych z użyciem pandas i PySpark.",
             "Automatyzacja raportowania BI (integracja z Power BI przez Python API).",
             "Optymalizacja zapytań SQL w PostgreSQL — redukcja czasu zapytań o 60%.",
         ]},
        {"title": "Python Developer", "company": "Freelance", "period": "2020–2021",
         "bullets": [
             "Scraping i agregacja danych dla klientów e-commerce (Scrapy, BeautifulSoup).",
             "Tworzenie dashboardów w Streamlit.",
         ]},
    ],
    education=[
        {"degree": "Magister Matematyki stosowanej", "school": "Politechnika Wrocławska", "year": "2020"},
    ],
    skills_text=(
        "Python (zaawansowany: pandas, PySpark, Airflow, SQLAlchemy, FastAPI, pytest) · "
        "SQL (PostgreSQL, MySQL) · Docker · Git · GCP (BigQuery, Cloud Storage) · "
        "Streamlit · Linux · REST API"
    ),
    languages="Polski (ojczysty) · Angielski (C1) · Rosyjski (B1)"
)

print("\n[✓] Wszystkie CV wygenerowane w folderze docs/")
