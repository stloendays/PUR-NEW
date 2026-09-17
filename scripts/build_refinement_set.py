#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_candidate_set import make_candidate

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def inclusive_grid(start: float, stop: float, step: float) -> list[float]:
    if step <= 0:
        raise ValueError("step must be positive")
    values: list[float] = []
    x = start
    while x <= stop + step * 1e-9:
        values.append(round(x, 8))
        x += step
    return values


def anchor_from_priors(priors: dict, expected_id: str = "E2") -> dict[str, float | str]:
    cfg = priors["local_reactive_core_anchor"]
    if str(cfg["formulation_id"]) != expected_id:
        raise ValueError(f"configured anchor is {cfg['formulation_id']!r}, expected {expected_id!r}")
    fractions = cfg["normalized_core_fractions"]
    return {
        "formulation_id": expected_id,
        "nco_oh": "1.80",
        "PPG2000_fraction": float(fractions["PPG2000"]),
        "PDP70_fraction": float(fractions["PDP70"]),
        "MDI_fraction": float(fractions["MDI"]),
    }


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Build the outcome-blind fine refinement space used after coarse resin-family identification. "
            "All modifier coordinates are normalized wt% of total formulation."
        )
    )
    p.add_argument("--output", type=Path, default=ROOT / "derived" / "candidate_set_refinement_v1.json")
    p.add_argument("--anchor-formulation", default="E2")
    p.add_argument("--step", type=float, default=1.0)
    args = p.parse_args()

    priors = read_json(ROOT / "configs" / "formulation_priors.json")
    acrylic_cfg = priors["candidate_axes"]["acrylic_like_modifier_pct_total"]
    tack_cfg = priors["candidate_axes"]["minor_tackifier_like_modifier_pct_total"]
    strong_support = float(priors["action_support_thresholds_pct_points"]["strong"])

    acrylic_anchors = [float(x) for x in acrylic_cfg["direct_evidence_anchors_pct"]]
    tack_grid = [float(x) for x in tack_cfg["grid"]]

    acrylic_min = max(0.0, min(acrylic_anchors) - strong_support)
    acrylic_max = max(acrylic_anchors)
    tackifier_min = min(tack_grid)
    tackifier_max = max(tack_grid)

    acrylic_grid = inclusive_grid(acrylic_min, acrylic_max, args.step)
    tackifier_grid = inclusive_grid(tackifier_min, tackifier_max, args.step)

    # Anti-leakage property: the refinement generator obtains its reactive-core
    # anchor exclusively from the audited pre-result prior configuration.
    anchor = anchor_from_priors(priors, expected_id=args.anchor_formulation)

    candidates = []
    for acrylic in acrylic_grid:
        for tackifier in tackifier_grid:
            candidate = make_candidate(acrylic, tackifier, anchor=anchor)
            candidate["formulation_state"]["design_layer"] = "fine_refinement"
            candidate["constraint_notes"].append(
                "Fine-refinement coordinates are normalized wt% of total formulation; source-reported lab parts must be normalized before comparison."
            )
            candidates.append(candidate)

    out = {
        "candidate_set_id": "EVIDENCE_DERIVED_FINE_REFINEMENT_V1",
        "decision_context": (
            "Outcome-blind fine-grid operationalization of the continuous resin-modified region after coarse formulation-family identification. "
            "It is intended for reproducible refinement and future prospective freezes, not as a reconstructed contemporaneous artifact of the historical validation recommendation."
        ),
        "candidates": candidates,
        "provenance": {
            "generator": "scripts/build_refinement_set.py",
            "coordinate_basis": "normalized_total_wt_percent",
            "design_layer": "fine_refinement",
            "anchor_formulation": args.anchor_formulation,
            "anchor_source": "configs/formulation_priors.json::local_reactive_core_anchor",
            "reads_formulations_csv": False,
            "grid_step_pct_points": args.step,
            "acrylic_domain_pct": [acrylic_min, acrylic_max],
            "tackifier_domain_pct": [tackifier_min, tackifier_max],
            "domain_derivation": {
                "acrylic_lower": "minimum directly commensurate acrylic evidence anchor minus predeclared strong-support distance",
                "acrylic_upper": "maximum directly commensurate acrylic evidence anchor",
                "tackifier": "independently documented coarse control-to-upper range"
            },
            "reads_follow_up_measurements": False,
            "uses_validation_recipe_numeric_values_to_generate_domain": False,
            "uses_validation_outcome_to_generate_domain": False,
            "historical_status": (
                "Current reproducible refinement formalization. It must not be described as the original historical freeze algorithm unless contemporaneous provenance is recovered."
            ),
            "basis_warning": (
                "Historical source-reported formulation parts and normalized-total wt% are different coordinate systems. "
                "Normalize lab recipes before any distance or region comparison."
            )
        }
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
