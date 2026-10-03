#!/usr/bin/env python3
"""Bayesian expected information gain (EIG) versus deterministic VOI, and global VOI weight sensitivity.

Task A  Reproduce the 292-card VOI table with the repository's own VOI tool, then compute the
        mutual information between the registered hypothesis variable {H-CORE, H-RESIN, H-DUAL}
        and each card's measurement outcome, and compare it with VOI and with D_hyp.
Task B  Joint random re-weighting of the six VOI weights (Dirichlet and uniform multipliers),
        Sobol first-order / total indices (Saltelli 2010 / Jansen estimators) and single-weight
        break-even multipliers.

Outcome-blind construction: the held-out validation formulation F1 and its measured hold drift are
never read. The only inputs are the registered hypothesis predictions (E1 reference drift), the
measurement catalog, the formulation priors and the outcome-blind 73-node candidate space, i.e. the
same decision-time inputs the VOI tool uses. Every repository file opened during the run is logged
through an audit hook and hashed into summary.json.

Run:  PYTHONPATH=src python scripts/voi_eig_and_global_sensitivity.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OPENED_FILES: set[str] = set()


def _audit(event: str, args: tuple) -> None:  # record every file opened during the run
    if event == "open" and args and isinstance(args[0], (str, bytes, Path)):
        try:
            path = Path(args[0] if not isinstance(args[0], bytes) else args[0].decode()).resolve()
        except Exception:  # noqa: BLE001
            return
        if path.suffix.lower() in {".json", ".csv"}:
            OPENED_FILES.add(str(path))


sys.addaudithook(_audit)
sys.path.insert(0, str(ROOT / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from scipy import stats  # noqa: E402
from scipy.special import ndtr  # noqa: E402
from scipy.stats import qmc  # noqa: E402

from pur_new.evidence_firewall import find_blind_payload_violations  # noqa: E402
from pur_new.voi import (  # noqa: E402
    BASE_WEIGHTS,
    POSITIVE_TERMS,
    RISK_TERMS,
    TIE_EPSILON,
    build_experiment_cards,
    load_hypothesis_registry,
    load_measurement_catalog,
    predict_drift,
    reactive_mass_fraction,
    voi_robustness_sweep,
)

OUT = ROOT / "analysis" / "results" / "upgrades_20261003" / "voi_eig_sensitivity"
CANDIDATE_SET = ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
FROZEN_RANKING = sorted((ROOT / "results" / "agent_v4_voi" / "series_n10").glob("run_*/EXP_*/voi_full_ranking.json"))
EXPECTED_TOP5 = sorted(f"S1C{n}::M-HOLD-120" for n in (41, 46, 51, 56, 61))
BLINDED_IDS = {"F1"}

MASTER_SEED = 20261003
N_WEIGHT_SAMPLES = 100_000
SOBOL_LOG2_N = 14
N_BOOT = 1000
MC_CHECK_N = 400_000

TERMS = list(BASE_WEIGHTS)  # fixed order: hyp, unc, dec, int, ext, proc
SIGN = np.array([1.0 if t in POSITIVE_TERMS else -1.0 for t in TERMS])
W0 = np.array([BASE_WEIGHTS[t] for t in TERMS])
SHORT = {
    "hypothesis_discrimination": "w_hyp",
    "uncertainty_reduction": "w_unc",
    "decision_relevance": "w_dec",
    "measurement_interpretability": "w_int",
    "extrapolation_risk": "w_ext",
    "process_state_risk": "w_proc",
}

# EIG model settings. Primary: uniform prior, point predictions, sigma = declared M-HOLD-120 resolution.
PRIORS = {
    "uniform": {"H-CORE": 1 / 3, "H-RESIN": 1 / 3, "H-DUAL": 1 / 3},
    "core_favoured": {"H-CORE": 0.50, "H-RESIN": 0.25, "H-DUAL": 0.25},
    "modifier_favoured": {"H-CORE": 0.20, "H-RESIN": 0.40, "H-DUAL": 0.40},
    "dual_favoured": {"H-CORE": 0.25, "H-RESIN": 0.25, "H-DUAL": 0.50},
}
SIGMAS = [0.5, 1.0, 2.0, 3.0, 4.0]
ENCODINGS = ["point", "interval"]
PRIMARY = {"prior": "uniform", "sigma": 2.0, "encoding": "point"}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------------------------
# Step 0: reproduce the 292-card VOI table exactly as the agent runner builds it
# --------------------------------------------------------------------------------------------
def reproduce_voi(candidates, registry, catalog) -> tuple[list[dict], dict]:
    cards = build_experiment_cards(candidates, registry=registry, catalog=catalog)  # as scripts/run_agent_v4.py
    best = max(c["voi_score"] for c in cards)
    tied = sorted(c["experiment_id"] for c in cards if abs(c["voi_score"] - best) <= TIE_EPSILON)
    check: dict[str, Any] = {
        "n_cards": len(cards),
        "n_candidates": len(candidates),
        "n_measurements": len(catalog["measurements"]),
        "top_voi": best,
        "tied_top_set": tied,
        "tied_top_set_matches_manuscript": tied == EXPECTED_TOP5,
    }
    mine = {c["experiment_id"]: c for c in cards}
    frozen_checks = []
    for path in FROZEN_RANKING:
        frozen = read_json(path)
        fz = {c["experiment_id"]: c for c in frozen["cards"]}
        same_ids = set(fz) == set(mine)
        score_eq = same_ids and all(fz[k]["voi_score"] == mine[k]["voi_score"] for k in mine)
        comp_eq = same_ids and all(fz[k]["voi_components"] == mine[k]["voi_components"] for k in mine)
        frozen_checks.append(
            {
                "frozen_file": str(path.relative_to(ROOT)).replace("\\", "/"),
                "same_292_ids": same_ids,
                "voi_scores_identical": score_eq,
                "voi_components_identical": comp_eq,
                "weights_identical": frozen.get("weights") == BASE_WEIGHTS,
            }
        )
    check["frozen_ranking_comparisons"] = frozen_checks
    check["all_frozen_rankings_identical"] = bool(frozen_checks) and all(
        r["same_292_ids"] and r["voi_scores_identical"] and r["voi_components_identical"] for r in frozen_checks
    )
    sweep = voi_robustness_sweep(candidates, registry=registry, catalog=catalog)
    check["one_at_a_time_sweep_0p5_1p5"] = {
        "n_scenarios": sweep["n_scenarios"],
        "multipliers": sweep["multipliers"],
        "stability": sweep["stability"],
        "base_margin_to_first_strictly_lower": sweep["base_margin_to_first_strictly_lower"],
    }
    if not check["tied_top_set_matches_manuscript"]:
        raise SystemExit(f"VOI top set not reproduced: {tied}")
    if not check["all_frozen_rankings_identical"]:
        raise SystemExit("reproduced VOI table differs from a frozen series_n10 ranking")
    return cards, check


# --------------------------------------------------------------------------------------------
# Task A: expected information gain about the hypothesis variable
# --------------------------------------------------------------------------------------------
def predictive_specs(card, candidate, registry, catalog_by_id, encoding) -> list[tuple] | None:
    """Per-hypothesis predictive distribution of the card's primary outcome, before noise.

    Returns None when the measurement does not observe the drift coordinate; such cards carry
    zero information about the hypothesis variable under the registry (see RESULTS.md).
    point:    each hypothesis is a point prediction, exactly voi.predict_drift (0.5 x linear for
              the low-drift regime, as coded in the VOI tool from suppression_factor_vs_linear_max).
    interval: the low-drift regime is the registry's support criterion, drift uniformly anywhere
              in [0, 0.5 x linear dilution]; near-linear predictions stay point predictions.
    """
    measurement = catalog_by_id[card["measurement_id"]]
    if "thermal_hold_drift" not in measurement.get("addresses", []):
        return None
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    linear = reference * reactive_mass_fraction(candidate)
    specs = []
    for hyp in registry["hypotheses"]:
        mu = predict_drift(hyp, candidate, reference)
        if encoding == "point" or mu >= linear - 1e-12:
            specs.append(("point", mu))
        else:
            factor = float(
                next(h for h in registry["hypotheses"] if h["hypothesis_id"] == "H-RESIN")[
                    "suppression_factor_vs_linear_max"
                ]
            )
            specs.append(("uniform", 0.0, factor * linear))
    return specs


def _density(spec: tuple, y: np.ndarray, sigma: float) -> np.ndarray:
    if spec[0] == "point":
        return np.exp(-0.5 * ((y - spec[1]) / sigma) ** 2) / (sigma * np.sqrt(2 * np.pi))
    a, b = spec[1], spec[2]
    return (ndtr((y - a) / sigma) - ndtr((y - b) / sigma)) / (b - a)


def mutual_information(specs: list[tuple], prior: np.ndarray, sigma: float) -> float:
    """I(H; Y) in nats by dense trapezoidal quadrature (deterministic)."""
    lo = min(s[1] for s in specs) - 12 * sigma
    hi = max(s[-1] for s in specs) + 12 * sigma
    y = np.linspace(lo, hi, 40001)
    dens = np.vstack([_density(s, y, sigma) for s in specs])
    mix = prior @ dens
    with np.errstate(divide="ignore", invalid="ignore"):
        integrand = np.where(dens > 0, dens * (np.log(dens) - np.log(mix)), 0.0)
    per_h = np.trapezoid(integrand, y, axis=1) if hasattr(np, "trapezoid") else np.trapz(integrand, y, axis=1)
    return float(max(0.0, prior @ per_h))


def mc_mutual_information(specs, prior, sigma, rng, n) -> float:
    h = rng.choice(len(specs), size=n, p=prior)
    y = np.empty(n)
    for i, s in enumerate(specs):
        idx = h == i
        base = s[1] if s[0] == "point" else rng.uniform(s[1], s[2], idx.sum())
        y[idx] = base + rng.normal(0.0, sigma, idx.sum())
    dens = np.vstack([_density(s, y, sigma) for s in specs])
    mix = prior @ dens
    return float(np.mean(np.log(dens[h, np.arange(n)]) - np.log(mix)))


def entropy(p: np.ndarray) -> float:
    p = p[p > 0]
    return float(-(p * np.log(p)).sum())


def compute_eig(cards, cand_by_id, registry, catalog_by_id, prior_name, sigma, encoding) -> np.ndarray:
    hyp_ids = [h["hypothesis_id"] for h in registry["hypotheses"]]
    prior = np.array([PRIORS[prior_name][h] for h in hyp_ids])
    cache: dict[tuple, float] = {}
    out = np.zeros(len(cards))
    for i, card in enumerate(cards):
        specs = predictive_specs(card, cand_by_id[card["candidate_id"]], registry, catalog_by_id, encoding)
        if specs is None:
            continue
        key = tuple(tuple(round(v, 12) if isinstance(v, float) else v for v in s) for s in specs)
        if key not in cache:
            cache[key] = mutual_information(list(specs), prior, sigma)
        out[i] = cache[key]
    return out


def top_set(values: np.ndarray, ids: list[str], tol: float = TIE_EPSILON) -> list[str]:
    best = values.max()
    return sorted(ids[i] for i in np.flatnonzero(values >= best - tol))


def rank_corr(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    rho, p_rho = stats.spearmanr(x, y)
    tau, p_tau = stats.kendalltau(x, y)  # tau-b, tie-corrected
    return {"spearman_rho": float(rho), "spearman_p": float(p_rho), "kendall_tau_b": float(tau), "kendall_p": float(p_tau)}


def eig_analysis(cards, candidates, registry, catalog) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    cand_by_id = {c["candidate_id"]: c for c in candidates}
    catalog_by_id = {m["measurement_id"]: m for m in catalog["measurements"]}
    hyp_ids = [h["hypothesis_id"] for h in registry["hypotheses"]]
    ids = [c["experiment_id"] for c in cards]
    comp = {t: np.array([c["voi_components"][t] for c in cards]) for t in TERMS}
    voi = np.array([c["voi_score"] for c in cards])
    is_hold = np.array([c["measurement_id"] == "M-HOLD-120" for c in cards])
    voi_top = top_set(voi, ids)

    table = pd.DataFrame(
        {
            "experiment_id": ids,
            "candidate_id": [c["candidate_id"] for c in cards],
            "measurement_id": [c["measurement_id"] for c in cards],
            "intervention_family": [c["intervention_family"] for c in cards],
            "acrylic_like_pct": [c["acrylic_like_pct"] for c in cards],
            "minor_tackifier_like_pct": [c["minor_tackifier_like_pct"] for c in cards],
            "reactive_mass_fraction": [c["reactive_mass_fraction"] for c in cards],
            **{f"D_hyp" if t == "hypothesis_discrimination" else t: comp[t] for t in TERMS},
            "voi_score": voi,
            "voi_rank": stats.rankdata(-voi, method="min").astype(int),
            "in_voi_top_set": [i in set(voi_top) for i in ids],
        }
    )
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    for h in registry["hypotheses"]:
        table[f"pred_drift_{h['hypothesis_id']}_pct"] = [
            predict_drift(h, cand_by_id[c["candidate_id"]], reference) if is_hold[i] else np.nan
            for i, c in enumerate(cards)
        ]

    rows = []
    primary_eig = None
    for encoding in ENCODINGS:
        for prior_name in PRIORS:
            prior = np.array([PRIORS[prior_name][h] for h in hyp_ids])
            h_prior = entropy(prior)
            for sigma in SIGMAS:
                eig = compute_eig(cards, cand_by_id, registry, catalog_by_id, prior_name, sigma, encoding)
                eig_n = eig / h_prior
                eig_risk = (
                    BASE_WEIGHTS["hypothesis_discrimination"] * eig_n
                    - BASE_WEIGHTS["extrapolation_risk"] * comp["extrapolation_risk"]
                    - BASE_WEIGHTS["process_state_risk"] * comp["process_state_risk"]
                )
                voi_eig = voi + BASE_WEIGHTS["hypothesis_discrimination"] * (eig_n - comp["hypothesis_discrimination"])
                e_top = top_set(eig, ids, tol=1e-9 * max(1.0, eig.max()))
                er_top = top_set(eig_risk, ids)
                ve_top = top_set(voi_eig, ids)
                row = {
                    "encoding": encoding,
                    "prior": prior_name,
                    "sigma_pct": sigma,
                    "is_primary": (encoding, prior_name, sigma)
                    == (PRIMARY["encoding"], PRIMARY["prior"], PRIMARY["sigma"]),
                    "prior_entropy_nats": h_prior,
                    "eig_max_nats": eig.max(),
                    "eig_max_bits": eig.max() / np.log(2),
                    "eig_top_set": ";".join(e_top),
                    "eig_top_n": len(e_top),
                    "eig_top_overlap_with_voi_top5": len(set(e_top) & set(voi_top)),
                    "eig_top5_by_rank": ";".join(np.array(ids)[np.lexsort((np.array(ids), -eig))][:5]),
                    "eig_rank_of_best_voi_top_card": int(stats.rankdata(-eig, method="min")[ids.index(voi_top[0])]),
                    "n_cards_eig_gt0": int((eig > 1e-12).sum()),
                    "eig_risk_top_set": ";".join(er_top),
                    "eig_risk_top_overlap_with_voi_top5": len(set(er_top) & set(voi_top)),
                    "voi_eig_substituted_top_set": ";".join(ve_top),
                    "voi_eig_substituted_top_overlap_with_voi_top5": len(set(ve_top) & set(voi_top)),
                }
                for label, mask in (("all", np.ones_like(is_hold)), ("hold", is_hold)):
                    for name, other in (("voi", voi), ("dhyp", comp["hypothesis_discrimination"])):
                        rc = rank_corr(eig[mask], other[mask])
                        row[f"eig_vs_{name}_{label}_spearman"] = rc["spearman_rho"]
                        row[f"eig_vs_{name}_{label}_kendall"] = rc["kendall_tau_b"]
                    for name, score in (("eig_risk", eig_risk), ("voi_eig_substituted", voi_eig)):
                        rc = rank_corr(score[mask], voi[mask])
                        row[f"{name}_vs_voi_{label}_spearman"] = rc["spearman_rho"]
                        row[f"{name}_vs_voi_{label}_kendall"] = rc["kendall_tau_b"]
                rows.append(row)
                tag = f"{encoding}_{prior_name}_s{sigma:g}"
                if (encoding, prior_name) == ("point", "uniform") or (encoding, prior_name, sigma) == (
                    "interval",
                    "uniform",
                    PRIMARY["sigma"],
                ):
                    table[f"eig_nats_{tag}"] = eig
                if row["is_primary"]:
                    primary_eig = eig
                    table["eig_nats_primary"] = eig
                    table["eig_bits_primary"] = eig / np.log(2)
                    table["eig_norm_primary"] = eig_n
                    table["eig_rank_primary"] = stats.rankdata(-eig, method="min").astype(int)
                    table["eig_risk_score_primary"] = eig_risk
                    table["voi_with_eig_for_dhyp_primary"] = voi_eig
                    table["in_eig_top_set_primary"] = [i in set(e_top) for i in ids]
    sens = pd.DataFrame(rows)

    # Monte Carlo cross-check of the quadrature for representative cards, fixed seed.
    rng = np.random.default_rng(MASTER_SEED)
    prior = np.array([PRIORS[PRIMARY["prior"]][h] for h in hyp_ids])
    mc = []
    for eid in (voi_top[0], "S1C10::M-HOLD-120", "S1C39::M-HOLD-120"):
        card = cards[ids.index(eid)]
        specs = predictive_specs(card, cand_by_id[card["candidate_id"]], registry, catalog_by_id, "point")
        mc.append(
            {
                "experiment_id": eid,
                "quadrature_nats": mutual_information(specs, prior, PRIMARY["sigma"]),
                "monte_carlo_nats": mc_mutual_information(specs, prior, PRIMARY["sigma"], rng, MC_CHECK_N),
                "monte_carlo_n": MC_CHECK_N,
            }
        )
    prim = sens[sens.is_primary].iloc[0].to_dict()
    return table, sens, {"primary": prim, "voi_top_set": voi_top, "mc_check": mc, "primary_eig": primary_eig}


# --------------------------------------------------------------------------------------------
# Task B: global weight sensitivity
# --------------------------------------------------------------------------------------------
def card_arrays(cards):
    C = np.array([[c["voi_components"][t] for t in TERMS] for c in cards]) * SIGN  # signed components
    ids = [c["experiment_id"] for c in cards]
    is_hold = np.array([c["measurement_id"] == "M-HOLD-120" for c in cards])
    is_dual = np.array([c["intervention_family"] == "dual_axis_resin_modified" for c in cards])
    zero_d = np.array([c["voi_components"]["hypothesis_discrimination"] <= 0 for c in cards])
    nominal = np.array([i in set(EXPECTED_TOP5) for i in ids])
    return C, ids, is_hold, is_dual, zero_d, nominal


def evaluate_weights(W, C, is_hold, is_dual, zero_d, nominal, chunk=20_000):
    n = W.shape[0]
    res = {k: np.zeros(n, dtype=bool) for k in ("top_eq_nominal", "top_all_hold", "top_all_dual", "top_all_dual_hold", "zero_dhyp_in_top")}
    res["n_tied"] = np.zeros(n, dtype=int)
    packed = []
    dual_hold = is_dual & is_hold
    for s in range(0, n, chunk):
        S = W[s : s + chunk] @ C.T
        best = S.max(axis=1, keepdims=True)
        tied = S >= best - TIE_EPSILON
        sl = slice(s, s + chunk)
        res["top_eq_nominal"][sl] = (tied == nominal).all(axis=1)
        res["top_all_hold"][sl] = ~(tied & ~is_hold).any(axis=1)
        res["top_all_dual"][sl] = ~(tied & ~is_dual).any(axis=1)
        res["top_all_dual_hold"][sl] = ~(tied & ~dual_hold).any(axis=1)
        res["zero_dhyp_in_top"][sl] = (tied & zero_d).any(axis=1)
        res["n_tied"][sl] = tied.sum(axis=1)
        packed.append(np.packbits(tied, axis=1))
    return res, np.vstack(packed)


def margin_dual_hold(W, C, is_dual, is_hold):
    S = W @ C.T
    dh = is_dual & is_hold
    return S[:, dh].max(axis=1) - S[:, ~dh].max(axis=1)


def sample_weights(scheme: str, rng: np.random.Generator, n: int) -> np.ndarray:
    if scheme.startswith("dirichlet_k"):
        kappa = float(scheme.split("_k")[1])
        return rng.dirichlet(kappa * W0, size=n)
    if scheme == "dirichlet_flat":
        return rng.dirichlet(np.ones(6), size=n)
    m = rng.uniform(0.5, 1.5, size=(n, 6))
    W = W0 * m
    if scheme == "uniform_mult_renorm":
        W = W / W.sum(axis=1, keepdims=True)
    return W


SCHEMES = ["dirichlet_k100", "dirichlet_k30", "dirichlet_k10", "dirichlet_flat", "uniform_mult_unrenorm", "uniform_mult_renorm"]


def global_sensitivity(cards):
    C, ids, is_hold, is_dual, zero_d, nominal = card_arrays(cards)
    ss = np.random.SeedSequence(MASTER_SEED)
    child = dict(zip(SCHEMES, ss.spawn(len(SCHEMES))))
    rows, topset_rows = [], []
    for scheme in SCHEMES:
        rng = np.random.default_rng(child[scheme])
        W = sample_weights(scheme, rng, N_WEIGHT_SAMPLES)
        res, packed = evaluate_weights(W, C, is_hold, is_dual, zero_d, nominal)
        n = N_WEIGHT_SAMPLES
        row = {"scheme": scheme, "n_samples": n, "seed_entropy": MASTER_SEED, "spawn_key": list(child[scheme].spawn_key)}
        for k in ("top_eq_nominal", "top_all_hold", "top_all_dual", "top_all_dual_hold", "zero_dhyp_in_top"):
            p = res[k].mean()
            row[f"frac_{k}"] = p
            row[f"mc_se_{k}"] = np.sqrt(p * (1 - p) / n)
        row["mean_n_tied_at_top"] = res["n_tied"].mean()
        row["frac_unique_top_card"] = (res["n_tied"] == 1).mean()
        rows.append(row)
        uniq, counts = np.unique(packed, axis=0, return_counts=True)
        order = np.argsort(-counts)
        for rank, j in enumerate(order[:10]):
            mask = np.unpackbits(uniq[j])[: len(ids)].astype(bool)
            members = [ids[i] for i in np.flatnonzero(mask)]
            fams = sorted({cards[i]["intervention_family"] for i in np.flatnonzero(mask)})
            meas = sorted({cards[i]["measurement_id"] for i in np.flatnonzero(mask)})
            topset_rows.append(
                {
                    "scheme": scheme,
                    "rank": rank + 1,
                    "count": int(counts[j]),
                    "fraction": counts[j] / n,
                    "n_cards": len(members),
                    "measurements": ";".join(meas),
                    "families": ";".join(fams),
                    "top_set": ";".join(members),
                }
            )
    return pd.DataFrame(rows), pd.DataFrame(topset_rows)


def sobol_indices(cards, lo=0.5, hi=1.5, seed_offset=1):
    C, ids, is_hold, is_dual, zero_d, nominal = card_arrays(cards)
    d = 6
    N = 2**SOBOL_LOG2_N
    sampler = qmc.Sobol(d=2 * d, scramble=True, seed=MASTER_SEED + seed_offset)
    X = qmc.scale(sampler.random_base2(SOBOL_LOG2_N), [lo] * (2 * d), [hi] * (2 * d))
    A, B = X[:, :d], X[:, d:]

    def f(M):
        m = margin_dual_hold(W0 * M, C, is_dual, is_hold)
        return {"margin": m, "indicator_top_is_dual_hold": (m > TIE_EPSILON).astype(float)}

    fA, fB = f(A), f(B)
    fAB = []
    for i in range(d):
        ABi = A.copy()
        ABi[:, i] = B[:, i]
        fAB.append(f(ABi))
    rng = np.random.default_rng(MASTER_SEED + seed_offset + 1)
    boot_idx = rng.integers(0, N, size=(N_BOOT, N))
    rows = []
    out_stats = {}
    for out in ("margin", "indicator_top_is_dual_hold"):
        ya, yb = fA[out], fB[out]
        yab = np.vstack([fAB[i][out] for i in range(d)])  # d x N

        def est(idx):
            a, b, ab = ya[idx], yb[idx], yab[:, idx]
            V = np.var(np.concatenate([a, b]), ddof=1)
            if V <= 0:
                return np.full(d, np.nan), np.full(d, np.nan)
            S1 = np.mean(b * (ab - a), axis=1) / V  # Saltelli 2010
            ST = 0.5 * np.mean((a - ab) ** 2, axis=1) / V  # Jansen 1999
            return S1, ST

        S1, ST = est(np.arange(N))
        bs = [est(ix) for ix in boot_idx]
        S1b = np.array([b[0] for b in bs])
        STb = np.array([b[1] for b in bs])
        allv = np.concatenate([ya, yb, yab.ravel()])
        out_stats[out] = {
            "mean": float(allv.mean()),
            "variance": float(np.var(np.concatenate([ya, yb]), ddof=1)),
            "min": float(allv.min()),
            "max": float(allv.max()),
            "frac_positive_or_one": float((allv > TIE_EPSILON).mean()),
            "n_model_evaluations": int(allv.size),
        }
        for i, t in enumerate(TERMS):
            rows.append(
                {
                    "multiplier_range": f"U({lo:g},{hi:g})",
                    "output": out,
                    "weight": SHORT[t],
                    "term": t,
                    "S1": S1[i],
                    "S1_ci_low": np.nanpercentile(S1b[:, i], 2.5) if np.isfinite(S1[i]) else np.nan,
                    "S1_ci_high": np.nanpercentile(S1b[:, i], 97.5) if np.isfinite(S1[i]) else np.nan,
                    "ST": ST[i],
                    "ST_ci_low": np.nanpercentile(STb[:, i], 2.5) if np.isfinite(ST[i]) else np.nan,
                    "ST_ci_high": np.nanpercentile(STb[:, i], 97.5) if np.isfinite(ST[i]) else np.nan,
                }
            )
    return pd.DataFrame(rows), {
        "multiplier_range": [lo, hi],
        "N_base": N,
        "d": d,
        "n_boot": N_BOOT,
        "sampler": f"scrambled Sobol (scipy.stats.qmc), seed MASTER_SEED+{seed_offset}; bootstrap seed MASTER_SEED+{seed_offset + 1}",
        "estimators": "first order: Saltelli et al. 2010; total: Jansen 1999",
        "outputs": out_stats,
    }


def break_even(cards):
    """Single-weight multiplier (others nominal, no renormalisation) at which each event first occurs."""
    C, ids, is_hold, is_dual, zero_d, nominal = card_arrays(cards)
    dual_hold = is_dual & is_hold

    def state(m, k):
        w = W0.copy()
        w[k] *= m
        S = C @ w
        tied = S >= S.max() - TIE_EPSILON
        return {
            "top_set_changes": not np.array_equal(tied, nominal),
            "intervention_family_leaves_dual": bool((tied & ~is_dual).any()),
            "dual_hold_family_breaks": bool((tied & ~dual_hold).any()),
            "measurement_leaves_hold": bool((tied & ~is_hold).any()),
            "zero_dhyp_enters_top": bool((tied & zero_d).any()),
            "tied": tied,
        }

    def search(k, event, direction):
        grid = np.arange(1.0, 20.0 + 1e-9, 1e-3) if direction > 0 else np.arange(1.0, -1e-9, -1e-3)
        prev = 1.0
        for m in grid[1:]:
            if state(m, k)[event]:
                lo, hi = prev, m  # event false at lo, true at hi
                for _ in range(40):
                    mid = 0.5 * (lo + hi)
                    if state(mid, k)[event]:
                        hi = mid
                    else:
                        lo = mid
                st = state(hi, k)
                new_top = [ids[i] for i in np.flatnonzero(st["tied"])]
                return hi, new_top
            prev = m
        return None, None

    rows = []
    for k, t in enumerate(TERMS):
        for event in ("top_set_changes", "intervention_family_leaves_dual", "dual_hold_family_breaks", "measurement_leaves_hold", "zero_dhyp_enters_top"):
            for direction, label in ((-1, "decrease"), (1, "increase")):
                m, top = search(k, event, direction)
                rows.append(
                    {
                        "weight": SHORT[t],
                        "term": t,
                        "event": event,
                        "direction": label,
                        "break_even_multiplier": None if m is None else round(m, 6),
                        "searched_range": "[0, 1)" if direction < 0 else "(1, 20]",
                        "top_set_just_past_break_even": None if top is None else ";".join(top[:8]) + (" ..." if top and len(top) > 8 else ""),
                        "n_top_just_past_break_even": None if top is None else len(top),
                    }
                )
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------------------------
# Figure
# --------------------------------------------------------------------------------------------
def make_figure(table, gs_df, sobol_df, path):
    plt.rcParams.update({"font.size": 11, "axes.labelcolor": "#111111", "xtick.color": "#111111", "ytick.color": "#111111"})
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.4), gridspec_kw={"width_ratios": [1.15, 1.2, 1.0]})
    colours = {"M-HOLD-120": "#c0392b", "M-REPEAT": "#2471a3", "M-ANCHOR": "#7d3c98", "M-SWEEP": "#1e8449"}
    ax = axes[0]
    rng = np.random.default_rng(0)
    for mid, col in colours.items():
        sub = table[table.measurement_id == mid]
        jitter = rng.uniform(-0.004, 0.004, len(sub)) if mid != "M-HOLD-120" else 0
        ax.scatter(sub.voi_score, sub.eig_bits_primary + jitter, s=22, c=col, alpha=0.8, label=mid, edgecolors="none")
    top = table[table.in_voi_top_set]
    ax.scatter(top.voi_score, top.eig_bits_primary, s=140, facecolors="none", edgecolors="#117a65", linewidths=2, label="VOI tied top 5")
    etop = table[table.in_eig_top_set_primary]
    ax.scatter(etop.voi_score, etop.eig_bits_primary, s=120, marker="x", c="#111111", linewidths=2, label="EIG top set")
    ax.set_xlabel("Deterministic VOI")
    ax.set_ylabel("EIG about {H-CORE, H-RESIN, H-DUAL} (bits)")
    ax.set_title("A  EIG vs VOI (uniform prior, σ = 2.0%)", loc="left", fontweight="bold")
    ax.legend(fontsize=9, loc="center left", frameon=True)

    ax = axes[1]
    labels = {
        "dirichlet_k100": "Dir κ=100",
        "dirichlet_k30": "Dir κ=30",
        "dirichlet_k10": "Dir κ=10",
        "dirichlet_flat": "Dir flat",
        "uniform_mult_unrenorm": "U(0.5,1.5)",
        "uniform_mult_renorm": "U(0.5,1.5) renorm",
    }
    metrics = [("frac_top_eq_nominal", "same five-card top set", "#117a65"), ("frac_top_all_hold", "top = 120 °C hold", "#c0392b"), ("frac_top_all_dual", "top = dual-axis family", "#2471a3")]
    x = np.arange(len(gs_df))
    width = 0.26
    for j, (col, lab, c) in enumerate(metrics):
        ax.bar(x + (j - 1) * width, gs_df[col], width, label=lab, color=c, edgecolor="#111111", linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([labels[s] for s in gs_df.scheme], rotation=30, ha="right")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Fraction of 100,000 weight samples")
    ax.set_title("B  Joint weight sampling", loc="left", fontweight="bold")
    ax.legend(fontsize=9, loc="lower left", frameon=True)

    ax = axes[2]
    series = [
        ("U(0.5,1.5)", "margin", "multipliers 0.5–1.5×", "#1f618d", 0.2),
        ("U(0.1,3)", "margin", "multipliers 0.1–3× (suppl.)", "#5dade2", -0.2),
    ]
    for rng_label, out, lab, col, off in series:
        sub = sobol_df[(sobol_df.multiplier_range == rng_label) & (sobol_df.output == out)]
        if sub.ST.isna().all():
            continue
        y = np.arange(len(sub))
        err = np.vstack([sub.ST - sub.ST_ci_low, sub.ST_ci_high - sub.ST]).clip(min=0)
        ax.barh(y + off, sub.ST, 0.38, xerr=err, color=col, edgecolor="#111111", linewidth=0.6, label=lab, capsize=3)
    ax.set_yticks(np.arange(6))
    ax.set_yticklabels([SHORT[t] for t in TERMS])
    ax.invert_yaxis()
    ax.set_xlabel("Sobol total index S_T of the VOI margin\n(best dual-axis hold minus best other card)")
    ax.set_title("C  Sobol total indices", loc="left", fontweight="bold")
    ax.legend(fontsize=9, loc="lower right", frameon=True)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


# --------------------------------------------------------------------------------------------
def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    candidate_set = read_json(CANDIDATE_SET)
    candidates = candidate_set["candidates"]

    # Outcome-blind guard on every structure this script reads directly.
    violations = find_blind_payload_violations(
        {"registry": registry, "catalog": catalog, "candidates": candidate_set}, blinded_formulation_ids=BLINDED_IDS
    )
    if violations:
        raise SystemExit(f"blind leakage in inputs: {violations[:5]}")

    cards, repro = reproduce_voi(candidates, registry, catalog)
    print(f"[0] reproduced {repro['n_cards']} cards; top set = {repro['tied_top_set']}; frozen identical = {repro['all_frozen_rankings_identical']}")

    table, eig_sens, eig_info = eig_analysis(cards, candidates, registry, catalog)
    table.to_csv(OUT / "voi_eig_card_table.csv", index=False)
    eig_sens.to_csv(OUT / "eig_sensitivity.csv", index=False)
    print("[A] primary EIG top set:", eig_info["primary"]["eig_top_set"])

    gs_df, topsets = global_sensitivity(cards)
    gs_df.to_csv(OUT / "weight_sampling_summary.csv", index=False)
    topsets.to_csv(OUT / "weight_sampling_top_sets.csv", index=False)
    print("[B] weight sampling done")
    sobol_main, meta_main = sobol_indices(cards, 0.5, 1.5, seed_offset=1)
    sobol_wide, meta_wide = sobol_indices(cards, 0.1, 3.0, seed_offset=3)
    sobol_df = pd.concat([sobol_main, sobol_wide], ignore_index=True)
    sobol_meta = {"primary_0p5_1p5": meta_main, "supplementary_0p1_3p0": meta_wide}
    sobol_df.to_csv(OUT / "sobol_indices.csv", index=False)
    be = break_even(cards)
    be.to_csv(OUT / "break_even_multipliers.csv", index=False)
    print("[B] sobol + break-even done")

    make_figure(table, gs_df, sobol_df, OUT / "voi_eig_sensitivity_diagnostic.png")

    # Hash every repository data/config file opened (by this script or by the VOI tool it calls).
    inputs = {}
    for p in sorted(OPENED_FILES):
        path = Path(p)
        try:
            rel = path.relative_to(ROOT)
        except ValueError:
            continue
        if rel.parts[0] in {"configs", "derived", "data", "results"}:
            inputs[str(rel).replace("\\", "/")] = sha256_file(path)
    code = {
        str(p.relative_to(ROOT)).replace("\\", "/"): sha256_file(p)
        for p in [Path(__file__).resolve(), *sorted((ROOT / "src" / "pur_new").glob("*.py"))]
    }
    forbidden_read = [k for k in inputs if "follow_up" in k.lower() or "adjudication" in k.lower()]

    prim = eig_info["primary"]
    bfam = be[be.event.isin(["intervention_family_leaves_dual", "dual_hold_family_breaks"]) & be.break_even_multiplier.notna()]
    summary = {
        "script": "scripts/voi_eig_and_global_sensitivity.py",
        "outcome_blind": {
            "statement": (
                "F1 composition and its measured hold drift are not read. Inputs: hypothesis registry (E1 "
                "reference drift 9.51%), measurement catalog, formulation priors, outcome-blind candidate "
                "space; frozen VOI rankings are read only to verify reproduction."
            ),
            "blinded_formulation_ids": sorted(BLINDED_IDS),
            "structural_leakage_findings": violations,
            "opened_files_matching_follow_up_or_adjudication": forbidden_read,
            "note_on_data_thermal_hold_csv": (
                "opened by the repository VOI tool only if listed in input_sha256; the tool loads hold rows with include_follow_up=False"
            ),
        },
        "seeds": {"master_seed": MASTER_SEED, "sobol_seed": MASTER_SEED + 1, "bootstrap_seed": MASTER_SEED + 2, "mc_check_seed": MASTER_SEED},
        "sample_sizes": {
            "weight_samples_per_scheme": N_WEIGHT_SAMPLES,
            "schemes": SCHEMES,
            "sobol_base_N": 2**SOBOL_LOG2_N,
            "sobol_model_evaluations": (6 + 2) * 2**SOBOL_LOG2_N,
            "bootstrap_replicates": N_BOOT,
            "eig_quadrature_points": 40001,
            "eig_mc_check_n": MC_CHECK_N,
        },
        "input_sha256": inputs,
        "code_sha256": code,
        "reproduction": repro,
        "eig": {
            "primary_setting": PRIMARY,
            "noise_basis": "sigma = M-HOLD-120 discrimination_threshold_pct (2.0%) read as one SD of the reported matched-window drift; swept 0.5-4.0%",
            "prediction_encoding": {
                "point": "voi.predict_drift: H-CORE = 9.51*phi_r; H-RESIN = 0.5*that if any modifier; H-DUAL = 0.5*that if tackifier > 0 else 9.51*phi_r",
                "interval": "low-drift regime = Uniform[0, 0.5*9.51*phi_r] (registry support criterion) convolved with N(0, sigma^2)",
            },
            "non_hold_cards": "EIG = 0: M-REPEAT, M-ANCHOR, M-SWEEP do not address thermal_hold_drift in the catalog and the registry makes no differential prediction for them",
            "primary": {k: (v.item() if hasattr(v, "item") else v) for k, v in prim.items()},
            "mc_check": eig_info["mc_check"],
            "settings_with_eig_top_overlapping_voi_top5": int((eig_sens.eig_top_overlap_with_voi_top5 > 0).sum()),
            "n_settings": int(len(eig_sens)),
            "eig_risk_top_overlap_range": [int(eig_sens.eig_risk_top_overlap_with_voi_top5.min()), int(eig_sens.eig_risk_top_overlap_with_voi_top5.max())],
            "voi_eig_substituted_top_overlap_range": [
                int(eig_sens.voi_eig_substituted_top_overlap_with_voi_top5.min()),
                int(eig_sens.voi_eig_substituted_top_overlap_with_voi_top5.max()),
            ],
        },
        "weight_sampling": gs_df.drop(columns=["spawn_key"]).to_dict(orient="records"),
        "sobol": {"meta": sobol_meta, "indices": sobol_df.to_dict(orient="records")},
        "break_even_events_found": be[be.break_even_multiplier.notna()].to_dict(orient="records"),
        "break_even_family_flip": bfam.to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=lambda o: o.item() if hasattr(o, "item") else str(o)) + "\n", encoding="utf-8")
    print(json.dumps({"inputs": inputs, "weight_sampling": gs_df[["scheme", "frac_top_eq_nominal", "frac_top_all_hold", "frac_top_all_dual", "frac_zero_dhyp_in_top"]].to_dict(orient="records")}, indent=1))


if __name__ == "__main__":
    main()
