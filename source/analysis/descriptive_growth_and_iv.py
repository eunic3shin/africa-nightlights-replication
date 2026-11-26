"""Calculate thesis Tables 1, 2, 5, 6, and 7 from archived inputs."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.sandbox.regression.gmm import IV2SLS


def descriptive(values):
    return [float(v) for v in (values.mean(), values.median(), values.std(),
                              values.min(), values.max(), values.count())]


def iv_fit(data, outcome, regressor, instrument, controls):
    x = sm.add_constant(data[[regressor, *controls]])
    z = sm.add_constant(data[[instrument, *controls]])
    y = data[outcome]
    fit = IV2SLS(y, x, z).fit()
    stage = sm.OLS(data[regressor], z).fit()
    augmented = sm.OLS(y, x.assign(first_stage_residual=stage.resid)).fit()
    diagnostics = {
        "first_stage_f": float(stage.tvalues[instrument] ** 2),
        "wu_hausman_p": float(augmented.pvalues["first_stage_residual"]),
    }
    return fit, diagnostics


def summarize(fit, terms):
    return {
        "n": int(fit.nobs),
        "r2": float(fit.rsquared),
        "adjusted_r2": float(fit.rsquared_adj),
        "residual_se": float(np.sqrt(fit.mse_resid)),
        "terms": {
            term: {
                "estimate": float(fit.params[term]),
                "se": float(fit.bse[term]),
                "p": float(fit.pvalues[term]),
            }
            for term in terms
        },
    }


def calculate(regdata, exports, country_data, country_lights, growth, coast):
    homelands = regdata.drop_duplicates("TRIBE_CODE").set_index("TRIBE_CODE")
    exports = exports.set_index("TRIBE_CODE").totalexports
    table1 = {
        "slave_exports": descriptive(exports),
        "average_lights": descriptive(homelands.meanlight_2000_2013),
        "log_average_lights": descriptive(np.log1p(homelands.meanlight_2000_2013)),
        "lights_per_capita": descriptive(homelands.lights_pc),
        "log_lights_per_square_km": descriptive(homelands.log_lights_km2),
        "distance_to_coast": descriptive(homelands.dist_coast_km),
        "log_distance_to_coast": descriptive(homelands.log_dist_coast),
    }

    countries = country_data.merge(
        country_lights, on="country", suffixes=("_nunn", ""), validate="one_to_one"
    )
    # STEP12 uses the lights file's land area. STEP7 uses Nunn's land area.
    countries["descriptive_log_lights"] = np.log(countries.meanlight20002013 / countries.land_area)
    countries["regression_log_lights"] = np.log(countries.meanlight20002013 / countries.land_area_nunn)
    countries["log_ports"] = np.log1p(countries.atlantic_distance_minimum.astype(float))
    table2 = {
        key: {"mean": float(countries[col].mean()), "sd": float(countries[col].std())}
        for key, col in [
            ("log_gdp", "ln_maddison_pcgdp2000"),
            ("log_lights", "descriptive_log_lights"),
            ("log_exports", "ln_export_area"),
            ("log_ports", "log_ports"),
        ]
    }
    table2["n"] = len(countries)

    # Preserve the archived STEP6 join multiplicity, including repeated coast keys.
    growth = growth.merge(coast, on="TRIBE_CODE", how="left")
    growth["coastal"] = growth.dist_coast_km.le(100).astype(int)
    growth["log_distance"] = np.log1p(growth.dist_coast_km)
    growth_fit = smf.ols("d_log_lights ~ log_exports * coastal + log_distance + C(country)", growth).fit()
    table5 = summarize(growth_fit, ["log_exports", "coastal", "log_exports:coastal", "log_distance"])

    ports = country_data[["country", "atlantic_distance_minimum"]].copy()
    ports["country"] = ports.country.replace({
        "Cote d'Ivoire": "Ivory Coast",
        "Congo, Dem. Rep.": "Democratic Republic of the Congo",
        "Congo, Rep.": "Republic of the Congo",
    })
    homeland = regdata.merge(ports, on="country", validate="many_to_one").dropna(
        subset=["meanlight_2000_2013", "totalexports", "atlantic_distance_minimum"]
    ).copy()
    homeland["log_lights"] = np.log1p(homeland.meanlight_2000_2013)
    homeland["log_exports"] = np.log1p(homeland.totalexports)
    homeland["log_ports"] = np.log1p(homeland.atlantic_distance_minimum)
    homeland["log_land"] = np.log1p(homeland.land_area)
    homeland_ols = smf.ols("log_lights ~ log_exports", homeland).fit()
    table6 = {"ols": summarize(homeland_ols, ["Intercept", "log_exports"])}
    for model, controls in [("iv", []), ("iv_land", ["log_land"])]:
        sample = homeland.dropna(subset=controls)
        fit, diagnostics = iv_fit(sample, "log_lights", "log_exports", "log_ports", controls)
        table6[model] = summarize(fit, ["const", "log_exports", *controls]) | diagnostics

    # The archive drops colony7, legor_uk, and region_c as collinear.
    controls = [f"colony{i}" for i in range(7)] + [
        "abs_latitude", "rain_min", "humid_max", "low_temp", "ln_coastline_area",
        "island_dum", "islam", "legor_fr", "region_n", "region_s", "region_w", "region_e",
    ]
    country_ols = sm.OLS(
        countries.regression_log_lights, sm.add_constant(countries[["ln_export_area", *controls]])
    ).fit()
    country_iv, diagnostics = iv_fit(
        countries, "regression_log_lights", "ln_export_area", "log_ports", controls
    )
    table7 = {
        "ols": summarize(country_ols, ["ln_export_area"]),
        "iv": summarize(country_iv, ["ln_export_area"]) | diagnostics,
    }
    return dict(THomeland=table1, TCountry=table2, TGrowth=table5, THomelandIV=table6, TCountryIV=table7)


def main():
    regdata, exports, country_data, lights, growth, coast, output = map(Path, sys.argv[1:])
    results = calculate(
        pd.read_csv(regdata), pd.read_csv(exports), pd.read_stata(country_data),
        pd.read_csv(lights), pd.read_csv(growth, keep_default_na=False, na_values=[""]),
        pd.read_csv(coast),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
