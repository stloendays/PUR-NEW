#!/usr/bin/env python3
"""Pre-result predictions and operating characteristics for the 2026-10-04 follow-up.

Adds two things to experiments/supplementary_20261004/ before any new measurement exists.
It does not change any threshold registered in PLAN.md.

1. Acrylic-only 120 C hold (registered acrylic-only card S1C39: 15 wt% acrylic-like, no
   tackifier-like modifier). Hypothesis-specific predictions come from the frozen registry
   through src/pur_new/voi.predict_drift. The decision statistic is the mean absolute
   15->60 min drift of n independent repeats. The script reports how often each hypothesis
   would be misclassified for n = 2, 3 and 4 repeats.
2. F1 direct 80-130 C sweeps. Under shape transfer, the curve is the E1-E3 shared quadratic
   shape plus a free level plus realization-specific noise. Under a shape change, the apparent
   temperature-response descriptor is shifted by dE. The script reports the probability that
   the registered criteria classify each case correctly: full-curve RMSE <= 1.10x / >= 1.20x,
   one 110 C anchor <= 1.13x / >= 1.20x, and E_eta inside 37.2-46.9 kJ/mol.

Noise models reuse the 2026-10-03 analyses:
- hold-drift repeatability from the within-trajectory point scatter (hcore_uncertainty);
- realization-specific sweep noise from the heteroscedastic hierarchical model
  (log sigma_r ~ N(lambda, omega^2), posterior medians and spread).

Outputs: experiments/supplementary_20261004/preregistration_addendum.json and
analysis/results/upgrades_20261003/preregistration_addendum/ (tables + RESULTS.md).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from pur_new.voi import load_hypothesis_registry, predict_drift, reactive_mass_fraction  # noqa: E402

SEED = 20261004
N_MC = 400_000
R_GAS = 8.314462618
TREF = 393.15
TEMPS_C = np.array([80, 90, 100, 110, 120, 130], dtype=float)
OUT_A = ROOT / "analysis" / "results" / "upgrades_20261003" / "preregistration_addendum"
OUT_E = ROOT / "experiments" / "supplementary_20261004"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def z(t_c: np.ndarray) -> np.ndarray:
    return 1e3 * (1.0 / (t_c + 273.15) - 1.0 / TREF)


# ---------------------------------------------------------------- acrylic-only hold
def acrylic_only(rng: np.random.Generator) -> dict:
    registry = load_hypothesis_registry()
    ref = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    cands = json.loads((ROOT / "derived" / "stage1_blind_candidate_space_v1.json").read_text(encoding="utf-8"))["candidates"]
    card = next(c for c in cands if c["candidate_id"] == "S1C39")
    phi = reactive_mass_fraction(card)
    preds = {h["hypothesis_id"]: predict_drift(h, card, ref) for h in registry["hypotheses"]}
    threshold = 0.5 * ref * phi  # registered H-RESIN support criterion: below half the dilution prediction

    hold = pd.read_csv(ROOT / "data" / "thermal_hold.csv")
    resid, dof = [], 0
    for _, g in hold.groupby(["formulation_id", "run_label"]):
        t = g["time_min"].to_numpy(float)
        y = np.log(g["viscosity_reported"].to_numpy(float))
        r = y - np.polyval(np.polyfit(t, y, 1), t)
        resid.extend(r)
        dof += len(t) - 2
    s_drift = float(np.sqrt(2.0) * np.sqrt(np.sum(np.square(resid)) / dof))

    def stat_draws(true_factor: float, n_rep: int, e1_repeats: int) -> np.ndarray:
        """Mean absolute drift of n_rep repeats when the true drift is true_factor x phi x D_E1."""
        sigma = np.sqrt(dof * s_drift**2 / rng.chisquare(dof, N_MC))
        # The reference drift is the mean of e1_repeats E1 holds (1 existing + new repeats).
        d_e1_true = np.log1p(ref / 100) + sigma / np.sqrt(e1_repeats) * rng.standard_normal(N_MC)
        true_pct = true_factor * phi * 100 * np.expm1(d_e1_true)
        reps = np.log1p(true_pct / 100)[:, None] + sigma[:, None] * rng.standard_normal((N_MC, n_rep))
        return np.mean(np.abs(100 * np.expm1(reps)), axis=1)

    rows = []
    for n_rep in (2, 3, 4):
        for e1_rep in (1, 3):
            dual = stat_draws(1.0, n_rep, e1_rep)          # H-DUAL (and H-CORE) for this card
            resin_edge = stat_draws(0.5, n_rep, e1_rep)    # H-RESIN at its registered boundary
            resin_like_f1 = stat_draws(1.60 / (ref * 0.8188), n_rep, e1_rep)  # H-RESIN at the F1-observed suppression
            rows.append({
                "n_acrylic_only_repeats": n_rep,
                "n_E1_reference_holds": e1_rep,
                "P_support_HRESIN_given_HDUAL_true": float(np.mean(dual < threshold)),
                "P_support_HRESIN_given_HRESIN_at_F1_suppression": float(np.mean(resin_like_f1 < threshold)),
                "P_support_HRESIN_given_HRESIN_at_boundary": float(np.mean(resin_edge < threshold)),
                "HDUAL_stat_95pct_interval": [float(x) for x in np.percentile(dual, [2.5, 97.5])],
                "HRESIN_F1like_stat_95pct_interval": [float(x) for x in np.percentile(resin_like_f1, [2.5, 97.5])],
            })
    return {
        "card": "S1C39::M-HOLD-120",
        "composition_wt_pct": {k: round(v, 3) for k, v in card["formulation_state"].items() if isinstance(v, float)},
        "reactive_mass_fraction": phi,
        "reference_E1_drift_pct": ref,
        "registered_predictions_pct": preds,
        "decision_threshold_pct": threshold,
        "decision_rule": (
            f"Mean absolute 15->60 min drift of the acrylic-only repeats below {threshold:.2f}% supports H-RESIN and "
            f"falsifies H-DUAL (acrylic alone reaches the low-drift regime). A value at or above {threshold:.2f}% falsifies "
            "H-RESIN's claim that resin modification without the tackifier axis suffices and supports H-DUAL. "
            "If new E1 reference holds are measured, the prediction and threshold are recomputed with the mean E1 drift "
            "using exactly the same formula (threshold = 0.5 x phi_r x mean E1 drift)."
        ),
        "hold_drift_sigma_ln": s_drift,
        "hold_drift_sigma_dof": dof,
        "operating_characteristics": rows,
    }


# ---------------------------------------------------------------- F1 sweep
def f1_sweep(rng: np.random.Generator) -> dict:
    sweeps = pd.read_csv(ROOT / "data" / "temperature_sweeps.csv")
    meta = pd.read_csv(ROOT / "data" / "realization_metadata.csv")
    role_col = "analysis_role" if "analysis_role" in meta.columns else None
    key_cols = [c for c in ("formulation_id", "run_label", "retest_after_1d") if c in meta.columns and c in sweeps.columns]
    prim = meta[meta[role_col].isin(["primary", "primary_with_caveat"])] if role_col else meta
    data = sweeps.merge(prim[key_cols].drop_duplicates(), on=key_cols)
    data = data[data["temperature_c"].isin(TEMPS_C)]
    curves = [g.sort_values("temperature_c") for _, g in data.groupby(key_cols)]
    assert len(curves) == 6 and sum(len(c) for c in curves) == 36, (len(curves), sum(len(c) for c in curves))

    def fit_shape(cs: list[pd.DataFrame]) -> np.ndarray:
        rows, y = [], []
        for i, c in enumerate(cs):
            zz = z(c["temperature_c"].to_numpy(float))
            for zv, v in zip(zz, np.log(c["viscosity_reported"].to_numpy(float))):
                ind = np.zeros(len(cs)); ind[i] = 1
                rows.append(np.r_[ind, zv, zv**2]); y.append(v)
        coef, *_ = np.linalg.lstsq(np.array(rows), np.array(y), rcond=None)
        return coef[-2:]

    beta_hat = fit_shape(curves)
    # Shape uncertainty: realization-level bootstrap of the shared shape.
    boot = np.array([fit_shape([curves[j] for j in rng.integers(0, 6, 6)]) for _ in range(2000)])
    lam_med, lam_sd, omega_med = -3.4313, 0.42, 0.8746  # heteroscedastic posterior (median; lambda 95% CrI -4.24..-2.60)

    zz = z(TEMPS_C)
    inv_t = 1.0 / (TEMPS_C + 273.15)
    g_hat = beta_hat[0] * zz + beta_hat[1] * zz**2
    n = 50_000
    results = []
    for dE in (-15, -10, -5, 0, 5, 10, 15):
        b = boot[rng.integers(0, len(boot), n)]
        g_true = b[:, :1] * zz + b[:, 1:] * zz**2 + (dE * 1e3 / R_GAS) * (inv_t - inv_t.mean())
        sigma = np.exp(rng.normal(lam_med, lam_sd, n) + omega_med * rng.standard_normal(n))
        y = g_true + sigma[:, None] * rng.standard_normal((n, len(zz)))
        # full-curve test: shared shape + free level
        a = np.mean(y - g_hat, axis=1, keepdims=True)
        full = np.exp(np.sqrt(np.mean((y - g_hat - a) ** 2, axis=1)))
        # one 110 C anchor predicting 120 and 130 C
        i110, tgt = 3, [4, 5]
        a1 = y[:, i110] - g_hat[i110]
        anchor = np.exp(np.sqrt(np.mean((y[:, tgt] - (a1[:, None] + g_hat[tgt])) ** 2, axis=1)))
        # apparent E_eta from ln eta vs 1/T
        slope = np.polyfit(inv_t, y.T, 1)[0]
        e_eta = R_GAS * slope / 1e3
        results.append({
            "dE_eta_kJ_mol": dE,
            "P_full_le_1.10": float(np.mean(full <= 1.10)),
            "P_full_ge_1.20": float(np.mean(full >= 1.20)),
            "P_anchor_le_1.13": float(np.mean(anchor <= 1.13)),
            "P_anchor_ge_1.20": float(np.mean(anchor >= 1.20)),
            "P_Eeta_in_37.2_46.9": float(np.mean((e_eta >= 37.2) & (e_eta <= 46.9))),
            "full_rmse_median": float(np.median(full)),
            "E_eta_median": float(np.median(e_eta)),
        })
    return {
        "shared_shape_beta": beta_hat.tolist(),
        "shape_bootstrap_reps": 2000,
        "noise_model": "log sigma_r ~ N(lambda, omega^2); lambda ~ N(-3.43, 0.42^2), omega = 0.87 (heteroscedastic hierarchical posterior)",
        "shape_change_model": "ln eta shifted by (dE/R)(1/T - mean 1/T), i.e. apparent E_eta changed by dE",
        "operating_characteristics": results,
    }


def main() -> None:
    rng = np.random.default_rng(SEED)
    OUT_A.mkdir(parents=True, exist_ok=True)
    acr = acrylic_only(rng)
    f1 = f1_sweep(rng)
    inputs = ["configs/hypothesis_registry.json", "derived/stage1_blind_candidate_space_v1.json",
              "data/thermal_hold.csv", "data/temperature_sweeps.csv", "data/realization_metadata.csv",
              "experiments/supplementary_20261004/PLAN.md", "experiments/supplementary_20261004/preregistered_targets.csv"]
    record = {
        "status": "pre-result addendum: computed before any 2026-10-04 follow-up measurement exists",
        "seed": SEED,
        "n_monte_carlo": N_MC,
        "inputs_sha256": {p: sha256(ROOT / p) for p in inputs},
        "registered_thresholds_unchanged": True,
        "acrylic_only_hold": acr,
        "f1_sweep": f1,
    }
    (OUT_E / "preregistration_addendum.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(acr["operating_characteristics"]).to_csv(OUT_A / "acrylic_only_operating_characteristics.csv", index=False)
    pd.DataFrame(f1["operating_characteristics"]).to_csv(OUT_A / "f1_sweep_operating_characteristics.csv", index=False)
    print(json.dumps({k: acr[k] for k in ("reactive_mass_fraction", "registered_predictions_pct", "decision_threshold_pct", "hold_drift_sigma_ln")}, indent=1))
    print(pd.DataFrame(acr["operating_characteristics"]).drop(columns=["HDUAL_stat_95pct_interval", "HRESIN_F1like_stat_95pct_interval"]).to_string(index=False))
    print(pd.DataFrame(f1["operating_characteristics"]).to_string(index=False))


if __name__ == "__main__":
    main()
