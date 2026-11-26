# Replication notes

- **Table 1.** The tables PDF uses the archived STEP13 per-capita definition. The full manuscript retains the printed per-capita row pending verification of its provenance.
- **Tables 2 and 7.** STEP12 uses land area from the lights file. STEP7 uses land area from the Nunn dataset.
- **Tables 3 and 4.** STEP16 uses conventional OLS standard errors. Displayed stars follow the archived R output, whose cutoffs differ from the printed legend.
- **Table 5.** STEP6 uses conventional OLS standard errors and preserves the archived join multiplicity. Adjusted R² rounds to 0.227 in the build and is printed as 0.228 in the thesis.
- **Table 6.** The build uses the conventional OLS and IV standard errors from STEP11.

The public build includes table generation, diagnostics, reconstructed spatial joins and figure redraws. The original Earth Engine scripts are included for the manual upstream export stage.

For the STEP13 diagnostic, run `uv run --locked scons output/africa_nightlights_diagnostic.pdf`. To redraw Figure 4 using a different master panel, add `MASTER_PANEL=path/to/homelands_dmsp_panel_master.csv` to the redraw command. Redrawn figures are written to `output/figures/redrawn/`. The redraw scripts use Quartz on macOS and Cairo elsewhere.

The public repository now includes recovered preprocessing and figure redraw routines. See [data acquisition](../DATA_AVAILABILITY.md) for exact prerequisites, reconstruction assumptions, and remaining validation gaps. The archived analysis scripts are preserved; reconstructed figures must not be assumed identical to publication PNGs.

## Original Earth Engine exports recovered

The author supplied all three original export scripts. The homeland panel uses the first stable_lights image returned for each calendar year, with zonal mean at 1,000 m. The GPW v4.11 2010 population export uses zonal sum at 1,000 m. The separate raster workflow uses the annual mean of satellite composites and clips to [-20, -35, 55, 38], exporting in EPSG:4326 at 1,000 m. These are not interchangeable. The first-image query has no explicit sort; the original collection ordering and uploaded geometry attributes remain potential sources of differences. The scripts preserve the original export logic, with the asset path parameterized. Numerical validation is pending.
