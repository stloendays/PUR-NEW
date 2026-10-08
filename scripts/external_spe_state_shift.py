#!/usr/bin/env python3
"""Test of the state-shift geometry outside polyurethanes: solid polymer electrolytes.

Data: the ionic-conductivity database of Bradford et al. (2023, ACS Cent. Sci. 9, 206-216; MIT licence),
neat polymer + one salt (no second component, no inorganic filler). A curve is one formulation's
ln(sigma) against temperature; a family is one polymer backbone; curves within a family differ by
salt, salt concentration and molecular weight.

The analysis mirrors scripts/external_state_shift_validation.py (the Pugar polyurethane test):

1. each family's curves are placed on a common temperature grid inside every included curve's
   measured range (per-curve quadratic in z(T), interpolation only);
2. SVD of the temperature-centred matrix: share of between-curve variance in the first mode and
   its cosine to a uniform vertical shift;
3. nested shape models: family level only, curve level + shared quadratic shape, curve-specific
   quadratic;
4. one-anchor transfer: leave one curve out, learn the shared shape from the other curves of the
   family, set the held curve's level from its warmest grid value, predict its other grid values.

Conventions: z(T) = 1e3 * (1/T - 1/Tref), T in kelvin, Tref = window midpoint; multiplicative error
= exp(RMSE of ln sigma); curve-level cluster bootstrap.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "external" / "bradford2023_spe"
CURVES_CSV = DATA_DIR / "spe_neat_curves.csv"
DEFAULT_RAW = Path(r"D:\Research\polymer-curve-datasets\raw\bradford2023_spe_conductivity\data\PolymerElectrolyteData.csv")
RAW_SHA256 = "5ad82b4b75b9bb95f8f402fd394686d69c97cd0edaa110ad9c330655268a9fab"
OUT = ROOT / "analysis" / "results" / "generality_20261008" / "spe_state_shift"

MIN_POINTS, MIN_SPAN_C = 5, 30.0          # curve inclusion (same rule as the PolyAnchor loader)
GRID_STEP_C, MIN_WINDOW_C = 5.0, 30.0     # common grid
MIN_IN_WINDOW = 4                         # measured points a curve needs inside the window
MIN_FAMILY_CURVES = 8
SEED, N_BOOT = 20261008, 10000


def sha256(path: Path, normalise_eol: bool = False) -> str:
    data = path.read_bytes()
    if normalise_eol:   # repository text files may be checked out with CRLF on Windows
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def z_of(t_c, t_ref_c):
    return 1e3 * (1.0 / (np.asarray(t_c, float) + 273.15) - 1.0 / (t_ref_c + 273.15))


# --------------------------------------------------------------------------- data
def build_curves(raw_path: Path) -> pd.DataFrame:
    """Neat polymer + one salt curves from the raw database (vendored as spe_neat_curves.csv)."""
    if sha256(raw_path) != RAW_SHA256:
        raise SystemExit(f"unexpected SHA-256 for {raw_path}")
    d = pd.read_csv(raw_path, low_memory=False)
    d = d[d["S1 SMILES"].astype(str).str.contains(r"\[Cu\]|\[Au\]", regex=True)]
    d = d[d["S2 SMILES"].isna() & d["IM1 Weight %"].isna() & d["Salt1 SMILES"].notna()]
    key = ["DOI", "S1 SMILES", "S1 Mn or Mw", "Salt1 SMILES", "Salt1 Molality (mol salt/kg polymer)",
           "Salt1 Weight %", "Notes", "Compound Notebook Name"]
    for c in key:
        d[c] = d[c].astype(str)
    d["curve_id"] = pd.util.hash_pandas_object(d[key], index=False).astype(str)
    d["temperature_c"] = (d["Temperature (oC)"] * 2).round() / 2
    agg = (d.groupby(["curve_id", "temperature_c"])
           .agg(log10_sigma=("log Conductivity (S/cm)", "mean"), family=("S1 SMILES", "first"),
                salt=("Salt1 SMILES", "first"), molality=("Salt1 Molality (mol salt/kg polymer)", "first"),
                doi=("DOI", "first"))
           .reset_index())
    ok = agg.groupby("curve_id")["temperature_c"].agg(lambda t: t.nunique() >= MIN_POINTS and t.max() - t.min() >= MIN_SPAN_C)
    agg = agg[agg["curve_id"].isin(ok[ok].index)].copy()
    agg["molality"] = pd.to_numeric(agg["molality"], errors="coerce")
    return agg.sort_values(["family", "curve_id", "temperature_c"]).reset_index(drop=True)


# --------------------------------------------------------------------------- grid
def choose_window(fam: pd.DataFrame):
    """Common window (5 C grid, width >= 30 C) covered by the most curves; ties -> wider, then warmer."""
    rng_ = fam.groupby("curve_id")["temperature_c"].agg(["min", "max"])
    lo = math.ceil(fam["temperature_c"].min() / GRID_STEP_C) * GRID_STEP_C
    hi = math.floor(fam["temperature_c"].max() / GRID_STEP_C) * GRID_STEP_C
    best = None
    for a in np.arange(lo, hi - MIN_WINDOW_C + 1e-9, GRID_STEP_C):
        for b in np.arange(a + MIN_WINDOW_C, hi + 1e-9, GRID_STEP_C):
            cov = rng_[(rng_["min"] <= a) & (rng_["max"] >= b)].index
            n_in = fam[fam["curve_id"].isin(cov) & fam["temperature_c"].between(a, b)].groupby("curve_id").size()
            ids = sorted(n_in[n_in >= MIN_IN_WINDOW].index)
            cand = (len(ids), b - a, a)
            if best is None or cand > best[0]:
                best = (cand, float(a), float(b), ids)
    return best


def grid_values(fam: pd.DataFrame, ids, a, b):
    t_ref = 0.5 * (a + b)
    nodes = np.arange(a, b + 1e-9, GRID_STEP_C)
    rows = []
    for cid in ids:
        g = fam[(fam["curve_id"] == cid) & fam["temperature_c"].between(a, b)]
        z = z_of(g["temperature_c"], t_ref)
        coef = np.polyfit(z, g["ln_sigma"], 2)
        for t in nodes:
            rows.append({"curve_id": cid, "temperature_c": float(t), "z": float(z_of(t, t_ref)),
                         "ln_sigma": float(np.polyval(coef, z_of(t, t_ref)))})
    return pd.DataFrame(rows), nodes


# --------------------------------------------------------------------------- analyses
def svd_geometry(grid: pd.DataFrame) -> dict:
    mat = grid.pivot(index="curve_id", columns="temperature_c", values="ln_sigma").to_numpy()
    c = mat - mat.mean(axis=0, keepdims=True)
    _, s, vt = np.linalg.svd(c, full_matrices=False)
    var = s**2 / np.sum(s**2)
    v1 = vt[0]
    return {"mode1_variance_fraction": float(var[0]), "mode2_variance_fraction": float(var[1]),
            "mode1_cosine_to_constant": float(abs(v1.sum()) / (np.linalg.norm(v1) * math.sqrt(len(v1))))}


def _sse(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    return float(r @ r)


def nested_shape_models(grid: pd.DataFrame) -> dict:
    y, z = grid["ln_sigma"].to_numpy(), grid["z"].to_numpy()
    D = pd.get_dummies(grid["curve_id"]).to_numpy(dtype=float)
    n = len(y)
    sst = float(np.sum((y - y.mean()) ** 2))
    sse0 = _sse(np.column_stack([np.ones(n), z, z**2]), y)
    sse1 = _sse(np.column_stack([D, z, z**2]), y)
    sse2 = _sse(np.column_stack([D, D * z[:, None], D * (z**2)[:, None]]), y)
    return {"r2_family_level_only": 1 - sse0 / sst, "r2_curve_level_shared_shape": 1 - sse1 / sst,
            "r2_curve_specific_quadratic": 1 - sse2 / sst,
            "mult_rmse_curve_level_shared_shape": math.exp(math.sqrt(sse1 / n))}


def anchor_transfer(grid: pd.DataFrame, family: str) -> pd.DataFrame:
    rows = []
    ids = sorted(grid["curve_id"].unique())
    t_anchor = grid["temperature_c"].max()
    for held in ids:
        tr = grid[grid["curve_id"] != held]
        D = pd.get_dummies(tr["curve_id"]).to_numpy(dtype=float)
        z = tr["z"].to_numpy()
        beta, *_ = np.linalg.lstsq(np.column_stack([D, z, z**2]), tr["ln_sigma"].to_numpy(), rcond=None)
        b1, b2 = beta[-2], beta[-1]
        mean_level = float(np.mean(beta[:-2]))
        h = grid[grid["curve_id"] == held].sort_values("temperature_c")
        z0 = float(h.loc[h["temperature_c"] == t_anchor, "z"].iloc[0])
        y0 = float(h.loc[h["temperature_c"] == t_anchor, "ln_sigma"].iloc[0])
        for _, r in h[h["temperature_c"] < t_anchor].iterrows():
            pred_anchor = y0 + b1 * (r["z"] - z0) + b2 * (r["z"] ** 2 - z0**2)
            pred_family = mean_level + b1 * r["z"] + b2 * r["z"] ** 2
            rows.append({"family": family, "curve_id": held, "temperature_c": r["temperature_c"],
                         "below_anchor_c": t_anchor - r["temperature_c"],
                         "err_anchor_log": pred_anchor - r["ln_sigma"], "err_family_mean_log": pred_family - r["ln_sigma"]})
    return pd.DataFrame(rows)


def pooled_mult(err: np.ndarray) -> float:
    return math.exp(math.sqrt(float(np.mean(err**2))))


def cluster_boot(df: pd.DataFrame, col: str, rng) -> tuple[float, float]:
    groups = [g[col].to_numpy() for _, g in df.groupby(["family", "curve_id"])]
    stats_ = []
    for _ in range(N_BOOT):
        pick = rng.integers(0, len(groups), len(groups))
        stats_.append(pooled_mult(np.concatenate([groups[i] for i in pick])))
    return float(np.quantile(stats_, 0.025)), float(np.quantile(stats_, 0.975))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, default=None,
                    help="rebuild the vendored curve table from PolymerElectrolyteData.csv (pinned SHA-256)")
    args = ap.parse_args()
    if args.raw is not None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        build_curves(args.raw).to_csv(CURVES_CSV, index=False, lineterminator="\n")
    curves = pd.read_csv(CURVES_CSV, dtype={"curve_id": str})
    curves["ln_sigma"] = curves["log10_sigma"] * math.log(10)
    OUT.mkdir(parents=True, exist_ok=True)

    fam_rows, grids, anchors = [], [], []
    for fam, g in curves.groupby("family"):
        if g["curve_id"].nunique() < MIN_FAMILY_CURVES:
            continue
        (n_cov, width, _), a, b, ids = choose_window(g)
        if len(ids) < MIN_FAMILY_CURVES:
            continue
        grid, nodes = grid_values(g, ids, a, b)
        grid.insert(0, "family", fam)
        grids.append(grid)
        anchors.append(anchor_transfer(grid, fam))
        fam_rows.append({"family": fam, "n_curves_family": g["curve_id"].nunique(), "n_curves_window": len(ids),
                         "window_lo_c": a, "window_hi_c": b, "n_grid_nodes": len(nodes),
                         **svd_geometry(grid), **nested_shape_models(grid)})
    fam_df = pd.DataFrame(fam_rows).sort_values("n_curves_window", ascending=False)
    grid_df = pd.concat(grids, ignore_index=True)
    anc = pd.concat(anchors, ignore_index=True)

    rng = np.random.default_rng(SEED)
    summary = {
        "source": "Bradford et al. 2023, ACS Cent. Sci. 9, 206-216, doi:10.1021/acscentsci.2c01123 (MIT licence)",
        "raw_sha256": RAW_SHA256, "curves_csv_sha256_lf": sha256(CURVES_CSV, normalise_eol=True),
        "n_curves_neat": int(curves["curve_id"].nunique()), "n_families_neat": int(curves["family"].nunique()),
        "n_families_analysed": int(len(fam_df)), "n_curves_analysed": int(fam_df["n_curves_window"].sum()),
        "mode1_variance_fraction_range": [float(fam_df["mode1_variance_fraction"].min()), float(fam_df["mode1_variance_fraction"].max())],
        "mode1_variance_fraction_median": float(fam_df["mode1_variance_fraction"].median()),
        "mode1_cosine_range": [float(fam_df["mode1_cosine_to_constant"].min()), float(fam_df["mode1_cosine_to_constant"].max())],
        "mode1_cosine_median": float(fam_df["mode1_cosine_to_constant"].median()),
        "r2_family_level_only_range": [float(fam_df["r2_family_level_only"].min()), float(fam_df["r2_family_level_only"].max())],
        "r2_curve_level_shared_shape_range": [float(fam_df["r2_curve_level_shared_shape"].min()), float(fam_df["r2_curve_level_shared_shape"].max())],
        "r2_curve_level_shared_shape_median": float(fam_df["r2_curve_level_shared_shape"].median()),
    }
    for col, name in (("err_anchor_log", "one_anchor"), ("err_family_mean_log", "family_mean_no_anchor")):
        lo, hi = cluster_boot(anc, col, rng)
        summary[f"{name}_pooled_mult"] = pooled_mult(anc[col].to_numpy())
        summary[f"{name}_pooled_mult_ci95"] = [lo, hi]
    near = anc[anc["below_anchor_c"] <= 20.0]
    lo, hi = cluster_boot(near, "err_anchor_log", rng)
    summary["one_anchor_within_20C_pooled_mult"] = pooled_mult(near["err_anchor_log"].to_numpy())
    summary["one_anchor_within_20C_pooled_mult_ci95"] = [lo, hi]
    summary["family_mean_no_anchor_within_20C_pooled_mult"] = pooled_mult(near["err_family_mean_log"].to_numpy())
    summary["one_anchor_within_20C_fraction_within_2x"] = float(np.mean(np.abs(near["err_anchor_log"]) <= math.log(2)))
    summary["n_anchor_predictions_within_20C"] = int(len(near))
    summary["n_anchor_predictions"] = int(len(anc))

    fam_df.to_csv(OUT / "family_svd_and_shape_models.csv", index=False, lineterminator="\n")
    grid_df.to_csv(OUT / "grid_ln_sigma.csv", index=False, lineterminator="\n")
    anc.to_csv(OUT / "anchor_per_prediction.csv", index=False, lineterminator="\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(fam_df[["n_curves_window", "window_lo_c", "window_hi_c", "mode1_variance_fraction", "mode1_cosine_to_constant",
                  "r2_family_level_only", "r2_curve_level_shared_shape"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main()
