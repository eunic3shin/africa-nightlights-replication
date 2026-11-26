"""Render the Nightlights paper's Tables 3 and 4."""

import csv
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


from render_remaining_tables import table_blocks


def value(row, field, digits, scientific=False):
    number = float(row[field])
    if scientific:
        lead, exponent = f"{number:.2e}".split("e")
        result = f"{lead} × 10<super>{int(exponent)}</super>"
    else:
        # The paper shortens the already rounded coast standard error in Table 4.
        if field == "se" and digits == 2:
            number = float(f"{number:.3f}")
        result = f"{number:.{digits}f}"
    if field == "estimate":
        p = float(row["p"])
        stars = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
        result += f"<super>{stars}</super>" if stars else ""
    else:
        result = f"({result})"
    return result.replace("-", "−")


def render_table(models, number, caption, headings, notes):
    centered = ParagraphStyle("Centered", fontName="Times-Roman", alignment=1, leading=13)
    note = ParagraphStyle("Note", fontName="Times-Roman", fontSize=9, leading=11)
    rows = [
        ["", *[f"({i})" for i in range(1, len(models) + 1)]],
        ["", *[Paragraph(h, centered) for h in headings]],
    ]
    for term, label in [
        ("logexports", "log(1 + exports<sub>i</sub>)"),
        ("logdistcoast", "log(1 + dist. to coast<sub>i</sub>)"),
    ]:
        for field in ("estimate", "se"):
            row = [Paragraph(label, note) if field == "estimate" else ""]
            for i, model in enumerate(models):
                digits = 2 if number == 4 and term == "logdistcoast" else 3
                rendered = value(model[term], field, digits, i == 2) if term in model else ""
                row.append(Paragraph(rendered, centered))
            rows.append(row)
    rows.extend([
        ["Country fixed effects", *["No" for _ in models]],
        ["Observations", *[model["logexports"]["n"] for model in models]],
        ["R²", *[f'{float(model["logexports"]["r2"]):.3f}' for model in models]],
    ])
    table = Table(rows, colWidths=[132, *[(458 - 132) / len(models)] * len(models)])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("LINEABOVE", (0, 0), (-1, 0), .8, colors.black),
        ("LINEBELOW", (0, 1), (-1, 1), .5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), .8, colors.black),
    ]))
    return [
        Paragraph(f"Table {number}: {caption}", centered),
        Spacer(1, 9), table, Spacer(1, 4),
        Paragraph(f"<i>Notes:</i> {notes}", note),
    ]


def main():
    input_csv, remaining, output_pdf = map(Path, sys.argv[1:])
    models = [{}, {}, {}]
    with input_csv.open(newline="", encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            models[int(row["model"]) - 1][row["term"]] = row

    stars = "∗ p &lt; 0.10, ∗∗ p &lt; 0.05, ∗∗∗ p &lt; 0.01.".replace("∗", "*")
    story = render_table(
        models[:2], 3,
        "Ethnic-homeland night lights per capita, slave exports, and distance to coast",
        ["Lights per capita (×10<super>6</super>)"] * 2,
        "Dependent variable is average night-time lights per capita between 2000 and 2013 for each ethnic "
        "homeland, scaled by 10<super>6</super>. The main regressor is log of one plus total slave exports "
        "at the homeland level. Column (2) adds log distance to the African coastline. All specifications are "
        "estimated without country fixed effects. Robust standard errors in parentheses. " + stars,
    )
    story += [Spacer(1, 28)]
    story += render_table(
        models, 4, "Homeland lights per million people, slave exports, and distance to coast",
        ["Lights per 10<super>6</super> people", "Lights per 10<super>6</super> people", "Log lights per km²"],
        "Dependent variable is average night-time lights per one million people over 2000–2013 in columns "
        "(1) and (2), and log lights per square kilometer in column (3). All regressions are estimated at the "
        "ethnic-homeland level using the subset of homelands for which gridded population data are available "
        "(833 observations). No specification includes country fixed effects. Standard errors in parentheses. " + stars,
    )
    story.extend([
        Spacer(1, 10),
        Paragraph(
            "Reproduction note: The archived STEP16 estimates use conventional OLS standard errors. "
            "The displayed stars follow the archived R output (0.05, 0.01, 0.001). "
            "The notes under the tables are preserved from the paper.",
            ParagraphStyle("Reproduction", fontName="Times-Italic", fontSize=9, leading=11),
        ),
    ])
    t1, t2, t5, t6, t7 = table_blocks(json.loads(remaining.read_text()))
    story = [
        *t1, Spacer(1, 24), *t2, PageBreak(), *story,
        PageBreak(), *t5, Spacer(1, 24), *t6, PageBreak(), *t7,
    ]
    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(output_pdf), invariant=1).build(story)


if __name__ == "__main__":
    main()
