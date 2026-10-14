#!/usr/bin/env python3
"""Leakage-aware raw-observation one-anchor validation for polymer electrolytes.

Input: committed Bradford 2023 neat-polymer observations and the frozen 2026-10-08
family grids. Only *training curves* contribute to a fitted shared shape.
The held curve contributes exactly one actually measured warm-end conductivity
value to the predictor; evaluation targets are distinct raw measured points.

Two holdout scopes:
  curve: all other curves from the polymer host train the thermal shape;
  doi: all curves from the held curve's publication are excluded from training.
DOI transfer is defined only for host families with >= 2 distinct DOIs.

The earlier gridded test was a descriptive interpolated-curve test; its anchor
was obtained by smoothing the entire held curve. This stricter validation must
not be conflated with that earlier descriptive statistic.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/external/bradford2023_spe/spe_neat_curves.csv"
GRID = ROOT / "analysis/results/generality_20261008/spe_state_shift/grid_ln_sigma.csv"
OUT = ROOT / "analysis/results/generality_20261014/raw_anchor"
TREF_FACTOR = 1000.0
HORIZONS_C = (5, 10, 15, 20, 25, 30)


def z_of(temp_c: np.ndarray | float, ref_c: float) -> np.ndarray:
    t = np.asarray(temp_c, dtype=float)
    return TREF_FACTOR * (1.0 / (t + 273.15) - 1.0 / (ref_c + 273.15))


def mult_rmse(values: np.ndarray) -> float:
    v = np.asarray(values, dtype=float)
    if len(v) == 0:
        raise ValueError("Cannot compute RMSE on an empty vector")
    return float(math.exp(math.sqrt(float(np.mean(v ** 2)))))


def shared_shape(train: pd.DataFrame) -> tuple[float, float, float]:
    """OLS with a separate level for each *training* curve and shared z/z^2."""
    if train["curve_id"].nunique() < 3:
        raise ValueError("Too few training curves for a held-out shape fit")
    z = train["z"].to_numpy(float)
    z2 = z ** 2
    y = train["ln_sigma"].to_numpy(float)
    by_curve = train.groupby("curve_id", sort=False)
    # Frisch-Waugh-Lovell curve-level demeaning: the training intercepts
    # cannot accidentally absorb information from the held-out curve.
    zx = z - by_curve["z"].transform("mean").to_numpy(float)
    train2 = train.assign(z_squared=z2)
    z2x = z2 - train2.groupby("curve_id")["z_squared"].transform("mean").to_numpy(float)
    yy = y - by_curve["ln_sigma"].transform("mean").to_numpy(float)
    beta, *_ = np.linalg.lstsq(np.column_stack((zx, z2x)), yy, rcond=None)
    b1, b2 = map(float, beta)
    residual_level = y - b1 * z - b2 * z2
    mean_training_level = float(
        train.assign(level=residual_level).groupby("curve_id")["level"].mean().mean()
    )
    return b1, b2, mean_training_level


def read_inputs() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    raw = pd.read_csv(SOURCE, dtype={"curve_id": str, "doi": str})
    grid = pd.read_csv(GRID, dtype={"curve_id": str})
    for frame, cols in (
        (raw, {"curve_id", "family", "temperature_c", "log10_sigma", "doi"}),
        (grid, {"curve_id", "family", "temperature_c", "z", "ln_sigma"}),
    ):
        missing = cols - set(frame.columns)
        if missing:
            raise ValueError(f"Missing required source columns: {sorted(missing)}")
    raw["ln_sigma"] = pd.to_numeric(raw["log10_sigma"], errors="raise") * math.log(10)
    if raw[["curve_id", "family", "doi", "temperature_c", "ln_sigma"]].isna().any().any():
        raise ValueError("Incomplete raw conductivity provenance")
    n_dois = raw.groupby("curve_id")["doi"].nunique()
    if not (n_dois == 1).all():
        raise ValueError("A conductivity curve must belong to exactly one source DOI")
    n_families = raw.groupby("curve_id")["family"].nunique()
    if not (n_families == 1).all():
        raise ValueError("A conductivity curve must belong to one host family")
    if raw.duplicated(["curve_id", "temperature_c"]).any():
        raise ValueError("Expected source data aggregated to unique temperatures per curve")
    doi_map = raw.groupby("curve_id")["doi"].first().to_dict()
    assert grid["family"].nunique() == 14
    return raw, grid, doi_map


def evaluate(raw: pd.DataFrame, grid: pd.DataFrame, doi_map: dict[str, str], scope: str) -> pd.DataFrame:
    records: list[dict] = []
    for family, gf in grid.groupby("family", sort=True):
        family_curves = sorted(gf["curve_id"].unique())
        family_dois = {doi_map[c] for c in family_curves}
        if scope == "doi" and len(family_dois) < 2:
            continue
        lo = float(gf["temperature_c"].min())
        hi = float(gf["temperature_c"].max())
        tref = 0.5 * (lo + hi)
        observed = raw[
            raw["curve_id"].isin(family_curves)
            & raw["family"].eq(family)
            & raw["temperature_c"].between(lo, hi)
        ]
        observations_by_curve = {
            cid: frm.sort_values("temperature_c")
            for cid, frm in observed.groupby("curve_id", sort=False)
        }
        fitted_by_group: dict[str, tuple[float, float, float]] = {}
        for cid in family_curves:
            held_doi = doi_map[cid]
            fitkey = cid if scope == "curve" else held_doi
            if fitkey not in fitted_by_group:
                train_ids = (
                    [x for x in family_curves if x != cid]
                    if scope == "curve"
                    else [x for x in family_curves if doi_map[x] != held_doi]
                )
                if len(train_ids) < 3:
                    continue
                train = gf[gf["curve_id"].isin(train_ids)]
                if scope == "doi" and any(doi_map[x] == held_doi for x in train_ids):
                    raise AssertionError("DOI holdout contamination")
                fitted_by_group[fitkey] = shared_shape(train)
            if fitkey not in fitted_by_group or cid not in observations_by_curve:
                continue
            held = observations_by_curve[cid]
            if len(held) < 2:
                continue
            anchor = held.iloc[-1]
            anchor_t, anchor_y = float(anchor["temperature_c"]), float(anchor["ln_sigma"])
            b1, b2, mean_level = fitted_by_group[fitkey]
            z0 = float(z_of(anchor_t, tref))
            for _, target in held.iloc[:-1].iterrows():
                temp = float(target["temperature_c"])
                zt = float(z_of(temp, tref))
                pred_anchor = anchor_y + b1 * (zt - z0) + b2 * (zt * zt - z0 * z0)
                pred_family = mean_level + b1 * zt + b2 * zt * zt
                target_y = float(target["ln_sigma"])
                records.append(
                    {
                        "holdout_scope": scope,
                        "family": family,
                        "curve_id": cid,
                        "doi": held_doi,
                        "anchor_temperature_c": anchor_t,
                        "target_temperature_c": temp,
                        "below_anchor_c": anchor_t - temp,
                        "err_anchor_log": pred_anchor - target_y,
                        "err_family_mean_log": pred_family - target_y,
                    }
                )
    result = pd.DataFrame.from_records(records)
    if result.empty:
        raise ValueError(f"No raw-point predictions generated for scope={scope}")
    if (result["below_anchor_c"] <= 0).any():
        raise AssertionError("Predictions must be strictly below the observed anchor")
    if result.duplicated(["holdout_scope", "family", "curve_id", "target_temperature_c"]).any():
        raise AssertionError("Prediction rows must be unique")
    return result.sort_values(["family", "curve_id", "target_temperature_c"]).reset_index(drop=True)


def metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"n_predictions": 0}
    err = df["err_anchor_log"].to_numpy(float)
    return {
        "n_predictions": int(len(df)),
        "n_curves": int(df[["family", "curve_id"]].drop_duplicates().shape[0]),
        "n_families": int(df["family"].nunique()),
        "n_publications": int(df["doi"].nunique()),
        "multiplicative_rmse": mult_rmse(err),
        "family_mean_without_anchor_multiplicative_rmse": mult_rmse(
            df["err_family_mean_log"].to_numpy(float)
        ),
        "fraction_within_factor_two": float(np.mean(np.abs(err) <= math.log(2))),
    }


def summarise_scope(df: pd.DataFrame, outdir: Path, scope: str) -> dict:
    close = df[df["below_anchor_c"] <= 20.0]
    family_rows: list[dict] = []
    for family, subgroup in close.groupby("family", sort=True):
        family_rows.append({"family": family, **metrics(subgroup)})
    fam = pd.DataFrame(family_rows)
    fam.to_csv(outdir / f"{scope}_by_family.csv", index=False, lineterminator="\n")
    horizons = []
    for h in HORIZONS_C:
        selected = df[df["below_anchor_c"] <= h]
        horizons.append({"max_below_anchor_c": h, **metrics(selected)})
    pd.DataFrame(horizons).to_csv(
        outdir / f"{scope}_by_horizon.csv", index=False, lineterminator="\n"
    )
    dominant = str(fam.sort_values("n_curves", ascending=False).iloc[0]["family"])
    other = close[close["family"] != dominant]
    mse_by_family = (
        close.assign(sq_error=close["err_anchor_log"] ** 2)
        .groupby("family")["sq_error"].mean()
    )
    return {
        "all_target_temperatures": metrics(df),
        "within_20_c": metrics(close),
        "within_10_c": metrics(df[df["below_anchor_c"] <= 10]),
        "within_30_c": metrics(df[df["below_anchor_c"] <= 30]),
        "dominant_family": dominant,
        "excluding_dominant_family_within_20_c": metrics(other),
        "family_equal_weight_multiplicative_rmse_within_20_c": float(
            math.exp(math.sqrt(float(mse_by_family.mean())))
        ),
        "eligible_family_count": int(close["family"].nunique()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Assert stable analysis counts and metrics against the 2026-10-14 computation",
    )
    args = parser.parse_args()
    raw, grid, doi_map = read_inputs()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    report = {
        "source": "Bradford et al. (2023), DOI 10.1021/acscentsci.2c01123",
        "raw_measurement_count": int(len(raw)),
        "source_raw": str(SOURCE.relative_to(ROOT)),
        "training_grid": str(GRID.relative_to(ROOT)),
        "method": "One actual measured warm-end anchor; distinct raw measurement targets; training shape from other held-out curves or publications only",
        "prediction_type": "interpolation within measured temperature windows, not chemical extrapolation",
    }
    for scope in ("curve", "doi"):
        predictions = evaluate(raw, grid, doi_map, scope)
        predictions.to_csv(
            out / f"{scope}_raw_predictions.csv", index=False, lineterminator="\n"
        )
        report[scope] = summarise_scope(predictions, out, scope)
    (out / "summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.check:
        expectations = {
            "curve": (979, 322, 1.65851),
            "doi": (767, 232, 1.70490),
        }
        for scope, (n, curves, factor) in expectations.items():
            got = report[scope]["within_20_c"]
            assert got["n_predictions"] == n, (scope, got)
            assert got["n_curves"] == curves, (scope, got)
            assert abs(got["multiplicative_rmse"] - factor) < 0.003, (scope, got)
        assert report["raw_measurement_count"] == 7640
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
