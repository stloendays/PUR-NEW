#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
T_REF_K = 393.15


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Model-free anchor normalization and group-bootstrap shared-shape analysis"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=ROOT / "data" / "temperature_sweeps.csv",
    )
    parser.add_argument("--anchor-temperature", type=float, default=120.0)
    parser.add_argument("--bootstrap", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=20260917)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "derived" / "master_curve_collapse",
    )
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["realization_id"] = (
        df["formulation_id"].astype(str)
        + "__"
        + df["run_label"].astype(str)
        + "__day1_"
        + df["retest_after_1d"].astype(str)
    )

    wide = df.pivot(
        index="realization_id", columns="temperature_c", values="viscosity_reported"
    ).sort_index(axis=1)
    if args.anchor_temperature not in wide.columns:
        raise ValueError("anchor temperature is absent from the recorded sweeps")

    normalized = wide.div(wide[args.anchor_temperature], axis=0)
    summary_rows = []
    for temperature_c in normalized.columns:
        values = normalized[temperature_c].dropna().to_numpy(dtype=float)
        mean = float(values.mean())
        sd = float(values.std(ddof=1)) if len(values) > 1 else 0.0
        summary_rows.append(
            {
                "temperature_c": float(temperature_c),
                "mean_relative_viscosity": mean,
                "sample_sd": sd,
                "cv": sd / mean if mean else 0.0,
                "min": float(values.min()),
                "max": float(values.max()),
                "n_realizations": int(len(values)),
            }
        )
    normalized_summary = pd.DataFrame(summary_rows)

    # Group bootstrap of the shared quadratic shape. Realization-specific offsets
    # are removed by within-realization centering before fitting the common shape.
    work = df.copy()
    work["ln_eta"] = np.log(work["viscosity_reported"])
    work["dx"] = 1000.0 / (work["temperature_c"] + 273.15) - 1000.0 / T_REF_K
    work["x2"] = work["dx"] ** 2

    groups = []
    for _, group in work.groupby("realization_id"):
        x = group[["dx", "x2"]].to_numpy()
        y = group["ln_eta"].to_numpy()
        groups.append((x - x.mean(axis=0), y - y.mean()))

    rng = np.random.default_rng(args.seed)
    temperatures = np.array(sorted(work["temperature_c"].unique()), dtype=float)
    bootstrap_values = np.empty((args.bootstrap, len(temperatures)))

    for iteration in range(args.bootstrap):
        sampled = rng.integers(0, len(groups), size=len(groups))
        x = np.vstack([groups[index][0] for index in sampled])
        y = np.concatenate([groups[index][1] for index in sampled])
        beta = np.linalg.lstsq(x, y, rcond=None)[0]
        dx = 1000.0 / (temperatures + 273.15) - 1000.0 / T_REF_K
        bootstrap_values[iteration, :] = np.exp(beta[0] * dx + beta[1] * dx**2)

    bootstrap_rows = []
    for index, temperature_c in enumerate(temperatures):
        q025, q500, q975 = np.quantile(
            bootstrap_values[:, index], [0.025, 0.5, 0.975]
        )
        bootstrap_rows.append(
            {
                "temperature_c": float(temperature_c),
                "relative_viscosity_p2_5": float(q025),
                "relative_viscosity_median": float(q500),
                "relative_viscosity_p97_5": float(q975),
            }
        )
    bootstrap_df = pd.DataFrame(bootstrap_rows)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    normalized.reset_index().to_csv(
        args.output_dir / "anchor_normalized_curves.csv", index=False
    )
    normalized_summary.to_csv(
        args.output_dir / "anchor_normalized_summary.csv", index=False
    )
    bootstrap_df.to_csv(
        args.output_dir / "shared_shape_group_bootstrap.csv", index=False
    )

    non_anchor = normalized_summary[
        normalized_summary["temperature_c"] != args.anchor_temperature
    ]
    summary = {
        "anchor_temperature_c": args.anchor_temperature,
        "n_realizations": int(len(wide)),
        "non_anchor_cv_range": [
            float(non_anchor["cv"].min()),
            float(non_anchor["cv"].max()),
        ],
        "non_anchor_mean_cv": float(non_anchor["cv"].mean()),
        "bootstrap_resamples": args.bootstrap,
        "bootstrap_seed": args.seed,
    }
    (args.output_dir / "master_curve_collapse_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output_dir / "master_curve_collapse_summary.json")


if __name__ == "__main__":
    main()
