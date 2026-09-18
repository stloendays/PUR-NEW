#!/usr/bin/env python3
"""Measure whether strategy revision improved pre-result decision quality.

The wet-lab outcome is treated as a FIXED measuring instrument, not as a claim under
test: it was completed before any of this, never enters the agent runtime, and is
identical for every strategy version. Everything else is held constant across versions
(candidate lattice, evidence snapshot, model, firewall, measurement), so the only
varying factor is the decision strategy.

For each version it reports, separately:
  * the deterministic-rule-only baseline  (what the rule layer alone would pick)
  * the agent's frozen selections         (what the full pipeline picked)
so that rule-layer and LLM-layer contributions are never conflated.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TRUTH_AC, TRUTH_TK = 14.00444847, 4.11895543

VERSIONS = [
    ("v1", "results/stage1_blind_replay_v1/arm_b_blind", "proximity-reward ranking (baseline)"),
    ("v2", "results/stage1_blind_replay_v2/arm_b_blind", "min-intervention, no coverage gate (truncated)"),
    ("v3", "results/stage1_blind_replay_v3/arm_b_blind", "+ coverage gate, ranking visible"),
    ("v4", "results/stage1_blind_replay_v4/arm_b_blind", "+ ranking withheld (pilot)"),
    ("v3h", "results/stage1_blind_replay_v3h/arm_b_blind", "+ ranking withheld (confirmatory N=10)"),
]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - m), min(1.0, c + m))


def modifier_l1(ac: float, tk: float) -> float:
    return abs(ac - TRUTH_AC) + abs(tk - TRUTH_TK)


def load_lattice() -> dict[str, dict]:
    cs = json.loads((ROOT / "derived" / "stage1_blind_candidate_space_v1.json").read_text(encoding="utf-8"))
    return {c["candidate_id"]: c["formulation_state"] for c in cs["candidates"]}


def collect(arm_dir: Path, lattice: dict[str, dict]) -> dict:
    """Read frozen recommendations directly; never re-derive a decision."""
    named, dists, modes, dets, devs = [], [], [], [], 0
    n_runs = 0
    for run_dir in sorted(d for d in arm_dir.glob("run_[0-9]*") if d.is_dir()):
        recs = sorted(run_dir.rglob("recommendation.json"))
        if not recs:
            n_runs += 1
            modes.append("invalid")
            continue
        n_runs += 1
        rec = json.loads(recs[0].read_text(encoding="utf-8"))
        modes.append(rec["decision_mode"])
        sel = rec.get("selected_candidate") or {}
        cid = sel.get("candidate_id")

        delib_paths = sorted(run_dir.rglob("deliberation.json"))
        det_rank1 = None
        if delib_paths:
            delib = json.loads(delib_paths[0].read_text(encoding="utf-8"))
            rankings = (delib.get("deterministic_decision_diagnostics") or {}).get("scenario_rankings") or {}
            order = rankings.get("performance_mitigation") or rankings.get("hypothesis_test_first") or []
            det_rank1 = order[0] if order else None
        if det_rank1:
            dets.append(det_rank1)

        if cid:
            fs = sel.get("formulation_state") or lattice.get(cid, {})
            ac = float(fs.get("AC1920") or 0.0)
            tk = float(fs.get("TK100") or 0.0)
            named.append((cid, ac, tk))
            dists.append(modifier_l1(ac, tk))
            if det_rank1 and cid != det_rank1:
                devs += 1

    det_mode = max(set(dets), key=dets.count) if dets else None
    det_dist = None
    if det_mode and det_mode in lattice:
        det_dist = modifier_l1(
            float(lattice[det_mode].get("AC1920") or 0.0),
            float(lattice[det_mode].get("TK100") or 0.0),
        )
    dual = sum(1 for _c, ac, tk in named if ac > 0 and tk > 0)
    near = sum(1 for d in dists if d <= 7.5)
    return {
        "n_runs": n_runs,
        "n_named": len(named),
        "n_abstain": sum(1 for m in modes if m == "abstain"),
        "n_invalid": sum(1 for m in modes if m == "invalid"),
        "selections": named,
        "dists": dists,
        "dual": dual,
        "near": near,
        "deterministic_rank1": det_mode,
        "deterministic_dist": det_dist,
        "deviated_from_deterministic": devs,
    }


def main() -> None:
    lattice = load_lattice()
    print(f"Fixed measuring instrument: wet-lab F1, normalized AC {TRUTH_AC:.4f} / TK {TRUTH_TK:.4f} wt%")
    print("Held constant across versions: 73-node lattice, evidence snapshot, model, firewall, metric.\n")

    rows = []
    for tag, rel, desc in VERSIONS:
        arm = ROOT / rel
        if not arm.exists():
            continue
        r = collect(arm, lattice)
        rows.append((tag, desc, r))

    hdr = f"{'ver':5s} {'N':>3s} {'named':>6s} {'abst':>5s} {'dual-axis':>10s} {'near':>6s} {'agent L1 mean':>14s} {'rule L1':>8s} {'agent-rule':>11s} {'dev':>5s}"
    print(hdr)
    print("-" * len(hdr))
    for tag, _desc, r in rows:
        am = sum(r["dists"]) / len(r["dists"]) if r["dists"] else None
        rl = r["deterministic_dist"]
        delta = (rl - am) if (am is not None and rl is not None) else None
        print(
            f"{tag:5s} {r['n_runs']:>3d} {r['n_named']:>6d} {r['n_abstain']:>5d} "
            f"{r['dual']:>4d}/{max(r['n_named'],1):<5d} {r['near']:>3d}/{max(r['n_named'],1):<2d} "
            f"{(f'{am:.3f}' if am is not None else '-'):>14s} {(f'{rl:.3f}' if rl is not None else '-'):>8s} "
            f"{(f'{delta:+.3f}' if delta is not None else '-'):>11s} {r['deviated_from_deterministic']:>3d}/{r['n_named']:<2d}"
        )

    print("\nSelection detail:")
    for tag, _desc, r in rows:
        counts: dict[str, int] = {}
        for cid, ac, tk in r["selections"]:
            counts[f"{cid} (AC {ac:g} / TK {tk:g})"] = counts.get(f"{cid} (AC {ac:g} / TK {tk:g})", 0) + 1
        detail = ", ".join(f"{k} x{v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])) or "none named"
        print(f"  {tag:5s} {detail}")

    print("\nDual-axis recovery among named runs (95% Wilson):")
    for tag, _desc, r in rows:
        if r["n_named"]:
            lo, hi = wilson(r["dual"], r["n_named"])
            print(f"  {tag:5s} {r['dual']}/{r['n_named']}  [{lo:.2f}, {hi:.2f}]")

    # Attribution of the total improvement, rule layer vs agent layer.
    first = rows[0][2]
    best = min((r for _t, _d, r in rows if r["dists"]), key=lambda r: sum(r["dists"]) / len(r["dists"]))
    base_rule = first["deterministic_dist"]
    best_rule = best["deterministic_dist"]
    best_agent = sum(best["dists"]) / len(best["dists"])
    if None not in (base_rule, best_rule):
        total = base_rule - best_agent
        rule_part = base_rule - best_rule
        agent_part = best_rule - best_agent
        print("\nImprovement attribution (modifier-plane L1, pct points):")
        print(f"  v1 rule-only baseline        {base_rule:7.3f}")
        print(f"  best rule-only baseline      {best_rule:7.3f}   rule layer contributed {rule_part:+.3f}")
        print(f"  best agent mean              {best_agent:7.3f}   agent layer contributed {agent_part:+.3f}")
        print(f"  total closed                 {total:7.3f}   -> rule {100*rule_part/total:.1f}% / agent {100*agent_part/total:.1f}%")
        print(f"  lattice floor (nearest node) {modifier_l1(15.0, 5.0):7.3f}   <- hard bound, truth is not a node")


if __name__ == "__main__":
    main()
