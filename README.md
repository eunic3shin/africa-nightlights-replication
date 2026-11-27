# Slave Trade's Shadow: Historical Slave Exports and Nighttime Lights

[![Archived v1.0.0 DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24588225.svg)](https://doi.org/10.5281/zenodo.24588225)

This replication code and manuscript source accompanies [Eunice Shin’s honors thesis](https://doi.org/10.5281/zenodo.24553066). The preferred manuscript citation is in [CITATION.cff](CITATION.cff).

## Running the analysis

Install Python 3.11–3.13, uv, and R with `Rscript` on your PATH. Additional R package requirements for preprocessing and figure redraws are listed in the data availability guide. Place the archived analysis inputs described in [Data availability](DATA_AVAILABILITY.md) under `data/`, then run from the repository root:

```sh
uv run --locked scons
```

The default build produces `output/africa_nightlights.pdf` (Tables 1–7) and `output/scalars.json` and `output/scalars.tex`. If `data/homelands_csv.zip` is present, the default build also extracts the two panel CSVs. The optional `redraw-figures` and `redraw-panel-figures` targets generate Figures 5 and 7 and Figure 4, respectively.

The archived datasets and published figure image files are not bundled. A fresh checkout requires separately acquired inputs to generate results. See the [replication notes](docs/replication-notes.md) for differences from the manuscript and the analyses covered by the code.

## Full manuscript build

After obtaining the authorized inputs and the published figure files at the paths listed in [archive correspondence](docs/archive-correspondence.md), install a full TeX distribution with `latexmk`.

```sh
uv run --locked scons manuscript
```

The manuscript target uses archived publication figures rather than claiming to regenerate every figure. The manuscript DOI identifies the paper; the software DOI below identifies the archived code version. See [data availability](DATA_AVAILABILITY.md) for access limitations.

## Starting from raw provider downloads

See the [complete acquisition and preparation workflow](DATA_AVAILABILITY.md). The reconstructed pipeline has been execution-tested; see the validation status and replication notes for the scope of numerical checks. To compile with newly drawn figures rather than separately obtained publication PNGs, use `uv run --locked scons manuscript FIGURES=redrawn` after completing preparation and figure redraws.

The original Earth Engine scripts supplied by the author are included under `source/data/`: [homeland lights](source/data/earth_engine_exports.js), [population](source/data/earth_engine_population.js), and [optional annual rasters](source/data/earth_engine_rasters.js). See the acquisition guide for asset setup and export steps.

## Validation status (2026-11-27)

Local macOS execution verified: raw preprocessing, master-panel comparison, Tables 1–7 generation, figure redraws and manuscript build. Tables 2–7 agree with historical notebook outputs at displayed precision. See replication notes for the unreconciled Table 1 per-capita row, inference-label differences and figure limitations.

## Cite the replication package

Shin, Eunice (2026). Slave Trade's Shadow: Historical Slave Exports and Nighttime Lights: Research replication archive. Version 1.0.0. Zenodo. https://doi.org/10.5281/zenodo.24588225.

The DOI identifies the archived [v1.0.0 release](https://github.com/eunic3shin/africa-nightlights-replication/releases/tag/v1.0.0), not subsequent changes on main. Cite the associated paper separately when discussing research findings.
