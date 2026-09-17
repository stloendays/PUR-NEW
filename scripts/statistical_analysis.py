#!/usr/bin/env python3
"""Reproduce the PUR-NEW statistical/model analysis.

Local analysis uses only the compact CSVs committed to this repository.
External-database context is optional and is added when --external-db points to
an HMPUR SQLite database containing `viscosity_curves` and `observations`.

Important interpretation rule: GJJ, ZYX and CHH are opaque realization labels
from the same operator. They are never interpreted as operator categories.
"""

from __future__ import annotations

import argparse
import json
import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

R_GAS = 8.314462618  # J mol^-1 K^-1
T_REF_C = 120.0
T_REF_K = T_REF_C + 273.15


def _rmse(residual: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.asarray(residual, dtype=float) ** 2)))


def _model_row(name: str, model) -> dict:
    rmse = _rmse(model.resid)
    return {
        "model": name,
        "n_parameters": int(len(model.params)),
        "r2": float(model.rsquared),
        "adjusted_r2": float(model.rsquared_adj),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "rmse_log": rmse,
        "mae_log": float(np.mean(np.abs(model.resid))),
        "multiplicative_rmse": float(np.exp(rmse)),
    }


def _nested_row(label: str, restricted, full) -> dict:
    f_stat, p_value, df_diff = full.compare_f_test(restricted)
    return {
        "comparison": label,
        "f_stat": float(f_stat),
        "p_value": float(p_value),
        "df_diff": float(df_diff),
    }


def prepare_temperature_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = (
        df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    )
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["temperature_k"] = df["temperature_c"] + 273.15
    df["invT1000"] = 1000.0 / df["temperature_k"]
    df["dx"] = df["invT1000"] - 1000.0 / T_REF_K
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}",
        axis=1,
    )
    return df


def local_model_comparison(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    models = {
        "M0_formulation_only": smf.ols(
            "ln_eta ~ C(formulation_id) + dx", data=df
        ).fit(),
        "M0b_formulation_specific_slope": smf.ols(
            "ln_eta ~ C(formulation_id) * dx", data=df
        ).fit(),
        "M1_plus_observed_day1_flag": smf.ols(
            "ln_eta ~ C(formulation_id) + dx + retest_after_1d", data=df
        ).fit(),
        "M2_state_intercept_linear": smf.ols(
            "ln_eta ~ C(realization_id) + dx", data=df
        ).fit(),
        "M2q_state_intercept_shared_quadratic": smf.ols(
            "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=df
        ).fit(),
        "M3_state_specific_slope": smf.ols(
            "ln_eta ~ C(realization_id) * dx", data=df
        ).fit(),
    }

    table = pd.DataFrame([_model_row(name, model) for name, model in models.items()])

    # Additional nested forms for scientifically useful tests.
    state_plus_formulation_slope = smf.ols(
        "ln_eta ~ C(realization_id) + dx + C(formulation_id):dx", data=df
    ).fit()
    nested = pd.DataFrame(
        [
            _nested_row(
                "formulation-only -> +day1 flag",
                models["M0_formulation_only"],
                models["M1_plus_observed_day1_flag"],
            ),
            _nested_row(
                "formulation-only -> realization intercept",
                models["M0_formulation_only"],
                models["M2_state_intercept_linear"],
            ),
            _nested_row(
                "realization intercept -> realization-specific thermal slopes",
                models["M2_state_intercept_linear"],
                models["M3_state_specific_slope"],
            ),
            _nested_row(
                "shared linear thermal shape -> shared quadratic thermal shape",
                models["M2_state_intercept_linear"],
                models["M2q_state_intercept_shared_quadratic"],
            ),
            _nested_row(
                "formulation-specific thermal slopes -> +realization intercept",
                models["M0b_formulation_specific_slope"],
                smf.ols(
                    "ln_eta ~ C(realization_id) + C(formulation_id) * dx", data=df
                ).fit(),
            ),
            _nested_row(
                "state intercept/common slope -> formulation-specific slopes",
                models["M2_state_intercept_linear"],
                state_plus_formulation_slope,
            ),
        ]
    )

    # Mixed-effects sensitivity: fixed formulation + shared quadratic thermal shape,
    # random intercept by realization. Seven groups is small, so this is supporting evidence.
    mixed = smf.mixedlm(
        "ln_eta ~ C(formulation_id) + dx + I(dx**2)",
        data=df,
        groups=df["realization_id"],
    ).fit(reml=False, method="lbfgs")
    random_var = float(mixed.cov_re.iloc[0, 0])
    residual_var = float(mixed.scale)
    mixed_summary = {
        "n_realization_groups": int(df["realization_id"].nunique()),
        "random_intercept_sd_log": math.sqrt(random_var),
        "residual_sd_log": math.sqrt(residual_var),
        "icc": random_var / (random_var + residual_var),
        "one_sd_state_scale_factor": math.exp(math.sqrt(random_var)),
    }

    return table, nested, mixed_summary


def leave_one_temperature_out(df: pd.DataFrame) -> pd.DataFrame:
    formulas = {
        "M0_formulation_only": "ln_eta ~ C(formulation_id) + dx",
        "M2_state_intercept_linear": "ln_eta ~ C(realization_id) + dx",
        "M2q_state_intercept_shared_quadratic": "ln_eta ~ C(realization_id) + dx + I(dx**2)",
    }
    out = []
    for name, formula in formulas.items():
        obs, pred = [], []
        for temp in sorted(df["temperature_c"].unique()):
            train = df[df["temperature_c"] != temp]
            test = df[df["temperature_c"] == temp]
            model = smf.ols(formula, data=train).fit()
            obs.extend(test["ln_eta"].tolist())
            pred.extend(model.predict(test).tolist())
        rmse = float(np.sqrt(np.mean((np.asarray(obs) - np.asarray(pred)) ** 2)))
        out.append(
            {
                "validation_type": "leave_one_temperature_out",
                "model": name,
                "anchor_temperature_c": np.nan,
                "rmse_log": rmse,
                "multiplicative_error_factor": float(np.exp(rmse)),
            }
        )
    return pd.DataFrame(out)


def one_point_state_calibration(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for anchor_temp in sorted(df["temperature_c"].unique()):
        obs, pred = [], []
        for realization_id, held in df.groupby("realization_id"):
            train = df[df["realization_id"] != realization_id]
            model = smf.ols(
                "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
            ).fit()
            beta1 = float(model.params["dx"])
            beta2 = float(model.params["I(dx ** 2)"])
            anchor = held[held["temperature_c"] == anchor_temp].iloc[0]
            for _, row in held[held["temperature_c"] != anchor_temp].iterrows():
                yhat = (
                    anchor["ln_eta"]
                    + beta1 * (row["dx"] - anchor["dx"])
                    + beta2 * (row["dx"] ** 2 - anchor["dx"] ** 2)
                )
                obs.append(float(row["ln_eta"]))
                pred.append(float(yhat))
        rmse = float(np.sqrt(np.mean((np.asarray(obs) - np.asarray(pred)) ** 2)))
        out.append(
            {
                "validation_type": "leave_one_realization_out_one_point_anchor",
                "model": "state_shared_quadratic",
                "anchor_temperature_c": float(anchor_temp),
                "rmse_log": rmse,
                "multiplicative_error_factor": float(np.exp(rmse)),
            }
        )
    return pd.DataFrame(out)


def local_thermal_curve_fits(df: pd.DataFrame) -> pd.DataFrame:
    out = []
    for realization_id, g in df.groupby("realization_id"):
        x = 1.0 / (g["temperature_c"].to_numpy() + 273.15)
        y = g["ln_eta"].to_numpy()
        fit = stats.linregress(x, y)
        first = g.iloc[0]
        out.append(
            {
                "realization_id": realization_id,
                "formulation_id": first["formulation_id"],
                "retest_after_1d": bool(first["retest_after_1d"]),
                "n_points": int(len(g)),
                "apparent_E_kJ_mol": float(fit.slope * R_GAS / 1000.0),
                "r2_lneta_vs_invT": float(fit.rvalue**2),
            }
        )
    return pd.DataFrame(out)


def local_hold_dynamics(path: Path) -> tuple[pd.DataFrame, dict]:
    df = pd.read_csv(path)
    for col in ["temperature_c", "time_min", "viscosity_reported"]:
        df[col] = pd.to_numeric(df[col], errors="raise")
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["time_h"] = df["time_min"] / 60.0

    out = []
    for (formulation_id, run_label), g in df.groupby(["formulation_id", "run_label"]):
        g = g.sort_values("time_min")
        first, last = g.iloc[0], g.iloc[-1]
        fit = stats.linregress(g["time_h"], g["ln_eta"])
        si = (last["viscosity_reported"] - first["viscosity_reported"]) / first[
            "viscosity_reported"
        ]
        endpoint_log_rate = math.log(
            last["viscosity_reported"] / first["viscosity_reported"]
        ) / (last["time_h"] - first["time_h"])
        out.append(
            {
                "formulation_id": formulation_id,
                "run_label": run_label,
                "n_points": int(len(g)),
                "time_start_min": float(first["time_min"]),
                "time_end_min": float(last["time_min"]),
                "SI_endpoint": float(si),
                "endpoint_log_drift_per_h": float(endpoint_log_rate),
                "linear_lneta_slope_per_h": float(fit.slope),
                "linear_lneta_r2": float(fit.rvalue**2),
            }
        )
    table = pd.DataFrame(out)

    # E1 versus E5 interaction over their common 15-90 min trajectories.
    orig = df[df["formulation_id"].isin(["E1", "E5"])].copy()
    base = smf.ols("ln_eta ~ time_h + C(formulation_id)", data=orig).fit()
    interaction = smf.ols("ln_eta ~ time_h * C(formulation_id)", data=orig).fit()
    f_stat, p_value, _ = interaction.compare_f_test(base)

    # F1 common-slope descriptive model with repeat intercept.
    f1 = df[df["formulation_id"] == "F1"].copy()
    f1_model = smf.ols("ln_eta ~ time_h + C(run_label)", data=f1).fit()
    ci = f1_model.conf_int().loc["time_h"].tolist()

    # Matched 15->60 SI values.
    def matched_si(formulation_id: str, run_label: str | None = None) -> float:
        subset = df[df["formulation_id"] == formulation_id].copy()
        if run_label is not None:
            subset = subset[subset["run_label"] == run_label]
        e0 = float(subset.loc[subset["time_min"] == 15, "viscosity_reported"].mean())
        e1 = float(subset.loc[subset["time_min"] == 60, "viscosity_reported"].mean())
        return (e1 - e0) / e0

    e1_si = matched_si("E1")
    e5_si = matched_si("E5")
    f1_si = matched_si("F1")

    # Repeat-level ratio stability across time.
    pivot = f1.pivot(index="time_min", columns="run_label", values="viscosity_reported")
    repeat_ratio = pivot.max(axis=1) / pivot.min(axis=1)

    summary = {
        "E1_vs_E5_time_slope_interaction_F": float(f_stat),
        "E1_vs_E5_time_slope_interaction_p": float(p_value),
        "F1_common_slope_per_h": float(f1_model.params["time_h"]),
        "F1_common_slope_95ci": [float(ci[0]), float(ci[1])],
        "F1_common_slope_p": float(f1_model.pvalues["time_h"]),
        "F1_repeat_mean_offset_ratio": float(repeat_ratio.mean()),
        "F1_repeat_ratio_cv": float(repeat_ratio.std(ddof=1) / repeat_ratio.mean()),
        "E1_SI_15_60": float(e1_si),
        "E5_SI_15_60": float(e5_si),
        "F1_mean_SI_15_60": float(f1_si),
        "F1_abs_drift_reduction_vs_E1": float(1.0 - abs(f1_si) / abs(e1_si)),
        "F1_abs_drift_reduction_vs_E5": float(1.0 - abs(f1_si) / abs(e5_si)),
    }
    return table, summary


def external_context(db_path: Path, output_dir: Path) -> dict:
    con = sqlite3.connect(str(db_path))
    try:
        curves = pd.read_sql_query("SELECT * FROM viscosity_curves", con)
        obs = pd.read_sql_query("SELECT * FROM observations", con)
    finally:
        con.close()

    for col in ["temperature_c", "viscosity_pa_s", "pNCO_pct"]:
        curves[col] = pd.to_numeric(curves[col], errors="coerce")
    curves = curves.dropna(subset=["temperature_c", "viscosity_pa_s"])
    curves = curves[curves["viscosity_pa_s"] > 0].copy()
    curves["ln_eta"] = np.log(curves["viscosity_pa_s"])
    curves["dx"] = 1000.0 / (curves["temperature_c"] + 273.15) - 1000.0 / (75.0 + 273.15)

    fit_rows = []
    for sample_id, g in curves.groupby("sample_id"):
        x = 1.0 / (g["temperature_c"].to_numpy() + 273.15)
        y = g["ln_eta"].to_numpy()
        fit = stats.linregress(x, y)
        first = g.iloc[0]
        ln_eta_75 = float(fit.intercept + fit.slope / (75.0 + 273.15))
        fit_rows.append(
            {
                "sample_id": sample_id,
                "polyol_code": first["polyol_code"],
                "isocyanate_code": first["isocyanate_code"],
                "pNCO_pct": pd.to_numeric(first["pNCO_pct"], errors="coerce"),
                "apparent_E_kJ_mol": float(fit.slope * R_GAS / 1000.0),
                "r2": float(fit.rvalue**2),
                "ln_eta_75": ln_eta_75,
            }
        )
    curve_fits = pd.DataFrame(fit_rows)

    m_e = smf.ols(
        "apparent_E_kJ_mol ~ pNCO_pct + C(polyol_code) + C(isocyanate_code)",
        data=curve_fits,
    ).fit()
    m_eta75 = smf.ols(
        "ln_eta_75 ~ pNCO_pct + C(polyol_code) + C(isocyanate_code)",
        data=curve_fits,
    ).fit()

    family_rows = []
    for polyol_code, g in curves.groupby("polyol_code"):
        linear = smf.ols("ln_eta ~ C(sample_id) + dx", data=g).fit()
        quadratic = smf.ols("ln_eta ~ C(sample_id) + dx + I(dx**2)", data=g).fit()
        linear_rmse = _rmse(linear.resid)
        quadratic_rmse = _rmse(quadratic.resid)
        family_rows.append(
            {
                "polyol_code": polyol_code,
                "n_curves": int(g["sample_id"].nunique()),
                "shared_linear_rmse_log": linear_rmse,
                "shared_linear_factor": float(np.exp(linear_rmse)),
                "shared_quadratic_rmse_log": quadratic_rmse,
                "shared_quadratic_factor": float(np.exp(quadratic_rmse)),
            }
        )
    pd.DataFrame(family_rows).to_csv(
        output_dir / "external_family_master_curve_summary.csv", index=False
    )

    obs["numeric_value"] = pd.to_numeric(obs["value"], errors="coerce")
    melt = obs[obs["property_name_normalized"] == "melt_viscosity"][
        ["formulation_id", "source_id", "sample_id", "numeric_value", "unit"]
    ].rename(columns={"numeric_value": "melt_viscosity"})
    rise = obs[obs["property_name_normalized"] == "viscosity_rise_rate"][
        ["formulation_id", "numeric_value"]
    ].rename(columns={"numeric_value": "viscosity_rise_rate"})
    pairs = melt.merge(rise, on="formulation_id", how="inner").dropna(
        subset=["melt_viscosity", "viscosity_rise_rate"]
    )
    # Preserve only directly comparable patent records (same source family and cP basis).
    if "PAT_US20030022973A1" in set(pairs["source_id"]):
        pairs = pairs[pairs["source_id"] == "PAT_US20030022973A1"].copy()
    pairs[["formulation_id", "source_id", "sample_id", "melt_viscosity", "viscosity_rise_rate"]].to_csv(
        output_dir / "external_static_viscosity_vs_stability_pairs.csv", index=False
    )

    log_v = np.log(pairs["melt_viscosity"].to_numpy())
    rise_v = pairs["viscosity_rise_rate"].to_numpy()
    pearson = stats.pearsonr(log_v, rise_v)
    spearman = stats.spearmanr(log_v, rise_v)

    return {
        "n_curves": int(curve_fits.shape[0]),
        "n_curve_points": int(curves.shape[0]),
        "median_curve_r2": float(curve_fits["r2"].median()),
        "n_curve_r2_ge_0_98": int((curve_fits["r2"] >= 0.98).sum()),
        "apparent_E_range_kJ_mol": [
            float(curve_fits["apparent_E_kJ_mol"].min()),
            float(curve_fits["apparent_E_kJ_mol"].max()),
        ],
        "composition_model_E_r2": float(m_e.rsquared),
        "composition_model_E_pNCO_coef_kJ_mol_per_pct": float(m_e.params["pNCO_pct"]),
        "composition_model_E_pNCO_p": float(m_e.pvalues["pNCO_pct"]),
        "composition_model_ln_eta75_r2": float(m_eta75.rsquared),
        "composition_model_eta75_multiplier_per_plus1pct_pNCO": float(
            np.exp(m_eta75.params["pNCO_pct"])
        ),
        "composition_model_eta75_pNCO_p": float(m_eta75.pvalues["pNCO_pct"]),
        "paired_static_viscosity_stability": {
            "n_paired_formulations": int(len(pairs)),
            "pearson_log_viscosity_vs_rise_rate_r": float(pearson.statistic),
            "pearson_p": float(pearson.pvalue),
            "spearman_rho": float(spearman.statistic),
            "spearman_p": float(spearman.pvalue),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis/results"))
    parser.add_argument("--external-db", type=Path, default=None)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    temp = prepare_temperature_data(args.data_dir / "temperature_sweeps.csv")
    model_table, nested_table, mixed_summary = local_model_comparison(temp)
    thermal_fits = local_thermal_curve_fits(temp)
    validation = pd.concat(
        [leave_one_temperature_out(temp), one_point_state_calibration(temp)],
        ignore_index=True,
    )
    hold_table, hold_summary = local_hold_dynamics(args.data_dir / "thermal_hold.csv")

    model_table.to_csv(args.output_dir / "local_model_comparison.csv", index=False)
    nested_table.to_csv(args.output_dir / "local_nested_model_tests.csv", index=False)
    validation.to_csv(args.output_dir / "local_validation.csv", index=False)
    thermal_fits.to_csv(args.output_dir / "local_thermal_curve_fits.csv", index=False)
    hold_table.to_csv(args.output_dir / "local_hold_dynamics.csv", index=False)

    local_mean_e = float(thermal_fits["apparent_E_kJ_mol"].mean())
    local_sd_e = float(thermal_fits["apparent_E_kJ_mol"].std(ddof=1))
    m2q = model_table.loc[
        model_table["model"] == "M2q_state_intercept_shared_quadratic"
    ].iloc[0]
    anchor_rows = validation[
        validation["validation_type"] == "leave_one_realization_out_one_point_anchor"
    ]

    summary = {
        "local_temperature": {
            "n_points": int(len(temp)),
            "n_formulations_with_full_sweeps": int(temp["formulation_id"].nunique()),
            "n_realizations": int(temp["realization_id"].nunique()),
            "local_apparent_E_mean_kJ_mol": local_mean_e,
            "local_apparent_E_sd_kJ_mol": local_sd_e,
            "local_apparent_E_cv": local_sd_e / local_mean_e,
            "median_curve_r2": float(thermal_fits["r2_lneta_vs_invT"].median()),
            "state_quadratic_fit_rmse_log": float(m2q["rmse_log"]),
            "state_quadratic_fit_factor": float(m2q["multiplicative_rmse"]),
            "one_point_anchor_min_factor": float(
                anchor_rows["multiplicative_error_factor"].min()
            ),
            "one_point_anchor_max_factor": float(
                anchor_rows["multiplicative_error_factor"].max()
            ),
            "mixed_effects": mixed_summary,
        },
        "local_hold": hold_summary,
    }

    if args.external_db is not None:
        summary["external_database"] = external_context(args.external_db, args.output_dir)

    with open(args.output_dir / "analysis_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
        fh.write("\n")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
