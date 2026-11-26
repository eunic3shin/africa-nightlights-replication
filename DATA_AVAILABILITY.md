# Data availability

Place the corresponding archived inputs under `data/` if you have authorized access. Public upstream products provide source material. The archived export settings and intermediate transformations are only partly documented, so downloading the upstream products alone cannot recreate the expected CSVs.

| File under `data/` | Role |
| --- | --- |
| `levels_df.csv`, `homelands_pop_2010.csv`, `distance_coast_by_tribe.csv` | Homeland regression inputs, including population and distance to coast |
| `homeland_lights_pc_regdata.csv`, `exports_by_tribe.csv`, `growthdf.csv` | Homeland cross-section, historical exports, and growth inputs |
| `ctrylights.csv`, `slave_trade_QJE.dta` | Country lights and historical slave-trade data |
| `homelands_csv.zip` | Optional original and master homeland-year panel CSVs for extraction and Figure 4 |

The source datasets include [NOAA DMSP–OLS annual nighttime lights composites](https://developers.google.com/earth-engine/datasets/catalog/NOAA_DMSP-OLS_NIGHTTIME_LIGHTS), GPWv4 population, [Nathan Nunn’s historical slave-export data](https://scholar.harvard.edu/files/nunn/files/empirical_slavery_appendix.pdf), Murdock–Gray homeland geometries, and Natural Earth coastlines. The archived coastal-distance workflow used homeland centroids in EPSG:3857. Exact release versions and redistribution terms for several inputs and derived datasets remain unverified. For access to the archived intermediates, contact the author through the associated manuscript record.

## Manuscript assets and redistribution

The manuscript target additionally needs the original published PNG files under `data/published-figures/` (see [archive correspondence](docs/archive-correspondence.md)). These are not bundled while source-data and asset rights are being checked. Do not substitute unrelated data for the archived inputs.
