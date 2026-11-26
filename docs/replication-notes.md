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

## Independent input validation (2026-11-27)

Using author-supplied original files in an isolated local analysis environment, the original shapefile and GeoPackage were readable and contained 844 valid features, with 844 matching TRIBE_CODE/NAME keys. An independent dissolve and ethnic-export join reproduced all 844 total-export attributes (including missing values). The maximum Hausdorff distance between matched original shapefile and GeoPackage geometries was approximately 1.5e-14 degrees. There are 836 distinct tribe codes; code alone is not a unique geographic feature key. The original Earth Engine panel contains 18,568 rows (844 per year, 1992–2013) and the 2010 population export has 844 rows with nonmissing population sums. The archived master panel has 31,108 rows and 1,321 distinct tribe-code/name/country crosswalk records, including missing country assignments. Joining the original raw panel to this archived crosswalk reproduced the master row count. All 31,108 master rows matched their original Earth Engine record on system:index, year and NAME, and numeric tribe code, mean light, land area, exports and log1p light were consistent with the original values (including missing values). The master contains 726 country entries encoded as NA; these are not established country identifiers. Preserve historical parsing conventions for each downstream analysis. This verifies source data consistency, not independent reconstruction of the Natural Earth spatial crosswalk or R regressions. R was unavailable in the independent execution environment; the full R/SCons/LaTeX workflow remains to be tested locally. No source data are redistributed.
