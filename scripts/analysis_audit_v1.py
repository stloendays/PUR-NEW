#!/usr/bin/env python3
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

ROOT = Path(__file__).resolve().parents[1]
R_GAS = 8.314462618
T_REF_K = 393.15


def _rmse(values) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def prepare_local(temperature_csv: Path, metadata_csv: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(temperature_csv)
    meta = pd.read_csv(metadata_csv)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["dx"] = 1000.0 / (df["temperature_c"] + 273.15) - 1000.0 / T_REF_K
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}", axis=1
    )
    merged = df.merge(
        meta[["realization_id", "chemistry_comparability", "analysis_role", "parent_sample_relation"]],
        on="realization_id",
        how="left",
        validate="many_to_one",
    )
    if merged["analysis_role"].isna().any():
        missing = sorted(merged.loc[merged["analysis_role"].isna(), "realization_id"].unique())
        raise ValueError(f"Missing realization metadata for: {missing}")
    audited = merged[merged["analysis_role"] != "sensitivity_only"].copy()
    return merged, audited


def fit_and_cv(df: pd.DataFrame) -> pd.DataFrame:
    formulas = {
        "formulation_only_linear": "ln_eta ~ C(formulation_id) + dx",
        "state_shared_quadratic": "ln_eta ~ C(realization_id) + dx + I(dx**2)",
    }
    rows = []
    for name, formula in formulas.items():
        model = smf.ols(formula, df).fit()
        fit_rmse = _rmse(model.resid)
        obs, pred = [], []
        for temp in sorted(df["temperature_c"].unique()):
            train = df[df["temperature_c"] != temp]
            test = df[df["temperature_c"] == temp]
            fitted = smf.ols(formula, train).fit()
            obs.extend(test["ln_eta"].tolist())
            pred.extend(fitted.predict(test).tolist())
        cv_rmse = _rmse(np.asarray(obs) - np.asarray(pred))
        rows.append(
            {
                "model": name,
                "n_points": int(len(df)),
                "n_realizations": int(df["realization_id"].nunique()),
                "r2": float(model.rsquared),
                "aic": float(model.aic),
                "bic": float(model.bic),
                "fit_multiplicative_rmse": math.exp(fit_rmse),
                "held_temperature_multiplicative_error": math.exp(cv_rmse),
            }
        )
    return pd.DataFrame(rows)


def model_free_state_shift(df: pd.DataFrame) -> dict:
    matrix = df.pivot(index="realization_id", columns="temperature_c", values="ln_eta").dropna()
    x = matrix.to_numpy(dtype=float)
    x = x - x.mean(axis=0, keepdims=True)
    _u, s, vt = np.linalg.svd(x, full_matrices=False)
    variance = s * s
    explained = variance / variance.sum()
    pc1 = vt[0]
    constant = np.ones_like(pc1) / np.sqrt(len(pc1))
    cosine = abs(float(np.dot(pc1, constant) / (np.linalg.norm(pc1) * np.linalg.norm(constant))))
    return {
        "n_complete_realizations": int(matrix.shape[0]),
        "n_temperatures": int(matrix.shape[1]),
        "pc1_explained_variance_fraction": float(explained[0]),
        "pc1_constant_shift_cosine_similarity": cosine,
        "pc1_loadings": [float(x) for x in pc1],
        "temperature_order_c": [float(x) for x in matrix.columns],
        "interpretation": (
            "After centering by temperature, the dominant between-realization mode is compared with a constant vertical log-viscosity shift."
        ),
    }


def leave_one_formulation_one_point(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    pooled = []
    detail = []
    for held_formulation in sorted(df["formulation_id"].unique()):
        train = df[df["formulation_id"] != held_formulation]
        held_all = df[df["formulation_id"] == held_formulation]
        shape = smf.ols("ln_eta ~ C(realization_id) + dx + I(dx**2)", train).fit()
        beta1 = float(shape.params["dx"])
        beta2 = float(shape.params["I(dx ** 2)"])
        for anchor_temp in sorted(df["temperature_c"].unique()):
            errors = []
            n_realizations = 0
            for realization_id, held in held_all.groupby("realization_id"):
                anchor_rows = held[held["temperature_c"] == anchor_temp]
                if anchor_rows.empty:
                    continue
                anchor = anchor_rows.iloc[0]
                test = held[held["temperature_c"] != anchor_temp]
                prediction = (
                    anchor["ln_eta"]
                    + beta1 * (test["dx"] - anchor["dx"])
                    + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
                )
                err = test["ln_eta"].to_numpy() - prediction.to_numpy()
                errors.extend(err.tolist())
                n_realizations += 1
                detail.append(
                    {
                        "held_formulation": held_formulation,
                        "held_realization": realization_id,
                        "anchor_temperature_c": float(anchor_temp),
                        "multiplicative_error": math.exp(_rmse(err)),
                    }
                )
            pooled.append(
                {
                    "held_formulation": held_formulation,
                    "anchor_temperature_c": float(anchor_temp),
                    "n_held_realizations": n_realizations,
                    "multiplicative_error": math.exp(_rmse(errors)),
                }
            )
    return pd.DataFrame(pooled), pd.DataFrame(detail)



def bounded_formulation_temperature_extrapolation(
    df: pd.DataFrame,
    anchor_temp_c: float = 110.0,
    target_temps_c: tuple[float, ...] = (120.0, 130.0),
    bootstrap_reps: int = 10000,
    bootstrap_seed: int = 20260918,
) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """Strict local extrapolation with formulation and target temperatures both held out.

    For each nominal formulation, the shared thermal shape is learned only from
    the other formulations and only at temperatures <= anchor_temp_c. One measured
    anchor from each realization of the held formulation locates its state offset.
    The held realization is then predicted at target_temps_c, which were not used
    in shape fitting.

    This is intentionally a short-range, local-chemistry test. It does not support
    cross-family or universal PUR extrapolation claims.
    """
    detail: list[dict] = []

    for held_formulation in sorted(df["formulation_id"].unique()):
        train = df[
            (df["formulation_id"] != held_formulation)
            & (df["temperature_c"] <= anchor_temp_c)
        ].copy()
        held_all = df[df["formulation_id"] == held_formulation].copy()

        shape = smf.ols(
            "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
        ).fit()
        beta1 = float(shape.params["dx"])
        beta2 = float(shape.params["I(dx ** 2)"])

        for realization_id, held in held_all.groupby("realization_id"):
            anchor_rows = held[held["temperature_c"] == anchor_temp_c]
            if anchor_rows.empty:
                continue
            anchor = anchor_rows.iloc[0]

            for target_temp in target_temps_c:
                rows = held[held["temperature_c"] == target_temp]
                if rows.empty:
                    continue
                row = rows.iloc[0]
                pred_ln = (
                    anchor["ln_eta"]
                    + beta1 * (row["dx"] - anchor["dx"])
                    + beta2 * (row["dx"] ** 2 - anchor["dx"] ** 2)
                )
                pred = math.exp(float(pred_ln))
                obs = float(row["viscosity_reported"])
                logerr = float(pred_ln - row["ln_eta"])
                detail.append(
                    {
                        "held_formulation": held_formulation,
                        "held_realization": realization_id,
                        "anchor_temperature_c": float(anchor_temp_c),
                        "target_temperature_c": float(target_temp),
                        "observed_viscosity_reported": obs,
                        "predicted_viscosity_reported": pred,
                        "log_error_pred_over_obs": logerr,
                        "absolute_percentage_error": abs(pred / obs - 1.0),
                    }
                )

    detail_df = pd.DataFrame(detail)
    if detail_df.empty:
        raise ValueError("No bounded formulation-temperature extrapolation rows were generated")

    def summarize(group: pd.DataFrame, scope: str, group_label: str) -> dict:
        rmse_log = _rmse(group["log_error_pred_over_obs"].to_numpy())
        return {
            "scope": scope,
            "group": group_label,
            "n_predictions": int(len(group)),
            "rmse_log": rmse_log,
            "multiplicative_rmse": math.exp(rmse_log),
            "median_absolute_percentage_error": float(
                group["absolute_percentage_error"].median()
            ),
            "mean_absolute_percentage_error": float(
                group["absolute_percentage_error"].mean()
            ),
            "max_multiplicative_error": float(
                np.exp(np.abs(group["log_error_pred_over_obs"]).max())
            ),
        }

    summary_rows = [summarize(detail_df, "overall", "all")]
    for temp, group in detail_df.groupby("target_temperature_c"):
        summary_rows.append(summarize(group, "target_temperature_c", f"{temp:g}"))
    for formulation, group in detail_df.groupby("held_formulation"):
        summary_rows.append(summarize(group, "held_formulation", str(formulation)))
    summary_df = pd.DataFrame(summary_rows)

    # Cluster bootstrap at the realization level so the two target temperatures
    # from one realization are always resampled together.
    rng = np.random.default_rng(bootstrap_seed)
    realization_ids = detail_df["held_realization"].drop_duplicates().to_numpy()
    boot = []
    for _ in range(bootstrap_reps):
        sampled = rng.choice(realization_ids, size=len(realization_ids), replace=True)
        pieces = [
            detail_df[detail_df["held_realization"] == realization_id]
            for realization_id in sampled
        ]
        resampled = pd.concat(pieces, ignore_index=True)
        boot.append(
            math.exp(_rmse(resampled["log_error_pred_over_obs"].to_numpy()))
        )
    bootstrap_ci = np.quantile(np.asarray(boot), [0.025, 0.5, 0.975])

    overall = summary_df.iloc[0].to_dict()
    overall.update(
        {
            "anchor_temperature_c": float(anchor_temp_c),
            "target_temperatures_c": [float(x) for x in target_temps_c],
            "n_held_formulations": int(detail_df["held_formulation"].nunique()),
            "n_held_realizations": int(detail_df["held_realization"].nunique()),
            "bootstrap_unit": "held_realization",
            "bootstrap_reps": int(bootstrap_reps),
            "bootstrap_seed": int(bootstrap_seed),
            "bootstrap_multiplicative_rmse_ci95": [
                float(bootstrap_ci[0]),
                float(bootstrap_ci[2]),
            ],
            "bootstrap_multiplicative_rmse_median": float(bootstrap_ci[1]),
            "claim_boundary": (
                "Short-range (10-20 C) local formulation-and-temperature extrapolation "
                "within the chemistry-audited E1-E3 neighborhood only; not cross-family "
                "or universal reactive-PUR extrapolation."
            ),
        }
    )
    return detail_df, summary_df, overall


def thermal_descriptor_summary(df: pd.DataFrame) -> dict:
    values = []
    for _rid, group in df.groupby("realization_id"):
        fit = stats.linregress(1.0 / (group["temperature_c"].to_numpy() + 273.15), group["ln_eta"].to_numpy())
        values.append(float(fit.slope * R_GAS / 1000.0))
    return {
        "n_realizations": len(values),
        "mean_apparent_E_eta_kJ_mol": float(np.mean(values)),
        "sd_apparent_E_eta_kJ_mol": float(np.std(values, ddof=1)),
        "cv_apparent_E_eta": float(np.std(values, ddof=1) / np.mean(values)),
    }


def external_grouped_cv(db_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
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

    descriptors = []
    for (source_id, sample_id), group in curves.groupby(["source_id", "sample_id"]):
        fit = stats.linregress(1.0 / (group["temperature_c"].to_numpy() + 273.15), group["ln_eta"].to_numpy())
        first = group.iloc[0]
        descriptors.append(
            {
                "source_id": source_id,
                "sample_id": sample_id,
                "polyol_code": first["polyol_code"],
                "isocyanate_code": first["isocyanate_code"],
                "pNCO_pct": float(first["pNCO_pct"]),
                "apparent_E_kJ_mol": float(fit.slope * R_GAS / 1000.0),
                "ln_eta_75": float(fit.intercept + fit.slope / (75.0 + 273.15)),
            }
        )
    df = pd.DataFrame(descriptors)
    df["chemistry_family"] = df["polyol_code"].astype(str) + "__" + df["isocyanate_code"].astype(str)

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

    family_rows = []
    summary_rows = []
    for model_name, (target, formula) in models.items():
        observed, predicted = [], []
        n_ood = 0
        for family, test in df.groupby("chemistry_family"):
            train = df[df["chemistry_family"] != family]
            unseen_polyol = set(test["polyol_code"]) - set(train["polyol_code"])
            unseen_iso = set(test["isocyanate_code"]) - set(train["isocyanate_code"])
            structural_ood = bool(unseen_polyol or unseen_iso)
            family_rows.append(
                {
                    "model": model_name,
                    "chemistry_family": family,
                    "n_curves": int(len(test)),
                    "structural_ood": structural_ood,
                    "unseen_polyol_levels": ";".join(sorted(map(str, unseen_polyol))),
                    "unseen_isocyanate_levels": ";".join(sorted(map(str, unseen_iso))),
                }
            )
            if structural_ood:
                n_ood += 1
                continue
            fitted = smf.ols(formula, train).fit()
            pred = fitted.predict(test)
            observed.extend(test[target].tolist())
            predicted.extend(pred.tolist())
        obs = np.asarray(observed, dtype=float)
        pred = np.asarray(predicted, dtype=float)
        residual = obs - pred
        r2 = 1.0 - float(np.sum(residual**2) / np.sum((obs - obs.mean()) ** 2))
        rmse = _rmse(residual)
        summary_rows.append(
            {
                "model": model_name,
                "n_predicted_curves": int(len(obs)),
                "n_structural_ood_families": int(n_ood),
                "grouped_family_cv_r2": r2,
                "grouped_family_cv_rmse": rmse,
                "grouped_family_cv_multiplicative_error": math.exp(rmse) if target == "ln_eta_75" else np.nan,
            }
        )
    return pd.DataFrame(summary_rows), pd.DataFrame(family_rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Provenance-aware robustness audit for PUR-NEW")
    parser.add_argument("--temperature-csv", type=Path, default=ROOT / "data" / "temperature_sweeps.csv")
    parser.add_argument("--metadata-csv", type=Path, default=ROOT / "data" / "realization_metadata.csv")
    parser.add_argument("--external-db", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "derived" / "analysis_audit_v1")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    all_rows, audited = prepare_local(args.temperature_csv, args.metadata_csv)
    all_fit = fit_and_cv(all_rows)
    all_fit.insert(0, "analysis_set", "all_recorded_curves")
    audited_fit = fit_and_cv(audited)
    audited_fit.insert(0, "analysis_set", "chemistry_audited_primary")
    model_table = pd.concat([all_fit, audited_fit], ignore_index=True)
    model_table.to_csv(args.output_dir / "provenance_aware_model_comparison.csv", index=False)

    lofo, lofo_detail = leave_one_formulation_one_point(audited)
    lofo.to_csv(args.output_dir / "leave_one_formulation_one_point.csv", index=False)
    lofo_detail.to_csv(args.output_dir / "leave_one_formulation_one_point_detail.csv", index=False)

    extrap_detail, extrap_summary, extrap_overall = bounded_formulation_temperature_extrapolation(audited)
    extrap_detail.to_csv(
        args.output_dir / "local_joint_formulation_temperature_extrapolation.csv",
        index=False,
    )
    extrap_summary.to_csv(
        args.output_dir / "local_joint_formulation_temperature_extrapolation_summary.csv",
        index=False,
    )

    pca = model_free_state_shift(audited)
    thermal = thermal_descriptor_summary(audited)
    summary = {
        "excluded_from_audited_primary": sorted(
            all_rows.loc[all_rows["analysis_role"] == "sensitivity_only", "realization_id"].unique().tolist()
        ),
        "exclusion_reason": (
            "The E1 +P realization is phosphoric-acid-labelled and is therefore treated as chemistry-flagged until its exact additive identity/amount is verified."
        ),
        "audited_primary_n_points": int(len(audited)),
        "audited_primary_n_realizations": int(audited["realization_id"].nunique()),
        "audited_primary_n_formulations": int(audited["formulation_id"].nunique()),
        "model_free_state_shift": pca,
        "audited_thermal_descriptor": thermal,
        "lofo_120c": lofo[lofo["anchor_temperature_c"] == 120.0].to_dict(orient="records"),
        "bounded_local_extrapolation": extrap_overall,
        "reporting_rule": (
            "Audits are chosen for scientific relevance before interpreting whether they strengthen or weaken a claim. Results that do not support a claim should not be silently deleted; they can remain exploratory/supporting rather than headline evidence."
        ),
    }

    if args.external_db:
        ext, family = external_grouped_cv(args.external_db)
        ext.to_csv(args.output_dir / "external_grouped_family_cv.csv", index=False)
        family.to_csv(args.output_dir / "external_grouped_family_cv_families.csv", index=False)
        summary["external_grouped_family_cv"] = ext.to_dict(orient="records")

    (args.output_dir / "audit_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
