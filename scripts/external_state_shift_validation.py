#!/usr/bin/env python3
"""External test of the state-shift geometry and one-point anchor transfer.

Uses the public dense prepolymer temperature-viscosity curves of Pugar et al. (2025)
as stored in the local external SQLite database (opened read-only). Tests, on data that
were not used to build the local claims:

1. whether between-curve variation inside a chemistry family is a vertical shift in
   ln(eta) on a shared quadratic response in z(T) (manuscript sections 2.2 / 3.4);
2. whether a family-shared thermal shape plus one anchor viscosity reconstructs a held
   curve (sections 2.3 / 3.5), and how this depends on where the shape comes from
   (same polyol x isocyanate family, same polyol family, other polyol family, all);
3. a strict analogue of the local 110 -> 120/130 C holdout.

Conventions follow scripts/statistical_robustness.py and scripts/master_curve_collapse.py:
z(T) = 1e3 * (1/T - 1/Tref) with T in kelvin, multiplicative RMSE = exp(RMSE of ln eta),
realization (curve)-level cluster bootstrap.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = Path(
    r"C:\Users\ASUS\Documents\Codex\2026-08-06\referenced-chatgpt-conversation-this-is-an"
    r"\outputs\HMPUR_引君database\database\hmpur_external.db"
)
DEFAULT_OUT = ROOT / "analysis" / "results" / "upgrades_20261003" / "external_state_shift"

R_GAS = 8.314462618
T_REF_C = 60.0
# Every node lies strictly inside the measured range of every full-range curve
# (largest curve minimum 40.32 C, smallest curve maximum 79.96 C), so no grid value is extrapolated.
GRID_C = np.round(np.arange(42.5, 77.5 + 1e-9, 2.5), 2)
LOESS_HALF_WIDTH_C = 2.5      # local quadratic window (+/- C)
SUPPORT_HALF_WIDTH_C = 1.25   # a node needs measured inliers within +/- this ...
MIN_SUPPORT_POINTS = 3        # ... at least this many, otherwise it sits in a data gap and is dropped
HAMPEL_WINDOW = 7
HAMPEL_K = 5.0
HAMPEL_FLOOR = 0.03           # minimum |deviation| in ln(eta) to flag a spike
PRIMARY_CURVE_R2 = 0.98       # manuscript section 3.8 primary-curve rule
REGIME_SCREEN_MULT = 1.05     # sensitivity set: curve's own grid quadratic must fit within 1.05x (no transition in window)
HEADLINE_ANCHOR_C = 60.0
STRICT_SPLITS_C = (47.5, 50.0, 52.5, 55.0, 57.5)
STRICT_PRIMARY_SPLIT_C = 57.5
STRICT_OFFSETS_C = (10.0, 20.0)
SEED = 20261003
N_BOOT = 10000

SOURCES = {
    "a_same_polyol_same_iso": "other curves, same polyol x isocyanate family",
    "b_same_polyol_other_iso": "same polyol family, different isocyanate",
    "c_other_polyol_same_iso": "same isocyanate, different polyol family (polyol-family holdout)",
    "d_all_other": "all other curves",
    "ref_own_curve": "held curve's own quadratic (reference floor, not a transfer)",
}
TRANSFER_SOURCES = [s for s in SOURCES if not s.startswith("ref_")]


def z_of(t_c):
    return 1e3 * (1.0 / (np.asarray(t_c, dtype=float) + 273.15) - 1.0 / (T_REF_C + 273.15))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------- data
def load_curves(db: Path) -> pd.DataFrame:
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        raw = pd.read_sql_query("SELECT * FROM viscosity_curves", con)
    finally:
        con.close()
    for col in ["temperature_c", "viscosity_pa_s", "pNCO_pct", "sequence_index"]:
        raw[col] = pd.to_numeric(raw[col], errors="raise")
    raw = raw[raw["viscosity_pa_s"] > 0].copy()
    raw["ln_eta"] = np.log(raw["viscosity_pa_s"])
    raw["z"] = z_of(raw["temperature_c"])
    return raw.sort_values(["sample_id", "temperature_c"]).reset_index(drop=True)


def flag_spikes(group: pd.DataFrame) -> np.ndarray:
    """Hampel filter on residuals from a per-curve quadratic: flags isolated spikes only.

    Only points with a full centred window are tested, so the first and last three points
    of a curve (where genuine end-of-range curvature lives) are never flagged.
    """
    z = group["z"].to_numpy()
    y = group["ln_eta"].to_numpy()
    r = y - np.polyval(np.polyfit(z, y, 2), z)
    med = pd.Series(r).rolling(HAMPEL_WINDOW, center=True, min_periods=HAMPEL_WINDOW).median().to_numpy()
    dev = r - med
    flagged = np.abs(dev) > max(HAMPEL_K * np.nanmedian(np.abs(dev - np.nanmedian(dev))) * 1.4826, HAMPEL_FLOOR)
    return np.where(np.isfinite(dev), flagged, False)


def loess_at(t0: float, t: np.ndarray, z: np.ndarray, y: np.ndarray) -> tuple[float, int]:
    """Tricube-weighted local quadratic in z around temperature t0 (interpolation only)."""
    u = (t - t0) / (LOESS_HALF_WIDTH_C * 1.0001)
    m = np.abs(u) < 1
    if m.sum() < 6:
        return float("nan"), int(m.sum())
    w = (1 - np.abs(u[m]) ** 3) ** 3
    dz = z[m] - z_of(t0)
    X = np.column_stack([np.ones_like(dz), dz, dz**2])
    sw = np.sqrt(w)
    beta, *_ = np.linalg.lstsq(X * sw[:, None], y[m] * sw, rcond=None)
    return float(beta[0]), int(m.sum())


def build_grid(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    grid_rows, curve_rows = [], []
    for sid, g in raw.groupby("sample_id", sort=True):
        g = g.sort_values("temperature_c")
        spikes = flag_spikes(g)
        t_all = g["temperature_c"].to_numpy()
        z_all = g["z"].to_numpy()
        y_all = g["ln_eta"].to_numpy()
        t, z, y = t_all[~spikes], z_all[~spikes], y_all[~spikes]
        # residual of the local smoother at each measured inlier point
        fitted = np.array([loess_at(ti, t, z, y)[0] for ti in t])
        resid = y - fitted
        lin = stats.linregress(1.0 / (t_all + 273.15), y_all)
        nodes_kept = []
        for node in GRID_C:
            inside = t.min() <= node <= t.max()
            support = int(np.sum(np.abs(t - node) <= SUPPORT_HALF_WIDTH_C))
            if not inside or support < MIN_SUPPORT_POINTS:
                continue
            val, nwin = loess_at(node, t, z, y)
            if not np.isfinite(val):
                continue
            nodes_kept.append(node)
            grid_rows.append(
                {
                    "sample_id": sid,
                    "temperature_c": float(node),
                    "z": float(z_of(node)),
                    "ln_eta": val,
                    "n_window_points": nwin,
                    "n_support_points": support,
                }
            )
        first = g.iloc[0]
        curve_rows.append(
            {
                "sample_id": sid,
                "polyol_code": first["polyol_code"],
                "isocyanate_code": first["isocyanate_code"],
                "pNCO_pct": float(first["pNCO_pct"]),
                "n_rows": int(len(g)),
                "t_min_c": float(t_all.min()),
                "t_max_c": float(t_all.max()),
                "apparent_E_eta_kJ_mol": float(lin.slope * R_GAS / 1000.0),
                "ln_eta_inv_T_r2": float(lin.rvalue**2),
                "n_spikes_flagged": int(spikes.sum()),
                "smoother_resid_rms_log": float(np.sqrt(np.nanmean(resid**2))),
                "smoother_resid_max_abs_log": float(np.nanmax(np.abs(resid))),
                "smoother_resid_n_points": int(np.isfinite(resid).sum()),
                "n_grid_nodes": len(nodes_kept),
                "complete_grid": len(nodes_kept) == len(GRID_C),
                "missing_nodes_c": ";".join(f"{n:g}" for n in GRID_C if n not in nodes_kept),
            }
        )
    curves = pd.DataFrame(curve_rows)
    curves["pair_family"] = curves["polyol_code"] + "_" + curves["isocyanate_code"]
    curves["primary_set"] = curves["ln_eta_inv_T_r2"] >= PRIMARY_CURVE_R2
    grid = pd.DataFrame(grid_rows).merge(
        curves[["sample_id", "polyol_code", "isocyanate_code", "pair_family"]], on="sample_id"
    )
    own = {}
    for sid, g in grid.groupby("sample_id"):
        r = g["ln_eta"] - np.polyval(np.polyfit(g["z"], g["ln_eta"], 2), g["z"])
        own[sid] = math.exp(math.sqrt(float(np.mean(r**2))))
    curves["own_grid_quadratic_mult_rmse"] = curves["sample_id"].map(own)
    curves["regime_screen_pass"] = curves["own_grid_quadratic_mult_rmse"] <= REGIME_SCREEN_MULT
    return grid, curves


# --------------------------------------------------------------------------- geometry
def svd_geometry(grid: pd.DataFrame, ids: list[str]) -> dict:
    mat = (
        grid[grid["sample_id"].isin(ids)]
        .pivot(index="sample_id", columns="temperature_c", values="ln_eta")
        .reindex(columns=GRID_C)
        .dropna(axis=0)
    )
    n = len(mat)
    if n < 3:
        return {"n_curves_svd": n}
    centred = mat.to_numpy() - mat.to_numpy().mean(axis=0, keepdims=True)
    u, s, vt = np.linalg.svd(centred, full_matrices=False)
    var = s**2 / np.sum(s**2)
    v1 = vt[0]
    row_mean_removed = centred - centred.mean(axis=1, keepdims=True)
    rank1_resid = centred - s[0] * np.outer(u[:, 0], vt[0])
    cos = abs(v1.sum()) / (np.linalg.norm(v1) * math.sqrt(len(v1)))
    return {
        "n_curves_svd": n,
        "mode1_variance_fraction": float(var[0]),
        "mode2_variance_fraction": float(var[1]) if len(var) > 1 else 0.0,
        "mode1_cosine_to_constant": float(cos),
        "total_between_curve_ss": float(np.sum(s**2)),
        "non_shift_rms_log": float(np.sqrt(np.mean(row_mean_removed**2))),
        "non_shift_mult": float(math.exp(np.sqrt(np.mean(row_mean_removed**2)))),
        "rank1_resid_rms_log": float(np.sqrt(np.mean(rank1_resid**2))),
        "max_over_min_level_ratio": float(
            math.exp(mat.to_numpy().mean(axis=1).max() - mat.to_numpy().mean(axis=1).min())
        ),
    }


def _ols_sse(X: np.ndarray, y: np.ndarray) -> float:
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    return float(r @ r)


def nested_shape_models(grid: pd.DataFrame, ids: list[str]) -> dict:
    sub = grid[grid["sample_id"].isin(ids)]
    k = sub["sample_id"].nunique()
    if k < 2:
        return {}
    y = sub["ln_eta"].to_numpy()
    z = sub["z"].to_numpy()
    n = len(y)
    D = pd.get_dummies(sub["sample_id"]).to_numpy(dtype=float)
    sst = float(np.sum((y - y.mean()) ** 2))
    X0 = np.column_stack([np.ones(n), z, z**2])
    X1 = np.column_stack([D, z, z**2])
    X2 = np.column_stack([D, D * z[:, None], D * (z**2)[:, None]])
    sse0, sse1, sse2 = _ols_sse(X0, y), _ols_sse(X1, y), _ols_sse(X2, y)
    df_num, df_den = 2 * k - 2, n - 3 * k
    f = ((sse1 - sse2) / df_num) / (sse2 / df_den) if df_den > 0 and sse2 > 0 else float("nan")
    return {
        "n_curves": k,
        "n_grid_values": n,
        "r2_family_level_only": 1 - sse0 / sst,
        "r2_curve_level_shared_shape": 1 - sse1 / sst,
        "r2_curve_specific_quadratic": 1 - sse2 / sst,
        "mult_rmse_family_level_only": math.exp(math.sqrt(sse0 / n)),
        "mult_rmse_curve_level_shared_shape": math.exp(math.sqrt(sse1 / n)),
        "mult_rmse_curve_specific_quadratic": math.exp(math.sqrt(sse2 / n)),
        "share_of_curve_level_residual_removed_by_own_shape": (sse1 - sse2) / sse1 if sse1 > 0 else float("nan"),
        "nested_F_shared_vs_curve_specific_shape": f,
        "nested_F_df": f"{df_num},{df_den}",
        "nested_F_p_diagnostic": float(stats.f.sf(f, df_num, df_den)) if np.isfinite(f) else float("nan"),
    }


def family_sets(curves: pd.DataFrame) -> list[tuple[str, str, list[str]]]:
    sets = []
    for pol, g in curves.groupby("polyol_code"):
        sets.append(("within_polyol_family", pol, g["sample_id"].tolist()))
    for fam, g in curves.groupby("pair_family"):
        if len(g) >= 3:
            sets.append(("within_polyol_x_iso_family", fam, g["sample_id"].tolist()))
    for iso, g in curves.groupby("isocyanate_code"):
        if g["polyol_code"].nunique() >= 2 and len(g) >= 3:
            sets.append(("same_iso_across_polyol_families", iso, g["sample_id"].tolist()))
    pols = sorted(curves["polyol_code"].unique())
    for i in range(len(pols)):
        for j in range(i + 1, len(pols)):
            ids = curves[curves["polyol_code"].isin([pols[i], pols[j]])]["sample_id"].tolist()
            sets.append(("two_polyol_families_pooled", f"{pols[i]}+{pols[j]}", ids))
    sets.append(("all_families_pooled", "all", curves["sample_id"].tolist()))
    return sets


# --------------------------------------------------------------------------- anchor transfer
def source_ids(curves: pd.DataFrame, held: pd.Series, source: str) -> list[str]:
    others = curves[curves["sample_id"] != held["sample_id"]]
    same_pol = others["polyol_code"] == held["polyol_code"]
    same_iso = others["isocyanate_code"] == held["isocyanate_code"]
    if source == "a_same_polyol_same_iso":
        sel = same_pol & same_iso
    elif source == "b_same_polyol_other_iso":
        sel = same_pol & ~same_iso
    elif source == "c_other_polyol_same_iso":
        sel = ~same_pol & same_iso
    elif source == "d_all_other":
        sel = pd.Series(True, index=others.index)
    else:
        return [held["sample_id"]]
    return others.loc[sel, "sample_id"].tolist()


def fit_shared_shape(grid: pd.DataFrame, ids: list[str], t_max: float | None = None):
    sub = grid[grid["sample_id"].isin(ids)]
    if t_max is not None:
        sub = sub[sub["temperature_c"] <= t_max + 1e-9]
    counts = sub.groupby("sample_id").size()
    sub = sub[sub["sample_id"].isin(counts[counts >= 3].index)]
    if sub.empty:
        return None
    z = sub["z"].to_numpy()
    D = pd.get_dummies(sub["sample_id"]).to_numpy(dtype=float)
    X = np.column_stack([D, z, z**2])
    beta, *_ = np.linalg.lstsq(X, sub["ln_eta"].to_numpy(), rcond=None)
    return float(beta[-2]), float(beta[-1]), int(sub["sample_id"].nunique())


def predict_from_anchor(b1, b2, y0, z0, z):
    return y0 + b1 * (z - z0) + b2 * (z**2 - z0**2)


def anchor_transfer(grid: pd.DataFrame, curves: pd.DataFrame, curve_set: str) -> pd.DataFrame:
    rows = []
    for _, held in curves.iterrows():
        hg = grid[grid["sample_id"] == held["sample_id"]].sort_values("temperature_c")
        for source in SOURCES:
            ids = source_ids(curves, held, source)
            if not ids:
                continue
            shape = fit_shared_shape(grid, ids)
            if shape is None:
                continue
            b1, b2, n_src = shape
            for _, a in hg.iterrows():
                test = hg[hg["temperature_c"] != a["temperature_c"]]
                pred = predict_from_anchor(b1, b2, a["ln_eta"], a["z"], test["z"].to_numpy())
                err = test["ln_eta"].to_numpy() - pred
                rows.append(
                    {
                        "curve_set": curve_set,
                        "sample_id": held["sample_id"],
                        "polyol_code": held["polyol_code"],
                        "isocyanate_code": held["isocyanate_code"],
                        "source": source,
                        "n_source_curves": n_src,
                        "anchor_c": float(a["temperature_c"]),
                        "n_pred": int(len(err)),
                        "sse_log": float(err @ err),
                        "rmse_log": float(math.sqrt(np.mean(err**2))),
                        "mult_rmse": float(math.exp(math.sqrt(np.mean(err**2)))),
                        "median_ape_pct": float(np.median(np.abs(np.expm1(-err))) * 100),
                        "max_abs_err_log": float(np.max(np.abs(err))),
                    }
                )
    return pd.DataFrame(rows)


def strict_extrapolation(grid: pd.DataFrame, curves: pd.DataFrame, curve_set: str) -> pd.DataFrame:
    rows = []
    for split in STRICT_SPLITS_C:
        targets = [split + o for o in STRICT_OFFSETS_C]
        for _, held in curves.iterrows():
            hg = grid[grid["sample_id"] == held["sample_id"]].set_index("temperature_c")
            if split not in hg.index:
                continue
            for source in SOURCES:
                ids = source_ids(curves, held, source)
                if not ids:
                    continue
                shape = fit_shared_shape(grid, ids, t_max=split)
                if shape is None:
                    continue
                b1, b2, n_src = shape
                y0, z0 = hg.loc[split, "ln_eta"], hg.loc[split, "z"]
                for off, tt in zip(STRICT_OFFSETS_C, targets):
                    if tt not in hg.index:
                        continue
                    pred = predict_from_anchor(b1, b2, y0, z0, hg.loc[tt, "z"])
                    err = float(hg.loc[tt, "ln_eta"] - pred)
                    rows.append(
                        {
                            "curve_set": curve_set,
                            "split_c": split,
                            "sample_id": held["sample_id"],
                            "polyol_code": held["polyol_code"],
                            "isocyanate_code": held["isocyanate_code"],
                            "source": source,
                            "n_source_curves": n_src,
                            "target_c": tt,
                            "offset_c": off,
                            "err_log": err,
                            "ape_pct": abs(math.expm1(-err)) * 100,
                        }
                    )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- bootstrap
def cluster_boot(sse: np.ndarray, n: np.ndarray, rng: np.random.Generator) -> tuple[float, float]:
    k = len(sse)
    idx = rng.integers(0, k, size=(N_BOOT, k))
    rm = np.sqrt(sse[idx].sum(axis=1) / n[idx].sum(axis=1))
    lo, hi = np.quantile(np.exp(rm), [0.025, 0.975])
    return float(lo), float(hi)


def pooled_row(per_curve: pd.DataFrame, rng) -> dict:
    sse = per_curve["sse_log"].to_numpy()
    n = per_curve["n_pred"].to_numpy()
    rm = math.sqrt(sse.sum() / n.sum())
    lo, hi = cluster_boot(sse, n, rng)
    return {
        "n_curves": int(len(per_curve)),
        "n_predictions": int(n.sum()),
        "pooled_rmse_log": rm,
        "pooled_mult_rmse": math.exp(rm),
        "boot95_lo": lo,
        "boot95_hi": hi,
        "median_curve_mult_rmse": float(per_curve["mult_rmse"].median()),
        "worst_curve_mult_rmse": float(per_curve["mult_rmse"].max()),
        "worst_curve": per_curve.loc[per_curve["mult_rmse"].idxmax(), "sample_id"],
    }


def common_curves(df: pd.DataFrame, key_cols: list[str]) -> set[str]:
    avail = df[df["source"].isin(TRANSFER_SOURCES)].groupby("sample_id")["source"].nunique()
    return set(avail[avail == len(TRANSFER_SOURCES)].index)


def pooled_anchor_table(anchor: pd.DataFrame, seed_offset: int) -> pd.DataFrame:
    rows = []
    rng = np.random.default_rng(SEED + seed_offset)
    common_by_anchor = {t0: common_curves(ga, ["sample_id"]) for t0, ga in anchor.groupby("anchor_c")}
    for (cset, source, t0), g in anchor.groupby(["curve_set", "source", "anchor_c"]):
        common = common_by_anchor[t0]
        for subset, gg in (("available", g), ("common_a_to_d", g[g["sample_id"].isin(common)])):
            if gg.empty:
                continue
            rows.append({"curve_set": cset, "source": source, "anchor_c": t0, "subset": subset, **pooled_row(gg, rng)})
    return pd.DataFrame(rows)


def paired_contrasts(anchor: pd.DataFrame, t0: float, seed_offset: int) -> pd.DataFrame:
    """Paired cluster bootstrap on curves with all four transfer sources available."""
    rng = np.random.default_rng(SEED + seed_offset)
    g = anchor[anchor["anchor_c"] == t0]
    common = sorted(common_curves(g, ["sample_id"]))
    pv = {
        s: g[g["source"] == s].set_index("sample_id").loc[common, ["sse_log", "n_pred"]]
        for s in SOURCES
        if set(common) <= set(g[g["source"] == s]["sample_id"])
    }
    idx = rng.integers(0, len(common), size=(N_BOOT, len(common)))
    out = []
    pairs = [
        ("b_same_polyol_other_iso", "a_same_polyol_same_iso"),
        ("c_other_polyol_same_iso", "a_same_polyol_same_iso"),
        ("c_other_polyol_same_iso", "b_same_polyol_other_iso"),
        ("d_all_other", "b_same_polyol_other_iso"),
        ("c_other_polyol_same_iso", "d_all_other"),
    ]
    for x, y in pairs:
        sx, nx = pv[x]["sse_log"].to_numpy(), pv[x]["n_pred"].to_numpy()
        sy, ny = pv[y]["sse_log"].to_numpy(), pv[y]["n_pred"].to_numpy()
        point = math.sqrt(sx.sum() / nx.sum()) / math.sqrt(sy.sum() / ny.sum())
        boot = np.sqrt(sx[idx].sum(1) / nx[idx].sum(1)) / np.sqrt(sy[idx].sum(1) / ny[idx].sum(1))
        lo, hi = np.quantile(boot, [0.025, 0.975])
        out.append(
            {
                "anchor_c": t0,
                "numerator_source": x,
                "denominator_source": y,
                "n_common_curves": len(common),
                "log_rmse_ratio": point,
                "boot95_lo": float(lo),
                "boot95_hi": float(hi),
                "share_boot_ratio_gt_1": float(np.mean(boot > 1)),
            }
        )
    return pd.DataFrame(out)


def pooled_strict_table(strict: pd.DataFrame, seed_offset: int) -> pd.DataFrame:
    rng = np.random.default_rng(SEED + seed_offset)
    rows = []
    per_split_common = {}
    for (cset, split), g in strict.groupby(["curve_set", "split_c"]):
        avail = g[g["source"].isin(TRANSFER_SOURCES)].groupby("sample_id")["source"].nunique()
        per_split_common[(cset, split)] = set(avail[avail == len(TRANSFER_SOURCES)].index)
    for (cset, split, source), g in strict.groupby(["curve_set", "split_c", "source"]):
        for subset, gg in (("available", g), ("common_a_to_d", g[g["sample_id"].isin(per_split_common[(cset, split)])])):
            if gg.empty:
                continue
            pc = gg.groupby("sample_id").agg(sse_log=("err_log", lambda e: float(np.sum(np.square(e)))), n_pred=("err_log", "size"))
            sse, n = pc["sse_log"].to_numpy(), pc["n_pred"].to_numpy()
            rm = math.sqrt(sse.sum() / n.sum())
            lo, hi = cluster_boot(sse, n, rng)
            row = {
                "curve_set": cset,
                "split_c": split,
                "source": source,
                "subset": subset,
                "n_curves": int(len(pc)),
                "n_predictions": int(n.sum()),
                "pooled_rmse_log": rm,
                "pooled_mult_rmse": math.exp(rm),
                "boot95_lo": lo,
                "boot95_hi": hi,
                "median_ape_pct": float(gg["ape_pct"].median()),
            }
            for off in STRICT_OFFSETS_C:
                e = gg.loc[gg["offset_c"] == off, "err_log"].to_numpy()
                row[f"mult_rmse_plus{int(off)}c"] = float(math.exp(math.sqrt(np.mean(e**2)))) if len(e) else float("nan")
                row[f"mean_bias_log_plus{int(off)}c"] = float(np.mean(e)) if len(e) else float("nan")
            rows.append(row)
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- figure
def make_figure(grid, curves, pooled, strict_tab, out_png: Path) -> str:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fam = curves[curves["primary_set"] & curves["complete_grid"]].groupby("polyol_code").size().idxmax()
    ids = curves[(curves["polyol_code"] == fam) & curves["primary_set"]]["sample_id"].tolist()
    sub = grid[grid["sample_id"].isin(ids)].copy()
    D = pd.get_dummies(sub["sample_id"])
    X = np.column_stack([D.to_numpy(float), sub["z"], sub["z"] ** 2])
    beta, *_ = np.linalg.lstsq(X, sub["ln_eta"].to_numpy(), rcond=None)
    levels = dict(zip(D.columns, beta[: D.shape[1]]))
    sub["collapsed"] = sub["ln_eta"] - sub["sample_id"].map(levels)

    isos = sorted(curves["isocyanate_code"].unique())
    palette = ["#1b6ca8", "#d1495b", "#2e8b57", "#e08e0b", "#6a4c93", "#00798c"]
    colour = {iso: palette[i % len(palette)] for i, iso in enumerate(isos)}
    plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "axes.titlesize": 12})
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6))
    for sid, g in sub.groupby("sample_id"):
        iso = g["isocyanate_code"].iloc[0]
        axes[0].plot(g["temperature_c"], g["ln_eta"], "-o", ms=2.5, lw=1.2, color=colour[iso])
        axes[1].plot(g["temperature_c"], g["collapsed"], "-o", ms=2.5, lw=1.2, color=colour[iso])
    zz = z_of(GRID_C)
    axes[1].plot(GRID_C, beta[-2] * zz + beta[-1] * zz**2, "k--", lw=1.5, label="shared quadratic g(T)")
    handles = [plt.Line2D([], [], color=colour[i], lw=2, label=i) for i in isos if i in set(sub["isocyanate_code"])]
    axes[0].legend(handles=handles, title="isocyanate", fontsize=9, frameon=False)
    axes[1].legend(fontsize=9, frameon=False)
    axes[0].set(xlabel="Temperature (°C)", ylabel="ln η (Pa·s)", title=f"A  Polyol family {fam}: {len(ids)} curves")
    axes[1].set(xlabel="Temperature (°C)", ylabel="ln η − curve level", title="B  Same curves, curve level removed")

    labels = {
        "a_same_polyol_same_iso": "(a) same polyol\n× iso",
        "b_same_polyol_other_iso": "(b) same polyol,\nother iso",
        "c_other_polyol_same_iso": "(c) other polyol,\nsame iso",
        "d_all_other": "(d) all other",
    }
    ax = axes[2]
    p = pooled[
        (pooled["curve_set"] == "primary")
        & (pooled["anchor_c"] == HEADLINE_ANCHOR_C)
        & (pooled["subset"] == "common_a_to_d")
    ].set_index("source")
    s = strict_tab[
        (strict_tab["curve_set"] == "primary")
        & (strict_tab["split_c"] == STRICT_PRIMARY_SPLIT_C)
        & (strict_tab["subset"] == "common_a_to_d")
    ].set_index("source")
    xs = np.arange(len(labels))
    for k, (tab, off, mk, lab) in enumerate(
        [
            (p, -0.12, "o", f"anchor {HEADLINE_ANCHOR_C:g} °C, all other nodes"),
            (s, 0.12, "s", f"strict: shape ≤{STRICT_PRIMARY_SPLIT_C:g} °C, predict +10/+20 °C"),
        ]
    ):
        y = tab.loc[list(labels), "pooled_mult_rmse"].to_numpy()
        lo = tab.loc[list(labels), "boot95_lo"].to_numpy()
        hi = tab.loc[list(labels), "boot95_hi"].to_numpy()
        ax.errorbar(xs + off, y, yerr=[y - lo, hi - y], fmt=mk, ms=7, capsize=4, lw=1.5,
                    color=["#1b6ca8", "#d1495b"][k], label=lab)
    ax.axhspan(1.06, 1.10, color="#2e8b57", alpha=0.15, lw=0)
    ax.text(len(labels) - 0.5, 1.08, "local E1–E3\n1.06–1.10×", ha="right", va="center", fontsize=9, color="#1d5c3a")
    ax.set_xticks(xs, list(labels.values()), fontsize=9)
    ax.set(ylabel="Pooled multiplicative RMSE (×)", title="C  One-point anchor error by shape source")
    ax.legend(fontsize=8.5, frameon=False, loc="upper left")
    for a in axes:
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)
    return fam


# --------------------------------------------------------------------------- main
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    raw = load_curves(args.db)
    grid, curves = build_grid(raw)
    curves.to_csv(out / "curve_inventory_and_smoothing.csv", index=False)
    grid.round(6).to_csv(out / "grid_ln_eta_smoothed.csv", index=False)

    curve_sets = {
        "primary": curves[curves["primary_set"]].reset_index(drop=True),
        "all_curves": curves.reset_index(drop=True),
        "primary_regime_screened": curves[curves["primary_set"] & curves["regime_screen_pass"]].reset_index(drop=True),
    }

    geo_rows = []
    for cs_name, cs in curve_sets.items():
        for kind, name, ids in family_sets(cs):
            row = {"curve_set": cs_name, "set_kind": kind, "set_name": name}
            row.update(svd_geometry(grid, ids))
            row.update(nested_shape_models(grid, ids))
            geo_rows.append(row)
    geo = pd.DataFrame(geo_rows)
    geo.to_csv(out / "family_svd_and_shape_models.csv", index=False)

    anchor = pd.concat([anchor_transfer(grid, cs, n) for n, cs in curve_sets.items()], ignore_index=True)
    anchor.to_csv(out / "anchor_per_curve.csv", index=False)
    pooled = pd.concat(
        [pooled_anchor_table(anchor[anchor["curve_set"] == n], i) for i, n in enumerate(curve_sets)],
        ignore_index=True,
    )
    pooled.to_csv(out / "anchor_pooled_by_source_and_anchor.csv", index=False)
    contrasts = pd.concat(
        [
            paired_contrasts(anchor[anchor["curve_set"] == n], HEADLINE_ANCHOR_C, 10 + i).assign(curve_set=n)
            for i, n in enumerate(curve_sets)
        ],
        ignore_index=True,
    )
    contrasts.to_csv(out / "anchor_paired_source_contrasts.csv", index=False)

    strict = pd.concat([strict_extrapolation(grid, cs, n) for n, cs in curve_sets.items()], ignore_index=True)
    strict.to_csv(out / "strict_extrapolation_per_prediction.csv", index=False)
    strict_tab = pooled_strict_table(strict, 20)
    strict_tab.to_csv(out / "strict_extrapolation_pooled.csv", index=False)

    fam = make_figure(grid, curve_sets["primary"], pooled, strict_tab, out / "external_state_shift_diagnostic.png")

    # ----------------------------------------------------------------- summary
    def g_(kind, cs="primary"):
        d = geo[(geo["curve_set"] == cs) & (geo["set_kind"] == kind)]
        return {
            r["set_name"]: {
                k: (round(r[k], 5) if isinstance(r[k], float) else r[k])
                for k in [
                    "n_curves_svd", "mode1_variance_fraction", "mode1_cosine_to_constant", "non_shift_mult",
                    "r2_family_level_only", "r2_curve_level_shared_shape", "r2_curve_specific_quadratic",
                    "mult_rmse_curve_level_shared_shape",
                ]
                if k in r and pd.notna(r[k])
            }
            for _, r in d.iterrows()
        }

    def p_(cs, t0, subset):
        d = pooled[(pooled["curve_set"] == cs) & (pooled["anchor_c"] == t0) & (pooled["subset"] == subset)]
        return {
            r["source"]: {
                "n_curves": int(r["n_curves"]),
                "pooled_mult_rmse": round(r["pooled_mult_rmse"], 4),
                "boot95": [round(r["boot95_lo"], 4), round(r["boot95_hi"], 4)],
                "worst_curve": r["worst_curve"],
                "worst_curve_mult_rmse": round(r["worst_curve_mult_rmse"], 4),
            }
            for _, r in d.iterrows()
        }

    def range_over_anchors(cs, subset):
        d = pooled[(pooled["curve_set"] == cs) & (pooled["subset"] == subset)]
        return {
            s: [round(float(g["pooled_mult_rmse"].min()), 4), round(float(g["pooled_mult_rmse"].max()), 4)]
            for s, g in d.groupby("source")
        }

    def s_(cs, split, subset):
        d = strict_tab[(strict_tab["curve_set"] == cs) & (strict_tab["split_c"] == split) & (strict_tab["subset"] == subset)]
        return {
            r["source"]: {
                "n_curves": int(r["n_curves"]),
                "n_predictions": int(r["n_predictions"]),
                "pooled_mult_rmse": round(r["pooled_mult_rmse"], 4),
                "boot95": [round(r["boot95_lo"], 4), round(r["boot95_hi"], 4)],
                "mult_rmse_plus10c": round(r["mult_rmse_plus10c"], 4),
                "mult_rmse_plus20c": round(r["mult_rmse_plus20c"], 4),
                "median_ape_pct": round(r["median_ape_pct"], 2),
            }
            for _, r in d.iterrows()
        }

    prim = curve_sets["primary"]
    summary = {
        "script": "scripts/external_state_shift_validation.py",
        "data": {
            "db_path": str(args.db),
            "db_sha256": sha256(args.db),
            "table": "viscosity_curves",
            "opened": "read-only (sqlite URI mode=ro)",
            "n_rows": int(len(raw)),
            "n_curves": int(raw["sample_id"].nunique()),
            "source": "Pugar et al. 2025, github.com/joepugar/viscosity-modeling",
        },
        "settings": {
            "T_ref_c": T_REF_C,
            "z_definition": "z = 1e3*(1/T - 1/Tref), T in K",
            "grid_c": GRID_C.tolist(),
            "grid_rule": "node kept only if inside the curve's measured range and >=3 spike-free measured points within +/-1.25 C (no extrapolation, no bridging of data gaps)",
            "smoother": "tricube-weighted local quadratic in z, half-width 2.5 C, after Hampel spike removal (window 7, 5 robust SD, floor 0.03 in ln eta) on per-curve quadratic residuals",
            "primary_curve_rule": f"ln eta vs 1/T R^2 >= {PRIMARY_CURVE_R2} (manuscript section 3.8)",
            "headline_anchor_c": HEADLINE_ANCHOR_C,
            "strict_primary": f"shape fitted on source curves at nodes <= {STRICT_PRIMARY_SPLIT_C} C; anchor {STRICT_PRIMARY_SPLIT_C} C; predict +10 and +20 C",
            "bootstrap": {"type": "curve-level cluster bootstrap", "n_resamples": N_BOOT, "seed_base": SEED,
                          "seeds": "SEED+i pooled anchor tables (i = curve-set index 0 primary, 1 all_curves, 2 primary_regime_screened), SEED+10+i paired contrasts, SEED+20 strict"},
        },
        "inclusion": {
            "primary_curves": prim["sample_id"].tolist(),
            "excluded_from_primary": curves.loc[~curves["primary_set"], ["sample_id", "ln_eta_inv_T_r2"]]
            .round(4).to_dict(orient="records"),
            "incomplete_grid_curves": curves.loc[~curves["complete_grid"], ["sample_id", "missing_nodes_c"]].to_dict(orient="records"),
            "svd_uses_complete_grid_curves_only": True,
            "anchor_and_shape_fits_use_all_kept_nodes": True,
        },
        "sanity": {
            "apparent_E_eta_range_kJ_mol_all39": [
                round(curves["apparent_E_eta_kJ_mol"].min(), 2), round(curves["apparent_E_eta_kJ_mol"].max(), 2)
            ],
            "n_curves_r2_ge_0_98": int(curves["primary_set"].sum()),
            "manuscript_range_kJ_mol": [34.7, 94.2],
            "apparent_E_eta_range_by_polyol_kJ_mol": {
                pol: [round(g["apparent_E_eta_kJ_mol"].min(), 1), round(g["apparent_E_eta_kJ_mol"].max(), 1)]
                for pol, g in curves.groupby("polyol_code")
            },
        },
        "smoothing": {
            "median_curve_resid_rms_log": round(float(curves["smoother_resid_rms_log"].median()), 5),
            "max_curve_resid_rms_log": round(float(curves["smoother_resid_rms_log"].max()), 5),
            "max_curve_resid_rms_curve": curves.loc[curves["smoother_resid_rms_log"].idxmax(), "sample_id"],
            "total_spikes_flagged": int(curves["n_spikes_flagged"].sum()),
        },
        "geometry_primary": {
            "within_polyol_family": g_("within_polyol_family"),
            "within_polyol_x_iso_family": g_("within_polyol_x_iso_family"),
            "same_iso_across_polyol_families": g_("same_iso_across_polyol_families"),
            "two_polyol_families_pooled": g_("two_polyol_families_pooled"),
            "all_families_pooled": g_("all_families_pooled"),
        },
        "anchor_headline_primary": {
            "anchor_c": HEADLINE_ANCHOR_C,
            "common_a_to_d": p_("primary", HEADLINE_ANCHOR_C, "common_a_to_d"),
            "available": p_("primary", HEADLINE_ANCHOR_C, "available"),
            "range_over_anchor_temperatures_common": range_over_anchors("primary", "common_a_to_d"),
            "paired_log_rmse_ratios": contrasts[contrasts["curve_set"] == "primary"]
            .round(4).drop(columns="curve_set").to_dict(orient="records"),
        },
        "anchor_headline_all_curves": {
            "common_a_to_d": p_("all_curves", HEADLINE_ANCHOR_C, "common_a_to_d"),
            "available": p_("all_curves", HEADLINE_ANCHOR_C, "available"),
        },
        "strict_primary": {
            "split_c": STRICT_PRIMARY_SPLIT_C,
            "common_a_to_d": s_("primary", STRICT_PRIMARY_SPLIT_C, "common_a_to_d"),
            "available": s_("primary", STRICT_PRIMARY_SPLIT_C, "available"),
        },
        "strict_all_curves": {"common_a_to_d": s_("all_curves", STRICT_PRIMARY_SPLIT_C, "common_a_to_d")},
        "regime_screened_sensitivity": {
            "rule": f"primary curves whose own quadratic over the grid fits within {REGIME_SCREEN_MULT}x",
            "removed": curves.loc[curves["primary_set"] & ~curves["regime_screen_pass"], ["sample_id", "own_grid_quadratic_mult_rmse"]]
            .round(4).to_dict(orient="records"),
            "geometry": {
                k: g_(k, "primary_regime_screened")
                for k in ["within_polyol_family", "same_iso_across_polyol_families", "all_families_pooled"]
            },
            "anchor_common_a_to_d": p_("primary_regime_screened", HEADLINE_ANCHOR_C, "common_a_to_d"),
            "range_over_anchor_temperatures_common": range_over_anchors("primary_regime_screened", "common_a_to_d"),
            "strict_common_a_to_d": s_("primary_regime_screened", STRICT_PRIMARY_SPLIT_C, "common_a_to_d"),
        },
        "figure": {"file": "external_state_shift_diagnostic.png", "panel_A_B_family": f"polyol family {fam} (primary curves)"},
    }
    with open(out / "summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False, default=float)
    print(json.dumps({k: summary[k] for k in ["data", "sanity", "smoothing"]}, indent=1, default=float))


if __name__ == "__main__":
    main()
