"""
PDF export of the validated menu: one dish per entry with its allergen numbers
("Allergens: 1, 7"), and the key to the 14 numbers at the bottom of every page.
The numbers follow the order of the 14 EU allergens (EU Regulation 1169/2011, Annex II).
"""

from datetime import date
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer

from menupilot.allergens import ALLERGENS

GREEN = colors.HexColor("#2f5d50")
GREY = colors.HexColor("#6b6b6b")
LINE = colors.HexColor("#d9ded8")


def _text(value):
    # The standard PDF fonts cover Western European characters only: replace the rest.
    return escape(str(value).encode("cp1252", errors="replace").decode("cp1252"))


def allergen_pdf(table, title="Menu"):
    """Return the PDF as bytes, with `title` as heading. `table` has a "Dish" column and one True/False column per allergen."""
    today = date.today().strftime("%d.%m.%Y")
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], fontSize=26, leading=30, textColor=GREEN,
                                 spaceAfter=2)
    dish_style = ParagraphStyle("dish", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=11.5,
                                leading=14)
    allergen_style = ParagraphStyle("allergens", parent=styles["Normal"], fontSize=9, leading=12,
                                    textColor=GREEN)

    title = (title or "").strip() or "Menu"
    story = [Paragraph(_text(title), title_style), Spacer(1, 0.5 * cm)]
    for _, row in table.iterrows():
        numbers = ", ".join(str(i) for i, a in enumerate(ALLERGENS, start=1) if row[a])
        story.append(KeepTogether([
            Paragraph(_text(row["Dish"]), dish_style),
            Paragraph(f"Allergens: {numbers}" if numbers else "Allergens: none", allergen_style),
            Spacer(1, 3),
            HRFlowable(width="100%", thickness=0.4, color=LINE, spaceAfter=7),
        ]))

    def footer(canvas, doc):
        left, right = 2 * cm, A4[0] - 2 * cm
        canvas.saveState()
        canvas.setStrokeColor(GREEN)
        canvas.setLineWidth(0.8)
        canvas.line(left, 3.1 * cm, right, 3.1 * cm)
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(GREEN)
        canvas.drawString(left, 2.7 * cm, "Allergens")
        step = (right - left) / 5  # three rows of five: 14 items
        for i, name in enumerate(ALLERGENS):
            x, y = left + (i % 5) * step, 2.25 * cm - (i // 5) * 0.4 * cm
            canvas.setFont("Helvetica-Bold", 7.5)
            canvas.setFillColor(GREEN)
            canvas.drawString(x, y, str(i + 1))
            canvas.setFont("Helvetica", 7.5)
            canvas.setFillColor(GREY)
            canvas.drawString(x + 0.5 * cm, y, name.capitalize())
        canvas.setFont("Helvetica-Bold", 7.5)
        canvas.setFillColor(GREEN)
        canvas.drawString(left, 0.95 * cm, f"Allergen information checked and validated by the owner on {today}.")
        canvas.setFont("Helvetica", 6.5)
        canvas.setFillColor(GREY)
        canvas.drawString(left, 0.5 * cm, "Made with MenuPilot. Allergens suggested by an AI model, "
                          "checked by the owner. Ask the staff if you have an allergy.")
        canvas.drawRightString(right, 0.5 * cm, f"Page {doc.page}")
        canvas.restoreState()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm,
                            bottomMargin=3.7 * cm, title=title, author="MenuPilot")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()
