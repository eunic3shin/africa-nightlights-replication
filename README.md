# Slave Trade's Shadow: Historical Slave Exports and Nighttime Lights

This code-only replication archive accompanies [Eunice Shin’s honors thesis](https://doi.org/10.5281/zenodo.24553066). The preferred manuscript citation is in [CITATION.cff](CITATION.cff).

## Running the analysis

Install Python 3.11–3.13, uv, and R with `Rscript` on your PATH. The R scripts use base R. Place the archived analysis inputs described in [Data availability](DATA_AVAILABILITY.md) under `data/`, then run from the repository root:

```sh
uv run --locked scons
```

The default build produces `output/africa_nightlights.pdf` (Tables 1–7) and `output/scalars.json` and `output/scalars.tex`. If `data/homelands_csv.zip` is present, the default build also extracts the two panel CSVs. The optional `redraw-figures` and `redraw-panel-figures` targets generate Figures 5 and 7 and Figure 4, respectively.

The archived data and manuscript assets are excluded. A fresh checkout requires separately acquired inputs to generate results. See the [replication notes](docs/replication-notes.md) for differences from the manuscript and the analyses covered by the code.
