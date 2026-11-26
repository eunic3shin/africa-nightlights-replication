# Slave Trade's Shadow: Historical Slave Exports and Nighttime Lights

This replication code and manuscript source accompanies [Eunice Shin’s honors thesis](https://doi.org/10.5281/zenodo.24553066). The preferred manuscript citation is in [CITATION.cff](CITATION.cff).

## Running the analysis

Install Python 3.11–3.13, uv, and R with `Rscript` on your PATH. The R scripts use base R. Place the archived analysis inputs described in [Data availability](DATA_AVAILABILITY.md) under `data/`, then run from the repository root:

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

The manuscript target uses archived publication figures rather than claiming to regenerate every figure. The manuscript DOI identifies the paper, not this code version. See [data availability](DATA_AVAILABILITY.md) for access limitations.

## Starting from raw provider downloads

See the [complete acquisition and preparation workflow](DATA_AVAILABILITY.md). The reconstructed pipeline is not yet verified against the archived numerical outputs. To compile with newly drawn figures rather than separately obtained publication PNGs, use `uv run --locked scons manuscript FIGURES=redrawn` after completing preparation and figure redraws.
