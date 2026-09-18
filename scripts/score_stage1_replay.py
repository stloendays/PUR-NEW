#!/usr/bin/env python3
"""Score the Stage-1 pre-result replay.

Two strictly ordered subcommands:

    summarize   reads only the frozen recommendations, emits frozen_recommendations.csv
                and blind_summary.json, and writes the BLIND PHASE CLOSED record.
                It must never touch the held-out truth.

    adjudicate  refuses to run until the closure record exists, then loads the
                held-out wet-lab truth and scores Levels 1-3.

All scoring rules are fixed in docs/STAGE1_BLIND_REPLAY_PROTOCOL.md before any run
and are not adjusted afterwards.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import selection_entropy  # noqa: E402

COMPONENTS = ["PPG2000", "PDP70", "AC1920", "TK100", "MDI"]
CLOSURE_FILENAME = "BLIND_PHASE_CLOSED.json"

# --- Level-1 classifier (transparent, fixed before unblinding) ----------------
# A recovery requires time-dependence at constant temperature, not merely any
# mention of temperature or viscosity.
HOLD_PATTERNS = [
    r"\bhold\b", r"isotherm", r"\bdrift\b", r"time[-\s]dependent",
    r"\bover time\b", r"viscosity (?:rise|build[-\s]?up|build|growth|increase)",
    r"\bSI[_\s]?15", r"stability index", r"thermal[-\s]stability",
]
TEMP_RESPONSE_PATTERNS = [r"temperature (?:response|sensitivity|dependence)", r"activation energy", r"E_eta"]
VISCOSITY_LEVEL_PATTERNS = [r"absolute viscosity", r"viscosity level", r"static viscosity"]
STATE_PATTERNS = [r"realization", r"state[-\s](?:shift|calibration)", r"process[-\s]state"]

CATEGORIES = {
    "thermal_hold_stability": HOLD_PATTERNS,
    "temperature_response": TEMP_RESPONSE_PATTERNS,
    "viscosity_level": VISCOSITY_LEVEL_PATTERNS,
    "realization_state": STATE_PATTERNS,
}

# --- Held-out truth: loaded ONLY by adjudicate() -----------------------------
HELD_OUT_SOURCE_PARTS = {"PPG2000": 39.60, "PDP70": 39.60, "AC1920": 17.0, "TK100": 5.0, "MDI": 20.19}
NEAR_REGION_L1_THRESHOLD = 7.5  # pct points, from configs/blind_benchmark_v2.json (pre-existing)


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def match_categories(text: str) -> list[str]:
    low = text.lower()
    return [name for name, pats in CATEGORIES.items() if any(re.search(p, low) for p in pats)]


def collect_runs(arm_dir: Path) -> list[dict[str, Any]]:
    """Gather one row per attempted run, including failures."""
    rows: list[dict[str, Any]] = []
    for run_dir in sorted(d for d in arm_dir.glob("run_[0-9]*") if d.is_dir()):
        log = json.loads((run_dir / "run_log.json").read_text(encoding="utf-8"))
        rec_paths = sorted(run_dir.rglob("recommendation.json"))
        row: dict[str, Any] = {
            "run_index": log["run_index"],
            "run_dir": str(run_dir.relative_to(ROOT)),
            "run_status": log["status"],
            "wall_seconds": log["wall_seconds"],
        }
        if not rec_paths:
            row.update({
                "recommendation_id": None, "decision_mode": "invalid",
                "selected_candidate_id": None, "abstain": False, "valid": False,
                "error_tail": log.get("stderr", "")[-300:],
            })
            rows.append(row)
            continue

        rec = json.loads(rec_paths[0].read_text(encoding="utf-8"))
        delib_paths = sorted(run_dir.rglob("deliberation.json"))
        delib = json.loads(delib_paths[0].read_text(encoding="utf-8")) if delib_paths else {}

        sel = rec.get("selected_candidate")
        fs = (sel or {}).get("formulation_state", {}) or {}
        planner = delib.get("planner", {}) or {}

        # Read-only diagnostics. The FROZEN selection is the primary result and is
        # never overridden by these. They exist because the Judge can emit
        # selected_candidate_id=null while its own upstream stages name a preferred
        # candidate, and that difference must stay visible rather than be lost.
        proposer = delib.get("proposer", {}) or {}
        proposer_ranked = proposer.get("ranked_candidates") or []
        robustness = delib.get("robustness_adjudication", {}) or {}
        det = (delib.get("deterministic_decision_diagnostics", {}) or {}).get("scenario_rankings", {})
        row.update({
            "diag_planner_intent": planner.get("experiment_intent"),
            "diag_proposer_rank1": (proposer_ranked[0] or {}).get("candidate_id") if proposer_ranked else None,
            "diag_proposer_mode": proposer.get("recommended_decision_mode"),
            "diag_robustness_preferred": robustness.get("preferred_candidate_id"),
            "diag_robustness_action": robustness.get("recommended_action"),
            "diag_judge_raw_mode": (delib.get("judge_raw", {}) or {}).get("decision_mode"),
            "diag_judge_raw_selected": (delib.get("judge_raw", {}) or {}).get("selected_candidate_id"),
            "diag_deterministic_rank1_mitigation": (det.get("performance_mitigation") or [None])[0],
        })

        objective_text = " ".join(str(x) for x in [
            planner.get("physical_failure_mode", ""),
            planner.get("decision_goal", ""),
            (rec.get("acceptance_criterion") or {}).get("claim", ""),
        ])
        full_text = " ".join(str(x) for x in [
            objective_text,
            (rec.get("acceptance_criterion") or {}).get("criterion", ""),
            (rec.get("acceptance_criterion") or {}).get("measurement_window", ""),
            rec.get("selection_rationale", ""),
        ])

        objective_cats = match_categories(objective_text)
        all_cats = match_categories(full_text)
        crit = rec.get("acceptance_criterion") or {}
        window_text = f"{crit.get('criterion','')} {crit.get('measurement_window','')}"

        row.update({
            "recommendation_id": rec.get("recommendation_id"),
            "created_utc": rec.get("created_utc"),
            "decision_mode": rec.get("decision_mode"),
            "selected_candidate_id": (sel or {}).get("candidate_id"),
            "abstain": rec.get("decision_mode") == "abstain",
            "valid": True,
            "model": rec.get("provenance", {}).get("model"),
            "prompt_hash": rec.get("provenance", {}).get("prompt_hash"),
            "input_hash": rec.get("provenance", {}).get("input_hash"),
            "git_commit": rec.get("provenance", {}).get("git_commit"),
            "recommendation_sha256": sha256_file(rec_paths[0]),
            **{c: (float(fs.get(c)) if fs.get(c) is not None else None) for c in COMPONENTS},
            "primary_objective_categories": ";".join(objective_cats),
            "all_mentioned_categories": ";".join(all_cats),
            "level1_thermal_hold_objective": "thermal_hold_stability" in objective_cats,
            "agent_chose_120c": bool(re.search(r"\b120\s*(?:°|deg(?:rees)?\s*)?c\b", window_text.lower())),
            "agent_chose_15_60_window": bool(re.search(r"15\D{0,12}60", window_text)),
            "acceptance_claim": (crit.get("claim") or "")[:300],
            "acceptance_criterion_text": (crit.get("criterion") or "")[:400],
            "n_alternatives": len(rec.get("alternatives_considered", []) or []),
        })
        rows.append(row)
    return rows


def cmd_summarize(args: argparse.Namespace) -> None:
    arm_dir = args.arm_dir
    rows = collect_runs(arm_dir)

    fields = sorted({k for r in rows for k in r})
    out_csv = arm_dir / "frozen_recommendations.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    valid = [r for r in rows if r.get("valid")]
    non_abstain = [r for r in valid if not r["abstain"]]
    n = len(rows)

    def rate(count: int) -> float:
        return round(count / n, 4) if n else 0.0

    summary = {
        "arm_dir": str(arm_dir.relative_to(ROOT)),
        "n_runs_attempted": n,
        "n_valid": len(valid),
        "n_invalid": n - len(valid),
        "n_abstain": sum(1 for r in valid if r["abstain"]),
        "invalid_rate": rate(n - len(valid)),
        "abstention_rate": rate(sum(1 for r in valid if r["abstain"])),
        "level1_thermal_hold_objective_recovery_rate": rate(
            sum(1 for r in valid if r.get("level1_thermal_hold_objective"))
        ),
        "agent_independently_chose_120c_rate": rate(sum(1 for r in valid if r.get("agent_chose_120c"))),
        "agent_independently_chose_15_60_window_rate": rate(
            sum(1 for r in valid if r.get("agent_chose_15_60_window"))
        ),
        "level2_resin_modified_rate": rate(
            sum(1 for r in non_abstain if (r.get("AC1920") or 0) + (r.get("TK100") or 0) > 0)
        ),
        "level2_acrylic_like_rate": rate(sum(1 for r in non_abstain if (r.get("AC1920") or 0) > 0)),
        "level2_minor_tackifier_rate": rate(sum(1 for r in non_abstain if (r.get("TK100") or 0) > 0)),
        "level2_both_axes_rate": rate(
            sum(1 for r in non_abstain if (r.get("AC1920") or 0) > 0 and (r.get("TK100") or 0) > 0)
        ),
        "selection_distribution": {
            cid: sum(1 for r in valid if r["selected_candidate_id"] == cid)
            for cid in sorted({r["selected_candidate_id"] for r in valid if r["selected_candidate_id"]})
        },
        "selection_entropy_bits": round(
            selection_entropy([r["selected_candidate_id"] for r in valid]), 4
        ),
        "objective_category_distribution": {
            cat: sum(1 for r in valid if cat in (r.get("primary_objective_categories") or ""))
            for cat in CATEGORIES
        },
        "held_out_truth_loaded": False,
        "note": "Computed with no access to the wet-lab outcome.",
    }
    (arm_dir / "blind_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    closure = {
        "status": "BLIND PHASE CLOSED",
        "arm_dir": str(arm_dir.relative_to(ROOT)),
        "closed_utc": utc_now(),
        "git_commit": git_commit(),
        "n_runs": n,
        "frozen_recommendations_csv_sha256": sha256_file(out_csv),
        "blind_summary_sha256": sha256_file(arm_dir / "blind_summary.json"),
        "per_run_recommendation_sha256": {
            str(r["run_index"]): r.get("recommendation_sha256") for r in rows
        },
        "declaration": (
            "All Stage-1 recommendations above were generated and written to disk before any "
            "held-out validation data were loaded. They are immutable from this timestamp."
        ),
    }
    (arm_dir / CLOSURE_FILENAME).write_text(
        json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print(f"\nBLIND PHASE CLOSED @ {closure['closed_utc']}  ({arm_dir})")


def cmd_adjudicate(args: argparse.Namespace) -> None:
    arm_dir = args.arm_dir
    closure_path = arm_dir / CLOSURE_FILENAME
    if not closure_path.exists():
        raise SystemExit(
            f"refusing to adjudicate: {CLOSURE_FILENAME} not found in {arm_dir}. "
            "Run 'summarize' first to freeze and close the blind phase."
        )
    closure = json.loads(closure_path.read_text(encoding="utf-8"))

    total = sum(HELD_OUT_SOURCE_PARTS.values())
    truth = {k: 100.0 * v / total for k, v in HELD_OUT_SOURCE_PARTS.items()}

    rows = list(csv.DictReader((arm_dir / "frozen_recommendations.csv").open(encoding="utf-8")))
    # Integrity: the frozen CSV must not have changed since closure.
    if sha256_file(arm_dir / "frozen_recommendations.csv") != closure["frozen_recommendations_csv_sha256"]:
        raise SystemExit("frozen_recommendations.csv changed after the blind phase was closed; refusing to score")

    out_rows = []
    for r in rows:
        rec: dict[str, Any] = {
            "run_index": r["run_index"],
            "recommendation_id": r["recommendation_id"],
            "decision_mode": r["decision_mode"],
            "selected_candidate_id": r["selected_candidate_id"],
            "level1_thermal_hold_objective": r.get("level1_thermal_hold_objective"),
            "agent_chose_120c": r.get("agent_chose_120c"),
            "agent_chose_15_60_window": r.get("agent_chose_15_60_window"),
        }
        if r.get("valid") != "True" or r["decision_mode"] == "abstain" or not r.get("AC1920"):
            if r.get("valid") == "True" and r["decision_mode"] != "abstain" and r.get("AC1920") == "0.0":
                pass  # a real zero-modifier selection: score it
            else:
                rec.update({k: None for k in [
                    "level2_resin_modified", "level2_acrylic_like", "level2_minor_tackifier",
                    "overall_l1_pct_points", "overall_l2_pct_points",
                    "modifier_plane_l1_pct_points", "modifier_plane_l2_pct_points",
                    "abs_acrylic_diff", "abs_tackifier_diff", "near_region_hit",
                ]})
                out_rows.append(rec)
                continue

        comp = {c: float(r[c]) for c in COMPONENTS}
        d = {c: comp[c] - truth[c] for c in COMPONENTS}
        mod_l1 = abs(d["AC1920"]) + abs(d["TK100"])
        rec.update({
            "level2_resin_modified": comp["AC1920"] + comp["TK100"] > 0,
            "level2_acrylic_like": comp["AC1920"] > 0,
            "level2_minor_tackifier": comp["TK100"] > 0,
            "overall_l1_pct_points": round(sum(abs(v) for v in d.values()), 4),
            "overall_l2_pct_points": round(math.sqrt(sum(v * v for v in d.values())), 4),
            "modifier_plane_l1_pct_points": round(mod_l1, 4),
            "modifier_plane_l2_pct_points": round(math.hypot(d["AC1920"], d["TK100"]), 4),
            "abs_acrylic_diff": round(abs(d["AC1920"]), 4),
            "abs_tackifier_diff": round(abs(d["TK100"]), 4),
            "near_region_hit": mod_l1 <= NEAR_REGION_L1_THRESHOLD,
        })
        out_rows.append(rec)

    fields = sorted({k for r in out_rows for k in r})
    out_csv = arm_dir / "post_unblind_adjudication.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    scored = [r for r in out_rows if r.get("modifier_plane_l1_pct_points") is not None]
    dists = [r["modifier_plane_l1_pct_points"] for r in scored]
    n = len(out_rows)

    def rate(c: int) -> float:
        return round(c / n, 4) if n else 0.0

    summary = {
        "arm_dir": str(arm_dir.relative_to(ROOT)),
        "unblinded_utc": utc_now(),
        "blind_phase_closed_utc": closure["closed_utc"],
        "held_out_truth_normalized_pct": {k: round(v, 6) for k, v in truth.items()},
        "n_runs": n,
        "n_scored": len(scored),
        "level1_thermal_hold_objective_recovery_rate": rate(
            sum(1 for r in out_rows if str(r.get("level1_thermal_hold_objective")) == "True")
        ),
        "level2_resin_modification_recovery_rate": rate(
            sum(1 for r in out_rows if r.get("level2_resin_modified") is True)
        ),
        "level2_acrylic_like_recovery_rate": rate(
            sum(1 for r in out_rows if r.get("level2_acrylic_like") is True)
        ),
        "level2_minor_tackifier_recovery_rate": rate(
            sum(1 for r in out_rows if r.get("level2_minor_tackifier") is True)
        ),
        "level3_near_region_rate": rate(sum(1 for r in out_rows if r.get("near_region_hit") is True)),
        "modifier_plane_l1": {
            "min": round(min(dists), 4) if dists else None,
            "median": round(sorted(dists)[len(dists) // 2], 4) if dists else None,
            "max": round(max(dists), 4) if dists else None,
            "mean": round(sum(dists) / len(dists), 4) if dists else None,
        },
        "near_region_l1_threshold_pct_points": NEAR_REGION_L1_THRESHOLD,
        "claim_boundary": (
            "Distances are to a formulation that is not a node of the Arm B candidate lattice; "
            "exact recovery was impossible by construction. Direction and region recovery are the "
            "scorable quantities."
        ),
    }
    (arm_dir / "adjudication_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, fn in (("summarize", cmd_summarize), ("adjudicate", cmd_adjudicate)):
        sp = sub.add_parser(name)
        sp.add_argument("--arm-dir", type=Path, required=True)
        sp.set_defaults(func=fn)
    args = p.parse_args()
    args.arm_dir = args.arm_dir.resolve()
    args.func(args)


if __name__ == "__main__":
    main()
