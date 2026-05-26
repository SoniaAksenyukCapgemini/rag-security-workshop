"""
txt_to_pdf.py — Konwertuje plik .txt na .pdf i wrzuca go do folderu docs/
Użycie: uv run python txt_to_pdf.py malicious_cv_template.txt
"""

import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT


def txt_to_pdf(input_path: str):
    src = Path(input_path)
    if not src.exists():
        print(f"[BŁĄD] Plik '{src}' nie istnieje.")
        sys.exit(1)

    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    output_path = docs_dir / src.with_suffix(".pdf").name

    styles = getSampleStyleSheet()
    body = styles["Normal"]
    body.fontSize = 10
    body.leading = 14

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    story = []
    for line in src.read_text(encoding="utf-8").splitlines():
        if line.strip():
            # Escape HTML special chars dla ReportLab
            safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe, body))
        else:
            story.append(Spacer(1, 6))

    doc.build(story)
    print(f"[+] Zapisano: {output_path}")
    print(f"    Teraz uruchom ponownie app.py, żeby zaindeksować nowy plik.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Użycie: uv run python txt_to_pdf.py <plik.txt>")
        sys.exit(1)
    txt_to_pdf(sys.argv[1])
