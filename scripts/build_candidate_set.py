#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def make_candidate(modifier_pct: float, *, ac_share: float, mdi_pct: float) -> dict:
    remaining = 100.0 - modifier_pct - mdi_pct
    if remaining <= 0:
        raise ValueError("modifier_pct + mdi_pct must be < 100")
    polyol_each = remaining / 2.0
    ac = modifier_pct * ac_share
    tk = modifier_pct - ac
    cid = f"GRID_M{modifier_pct:04.1f}".replace(".", "p")
    return {
        "candidate_id": cid,
        "formulation_state": {
            "basis": "normalized_parts_per_100_total",
            "PPG2000": round(polyol_each, 4),
            "PDP70": round(polyol_each, 4),
            "AC1920": round(ac, 4),
            "TK100": round(tk, 4),
            "MDI": round(mdi_pct, 4),
            "PPG2000_PDP70_ratio": "50/50",
            "modifier_total_pct": modifier_pct,
            "modifier_split_assumption": f"AC1920/TK100={ac_share:.2f}/{1-ac_share:.2f}",
        },
        "process_state": {
            "hold_temperature_c": 120.0,
            "hold_time_min": [15, 30, 45, 60],
            "reaction_temperature_c": None,
            "reaction_time_min": None,
            "mixing_history": None,
            "sample_age": None,
        },
        "evidence_references": [
            "data/external_evidence_hints.csv",
            "data/thermal_hold.csv::original_only",
        ],
        "constraint_notes": [
            "Modifier loading is a design variable; literature/database evidence is an analogue prior, not proof of optimum.",
            "The 80/20 AC1920/TK100 split is a transparent heuristic for grid construction, not a measured mechanistic rule.",
            "Reaction-history fields remain unknown and therefore contribute uncertainty.",
        ],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Build an admissible resin-modifier candidate grid")
    p.add_argument("--output", type=Path, default=ROOT / "derived" / "candidate_set_external_prior_grid.json")
    p.add_argument("--modifier-grid", default="0,5,10,15,18,20,25")
    p.add_argument("--ac-share", type=float, default=0.80)
    p.add_argument("--mdi-pct", type=float, default=16.63, help="Normalized MDI fraction used only to define this candidate family")
    args = p.parse_args()

    grid = [float(x.strip()) for x in args.modifier_grid.split(",") if x.strip()]
    candidates = [make_candidate(x, ac_share=args.ac_share, mdi_pct=args.mdi_pct) for x in grid]
    out = {
        "candidate_set_id": "EXTERNAL_PRIOR_RESIN_GRID_V1",
        "decision_context": "Compare a reactive-only baseline with resin-modified 50/50 PPG2000/PDP70 candidates under a shared 120 C hold plan. The grid is informed by external PUR analogue evidence and does not use follow-up hold outcomes.",
        "candidates": candidates,
        "provenance": {
            "generator": "scripts/build_candidate_set.py",
            "uses_follow_up_hold_results": False,
            "external_prior_file": "data/external_evidence_hints.csv",
            "note": "Candidate-generation assumptions must be frozen before a run claimed as blind/prospective."
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
