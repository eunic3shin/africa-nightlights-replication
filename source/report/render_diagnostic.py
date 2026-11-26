"""Render the archived STEP13 regression summary as a PDF."""

import argparse
import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()

    with args.input_csv.open(newline="", encoding="utf-8") as stream:
        models = list(csv.DictReader(stream))
    cells = [["", "PC, no coast", "PC, with coast", "km², with coast"]]
    for field, label in [
        ("beta_exports", "Log exports"),
        ("se_exports", "Standard error"),
        ("beta_coast", "Log distance to coast"),
        ("se_coast", "Standard error"),
        ("n", "Observations"),
        ("r2", "R²"),
    ]:
        values = [model[field] for model in models]
        formatted = [
            "—" if value == "NA" else value if field == "n" else f"{float(value):.4g}"
            for value in values
        ]
        cells.append([label, *formatted])

    table = Table(cells, colWidths=[154, 94, 94, 94], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e9eef4")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    title = "Africa Nightlights"
    styles = getSampleStyleSheet()
    args.output_pdf.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(args.output_pdf), title=title, invariant=1)
    document.build([
        Paragraph(title, styles["Title"]),
        Paragraph("Nightlights per capita and per km²", styles["Heading2"]),
        table,
        Paragraph("PC denotes per capita. All specifications include country fixed effects.", styles["BodyText"]),
    ])


if __name__ == "__main__":
    main()
