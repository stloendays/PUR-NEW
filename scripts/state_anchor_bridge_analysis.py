#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

T_REF_K = 393.15
PRIMARY_ROLES = {"primary", "primary_with_caveat"}


def _rmse(values) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


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
    df = df.merge(
        meta[["realization_id", "analysis_role"]],
        on="realization_id",
        how="left",
        validate="many_to_one",
    )
    if df["analysis_role"].isna().any():
        missing = sorted(df.loc[df["analysis_role"].isna(), "realization_id"].unique())
        raise ValueError(f"Missing realization metadata for: {missing}")
    primary = df[df["analysis_role"].isin(PRIMARY_ROLES)].copy()
    if len(primary) != 36 or primary["realization_id"].nunique() != 6:
        raise ValueError("Expected 36 chemistry-audited points from six realizations")
    return primary


def same_formulation_anchor_bridge(
    df: pd.DataFrame,
    *,
    formulation_id: str = "E2",
    anchor_temperature_c: float = 110.0,
    target_temperatures_c: tuple[float, ...] = (120.0, 130.0),
) -> pd.DataFrame:
    subset = df[df["formulation_id"] == formulation_id]
    held_ids = sorted(subset["realization_id"].unique())
    if len(held_ids) < 2:
        raise ValueError("Same-formulation bridge requires at least two realizations")

    rows: list[dict] = []
    for held_id in held_ids:
        train = df[df["realization_id"] != held_id].copy()
        held = df[df["realization_id"] == held_id].copy()
        if formulation_id not in set(train["formulation_id"]):
            raise ValueError("Held formulation is absent from training data")

        formulation_only = smf.ols(
            "ln_eta ~ C(formulation_id) + dx + I(dx**2)", data=train
        ).fit()
        state_shape = smf.ols(
            "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
        ).fit()
        beta1 = float(state_shape.params["dx"])
        beta2 = float(state_shape.params["I(dx ** 2)"])

        anchor_rows = held[held["temperature_c"] == anchor_temperature_c]
        if len(anchor_rows) != 1:
            raise ValueError(f"Expected one {anchor_temperature_c:g} C anchor for {held_id}")
        anchor = anchor_rows.iloc[0]
        test = held[held["temperature_c"].isin(target_temperatures_c)].copy()
        if len(test) != len(target_temperatures_c):
            raise ValueError(f"Missing target temperature for {held_id}")

        baseline_pred = formulation_only.predict(test).to_numpy()
        anchor_pred = (
            anchor["ln_eta"]
            + beta1 * (test["dx"] - anchor["dx"])
            + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
        ).to_numpy()

        for idx, (_, row) in enumerate(test.iterrows()):
            rows.append(
                {
                    "held_formulation": formulation_id,
                    "held_realization": held_id,
                    "anchor_temperature_c": float(anchor_temperature_c),
                    "anchor_viscosity_reported": float(anchor["viscosity_reported"]),
                    "target_temperature_c": float(row["temperature_c"]),
                    "observed_viscosity_reported": float(row["viscosity_reported"]),
                    "formulation_only_predicted_viscosity": float(math.exp(baseline_pred[idx])),
                    "one_anchor_predicted_viscosity": float(math.exp(anchor_pred[idx])),
                    "formulation_only_log_error": float(baseline_pred[idx] - row["ln_eta"]),
                    "one_anchor_log_error": float(anchor_pred[idx] - row["ln_eta"]),
                }
            )
    return pd.DataFrame(rows)


def summarize(detail: pd.DataFrame, *, bootstrap_reps: int, bootstrap_seed: int) -> dict:
    baseline_rmse = _rmse(detail["formulation_only_log_error"])
    anchor_rmse = _rmse(detail["one_anchor_log_error"])

    by_realization = []
    for rid, group in detail.groupby("held_realization"):
        b = _rmse(group["formulation_only_log_error"])
        a = _rmse(group["one_anchor_log_error"])
        by_realization.append(
            {
                "held_realization": rid,
                "formulation_only_multiplicative_rmse": math.exp(b),
                "one_anchor_multiplicative_rmse": math.exp(a),
                "log_rmse_reduction_fraction": 1.0 - a / b,
            }
        )

    rng = np.random.default_rng(bootstrap_seed)
    realization_ids = detail["held_realization"].drop_duplicates().to_numpy()
    boot = []
    for _ in range(bootstrap_reps):
        sampled = rng.choice(realization_ids, size=len(realization_ids), replace=True)
        resampled = pd.concat(
            [detail[detail["held_realization"] == rid] for rid in sampled], ignore_index=True
        )
        b = _rmse(resampled["formulation_only_log_error"])
        a = _rmse(resampled["one_anchor_log_error"])
        boot.append([math.exp(b), math.exp(a), 1.0 - a / b])
    boot = np.asarray(boot)

    return {
        "analysis_population": (
            "chemistry-audited primary data; same-formulation holdout restricted to E2 "
            "because E2 is the only nominal formulation with multiple audited realizations"
        ),
        "anchor_temperature_c": float(detail["anchor_temperature_c"].iloc[0]),
        "target_temperatures_c": sorted(detail["target_temperature_c"].unique().tolist()),
        "n_held_realizations": int(detail["held_realization"].nunique()),
        "n_predictions": int(len(detail)),
        "formulation_only": {
            "rmse_log": baseline_rmse,
            "multiplicative_rmse": math.exp(baseline_rmse),
        },
        "one_anchor_state_calibration": {
            "rmse_log": anchor_rmse,
            "multiplicative_rmse": math.exp(anchor_rmse),
        },
        "log_rmse_reduction_fraction": 1.0 - anchor_rmse / baseline_rmse,
        "multiplicative_excess_error_reduction_fraction": (
            1.0 - (math.exp(anchor_rmse) - 1.0) / (math.exp(baseline_rmse) - 1.0)
        ),
        "per_realization": by_realization,
        "cluster_bootstrap": {
            "unit": "held_realization",
            "reps": int(bootstrap_reps),
            "seed": int(bootstrap_seed),
            "formulation_only_multiplicative_rmse_ci95": [
                float(x) for x in np.quantile(boot[:, 0], [0.025, 0.975])
            ],
            "one_anchor_multiplicative_rmse_ci95": [
                float(x) for x in np.quantile(boot[:, 1], [0.025, 0.975])
            ],
            "log_rmse_reduction_fraction_ci95": [
                float(x) for x in np.quantile(boot[:, 2], [0.025, 0.975])
            ],
        },
        "interpretation": (
            "Within repeated E2 realizations, formulation identity alone poorly locates the realized "
            "viscosity level. A single 110 C measurement supplies state information that substantially "
            "improves 120-130 C reconstruction when the shared-shape assumption is valid."
        ),
        "agent_link": (
            "This quantifies the scientific value of M-ANCHOR inside validated shared-shape support. "
            "It does not justify M-ANCHOR after a chemistry shift: the pre-registered Agent V5 chemistry-domain "
            "rule requires direct M-SWEEP verification first for resin-modified or otherwise shifted chemistry."
        ),
    }


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--temperature-csv", type=Path, default=root / "data" / "temperature_sweeps.csv")
    parser.add_argument("--metadata-csv", type=Path, default=root / "data" / "realization_metadata.csv")
    parser.add_argument("--output-dir", type=Path, default=root / "derived" / "state_anchor_bridge")
    parser.add_argument("--bootstrap-reps", type=int, default=10000)
    parser.add_argument("--bootstrap-seed", type=int, default=20260923)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    df = prepare_primary(args.temperature_csv, args.metadata_csv)
    detail = same_formulation_anchor_bridge(df)
    summary = summarize(detail, bootstrap_reps=args.bootstrap_reps, bootstrap_seed=args.bootstrap_seed)

    detail.to_csv(args.output_dir / "same_formulation_anchor_110_to_120_130.csv", index=False)
    (args.output_dir / "state_anchor_bridge_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
