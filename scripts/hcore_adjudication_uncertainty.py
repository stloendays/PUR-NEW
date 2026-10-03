#!/usr/bin/env python3
"""Propagate measurement uncertainty into the registered H-CORE adjudication.

Section 2.9 compares the observed mean absolute 15-60 min drift of the resin-modified
validation formulation (two 120 C hold repeats) with the H-CORE proportional-dilution
prediction f_reactive x D_E1 = 0.819 x 9.51% = 7.79% and with the registered H-RESIN
support threshold (half of that prediction, 3.89%). Both D_E1 and the two validation
drifts are single hold trajectories, so this script asks how often H-CORE could produce
the observed result once the repeatability of a hold-drift measurement is propagated.

Uncertainty sources
- hold-drift repeatability: (i) point-level scatter of ln(eta) about a straight line in
  time within every measured hold trajectory (E1, E5, both validation repeats), which
  gives sigma_point and therefore sigma_drift = sqrt(2) sigma_point for a two-point
  15->60 min drift; (ii) the between-repeat spread of the two validation drifts, which
  also contains preparation-to-preparation variation. The larger of the two is the
  primary drift sigma; the estimate's own uncertainty is propagated by drawing sigma
  from its scaled-inverse-chi-square posterior.
- the single E1 reference drift that defines H-CORE;
- the reactive mass fraction of the validation formulation (source-reported parts).

Outputs go to analysis/results/upgrades_20261003/hcore_uncertainty/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
HOLD = ROOT / "data" / "thermal_hold.csv"
FORM = ROOT / "data" / "formulations.csv"
OUT = ROOT / "analysis" / "results" / "upgrades_20261003" / "hcore_uncertainty"
SEED = 20261003
N_MC = 1_000_000


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def log_drift(curve: pd.DataFrame, t0: float = 15, t1: float = 60) -> float:
    v = curve.set_index("time_min")["viscosity_reported"]
    return float(np.log(v[t1] / v[t0]))


def pct(d: np.ndarray | float) -> np.ndarray | float:
    return 100.0 * (np.exp(d) - 1.0)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    hold = pd.read_csv(HOLD)
    form = pd.read_csv(FORM).set_index("formulation_id")

    curves = {f"{f}:{r}": g.sort_values("time_min") for (f, r), g in hold.groupby(["formulation_id", "run_label"])}

    # Point-level scatter: residuals of ln(eta) about a per-curve straight line in time.
    resid, dof = [], 0
    rows = []
    for key, g in curves.items():
        t = g["time_min"].to_numpy(float)
        y = np.log(g["viscosity_reported"].to_numpy(float))
        coef = np.polyfit(t, y, 1)
        r = y - np.polyval(coef, t)
        resid.extend(r)
        dof += len(t) - 2
        rows.append({"curve": key, "n_points": len(t), "slope_per_h": coef[0] * 60,
                     "resid_sd_ln": float(np.sqrt((r ** 2).sum() / (len(t) - 2))),
                     "drift_15_60_pct": float(pct(log_drift(g)))})
    s_point = float(np.sqrt(np.sum(np.square(resid)) / dof))
    s_drift_point = np.sqrt(2.0) * s_point

    d_f1 = np.array([log_drift(curves["F1:repeat_1"]), log_drift(curves["F1:repeat_2"])])
    s_drift_rep = float(np.std(d_f1, ddof=1))  # 1 degree of freedom
    d_e1 = log_drift(curves["E1:R01"])

    f1 = form.loc["F1"]
    reactive = f1["ppg2000"] + f1["pdp70"] + f1["mdi"]
    total = reactive + f1["ac1920"] + f1["tk100"]
    f_react = float(reactive / total)

    obs_mean_abs = float(np.mean(np.abs(pct(d_f1))))
    pred_core = float(f_react * pct(d_e1))
    threshold = pred_core / 2.0

    # Primary sigma: the larger (more conservative) of the two estimates, with its own
    # sampling uncertainty (scaled-inverse-chi-square with the matching degrees of freedom).
    if s_drift_rep >= s_drift_point:
        sigma_hat, sigma_dof, sigma_source = s_drift_rep, 1, "between-repeat spread of the two validation drifts"
    else:
        sigma_hat, sigma_dof, sigma_source = s_drift_point, dof, "within-trajectory point scatter (sqrt 2 x)"

    def simulate(sigma_draws: np.ndarray, f_draws: np.ndarray) -> dict:
        # True E1 reference drift given its single measurement, then the H-CORE truth for F1.
        d_e1_true = d_e1 + sigma_draws * rng.standard_normal(sigma_draws.size)
        drift_core_true_pct = f_draws * pct(d_e1_true)
        d_core_true = np.log1p(drift_core_true_pct / 100.0)
        # Two independent validation repeats measured under H-CORE.
        reps = d_core_true[:, None] + sigma_draws[:, None] * rng.standard_normal((sigma_draws.size, 2))
        stat = np.mean(np.abs(pct(reps)), axis=1)
        # The registered criterion is evaluated against the H-CORE prediction computed from
        # the MEASURED E1 drift, exactly as in the manuscript.
        return {
            "p_mean_abs_le_observed": float(np.mean(stat <= obs_mean_abs)),
            "p_registered_support_under_hcore": float(np.mean(stat < threshold)),
            "hcore_true_drift_pct_median": float(np.median(drift_core_true_pct)),
            "hcore_true_drift_pct_95": [float(x) for x in np.percentile(drift_core_true_pct, [2.5, 97.5])],
            "stat_under_hcore_pct_95": [float(x) for x in np.percentile(stat, [2.5, 97.5])],
        }

    f_draws_nominal = np.full(N_MC, f_react)
    f_draws_uncertain = rng.uniform(f_react - 0.03, f_react + 0.03, N_MC)

    scenarios = []

    def add(name: str, sigma_draws: np.ndarray, f_draws: np.ndarray, note: str) -> None:
        res = simulate(sigma_draws, f_draws)
        res.update({"scenario": name, "sigma_median_ln": float(np.median(sigma_draws)), "note": note})
        scenarios.append(res)

    fixed = lambda s: np.full(N_MC, s)
    # Posterior draws of sigma: sigma^2 = dof * s^2 / chi2_dof.
    post = lambda s, k: np.sqrt(k * s ** 2 / rng.chisquare(k, N_MC))

    add("primary", post(sigma_hat, sigma_dof), f_draws_uncertain,
        f"sigma from {sigma_source}; its uncertainty propagated (dof={sigma_dof}); reactive fraction +/-0.03")
    add("sigma_point_fixed", fixed(s_drift_point), f_draws_nominal, "within-trajectory scatter only, fixed")
    add("sigma_rep_fixed", fixed(s_drift_rep), f_draws_nominal, "between-repeat spread only, fixed")
    for k in (2, 3):
        add(f"sigma_rep_x{k}", fixed(k * s_drift_rep), f_draws_uncertain, f"between-repeat spread inflated {k}x")

    # Smallest sigma multiple at which H-CORE reproduces the observation 5% of the time.
    grid = np.linspace(1, 8, 141)
    p_grid = []
    for m in grid:
        p_grid.append(simulate(fixed(m * s_drift_rep)[:200_000], f_draws_nominal[:200_000])["p_mean_abs_le_observed"])
    p_grid = np.array(p_grid)
    breakeven = float(grid[np.argmax(p_grid >= 0.05)]) if np.any(p_grid >= 0.05) else None

    summary = {
        "seed": SEED,
        "n_monte_carlo": N_MC,
        "inputs_sha256": {"data/thermal_hold.csv": sha256(HOLD), "data/formulations.csv": sha256(FORM)},
        "reactive_mass_fraction": f_react,
        "e1_drift_15_60_pct": float(pct(d_e1)),
        "hcore_prediction_pct": pred_core,
        "hresin_support_threshold_pct": threshold,
        "validation_drifts_pct": [float(x) for x in pct(d_f1)],
        "observed_mean_abs_drift_pct": obs_mean_abs,
        "sigma_point_ln": s_point,
        "sigma_point_dof": dof,
        "sigma_drift_from_point_scatter_ln": s_drift_point,
        "sigma_drift_from_validation_repeats_ln": s_drift_rep,
        "primary_sigma_source": sigma_source,
        "scenarios": scenarios,
        "sigma_multiple_needed_for_p_0_05": breakeven,
        "outcome_blindness_note": "The H-CORE prediction and the registered threshold are computed exactly as registered "
                                  "(E1 reference drift x source-reported reactive fraction); the validation drifts enter only "
                                  "as the observed statistic and, conservatively, as one estimate of hold-drift repeatability.",
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT / "hold_trajectory_scatter.csv", index=False)
    pd.DataFrame(scenarios).to_csv(OUT / "hcore_scenarios.csv", index=False)
    pd.DataFrame({"sigma_multiple_of_repeat_spread": grid, "p_mean_abs_le_observed": p_grid}).to_csv(
        OUT / "hcore_sigma_breakeven.csv", index=False)
    print(json.dumps({k: summary[k] for k in ("hcore_prediction_pct", "hresin_support_threshold_pct",
                                              "observed_mean_abs_drift_pct", "sigma_drift_from_point_scatter_ln",
                                              "sigma_drift_from_validation_repeats_ln", "sigma_multiple_needed_for_p_0_05")}, indent=1))
    for s in scenarios:
        print(s["scenario"], round(s["p_mean_abs_le_observed"], 6), round(s["p_registered_support_under_hcore"], 6),
              s["stat_under_hcore_pct_95"])


if __name__ == "__main__":
    main()
