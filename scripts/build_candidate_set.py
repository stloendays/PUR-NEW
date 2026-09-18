#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_anchor_core(formulation_id: str = "E2") -> dict[str, float | str]:
    rows = read_csv(ROOT / "data" / "formulations.csv")
    row = next((r for r in rows if r["formulation_id"] == formulation_id), None)
    if row is None:
        raise KeyError(f"anchor formulation not found: {formulation_id}")

    ppg = float(row["ppg2000"])
    pdp = float(row["pdp70"])
    mdi = float(row["mdi"])
    total = ppg + pdp + mdi
    if total <= 0:
        raise ValueError("anchor reactive-core total must be positive")

    return {
        "formulation_id": formulation_id,
        "nco_oh": row.get("nco_oh") or "",
        "PPG2000_fraction": ppg / total,
        "PDP70_fraction": pdp / total,
        "MDI_fraction": mdi / total,
    }


def make_candidate(
    acrylic_pct: float,
    tackifier_pct: float,
    *,
    anchor: dict[str, float | str],
) -> dict:
    modifier_total = acrylic_pct + tackifier_pct
    if acrylic_pct < 0 or tackifier_pct < 0:
        raise ValueError("modifier levels must be non-negative")
    if modifier_total >= 100:
        raise ValueError("total modifier level must be below 100%")

    core_fraction = 1.0 - modifier_total / 100.0
    ppg = 100.0 * core_fraction * float(anchor["PPG2000_fraction"])
    pdp = 100.0 * core_fraction * float(anchor["PDP70_fraction"])
    mdi = 100.0 * core_fraction * float(anchor["MDI_fraction"])

    cid = f"HYP_A{acrylic_pct:04.1f}_T{tackifier_pct:04.1f}".replace(".", "p")
    return {
        "candidate_id": cid,
        "formulation_state": {
            "basis": "normalized_parts_per_100_total",
            "PPG2000": round(ppg, 4),
            "PDP70": round(pdp, 4),
            "AC1920": round(acrylic_pct, 4),
            "TK100": round(tackifier_pct, 4),
            "MDI": round(mdi, 4),
            "PPG2000_PDP70_ratio": "50/50",
            "acrylic_like_modifier_pct": round(acrylic_pct, 4),
            "minor_tackifier_like_modifier_pct": round(tackifier_pct, 4),
            "modifier_total_pct": round(modifier_total, 4),
            "reactive_core_anchor": str(anchor["formulation_id"]),
            "anchor_nco_oh_label": anchor["nco_oh"] or None,
            "anchor_stoichiometry_applicability": "conditional_on_modifier_reactivity",
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
            "docs/CANDIDATE_SPACE_HYPOTHESIS.md",
            "configs/formulation_priors.json",
            "data/external_evidence_hints.csv",
            "data/formulations.csv::E2",
            "data/thermal_hold.csv::original_only",
        ],
        "constraint_notes": [
            "Acrylic-like and tackifier-like levels come from independent external evidence anchors, not from the validation formulation's numeric composition.",
            "The PPG2000/PDP70/MDI core is the original E2 formulation normalized and scaled into the remaining mass fraction.",
            "The original E2 NCO:OH label remains valid only if added modifiers do not contribute NCO-reactive functionality; true stoichiometry must be recalculated when modifier chemistry is verified.",
            "Reaction-history fields remain unknown and therefore contribute process-history uncertainty.",
        ],
    }


def parse_grid(text: str) -> list[float]:
    values = [float(x.strip()) for x in text.split(",") if x.strip()]
    if not values:
        raise ValueError("grid must contain at least one value")
    return values


def main() -> None:
    p = argparse.ArgumentParser(description="Build the evidence-derived PUR-NEW hypothesis candidate grid")
    p.add_argument("--output", type=Path, default=ROOT / "derived" / "candidate_set_hypothesis_v2.json")
    p.add_argument("--acrylic-grid", default="0,15,20,25")
    p.add_argument("--tackifier-grid", default="0,5,10")
    p.add_argument("--anchor-formulation", default="E2")
    args = p.parse_args()

    acrylic_grid = parse_grid(args.acrylic_grid)
    tackifier_grid = parse_grid(args.tackifier_grid)
    anchor = load_anchor_core(args.anchor_formulation)

    candidates = [
        make_candidate(acrylic, tackifier, anchor=anchor)
        for acrylic in acrylic_grid
        for tackifier in tackifier_grid
    ]

    out = {
        "candidate_set_id": "EVIDENCE_DERIVED_HYPOTHESIS_GRID_V2",
        "decision_context": (
            "Formalize the evidence-constrained resin-modification region for outcome-blind preexperimental reconstruction and future design rounds. "
            "The grid preserves the original E2 reactive-core proportions and varies only independently supported coarse acrylic-like and minor-tackifier-like modifier levels."
        ),
        "candidates": candidates,
        "provenance": {
            "generator": "scripts/build_candidate_set.py",
            "hypothesis_document": "docs/CANDIDATE_SPACE_HYPOTHESIS.md",
            "chronology_document": "docs/EXPERIMENTAL_CHRONOLOGY.md",
            "prior_file": "configs/formulation_priors.json",
            "external_evidence_file": "data/external_evidence_hints.csv",
            "local_anchor_formulation": args.anchor_formulation,
            "candidate_axes": {
                "acrylic_like_modifier_pct": acrylic_grid,
                "minor_tackifier_like_modifier_pct": tackifier_grid,
            },
            "uses_validation_recipe_numeric_values_to_generate_candidates": False,
            "agent_validation_formulation_recommended_before_target_result_known": True,
            "current_exact_v2_grid_formalized_after_validation_experiment": True,
            "repository_contains_original_contemporaneous_freeze_artifact": False,
            "historical_interpretation": (
                "The research team confirms that the Agent recommendation preceded knowledge of the validation result. "
                "The current exact V2 4x3 software grid is a later reproducible formalization of the evidence-constrained candidate region and must not be represented as the original freeze artifact unless older provenance is recovered."
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
