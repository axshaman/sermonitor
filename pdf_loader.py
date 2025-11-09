"""PDF report generation helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

FONT_NAME = "FreeSans"
FONT_PATH = Path("FreeSans.ttf")
REPORTS_DIR = Path("reports")


def generate_pdf_report(user, results: Iterable[Mapping[str, str]]) -> str:
    """Generate a PDF report for the provided search results."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))

    filename = f"{user.name}_{user.surname}_{user.telegram_id}.pdf"
    output_path = REPORTS_DIR / filename

    pdf = canvas.Canvas(str(output_path), pagesize=A4)
    pdf.setFont(FONT_NAME, 12)

    pdf.drawString(40, 800, "SERM Monitoring Report")
    pdf.drawString(40, 780, f"User: {user.name} {user.surname}")

    y_position = 740
    for result in results:
        pdf.drawString(40, y_position, f"[{result.get('id')}] {result.get('headline', '')}")
        y_position -= 16
        pdf.drawString(40, y_position, result.get("url", ""))
        y_position -= 16
        snippet = result.get("snippet", "")
        for line in _wrap_text(snippet, 90):
            pdf.drawString(40, y_position, line)
            y_position -= 14
        y_position -= 10

        if y_position < 80:
            pdf.showPage()
            pdf.setFont(FONT_NAME, 12)
            y_position = 780

    pdf.save()
    return str(output_path)


def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]

    lines = []
    current_line = words.pop(0)
    for word in words:
        if len(current_line) + 1 + len(word) <= width:
            current_line += " " + word
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


__all__ = ["generate_pdf_report"]
