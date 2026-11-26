# Replication notes

- **Table 1.** The tables PDF uses the archived STEP13 per-capita definition. The full manuscript retains the printed per-capita row pending verification of its provenance.
- **Tables 2 and 7.** STEP12 uses land area from the lights file. STEP7 uses land area from the Nunn dataset.
- **Tables 3 and 4.** STEP16 uses conventional OLS standard errors. Displayed stars follow the archived R output, whose cutoffs differ from the printed legend.
- **Table 5.** STEP6 uses conventional OLS standard errors and preserves the archived join multiplicity. Adjusted R² rounds to 0.227 in the build and is printed as 0.228 in the thesis.
- **Table 6.** The build uses the conventional OLS and IV standard errors from STEP11.

The public build covers table generation, diagnostics, and redraws for Figures 4, 5, and 7. Upstream raster processing, spatial joins, and the remaining figure redraws are outside this build.

For the STEP13 diagnostic, run `uv run --locked scons output/africa_nightlights_diagnostic.pdf`. To redraw Figure 4 using a different master panel, add `MASTER_PANEL=path/to/homelands_dmsp_panel_master.csv` to the redraw command. Redrawn figures are written to `output/figures/redrawn/`. The redraw scripts use Quartz on macOS and Cairo elsewhere.

The public repository now includes recovered preprocessing and figure redraw routines. See [data acquisition](../DATA_AVAILABILITY.md) for exact prerequisites, reconstruction assumptions, and remaining validation gaps. The archived analysis scripts are preserved; reconstructed figures must not be assumed identical to publication PNGs.
