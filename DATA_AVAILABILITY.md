# Data acquisition and preparation

The repository does not distribute third-party datasets. Download them directly from their providers, observe their access conditions, and keep a record of the version and download date. The published manuscript is [available on Zenodo](https://doi.org/10.5281/zenodo.24553066).

## 1. Obtain the upstream data

| Source | Acquisition instructions |
| --- | --- |
| [NOAA DMSP–OLS version 4](https://developers.google.com/earth-engine/datasets/catalog/NOAA_DMSP-OLS_NIGHTTIME_LIGHTS) | Open the collection in Earth Engine; obtain annual composites for 1992–2013. Alternatively download GeoTIFFs from the [EOG archive](https://eogdata.mines.edu/dmsp/downloadV4composites.html). |
| [GPW v4.11 population count](https://developers.google.com/earth-engine/datasets/catalog/CIESIN_GPWv411_GPW_Population_Count) | Obtain the 2010 population-count raster (not density). Revision 11 is confirmed by the original Earth Engine script supplied by the author. |
| [Nunn (2008) replication ZIP](https://nathannunn.sites.olt.ubc.ca/files/2022/02/DATA-22The-Long-Term-Effects-of-Africas-Slave-Trades22-slave_trade_qje_replication_dataset.zip) | Download and extract; locate slave_trade_QJE.dta. See the [data appendix](https://scholar.harvard.edu/files/nunn/files/empirical_slavery_appendix.pdf). |
| [Nunn and Wantchekon (2011)](https://www.aeaweb.org/articles?id=10.1257/aer.101.7.3221) | Consult the article's data and replication materials for ethnic-level exports and geographic source references; locate the original tribe-level export file if provided. See the [author's data notes](https://nathannunn.sites.olt.ubc.ca/files/2022/03/Nathan_Nunn_Read-Me.pdf). The exact source and release of the archived Murdock–Gray polygon file have not been confirmed. |
| [Natural Earth coastlines](https://www.naturalearthdata.com/downloads/10m-physical-vectors/) | Use Natural Earth medium scale (1:50m) coastlines, as recovered from the historical notebook; the exact archived release is unverified. |

## 2. Prepare local analysis inputs

Create a local data directory with `mkdir -p data`. The upstream downloads are not interchangeable with the prepared inputs below. Do not rename raw rasters or unrelated CSVs to satisfy the filenames.

| File under data/ | Required preparation and key fields |
| --- | --- |
| slave_trade_QJE.dta | Extract the country-level Stata file from Nunn's replication ZIP; retain original variables. |
| exports_by_tribe.csv | Aggregate historical exports by homeland; TRIBE_CODE, totalexports. Confirm the historical trade coverage and crosswalk. |
| homelands_pop_2010.csv | Sum 2010 population counts within homeland polygons; TRIBE_C, land_ar, sum. |
| distance_coast_by_tribe.csv | Calculate homeland centroid-to-coast distances in EPSG:3857, convert metres to km; TRIBE_CODE, dist_coast_km. Preserve archived join multiplicity for Table 5. |
| levels_df.csv | Construct homeland lights/export levels; TRIBE_C, avg_loglights, logexports. |
| homeland_lights_pc_regdata.csv | Join homeland lights, population, exports, land area and coast distance; TRIBE_CODE, country, meanlight_2000_2013, totalexports, land_area, lights_pc, log_lights_pc, log_lights_km2, log_exports, dist_coast_km, log_dist_coast. Preserve literal country label NA where applicable. |
| ctrylights.csv | Country-level lights for 2000–2013 and land area; country, meanlight20002013, land_area. Country keys must match Nunn's file. |
| growthdf.csv | Homeland growth sample; TRIBE_CODE, country, d_log_lights, log_exports. Use the earliest and latest nonmissing log lights, as recovered from the historical notebook. |
| homelands_csv.zip | Optional: ZIP with homelands_dmsp_panel.csv and homelands_dmsp_panel_master.csv at its root. Master panel requires TRIBE_CODE, year, log_lights, ttl_xpr for Figure 4. |

The original Earth Engine scripts establish the raster band, satellite-year compositing, GPW release, reducers and 1,000 m scale. The exact historical uploaded geometry asset, geographic crosswalk and Natural Earth release still require numerical verification. Exact numerical replication requires matching the archived intermediates. For those inputs, consult the author under applicable provider terms. Optional archive-only inputs and hashes are listed in [archive correspondence](docs/archive-correspondence.md).

## 3. Run the analysis

Install uv, Python 3.11–3.13 and R. From the repository root:

```sh
uv run --locked scons
uv run --locked scons redraw-figures
```

With the optional panel ZIP, run `uv run --locked scons redraw-panel-figures`. For a separately prepared master CSV, use `uv run --locked scons redraw-panel-figures MASTER_PANEL=/path/to/panel.csv`.

For the full manuscript, the published figure PNGs listed in [archive correspondence](docs/archive-correspondence.md) must also be obtained separately; the paper DOI provides the visual reference, not necessarily the original image files. Install LaTeX and latexmk, then run `uv run --locked scons manuscript`.

See [replication notes](docs/replication-notes.md) for known numerical discrepancies. No third-party data are bundled. The local data directory is gitignored.

## Recovered preprocessing workflow

Install the additional R preprocessing packages once:

```r
install.packages(c("readr", "dplyr", "sf", "haven", "rnaturalearth", "rnaturalearthdata"))
```

Place the original Murdock_Map_2020 shapefile and sidecars, tribe_level_slave_exports_Atlantic_Indian.dta, slave_trade_QJE.dta, and the two Earth Engine CSV exports (homelands_dmsp_panel.csv and homelands_pop_2010.csv) in data/raw/. The historical coast and country joins use Natural Earth medium scale (1:50m), not 1:10m. Exact release versions remain unverified.

Run from the repository root:

```sh
uv run --locked scons prepare-data
uv run --locked scons
uv run --locked scons redraw-panel-figures MASTER_PANEL=data/homelands_dmsp_panel_master.csv
```

The [preprocessing script](source/data/prepare_inputs.R) ports the historical geometry, exports, coast, master panel, levels, growth, country totals and per-capita cross-section routines. The original Earth Engine export code has now been recovered directly from the author; see the three scripts below. Independent checks of the author-supplied source geometry, export attributes, raw panel and archived master panel are documented in replication notes. The R-generated intermediates still require local validation.

## Complete reconstructed workflow

1. Download the sources above and put the Murdock shapefile sidecars and ethnic export Stata file in data/raw/.
2. Install the R packages listed above plus ggplot2 and patchwork. Run `uv run --locked scons prepare-geometry`.
3. Convert data/homelands_exports.gpkg to a shapefile using QGIS or `ogr2ogr -f 'ESRI Shapefile' data/raw/homelands_exports.shp data/homelands_exports.gpkg`. Verify the attributes in the resulting file: the historical Earth Engine exports used TRIBE_C, ttl_xpr and land_ar. Shapefile field truncation alone does not guarantee those exact names; explicitly rename TRIBE_CODE, total_exports and land_area to those historical aliases before upload, preserving other fields and geometry. Upload the shapefile and sidecars to your own [Earth Engine project](https://code.earthengine.google.com/). Run [earth_engine_exports.js](source/data/earth_engine_exports.js) and [earth_engine_population.js](source/data/earth_engine_population.js) separately after replacing the asset ID. Start their CSV export tasks and download both files to data/raw/. The original panel uses the first stable_lights image in each year and a mean reducer at scale 1000; population uses GPW v4.11 2010 and a sum reducer at scale 1000. The optional [earth_engine_rasters.js](source/data/earth_engine_rasters.js) exports annual mean satellite rasters over the Africa bounding box, in EPSG:4326 at scale 1000. These rasters are not the input to the homeland panel.
4. Put slave_trade_QJE.dta in data/raw/ and run:

```sh
uv run --locked scons prepare-data
uv run --locked scons
uv run --locked scons redraw-spatial-figures redraw-figures redraw-panel-figures
uv run --locked scons manuscript FIGURES=redrawn
```

The last command compiles with regenerated figures rather than archived PNGs. It is a reconstructed manuscript, not a bitwise copy of the publication. The spatial redraw simplifies the original layout and uses the mean homeland-year lights/land-area ratio for Figure 3; that denominator is land area, not population. No exact numerical or visual equivalence has yet been demonstrated.

## Numerical validation against an authorized reference archive

After preparation, if you have access to the original archived intermediate CSVs, run:

```sh
uv run --locked python source/verify_inputs.py data /path/to/archive/data exports_by_tribe.csv distance_coast_by_tribe.csv levels_df.csv growthdf.csv ctrylights.csv homeland_lights_pc_regdata.csv
```

The checker compares schemas, row counts, duplicate-preserving sorted rows and numeric values within a stated tolerance. It fails on discrepancies or missing files. Sorting by all columns may make near-tied numeric rows compare out of order; inspect such failures individually. No archived input data are included or requested by this checker. This comparison is not a substitute for validating the final regression estimates or figure outputs.
