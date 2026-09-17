#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
import sqlite3
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
R_GAS = 8.314462618
T_REF_K = 393.15


def _rmse(values) -> float:
    values = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(values * values)))


def prepare_local(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = (
        df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    )
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["dx"] = 1000.0 / (df["temperature_c"] + 273.15) - 1000.0 / T_REF_K
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}",
        axis=1,
    )
    return df


def _fit_metrics(name: str, formula: str, df: pd.DataFrame) -> dict:
    model = smf.ols(formula, df).fit()
    err = _rmse(model.resid)
    return {
        "model": name,
        "r2": float(model.rsquared),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "rmse_log": err,
        "multiplicative_rmse": math.exp(err),
    }


def functional_form_sensitivity(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    forms = {
        "invT_linear": "ln_eta ~ C(realization_id) + dx",
        "invT_quadratic": "ln_eta ~ C(realization_id) + dx + I(dx**2)",
        "invT_cubic": "ln_eta ~ C(realization_id) + dx + I(dx**2) + I(dx**3)",
        "temperature_linear": "ln_eta ~ C(realization_id) + temperature_c",
        "temperature_quadratic": "ln_eta ~ C(realization_id) + temperature_c + I(temperature_c**2)",
    }
    fit_table = pd.DataFrame([_fit_metrics(name, formula, df) for name, formula in forms.items()])

    cv_rows = []
    for name, formula in forms.items():
        observed, predicted = [], []
        for temperature_c in sorted(df["temperature_c"].unique()):
            train = df[df["temperature_c"] != temperature_c]
            test = df[df["temperature_c"] == temperature_c]
            model = smf.ols(formula, train).fit()
            observed.extend(test["ln_eta"].tolist())
            predicted.extend(model.predict(test).tolist())
        err = _rmse(np.asarray(observed) - np.asarray(predicted))
        cv_rows.append(
            {
                "model": name,
                "held_temperature_rmse_log": err,
                "held_temperature_multiplicative_error": math.exp(err),
            }
        )
    return fit_table, pd.DataFrame(cv_rows)


def one_point_anchor(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for anchor_temperature_c in sorted(df["temperature_c"].unique()):
        errors = []
        for realization_id, held in df.groupby("realization_id"):
            train = df[df["realization_id"] != realization_id]
            model = smf.ols(
                "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
            ).fit()
            beta1 = float(model.params["dx"])
            beta2 = float(model.params["I(dx ** 2)"])
            anchor = held[held["temperature_c"] == anchor_temperature_c].iloc[0]
            test = held[held["temperature_c"] != anchor_temperature_c]
            prediction = (
                anchor["ln_eta"]
                + beta1 * (test["dx"] - anchor["dx"])
                + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
            )
            errors.extend(test["ln_eta"].to_numpy() - prediction.to_numpy())
        err = _rmse(errors)
        rows.append(
            {
                "anchor_temperature_c": float(anchor_temperature_c),
                "rmse_log": err,
                "multiplicative_error": math.exp(err),
            }
        )
    return pd.DataFrame(rows)


def leave_one_realization_comparison(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Strict unseen-realization test for formulations represented by another realization.

    The formulation-only baseline is deliberately given the same quadratic shared
    thermal form. The state-calibrated model sees one anchor point from the held
    realization and predicts the remaining temperatures.
    """
    pooled_rows = []
    detail_rows = []
    for anchor_temperature_c in sorted(df["temperature_c"].unique()):
        formulation_errors, anchor_errors = [], []
        n_predictions = 0
        n_groups = 0
        for realization_id, held in df.groupby("realization_id"):
            train = df[df["realization_id"] != realization_id]
            formulation_id = held["formulation_id"].iloc[0]
            if formulation_id not in set(train["formulation_id"]):
                continue

            test = held[held["temperature_c"] != anchor_temperature_c]
            baseline = smf.ols(
                "ln_eta ~ C(formulation_id) + dx + I(dx**2)", data=train
            ).fit()
            baseline_error = test["ln_eta"].to_numpy() - baseline.predict(test).to_numpy()

            state_model = smf.ols(
                "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
            ).fit()
            beta1 = float(state_model.params["dx"])
            beta2 = float(state_model.params["I(dx ** 2)"])
            anchor = held[held["temperature_c"] == anchor_temperature_c].iloc[0]
            prediction = (
                anchor["ln_eta"]
                + beta1 * (test["dx"] - anchor["dx"])
                + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
            )
            state_error = test["ln_eta"].to_numpy() - prediction.to_numpy()

            formulation_errors.extend(baseline_error)
            anchor_errors.extend(state_error)
            n_predictions += len(test)
            n_groups += 1

            detail_rows.append(
                {
                    "anchor_temperature_c": float(anchor_temperature_c),
                    "realization_id": realization_id,
                    "formulation_id": formulation_id,
                    "formulation_only_multiplicative_error": math.exp(_rmse(baseline_error)),
                    "one_point_multiplicative_error": math.exp(_rmse(state_error)),
                }
            )

        baseline_rmse = _rmse(formulation_errors)
        anchor_rmse = _rmse(anchor_errors)
        pooled_rows.append(
            {
                "anchor_temperature_c": float(anchor_temperature_c),
                "n_held_realizations": n_groups,
                "n_predictions": n_predictions,
                "formulation_only_rmse_log": baseline_rmse,
                "formulation_only_multiplicative_error": math.exp(baseline_rmse),
                "one_point_rmse_log": anchor_rmse,
                "one_point_multiplicative_error": math.exp(anchor_rmse),
                "log_rmse_reduction": 1.0 - anchor_rmse / baseline_rmse,
            }
        )
    return pd.DataFrame(pooled_rows), pd.DataFrame(detail_rows)


def ratio_stability(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for formulation_id in ["E1", "E2"]:
        subset = df[df["formulation_id"] == formulation_id]
        curves = {
            realization_id: group.set_index("temperature_c")["viscosity_reported"]
            for realization_id, group in subset.groupby("realization_id")
        }
        for realization_a, realization_b in combinations(curves, 2):
            ratio = (curves[realization_a] / curves[realization_b]).dropna()
            rows.append(
                {
                    "formulation_id": formulation_id,
                    "realization_a": realization_a,
                    "realization_b": realization_b,
                    "mean_ratio": float(ratio.mean()),
                    "ratio_cv": float(ratio.std(ddof=1) / ratio.mean()),
                    "ratio_min": float(ratio.min()),
                    "ratio_max": float(ratio.max()),
                }
            )
    return pd.DataFrame(rows)


def e2_variance_collapse(df: pd.DataFrame) -> dict:
    subset = df[df["formulation_id"] == "E2"].copy()
    model = smf.ols(
        "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=subset
    ).fit()
    subset["residual"] = model.resid
    raw_sd = float(subset.groupby("temperature_c")["ln_eta"].std(ddof=1).mean())
    residual_sd = float(subset.groupby("temperature_c")["residual"].std(ddof=1).mean())
    return {
        "mean_raw_between_realization_log_sd": raw_sd,
        "mean_post_shift_residual_log_sd": residual_sd,
        "sd_reduction_fraction": 1.0 - residual_sd / raw_sd,
    }


def external_curve_level(db_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    con = sqlite3.connect(str(db_path))
    try:
        curves = pd.read_sql_query("SELECT * FROM viscosity_curves", con)
    finally:
        con.close()

    for col in ["temperature_c", "viscosity_pa_s", "pNCO_pct"]:
        curves[col] = pd.to_numeric(curves[col], errors="coerce")
    curves = curves.dropna(
        subset=["temperature_c", "viscosity_pa_s", "pNCO_pct", "polyol_code", "isocyanate_code"]
    )
    curves = curves[curves["viscosity_pa_s"] > 0].copy()
    curves["ln_eta"] = np.log(curves["viscosity_pa_s"])

    descriptor_rows = []
    for (source_id, sample_id), group in curves.groupby(["source_id", "sample_id"]):
        fit = stats.linregress(
            1.0 / (group["temperature_c"].to_numpy() + 273.15),
            group["ln_eta"].to_numpy(),
        )
        first = group.iloc[0]
        descriptor_rows.append(
            {
                "source_id": source_id,
                "sample_id": sample_id,
                "polyol_code": first["polyol_code"],
                "isocyanate_code": first["isocyanate_code"],
                "pNCO_pct": float(first["pNCO_pct"]),
                "apparent_E_kJ_mol": float(fit.slope * R_GAS / 1000.0),
                "r2_curve": float(fit.rvalue**2),
                "ln_eta_75": float(fit.intercept + fit.slope / (75.0 + 273.15)),
            }
        )
    descriptor_df = pd.DataFrame(descriptor_rows)

    models = {
        "thermal_additive": (
            "apparent_E_kJ_mol",
            "apparent_E_kJ_mol ~ pNCO_pct + C(polyol_code) + C(isocyanate_code)",
        ),
        "thermal_pNCO_by_polyol": (
            "apparent_E_kJ_mol",
            "apparent_E_kJ_mol ~ pNCO_pct * C(polyol_code) + C(isocyanate_code)",
        ),
        "viscosity75_additive": (
            "ln_eta_75",
            "ln_eta_75 ~ pNCO_pct + C(polyol_code) + C(isocyanate_code)",
        ),
        "viscosity75_pNCO_by_polyol": (
            "ln_eta_75",
            "ln_eta_75 ~ pNCO_pct * C(polyol_code) + C(isocyanate_code)",
        ),
    }

    model_rows = []
    for model_name, (target, formula) in models.items():
        fitted = smf.ols(formula, descriptor_df).fit()
        observed, predicted = [], []
        for index in descriptor_df.index:
            train = descriptor_df.drop(index)
            test = descriptor_df.loc[[index]]
            model = smf.ols(formula, train).fit()
            observed.append(float(test[target].iloc[0]))
            predicted.append(float(model.predict(test).iloc[0]))
        observed = np.asarray(observed)
        predicted = np.asarray(predicted)
        residual = observed - predicted
        cv_r2 = 1.0 - float(
            np.sum(residual**2) / np.sum((observed - observed.mean()) ** 2)
        )
        cv_rmse = _rmse(residual)
        model_rows.append(
            {
                "model": model_name,
                "in_sample_r2": float(fitted.rsquared),
                "aic": float(fitted.aic),
                "bic": float(fitted.bic),
                "loocv_r2": cv_r2,
                "loocv_rmse": cv_rmse,
                "loocv_multiplicative_error": (
                    math.exp(cv_rmse) if target == "ln_eta_75" else None
                ),
            }
        )

    summary = {
        "n_curves": int(len(descriptor_df)),
        "median_curve_r2": float(descriptor_df["r2_curve"].median()),
        "n_curve_r2_ge_0_98": int((descriptor_df["r2_curve"] >= 0.98).sum()),
        "apparent_E_range_kJ_mol": [
            float(descriptor_df["apparent_E_kJ_mol"].min()),
            float(descriptor_df["apparent_E_kJ_mol"].max()),
        ],
    }
    return descriptor_df, pd.DataFrame(model_rows), summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Robustness checks for PUR-NEW statistical claims")
    parser.add_argument(
        "--temperature-csv",
        type=Path,
        default=ROOT / "data" / "temperature_sweeps.csv",
    )
    parser.add_argument("--external-db", type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "derived" / "statistical_robustness",
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = prepare_local(args.temperature_csv)
    fit_table, cv_table = functional_form_sensitivity(df)
    anchor_table = one_point_anchor(df)
    strict_table, strict_detail = leave_one_realization_comparison(df)
    ratio_table = ratio_stability(df)
    collapse = e2_variance_collapse(df)

    fit_table.to_csv(args.output_dir / "functional_form_fit.csv", index=False)
    cv_table.to_csv(args.output_dir / "functional_form_cv.csv", index=False)
    anchor_table.to_csv(args.output_dir / "one_point_anchor.csv", index=False)
    strict_table.to_csv(args.output_dir / "leave_one_realization.csv", index=False)
    strict_detail.to_csv(args.output_dir / "leave_one_realization_detail.csv", index=False)
    ratio_table.to_csv(args.output_dir / "pairwise_ratio_stability.csv", index=False)

    summary = {
        "e2_variance_collapse": collapse,
        "anchor_error_range": [
            float(anchor_table["multiplicative_error"].min()),
            float(anchor_table["multiplicative_error"].max()),
        ],
        "strict_formulation_only_error_range": [
            float(strict_table["formulation_only_multiplicative_error"].min()),
            float(strict_table["formulation_only_multiplicative_error"].max()),
        ],
        "strict_one_point_error_range": [
            float(strict_table["one_point_multiplicative_error"].min()),
            float(strict_table["one_point_multiplicative_error"].max()),
        ],
        "e2_pairwise_ratio_cv_median": float(
            ratio_table.loc[ratio_table["formulation_id"] == "E2", "ratio_cv"].median()
        ),
    }

    if args.external_db:
        descriptors, external_models, external_summary = external_curve_level(args.external_db)
        descriptors.to_csv(args.output_dir / "external_curve_descriptors.csv", index=False)
        external_models.to_csv(args.output_dir / "external_curve_model_cv.csv", index=False)
        summary["external"] = external_summary

    (args.output_dir / "robustness_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output_dir / "robustness_summary.json")


if __name__ == "__main__":
    main()
