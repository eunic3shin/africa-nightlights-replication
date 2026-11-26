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
if ARGUMENTS.get("FIGURES") == "redrawn":
    figure_sources = {name: f"output/figures/redrawn/{name}.png" for name in figure_sources}
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

master_panel = ARGUMENTS.get("MASTER_PANEL", "data/homelands_dmsp_panel_master.csv" if Path("data/homelands_dmsp_panel_master.csv").is_file() else panels[1])
panel_figures = env.Command(
    ["output/figures/redrawn/figure_4.png", "output/figures/redrawn/figure_4_data.csv"],
    ["source/figures/luminosity_by_export_tercile.R", master_panel],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${TARGETS[0].dir}"',
    RSCRIPT=rscript,
)
Alias("redraw-panel-figures", panel_figures)


# Explicit upstream preparation; keep existing archived-input build unchanged.
if "prepare-data" in COMMAND_LINE_TARGETS:
    prep = env.Command(
    ["data/exports_by_tribe.csv", "data/distance_coast_by_tribe.csv",
     "data/homelands_dmsp_panel_master.csv", "data/levels_df.csv",
     "data/growthdf.csv", "data/ctrylights.csv",
     "data/homeland_lights_pc_regdata.csv", "data/homelands_pop_2010.csv",
     "data/slave_trade_QJE.dta"],
    ["source/data/prepare_inputs.R", "data/raw/Murdock_Map_2020.shp",
     "data/raw/Murdock_Map_2020.dbf", "data/raw/Murdock_Map_2020.shx",
     "data/raw/Murdock_Map_2020.prj",
     "data/raw/tribe_level_slave_exports_Atlantic_Indian.dta",
     "data/raw/homelands_dmsp_panel.csv", "data/raw/homelands_pop_2010.csv",
     "data/raw/slave_trade_QJE.dta"],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" data/raw data',
    RSCRIPT=rscript,
)
    Alias("prepare-data", prep)

# Build geometry before uploading it to Earth Engine (manual export step).
geometry = env.Command("data/homelands_exports.gpkg",
    ["source/data/prepare_geometry.R","data/raw/Murdock_Map_2020.shp",
     "data/raw/tribe_level_slave_exports_Atlantic_Indian.dta","data/raw/Murdock_Map_2020.dbf",
     "data/raw/Murdock_Map_2020.shx","data/raw/Murdock_Map_2020.prj"],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "$TARGET"',RSCRIPT=rscript)
Alias("prepare-geometry",geometry)
map_redraw = env.Command(
    ["output/figures/redrawn/"+name for name in ("figure_1.png","figure_2.png","figure_3_country.png","figure_3_homeland.png","figure_6.png")],
    ["source/figures/spatial_figures.R",geometry,"data/homelands_dmsp_panel_master.csv","data/distance_coast_by_tribe.csv"],
    '"$RSCRIPT" --vanilla "${SOURCES[0]}" "${SOURCES[1]}" "${SOURCES[2]}" "${SOURCES[3]}" "${TARGETS[0].dir}"',RSCRIPT=rscript)
Alias("redraw-spatial-figures",map_redraw)
