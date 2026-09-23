#!/usr/bin/env python3
"""Functional-form, hierarchical-slope and optimizer robustness for PUR-NEW.

This analysis uses the same chemistry-audited 36-point E1-E3 population as the
canonical V5 manuscript. The phosphoric-acid E1 +P curve is retained in source
data but excluded here through realization_metadata.csv because it is a defined
chemical perturbation.

The purpose is not to replace the canonical state-conditioned quadratic model.
It tests whether (i) quadratic curvature is supported over a linear Arrhenius
shape, (ii) cubic flexibility is justified, (iii) the apparent shared thermal
slope is stable to hierarchical/random-intercept treatment and to allowing
realization-specific slopes, and (iv) a nonlinear VFT/shifted-Andrade form gives
the same scientific conclusion under both bounded local optimization and a
dual-annealing global search.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[1]
R_GAS = 8.314462618
T_REF_K = 393.15
PRIMARY_ROLES = {"primary", "primary_with_caveat"}


def _rmse(values) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def _aicc_from_rss(rss: float, n: int, k: int) -> float:
    aic = n * (math.log(2.0 * math.pi) + 1.0 + math.log(rss / n)) + 2.0 * k
    if n <= k + 1:
        return float("nan")
    return float(aic + 2.0 * k * (k + 1.0) / (n - k - 1.0))


def prepare_primary(temperature_csv: Path, metadata_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(temperature_csv)
    meta = pd.read_csv(metadata_csv)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = (
        df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    )
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["temperature_k"] = df["temperature_c"] + 273.15
    df["dx"] = 1000.0 / df["temperature_k"] - 1000.0 / T_REF_K
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}",
        axis=1,
    )
    merged = df.merge(
        meta[["realization_id", "analysis_role"]],
        on="realization_id",
        how="left",
        validate="many_to_one",
    )
    if merged["analysis_role"].isna().any():
        missing = sorted(merged.loc[merged["analysis_role"].isna(), "realization_id"].unique())
        raise ValueError(f"Missing realization metadata for: {missing}")
    primary = merged[merged["analysis_role"].isin(PRIMARY_ROLES)].copy()
    if len(primary) != 36 or primary["realization_id"].nunique() != 6:
        raise ValueError(
            "Expected the V5 chemistry-audited population to contain 36 points from 6 realizations; "
            f"found {len(primary)} points from {primary['realization_id'].nunique()} realizations."
        )
    return primary


def _leave_one_temperature_out(df: pd.DataFrame, formula: str) -> float:
    observed: list[float] = []
    predicted: list[float] = []
    for temperature_c in sorted(df["temperature_c"].unique()):
        train = df[df["temperature_c"] != temperature_c]
        test = df[df["temperature_c"] == temperature_c]
        model = smf.ols(formula, data=train).fit()
        observed.extend(test["ln_eta"].tolist())
        predicted.extend(model.predict(test).tolist())
    return _rmse(np.asarray(observed) - np.asarray(predicted))


def _fit_vft(df: pd.DataFrame, optimizer: str) -> tuple[float, object]:
    """Profile a shared VFT/shifted-Andrade T0 with realization-specific intercepts.

    ln(eta_ir) = a_r + B / (T - T0) + error.
    T0 is constrained below the measured range. For any candidate T0, a_r and B
    are obtained by ordinary least squares; only the one-dimensional T0 profile
    is optimized nonlinearly.
    """
    lower = 150.0
    upper = min(330.0, float(df["temperature_k"].min()) - 10.0)

    def sse(t0: float) -> float:
        work = df.copy()
        work["vft_x"] = 1.0 / (work["temperature_k"] - float(t0))
        model = smf.ols("ln_eta ~ C(realization_id) + vft_x", data=work).fit()
        return float(np.sum(np.asarray(model.resid) ** 2))

    if optimizer == "bounded":
        result = optimize.minimize_scalar(
            sse,
            bounds=(lower, upper),
            method="bounded",
            options={"xatol": 1e-10},
        )
        t0 = float(result.x)
    elif optimizer == "dual_annealing":
        result = optimize.dual_annealing(
            lambda x: sse(float(x[0])),
            bounds=[(lower, upper)],
            seed=20260923,
            maxiter=1000,
            no_local_search=False,
        )
        t0 = float(result.x[0])
    else:
        raise ValueError(f"Unknown optimizer: {optimizer}")

    work = df.copy()
    work["vft_x"] = 1.0 / (work["temperature_k"] - t0)
    model = smf.ols("ln_eta ~ C(realization_id) + vft_x", data=work).fit()
    return t0, model


def _vft_leave_one_temperature_out(df: pd.DataFrame) -> tuple[float, list[dict]]:
    observed: list[float] = []
    predicted: list[float] = []
    folds: list[dict] = []
    for temperature_c in sorted(df["temperature_c"].unique()):
        train = df[df["temperature_c"] != temperature_c].copy()
        test = df[df["temperature_c"] == temperature_c].copy()
        t0, model = _fit_vft(train, "bounded")
        test["vft_x"] = 1.0 / (test["temperature_k"] - t0)
        observed.extend(test["ln_eta"].tolist())
        predicted.extend(model.predict(test).tolist())
        folds.append(
            {"held_temperature_c": float(temperature_c), "T0_K": t0, "T0_C": t0 - 273.15}
        )
    return _rmse(np.asarray(observed) - np.asarray(predicted)), folds


def functional_form_table(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    formulas = {
        "state_shared_linear": "ln_eta ~ C(realization_id) + dx",
        "state_shared_quadratic": "ln_eta ~ C(realization_id) + dx + I(dx**2)",
        "state_shared_cubic": "ln_eta ~ C(realization_id) + dx + I(dx**2) + I(dx**3)",
    }
    fitted = {name: smf.ols(formula, data=df).fit() for name, formula in formulas.items()}
    rows: list[dict] = []
    for name, formula in formulas.items():
        model = fitted[name]
        fit_rmse = _rmse(model.resid)
        cv_rmse = _leave_one_temperature_out(df, formula)
        rows.append(
            {
                "model": name,
                "n_parameters": int(len(model.params)),
                "r2": float(model.rsquared),
                "fit_rmse_log": fit_rmse,
                "fit_multiplicative_rmse": math.exp(fit_rmse),
                "held_temperature_rmse_log": cv_rmse,
                "held_temperature_multiplicative_error": math.exp(cv_rmse),
                "aicc": _aicc_from_rss(
                    float(np.sum(np.asarray(model.resid) ** 2)), len(df), len(model.params)
                ),
            }
        )

    t0_bounded, vft_bounded = _fit_vft(df, "bounded")
    vft_fit_rmse = _rmse(vft_bounded.resid)
    vft_cv_rmse, fold_t0 = _vft_leave_one_temperature_out(df)
    vft_k = len(vft_bounded.params) + 1
    rows.append(
        {
            "model": "state_shared_vft",
            "n_parameters": int(vft_k),
            "r2": np.nan,
            "fit_rmse_log": vft_fit_rmse,
            "fit_multiplicative_rmse": math.exp(vft_fit_rmse),
            "held_temperature_rmse_log": vft_cv_rmse,
            "held_temperature_multiplicative_error": math.exp(vft_cv_rmse),
            "aicc": _aicc_from_rss(
                float(np.sum(np.asarray(vft_bounded.resid) ** 2)), len(df), vft_k
            ),
        }
    )

    quad = fitted["state_shared_quadratic"]
    lin = fitted["state_shared_linear"]
    cubic = fitted["state_shared_cubic"]
    specific = smf.ols("ln_eta ~ C(realization_id) * dx", data=df).fit()
    nested_rows = []
    for label, restricted, full in [
        ("shared linear -> shared quadratic", lin, quad),
        ("shared quadratic -> shared cubic", quad, cubic),
        ("shared linear slope -> realization-specific linear slopes", lin, specific),
    ]:
        f_stat, p_value, df_diff = full.compare_f_test(restricted)
        nested_rows.append(
            {
                "comparison": label,
                "F": float(f_stat),
                "p_value": float(p_value),
                "df_difference": float(df_diff),
                "full_model_residual_df": float(full.df_resid),
            }
        )

    t0_dual, vft_dual = _fit_vft(df, "dual_annealing")
    optimizer_summary = {
        "bounded": {
            "T0_K": t0_bounded,
            "T0_C": t0_bounded - 273.15,
            "B_K": float(vft_bounded.params["vft_x"]),
            "fit_rmse_log": vft_fit_rmse,
            "fit_multiplicative_rmse": math.exp(vft_fit_rmse),
        },
        "dual_annealing": {
            "T0_K": t0_dual,
            "T0_C": t0_dual - 273.15,
            "B_K": float(vft_dual.params["vft_x"]),
            "fit_rmse_log": _rmse(vft_dual.resid),
            "fit_multiplicative_rmse": math.exp(_rmse(vft_dual.resid)),
        },
        "absolute_T0_difference_K": abs(t0_dual - t0_bounded),
        "leave_one_temperature_T0": fold_t0,
    }
    return pd.DataFrame(rows), pd.DataFrame(nested_rows), optimizer_summary


def shared_slope_summary(df: pd.DataFrame) -> dict:
    fixed_common = smf.ols("ln_eta ~ C(realization_id) + dx", data=df).fit()
    beta = float(fixed_common.params["dx"])
    beta_ci = [float(x) for x in fixed_common.conf_int().loc["dx"].tolist()]

    mixed = smf.mixedlm("ln_eta ~ dx", data=df, groups=df["realization_id"]).fit(
        reml=False, method="lbfgs"
    )
    mixed_beta = float(mixed.params["dx"])
    mixed_ci = [float(x) for x in mixed.conf_int().loc["dx"].tolist()]

    specific = smf.ols("ln_eta ~ C(realization_id) * dx", data=df).fit()
    f_stat, p_value, df_diff = specific.compare_f_test(fixed_common)

    return {
        "n_points": int(len(df)),
        "n_realizations": int(df["realization_id"].nunique()),
        "fixed_realization_intercepts_shared_slope": {
            "E_eta_kJ_mol": beta * R_GAS,
            "ci95_kJ_mol": [beta_ci[0] * R_GAS, beta_ci[1] * R_GAS],
        },
        "random_intercept_mixed_model_shared_slope": {
            "E_eta_kJ_mol": mixed_beta * R_GAS,
            "ci95_kJ_mol": [mixed_ci[0] * R_GAS, mixed_ci[1] * R_GAS],
            "random_intercept_sd_log": math.sqrt(float(mixed.cov_re.iloc[0, 0])),
            "residual_sd_log": math.sqrt(float(mixed.scale)),
            "interpretation": (
                "Supporting hierarchical sensitivity only; six realization groups are too few "
                "for strong variance-component inference."
            ),
        },
        "realization_specific_slope_test": {
            "F": float(f_stat),
            "df_num": int(df_diff),
            "df_den": int(specific.df_resid),
            "p_value": float(p_value),
            "interpretation": (
                "No evidence that realization-specific linear thermal slopes improve the "
                "audited local model at conventional thresholds."
            ),
        },
    }


def vft_leave_one_realization_stability(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for held_realization in sorted(df["realization_id"].unique()):
        train = df[df["realization_id"] != held_realization].copy()
        t0, model = _fit_vft(train, "bounded")
        rows.append(
            {
                "held_realization": held_realization,
                "T0_K": t0,
                "T0_C": t0 - 273.15,
                "B_K": float(model.params["vft_x"]),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Thermal-model robustness analysis for PUR-NEW V5")
    parser.add_argument(
        "--temperature-csv", type=Path, default=ROOT / "data" / "temperature_sweeps.csv"
    )
    parser.add_argument(
        "--metadata-csv", type=Path, default=ROOT / "data" / "realization_metadata.csv"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=ROOT / "derived" / "thermal_model_robustness"
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = prepare_primary(args.temperature_csv, args.metadata_csv)
    models, nested, optimizer_summary = functional_form_table(df)
    hierarchical = shared_slope_summary(df)
    vft_loo = vft_leave_one_realization_stability(df)

    models.to_csv(args.output_dir / "functional_form_model_comparison.csv", index=False)
    nested.to_csv(args.output_dir / "nested_functional_form_tests.csv", index=False)
    vft_loo.to_csv(args.output_dir / "vft_leave_one_realization_stability.csv", index=False)

    summary = {
        "analysis_population": {
            "n_points": int(len(df)),
            "n_realizations": int(df["realization_id"].nunique()),
            "n_formulations": int(df["formulation_id"].nunique()),
            "excluded_by_metadata": "E1 +P chemical perturbation",
        },
        "hierarchical_shared_slope": hierarchical,
        "vft_optimizer_sensitivity": optimizer_summary,
        "vft_leave_one_realization_T0_C_range": [
            float(vft_loo["T0_C"].min()),
            float(vft_loo["T0_C"].max()),
        ],
        "claim_boundary": (
            "The quadratic model remains the canonical local representation. VFT and "
            "dual-annealing results are functional-form and numerical-optimizer sensitivity "
            "analyses, not independent molecular-parameter claims."
        ),
    }
    (args.output_dir / "thermal_model_robustness_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
