"""Format the additional thesis tables and export reusable numeric scalars."""

import csv
import json
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle


def block(title, headers, rows, note=None):
    centered = ParagraphStyle("TableCaption", fontName="Times-Roman", alignment=1, leading=13)
    footnote = ParagraphStyle("TableNote", fontName="Times-Roman", fontSize=9, leading=11)
    width = 168 if len(headers) < 6 else 140
    table = Table([headers, *rows], colWidths=[width, *[(458 - width) / (len(headers) - 1)] * (len(headers) - 1)])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Times-Roman"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("LINEABOVE", (0, 0), (-1, 0), .8, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), .5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), .8, colors.black),
    ]))
    result = [Paragraph(title, centered), Spacer(1, 8), table]
    if note:
        result.extend([Spacer(1, 5), Paragraph(note, footnote)])
    return result


def regression_rows(models, terms, stars=False):
    rows = []
    for label, names in terms:
        values = [m["terms"].get(name) for m, name in zip(models, names, strict=True)]
        estimates = []
        for value in values:
            if value is None:
                estimates.append("")
                continue
            p = value["p"]
            marker = ("***" if p < .01 else "**" if p < .05 else "*" if p < .1 else "") if stars else ""
            estimates.append(f'{value["estimate"]:.3f}{marker}')
        rows.extend([[label, *estimates], ["", *[f'({v["se"]:.3f})' if v else "" for v in values]]])
    return rows


def table_blocks(data):
    labels = [
        ("slave_exports", "Homeland slave exports"),
        ("average_lights", "Avg. lights, 2000–2013"),
        ("log_average_lights", "Log average lights"),
        ("lights_per_capita", "Avg. lights per capita"),
        ("log_lights_per_square_km", "Log avg. lights per km²"),
        ("distance_to_coast", "Distance to coast (km)"),
        ("log_distance_to_coast", "Log distance to coast"),
    ]
    t1 = []
    for key, label in labels:
        values = data["THomeland"][key]
        digits = 3 if key != "lights_per_capita" else 8
        t1.append([label, *[f"{v:,.{digits}f}" for v in values[:-1]], f"{int(values[-1]):,}"])
    t2 = []
    country = data["TCountry"]
    for key, label in [
        ("log_gdp", "Log GDP per capita, 2000"),
        ("log_lights", "Log lights per km², 2000–2013"),
        ("log_exports", "Log slave exports per land area"),
        ("log_ports", "Log distance to Atlantic slave port"),
    ]:
        t2.append([label, f'{country[key]["mean"]:.3f}', f'{country[key]["sd"]:.3f}'])
    t2.append(["Observations", "", str(country["n"])])

    growth = data["TGrowth"]
    t5 = regression_rows([growth], [
        ("log(1 + exports) (interior)", ["log_exports"]),
        ("Coastal homeland (≤ 100 km)", ["coastal"]),
        ("log(1 + exports) × Coastal", ["log_exports:coastal"]),
        ("log(1 + dist. to coast)", ["log_distance"]),
    ], stars=True)
    t5.extend([["Country fixed effects", "Yes"], ["Observations", f'{growth["n"]:,}'],
               ["R²", f'{growth["r2"]:.3f}'], ["Adjusted R²", f'{growth["adjusted_r2"]:.3f}']])

    h = data["THomelandIV"]
    hmodels = [h[k] for k in ("ols", "iv", "iv_land")]
    t6 = regression_rows(hmodels, [
        ("log exports", ["log_exports"] * 3),
        ("log land area", ["log_land"] * 3),
        ("Constant", ["Intercept", "const", "const"]),
    ])
    for key, label, digits in [
        ("first_stage_f", "First-stage F (distance)", 1),
        ("wu_hausman_p", "Wu–Hausman p-value", 2),
    ]:
        t6.append([label, *[f"{m[key]:.{digits}f}" if key in m else "—" for m in hmodels]])
    t6.append(["Observations", *[f'{m["n"]:,}' for m in hmodels]])

    c = data["TCountryIV"]
    cmodels = [c["ols"], c["iv"]]
    t7 = regression_rows(cmodels, [("ln(exports per area)", ["ln_export_area"] * 2)])
    for label in ("Colony dummies", "Geographic controls", "Island dummy",
                  "Islam share", "Legal origin", "Region dummies"):
        t7.append([label, "Yes", "Yes"])
    t7.append(["Observations", *[str(m["n"]) for m in cmodels]])
    for key, label in [("r2", "R²"), ("adjusted_r2", "Adjusted R²"), ("residual_se", "Residual s.e.")]:
        t7.append([label, *[f"{m[key]:.3f}" for m in cmodels]])
    t7.append(["First-stage F", "—", f'{c["iv"]["first_stage_f"]:.2f}'])

    return (
        block("Table 1: Summary statistics: ethnic homelands",
              ["Variable", "Mean", "Median", "Std. dev.", "Min", "Max", "N"], t1,
              "Reproduction note: The per-capita row uses the archived STEP13 definition and differs from the printed row."),
        block("Table 2: Country-level descriptive statistics: GDP, lights, and slave exports",
              ["Variable", "Mean", "Std. dev."], t2),
        block("Table 5: Growth in night lights and slave exports: coastal vs interior homelands",
              ["", "Δ log(lights)"], t5,
              "Reproduction note: The archived STEP6 specification reports conventional OLS standard errors."),
        block("Table 6: Homeland average night lights and historical slave exports",
              ["", "(1) OLS", "(2) IV", "(3) IV + log land"], t6,
              "Reproduction note: Standard errors follow the archived STEP11 OLS and IV fits."),
        block("Table 7: Country-level night lights and historical slave exports",
              ["", "(1) OLS", "(2) IV"], t7),
    )


def flatten(value, prefix=""):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from flatten(item, f"{prefix}.{key}" if prefix else key)
    elif isinstance(value, list):
        for key, item in zip(("mean", "median", "sd", "min", "max", "n"), value, strict=True):
            yield from flatten(item, f"{prefix}.{key}")
    elif isinstance(value, (int, float)):
        yield prefix, value


def main():
    step16, remaining, json_output, tex_output = map(Path, sys.argv[1:])
    data = json.loads(remaining.read_text())
    models = {}
    with step16.open(newline="") as stream:
        for row in csv.DictReader(stream):
            model = models.setdefault(row["model"], {"n": int(row["n"]), "r2": float(row["r2"]), "terms": {}})
            model["terms"][row["term"]] = {k: float(row[k]) for k in ("estimate", "se", "p")}
    data["TPerCapita"] = {k: models[k] for k in ("1", "2")}
    data["TPerMillion"] = models
    scalars = dict(flatten(data))
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(scalars, indent=2) + "\n")
    lines = [r"\providecommand{\NightlightsScalar}[1]{\csname NightlightsScalar:#1\endcsname}"]
    lines.extend(rf"\expandafter\def\csname NightlightsScalar:{key}\endcsname{{{value:.12g}}}"
                 for key, value in scalars.items())
    tex_output.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
