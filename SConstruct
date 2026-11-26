import json
import os
from pathlib import Path
import sys

env = Environment(ENV=os.environ, PYTHON=sys.executable)
rscript = env.WhereIs("Rscript")
if not rscript:
    print("Rscript is required. Install R and add Rscript to PATH.")
    Exit(1)

table = env.Command(
    "output/tables/lights_per_capita.csv",
    ["source/analysis/per_capita_diagnostic.R", "data/homeland_lights_pc_regdata.csv"],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "$TARGET"',
    RSCRIPT=rscript,
)
report = env.Command(
    "output/africa_nightlights_diagnostic.pdf",
    ["source/report/render_diagnostic.py", table, "uv.lock"],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "$TARGET"',
)

paper_table = env.Command(
    "output/tables/paper_tables.csv",
    [
        "source/analysis/homeland_lights_regressions.R", "data/levels_df.csv",
        "data/homelands_pop_2010.csv", "data/distance_coast_by_tribe.csv",
    ],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "${SOURCES[3]}" "$TARGET"',
    RSCRIPT=rscript,
)
remaining = env.Command(
    "output/tables/remaining.json",
    [
        "source/analysis/descriptive_growth_and_iv.py", "data/homeland_lights_pc_regdata.csv",
        "data/exports_by_tribe.csv", "data/slave_trade_QJE.dta", "data/ctrylights.csv",
        "data/growthdf.csv", "data/distance_coast_by_tribe.csv", "uv.lock",
    ],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "${SOURCES[3]}" "${SOURCES[4]}" "${SOURCES[5]}" "${SOURCES[6]}" "$TARGET"',
)
scalars = env.Command(
    ["output/scalars.json", "output/scalars.tex"],
    ["source/report/render_remaining_tables.py", paper_table, remaining, "uv.lock"],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "${TARGETS[0]}" "${TARGETS[1]}"',
)
paper = env.Command(
    "output/africa_nightlights.pdf",
    ["source/report/render_paper_tables.py", paper_table, remaining, "source/report/render_remaining_tables.py", "uv.lock"],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "$TARGET"',
)
figure_sources = json.loads(Path("source/thesis_figures.json").read_text())
figures = [
    env.Command(f"output/figures/{name}.png", path, Copy("$TARGET", "$SOURCE"))
    for name, path in figure_sources.items()
]
Default(paper, scalars)
Alias("published-figures", figures)

redrawn = env.Command(
    ["output/figures/redrawn/figure_5.png", "output/figures/redrawn/figure_7.png"],
    ["source/figures/export_scatter_and_histogram.R", "data/homeland_lights_pc_regdata.csv", "data/exports_by_tribe.csv"],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "${TARGETS[0].dir}"',
    RSCRIPT=rscript,
)
Alias("redraw-figures", redrawn)

manuscript = env.Command(
    "output/africa_nightlights_manuscript.pdf",
    [
        "source/manuscript/build.py", "source/manuscript/main.tex",
        scalars[0], "source/manuscript/references_honors.bib", figures,
    ],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "$TARGET"',
)
Alias("manuscript", manuscript)

panel_archive = File("data/homelands_csv.zip")
panels = env.Command(
    ["output/data/homelands_dmsp_panel.csv", "output/data/homelands_dmsp_panel_master.csv"],
    ["source/data/extract_panels.py", panel_archive],
    '"$PYTHON" "${SOURCES[0]}" "${SOURCES[1]}" "${TARGETS[0]}" "${TARGETS[1]}"',
)
Alias("extract-panels", panels)
# Keep table-only builds usable before the LFS asset is available.
if Path(panel_archive.path).is_file():
    Default(panels)

master_panel = ARGUMENTS.get("MASTER_PANEL", panels[1])
panel_figures = env.Command(
    ["output/figures/redrawn/figure_4.png", "output/figures/redrawn/figure_4_data.csv"],
    ["source/figures/luminosity_by_export_tercile.R", master_panel],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${TARGETS[0].dir}"',
    RSCRIPT=rscript,
)
Alias("redraw-panel-figures", panel_figures)
