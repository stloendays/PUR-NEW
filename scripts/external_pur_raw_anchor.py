#!/usr/bin/env python3
"""Raw-measurement, chemically controlled one-anchor PUR prepolymer test.

Published source: Pugar et al., Digital Discovery (2025), DOI D5DD00287G.
Source workbook: joepugar/viscosity-modeling/ViscTempData.xlsx, pinned commit
57ede2b22f964a99d6467d627236c37d0a7231d2, SHA256
bbec41da4ff3cae1231686e5d219ec217ac53d85e0f5fc561e408e78fdaf7085.

The held prepolymer contributes exactly one raw viscosity at ~60 deg C.
Its raw 40, 50, 70 and 80 deg C readings are separate test observations.
The thermal shape is trained on *other* formulation curves, never on the
held one's smoothed or raw other-temperature observations.

Paired chemistry comparison is matched in number of training curves (2):
same polyol / different isocyanate versus different polyol / same isocyanate.
Each training pair is chosen by proximity of reported pNCO to the held curve,
breaking ties on sample ID. This is a controlled *diagnostic*, not a
causal estimate: candidate pool size and pNCO match are not identical.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "57ede2b22f964a99d6467d627236c37d0a7231d2"
SOURCE_SHA256 = "bbec41da4ff3cae1231686e5d219ec217ac53d85e0f5fc561e408e78fdaf7085"
SOURCE_DOI = "10.1039/D5DD00287G"
OUT = ROOT / "analysis/results/generality_20261014/pur_raw_anchor"
TREF_K = 333.15
TARGETS_C = (40.0, 50.0, 70.0, 80.0)
SEED = 20261014
N_BOOT = 10000


def read_workbook(path: Path) -> pd.DataFrame:
    actual_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_sha != SOURCE_SHA256:
        raise ValueError(f"Source workbook SHA256 mismatch: {actual_sha}")
    xls = pd.ExcelFile(path)
    result: list[pd.DataFrame] = []
    for name in xls.sheet_names:
        if not re.fullmatch(r"[CDP]_[A-Za-z0-9]+_[0-9]+", name):
            continue
        bits = name.split("_")
        if len(bits) != 3:
            raise ValueError(f"Unexpected formulation naming: {name}")
        frame = pd.read_excel(xls, sheet_name=name, header=None, usecols=[0, 1])
        viscosity = pd.to_numeric(frame.iloc[:, 0], errors="coerce")
        temp = pd.to_numeric(frame.iloc[:, 1], errors="coerce")
        valid = viscosity.notna() & temp.notna()
        sub = pd.DataFrame({
            "sample_id": name,
            "polyol_code": bits[0],
            "isocyanate_code": bits[1],
            "pNCO_pct": float(bits[2]),
            "temperature_c": temp[valid].to_numpy(float),
            "viscosity_pa_s": viscosity[valid].to_numpy(float),
        })
        if len(sub) < 20:
            raise ValueError(f"Too few raw measurements in {name}: {len(sub)}")
        result.append(sub)
    if not result:
        raise ValueError("No eligible sample sheets found")
    df = pd.concat(result, ignore_index=True)
    if len(df) != 4559 or df["sample_id"].nunique() != 39:
        raise ValueError(f"Expected 4559 observations / 39 curves, got {len(df)} / {df.sample_id.nunique()}")
    if (df["viscosity_pa_s"] <= 0).any() or (df["temperature_c"] <= 0).any():
        raise ValueError("Non-positive raw temperature or viscosity")
    if df.duplicated(["sample_id", "temperature_c"]).any():
        raise ValueError("Duplicate original temperature within a formulation")
    df["z"] = 1000.0 * (1.0 / (df["temperature_c"] + 273.15) - 1.0 / TREF_K)
    df["ln_eta"] = np.log(df["viscosity_pa_s"])
    return df


def fit_shared_shape(train: pd.DataFrame) -> tuple[np.ndarray, float]:
    """One intercept per training curve, each curve equally weighted."""
    if train["sample_id"].nunique() < 2:
        raise ValueError("Paired chemistry test requires two training curves")
    by = train.groupby("sample_id", sort=False)
    z = train["z"].to_numpy(float)
    z2 = z**2
    y = train["ln_eta"].to_numpy(float)
    z1_center = z - by["z"].transform("mean").to_numpy(float)
    z2_center = z2 - train.assign(z2=z2).groupby("sample_id")["z2"].transform("mean").to_numpy(float)
    y_center = y - by["ln_eta"].transform("mean").to_numpy(float)
    group_n = by["sample_id"].transform("size").to_numpy(float)
    X = np.column_stack([z1_center, z2_center])
    beta, *_ = np.linalg.lstsq(
        X / np.sqrt(group_n)[:, None],
        y_center / np.sqrt(group_n),
        rcond=None,
    )
    level_by_curve = (
        train.assign(level=y - beta[0] * z - beta[1] * z2)
        .groupby("sample_id")["level"].mean()
    )
    return beta, float(level_by_curve.mean())


def nearest_reading(group: pd.DataFrame, temp_c: float, tolerance_c: float) -> pd.Series | None:
    idx = (group["temperature_c"] - temp_c).abs().idxmin()
    row = group.loc[idx]
    if abs(float(row["temperature_c"]) - temp_c) > tolerance_c:
        return None
    return row


def calculate(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    meta = df.drop_duplicates("sample_id")[
        ["sample_id", "polyol_code", "isocyanate_code", "pNCO_pct"]
    ]
    all_rows: list[dict] = []
    excluded_anchor: list[str] = []
    excluded_pool: list[str] = []
    for held_id, held in df.groupby("sample_id"):
        held = held.sort_values("temperature_c")
        anchor = nearest_reading(held, 60, tolerance_c=0.5)
        if anchor is None:
            excluded_anchor.append(held_id)
            continue
        desc = meta.loc[meta["sample_id"] == held_id].iloc[0]
        poly, iso, nco = str(desc["polyol_code"]), str(desc["isocyanate_code"]), float(desc["pNCO_pct"])
        pool_poly = meta[
            (meta["sample_id"] != held_id)
            & (meta["polyol_code"] == poly)
            & (meta["isocyanate_code"] != iso)
        ].copy()
        pool_isi = meta[
            (meta["sample_id"] != held_id)
            & (meta["polyol_code"] != poly)
            & (meta["isocyanate_code"] == iso)
        ].copy()
        if len(pool_poly) < 2 or len(pool_isi) < 2:
            excluded_pool.append(held_id)
            continue
        for scope, pool in (
            ("same_polyol_different_isocyanate", pool_poly),
            ("different_polyol_same_isocyanate", pool_isi),
        ):
            pool["nco_gap"] = (pool["pNCO_pct"] - nco).abs()
            chosen = pool.sort_values(["nco_gap", "sample_id"]).head(2)
            train_ids = chosen["sample_id"].tolist()
            if held_id in train_ids:
                raise AssertionError("Target leaked into training group")
            train = df[df["sample_id"].isin(train_ids)]
            beta, no_anchor_level = fit_shared_shape(train)
            z0, y0 = float(anchor["z"]), float(anchor["ln_eta"])
            for target_temp in TARGETS_C:
                target = nearest_reading(held, target_temp, tolerance_c=0.5)
                if target is None or float(target["temperature_c"]) == float(anchor["temperature_c"]):
                    continue
                zt, yt = float(target["z"]), float(target["ln_eta"])
                predicted = y0 + beta[0] * (zt - z0) + beta[1] * (zt**2 - z0**2)
                without_anchor = no_anchor_level + beta[0] * zt + beta[1] * zt**2
                all_rows.append({
                    "sample_id": held_id,
                    "polyol_code": poly,
                    "isocyanate_code": iso,
                    "pNCO_pct": nco,
                    "training_scope": scope,
                    "training_ids": ";".join(train_ids),
                    "mean_training_pNCO_gap_pct": float(chosen["nco_gap"].mean()),
                    "anchor_temperature_c": float(anchor["temperature_c"]),
                    "anchor_viscosity_pa_s": float(anchor["viscosity_pa_s"]),
                    "target_nominal_c": target_temp,
                    "target_actual_c": float(target["temperature_c"]),
                    "target_viscosity_pa_s": float(target["viscosity_pa_s"]),
                    "err_one_raw_anchor_log": predicted - yt,
                    "err_no_anchor_log": without_anchor - yt,
                    "err_flat_anchor_log": y0 - yt,
                })
    predictions = pd.DataFrame(all_rows)
    if predictions.empty:
        raise ValueError("No valid held-curve predictions")
    report = {
        "source": "Pugar et al. 2025, Digital Discovery, DOI " + SOURCE_DOI,
        "source_repo_sha": SOURCE_COMMIT,
        "source_workbook_sha256": SOURCE_SHA256,
        "n_raw_measurements": len(df),
        "n_raw_curves": df["sample_id"].nunique(),
        "n_raw_polyol_families": df["polyol_code"].nunique(),
        "n_raw_polyol_isocyanate_pairs": df.groupby(["polyol_code", "isocyanate_code"]).ngroups,
        "excluded_no_60C_anchor_within_half_degree": sorted(excluded_anchor),
        "excluded_no_two_curve_chemistry_pool": sorted(excluded_pool),
        "paired_train_curve_count_per_scope": 2,
        "comparison_design": (
            "One real measured ~60 C anchor; predictions near 40/50/70/80 C "
            "at other measured source temperatures; two pNCO-nearest, "
            "equal-count training curves per comparison"
        ),
    }
    return predictions, report


def mult_rmse(values: np.ndarray) -> float:
    return float(np.exp(np.sqrt(np.mean(np.square(np.asarray(values, float))))))


def summarize(pred: pd.DataFrame, report: dict) -> dict:
    rows = []
    for scope, g in pred.groupby("training_scope"):
        for horizon_name, temps in [
            ("within_10C", (50.0, 70.0)),
            ("within_20C", (40.0, 80.0)),
            ("all_four_targets", TARGETS_C),
        ]:
            sub = g[g["target_nominal_c"].isin(temps)]
            rows.append({
                "scope": scope,
                "evaluation": horizon_name,
                "n_held_curves": int(sub["sample_id"].nunique()),
                "n_predictions": int(len(sub)),
                "multiplicative_rmse": mult_rmse(sub["err_one_raw_anchor_log"].to_numpy(float)),
                "no_anchor_multiplicative_rmse": mult_rmse(sub["err_no_anchor_log"].to_numpy(float)),
                "constant_viscosity_anchor_mult_rmse": mult_rmse(sub["err_flat_anchor_log"].to_numpy(float)),
                "fraction_within_1p2x": float(
                    np.mean(np.abs(sub["err_one_raw_anchor_log"]) <= math.log(1.2))
                ),
                "mean_training_pNCO_gap": float(sub["mean_training_pNCO_gap_pct"].mean()),
            })
    report["results"] = rows
    short = pred[pred["target_nominal_c"].isin((50.0, 70.0))]
    wide = short.pivot(
        index=["sample_id", "target_nominal_c"],
        columns="training_scope",
        values="err_one_raw_anchor_log",
    ).dropna()
    expected = ["different_polyol_same_isocyanate", "same_polyol_different_isocyanate"]
    if sorted(wide.columns) != expected:
        raise AssertionError(f"Unexpected comparison scope: {wide.columns.tolist()}")
    held_ids = sorted(wide.index.get_level_values("sample_id").unique())
    if len(held_ids) < 10:
        raise ValueError("Too few independent held formulation curves")
    errs = {
        x: wide.loc[x][expected].to_numpy(float)
        for x in held_ids
    }
    rng = np.random.default_rng(SEED)
    boots = np.empty((N_BOOT, 3), dtype=float)
    for b in range(N_BOOT):
        picked = rng.choice(held_ids, size=len(held_ids), replace=True)
        arr = np.concatenate([errs[x] for x in picked], axis=0)
        logrmse = np.sqrt(np.mean(arr**2, axis=0))
        boots[b, :2] = np.exp(logrmse)
        boots[b, 2] = logrmse[0] - logrmse[1]
    initial = np.sqrt(np.mean(wide[expected].to_numpy(float)**2, axis=0))
    report["paired_10C_comparison"] = {
        "held_curve_unit": "one source formulation / full matched two-target curve",
        "n_held_curves": len(held_ids),
        "n_predictions": len(wide),
        "source_order": expected,
        "cross_polyol_multiplicative_error": math.exp(float(initial[0])),
        "same_polyol_multiplicative_error": math.exp(float(initial[1])),
        "cross_polyol_mult_ci95": [float(x) for x in np.quantile(boots[:, 0], [0.025, 0.975])],
        "same_polyol_mult_ci95": [float(x) for x in np.quantile(boots[:, 1], [0.025, 0.975])],
        "difference_log_rmse_cross_minus_same": float(initial[0] - initial[1]),
        "difference_log_rmse_bootstrap_ci95": [float(x) for x in np.quantile(boots[:, 2], [0.025, 0.975])],
        "curve_bootstrap_reps": N_BOOT,
        "curve_bootstrap_seed": SEED,
        "interpretation": (
            "Matching the number of training curves, transferring thermal response "
            "across polyol identity is less accurate than retaining polyol identity "
            "across isocyanates. This is a matched predictive comparison, not "
            "identification of a molecular causal mechanism; pNCO proximity differs."
        ),
    }
    # Sensitivity to the pNCO-matching imbalance: retain only held curves
    # for which *both* two-curve training pools match within a mean of
    # one NCO percentage point. Report on paired identical target points.
    nco_by_curve = (
        short.groupby(["sample_id", "training_scope"])["mean_training_pNCO_gap_pct"]
        .first()
        .unstack("training_scope")
        .dropna()
    )
    eligible = nco_by_curve.loc[
        (nco_by_curve[expected[0]] <= 1.0)
        & (nco_by_curve[expected[1]] <= 1.0)
    ].index
    near = wide.loc[wide.index.get_level_values("sample_id").isin(eligible)]
    report["pNCO_proximity_sensitivity_10C"] = {
        "max_mean_pNCO_gap_pp_per_training_pool": 1.0,
        "n_held_curves": int(len(eligible)),
        "n_predictions": int(len(near)),
        "cross_polyol_multiplicative_rmse": mult_rmse(near[expected[0]].to_numpy()),
        "same_polyol_multiplicative_rmse": mult_rmse(near[expected[1]].to_numpy()),
        "interpretation": "Paired held curves where both chemical-domain training pools have mean pNCO distance no more than 1 percentage point; residual polyol/iso chemistry differences persist.",
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workbook", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    df = read_workbook(args.workbook)
    pred, report = calculate(df)
    report = summarize(pred, report)
    args.out.mkdir(parents=True, exist_ok=True)
    pred.to_csv(args.out / "raw_predictions.csv", index=False, lineterminator="\n")
    pd.DataFrame(report["results"]).to_csv(
        args.out / "scope_and_horizon_summary.csv", index=False, lineterminator="\n"
    )
    (args.out / "summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.check:
        assert report["n_raw_measurements"] == 4559
        assert report["n_raw_curves"] == 39
        assert report["paired_10C_comparison"]["n_held_curves"] == 34
        assert report["paired_10C_comparison"]["n_predictions"] == 68
        assert abs(report["paired_10C_comparison"]["same_polyol_multiplicative_error"] - 1.07645) < 0.01
        assert abs(report["paired_10C_comparison"]["cross_polyol_multiplicative_error"] - 1.23841) < 0.01
        assert report["pNCO_proximity_sensitivity_10C"]["n_held_curves"] == 22
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
