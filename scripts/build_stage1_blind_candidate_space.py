#!/usr/bin/env python3
"""Build the Stage-1 target-blind candidate space from pre-result evidence only.

Provenance rule (pre-registered, outcome-blind)
----------------------------------------------
1. Reactive core is anchored on E2, read from data/formulations.csv. E2 is the
   geometric centre of the measured local five-point design (50/50 PPG2000/PDP70,
   NCO:OH=1.80, between the E1/E3 stoichiometric and E4/E5 ratio perturbations).
2. Two modifier axes are laid out as UNIFORM lattices anchored at zero:
      acrylic-like AC1920   : 0..30 wt% in steps of 2.5
      tackifier-like TK100  : 0..10 wt% in steps of 2.5
   The acrylic upper bound is the first lattice node at or above the largest
   directly commensurate external acrylic anchor (25 wt%, H09/H10). The tackifier
   upper bound is the explicit "below about 10 wt%" guidance (H13).
   Neither the step nor the bound is derived from any later measurement.
3. The measured reactive-core-only family E1..E5 is admitted unchanged, plus four
   midpoint interpolations strictly inside the measured local design, so that
   staying in the original non-resin design space is a genuinely competitive
   option rather than a token control.
4. No candidate carries a measurement plan or a hold temperature/time. The Agent
   must derive the experiment and the acceptance criterion itself.

The later wet-lab formulation is NOT a node of this lattice by construction.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ACRYLIC_GRID = [0.0, 2.5, 5.0, 7.5, 10.0, 12.5, 15.0, 17.5, 20.0, 22.5, 25.0, 27.5, 30.0]
TACKIFIER_GRID = [0.0, 2.5, 5.0, 7.5, 10.0]

# Midpoint interpolations strictly inside the measured local reactive-core design.
CORE_INTERPOLATIONS = [
    ("E1", "E2", "stoichiometry midpoint between NCO:OH 1.70 and 1.80 at 50/50"),
    ("E2", "E3", "stoichiometry midpoint between NCO:OH 1.80 and 1.90 at 50/50"),
    ("E4", "E2", "polyol-ratio midpoint between 60/40 and 50/50 at NCO:OH 1.80"),
    ("E2", "E5", "polyol-ratio midpoint between 50/50 and 40/60 at NCO:OH 1.80"),
]

ACRYLIC_STRONG_ANCHORS = [19.37, 19.57, 19.78, 19.98, 25.0]
TACKIFIER_STRONG_ANCHORS = [4.8, 5.3, 5.7, 5.8, 5.9, 6.4]

PROCESS_STATE_UNKNOWN = {
    "reaction_temperature_c": None,
    "reaction_time_min": None,
    "mixing_history": None,
    "sample_age": None,
    "hold_temperature_c": None,
    "hold_time_min": None,
}


def read_formulations() -> list[dict[str, str]]:
    with (ROOT / "data" / "formulations.csv").open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def original_rows() -> list[dict[str, str]]:
    """Only stage == 'original'. The follow-up row is never read."""
    return [r for r in read_formulations() if r.get("stage") == "original"]


def normalized_core(row: dict[str, str]) -> dict[str, float]:
    ppg, pdp, mdi = float(row["ppg2000"]), float(row["pdp70"]), float(row["mdi"])
    total = ppg + pdp + mdi
    return {"PPG2000": ppg / total, "PDP70": pdp / total, "MDI": mdi / total}


def acrylic_evidence(pct: float) -> list[str]:
    if pct == 0:
        return ["LOCAL_FORMULATIONS"]
    refs: list[str] = []
    if min(abs(pct - a) for a in ACRYLIC_STRONG_ANCHORS) <= 5.0:
        refs += ["H03", "H04", "H05", "H06"] if pct < 22.5 else ["H09", "H10"]
    if abs(pct - 15.0) <= 2.5:
        refs.append("H08")
    return refs or ["H07"]


def tackifier_evidence(pct: float) -> list[str]:
    if pct == 0:
        return []
    refs: list[str] = []
    if min(abs(pct - a) for a in TACKIFIER_STRONG_ANCHORS) <= 5.0:
        refs += ["H01", "H02"]
    if pct >= 7.5:
        refs.append("H13")
    return refs or ["H13"]


def axis_note(pct: float, axis: str) -> str:
    if pct == 0:
        return f"{axis} axis held at zero (control level on this axis)."
    return f"{axis} axis at {pct:g} wt% of total formulation."


def build() -> dict[str, Any]:
    rows = original_rows()
    by_id = {r["formulation_id"]: r for r in rows}
    if "F1" in by_id:
        raise SystemExit("follow-up formulation leaked into the blind generator")
    e2_core = normalized_core(by_id["E2"])

    candidates: list[dict[str, Any]] = []
    provenance_rows: list[dict[str, Any]] = []
    idx = 0

    # --- Family A: measured reactive-core-only formulations (no modifier) ---
    for fid in ["E1", "E2", "E3", "E4", "E5"]:
        row = by_id[fid]
        core = normalized_core(row)
        idx += 1
        cid = f"S1C{idx:02d}"
        candidates.append(
            {
                "candidate_id": cid,
                "formulation_state": {
                    "PPG2000": round(100.0 * core["PPG2000"], 10),
                    "PDP70": round(100.0 * core["PDP70"], 10),
                    "AC1920": 0.0,
                    "TK100": 0.0,
                    "MDI": round(100.0 * core["MDI"], 10),
                    "amount_basis": "normalized_total_wt_percent",
                    "design_layer": "measured_reactive_core_only",
                },
                "process_state": dict(PROCESS_STATE_UNKNOWN),
                "evidence_references": ["LOCAL_FORMULATIONS", "LOCAL_TEMPERATURE_SWEEPS"]
                + (["LOCAL_HOLD"] if fid in ("E1", "E5") else []),
                "constraint_notes": [
                    f"Reactive-core-only formulation matching measured local design point {fid} "
                    f"(PPG2000/PDP70 = {row['ppg2000_pdp70_ratio']}, NCO:OH = {row['nco_oh']}), "
                    "renormalized to total wt%.",
                    "Admissible because it stays entirely inside the measured local chemistry; "
                    "it tests reactive-core / stoichiometry tuning rather than resin modification.",
                    "Search dimension introduced by the original local E1-E5 experimental design.",
                    "No post-result information was used to construct this candidate.",
                ],
            }
        )
        provenance_rows.append(
            {
                "candidate_id": cid,
                "family": "measured_reactive_core_only",
                "AC1920_pct": 0.0,
                "TK100_pct": 0.0,
                "why_admissible": (
                    f"Matches measured local design point {fid}; chemically and operationally realizable."
                ),
                "pre_result_evidence": "data/formulations.csv;data/temperature_sweeps.csv"
                + (";data/thermal_hold.csv" if fid in ("E1", "E5") else ""),
                "dimension_introduced": "Original local five-point design (pre-result).",
                "post_result_influence": "none",
            }
        )

    # --- Family A2: midpoint interpolations inside the measured reactive core ---
    for left, right, description in CORE_INTERPOLATIONS:
        a, b = normalized_core(by_id[left]), normalized_core(by_id[right])
        mid = {k: 0.5 * (a[k] + b[k]) for k in a}
        idx += 1
        cid = f"S1C{idx:02d}"
        candidates.append(
            {
                "candidate_id": cid,
                "formulation_state": {
                    "PPG2000": round(100.0 * mid["PPG2000"], 10),
                    "PDP70": round(100.0 * mid["PDP70"], 10),
                    "AC1920": 0.0,
                    "TK100": 0.0,
                    "MDI": round(100.0 * mid["MDI"], 10),
                    "amount_basis": "normalized_total_wt_percent",
                    "design_layer": "interpolated_reactive_core_only",
                },
                "process_state": dict(PROCESS_STATE_UNKNOWN),
                "evidence_references": ["LOCAL_FORMULATIONS", "LOCAL_TEMPERATURE_SWEEPS"],
                "constraint_notes": [
                    f"Reactive-core-only interpolation: {description}.",
                    "Admissible because it lies strictly between two measured local design points, "
                    "so it requires no extrapolation beyond the measured chemistry.",
                    "Search dimension introduced by the original local E1-E5 design; this candidate "
                    "exists so that continued reactive-core / stoichiometry tuning is a fully "
                    "competitive alternative to resin modification.",
                    "No post-result information was used to construct this candidate.",
                ],
            }
        )
        provenance_rows.append(
            {
                "candidate_id": cid,
                "family": "interpolated_reactive_core_only",
                "AC1920_pct": 0.0,
                "TK100_pct": 0.0,
                "why_admissible": f"Interpolation inside the measured local design ({description}).",
                "pre_result_evidence": "data/formulations.csv;data/temperature_sweeps.csv",
                "dimension_introduced": "Original local five-point design (pre-result).",
                "post_result_influence": "none",
            }
        )

    # --- Family B: uniform modifier lattice on the E2 reactive core ---
    for ac in ACRYLIC_GRID:
        for tk in TACKIFIER_GRID:
            if ac == 0.0 and tk == 0.0:
                continue  # already represented by the measured E2 point
            m = (ac + tk) / 100.0
            idx += 1
            cid = f"S1C{idx:02d}"
            refs = acrylic_evidence(ac) + tackifier_evidence(tk)
            candidates.append(
                {
                    "candidate_id": cid,
                    "formulation_state": {
                        "PPG2000": round(100.0 * (1 - m) * e2_core["PPG2000"], 10),
                        "PDP70": round(100.0 * (1 - m) * e2_core["PDP70"], 10),
                        "AC1920": ac,
                        "TK100": tk,
                        "MDI": round(100.0 * (1 - m) * e2_core["MDI"], 10),
                        "amount_basis": "normalized_total_wt_percent",
                        "design_layer": "uniform_modifier_lattice_on_E2_core",
                    },
                    "process_state": dict(PROCESS_STATE_UNKNOWN),
                    "evidence_references": sorted(set(refs)),
                    "constraint_notes": [
                        axis_note(ac, "Acrylic-like AC1920"),
                        axis_note(tk, "Tackifier-like TK100"),
                        "E2 reactive-core proportions are preserved and scaled into the remaining "
                        "total-formulation fraction, so only the modifier axes vary.",
                        "Lattice node of a uniform grid (acrylic 0-30 step 5; tackifier 0-10 step 2.5) "
                        "whose bounds come from external pre-result literature anchors only.",
                        "No post-result information was used to construct this candidate.",
                    ],
                }
            )
            provenance_rows.append(
                {
                    "candidate_id": cid,
                    "family": "uniform_modifier_lattice_on_E2_core",
                    "AC1920_pct": ac,
                    "TK100_pct": tk,
                    "why_admissible": (
                        "Chemically plausible resin-modified reactive PUR; modifier burden within "
                        "externally documented ranges."
                    ),
                    "pre_result_evidence": ";".join(sorted(set(refs))),
                    "dimension_introduced": (
                        "External curated PUR literature/patent evidence published before the local "
                        "validation experiment; the local E1-E5 design contains no resin modifier and "
                        "therefore cannot inform this axis."
                    ),
                    "post_result_influence": "none",
                }
            )

    return {
        "candidate_set_id": "PUR_NEW_STAGE1_BLIND_CANDIDATE_SPACE_V1",
        "decision_context": (
            "Target-blind Stage-1 pre-result candidate space. Built only from the measured local "
            "E1-E5 design and curated external PUR literature anchors. Candidate order and IDs "
            "encode no preference. No candidate carries a measurement plan or hold schedule: the "
            "Agent must decide what to measure and define its own falsifiable acceptance criterion."
        ),
        "candidates": candidates,
        "provenance": {
            "generator": "scripts/build_stage1_blind_candidate_space.py",
            "reactive_core_anchor": "E2 (data/formulations.csv, stage=original)",
            "acrylic_like_grid_pct": ACRYLIC_GRID,
            "tackifier_like_grid_pct": TACKIFIER_GRID,
            "grid_rule": "uniform lattice anchored at zero; acrylic step 2.5 to 30.0; tackifier step 2.5 to 10.0",
            "acrylic_upper_bound_rule": (
                "first lattice node at or above the largest directly commensurate external acrylic "
                "anchor (25 wt%, H09/H10)"
            ),
            "tackifier_upper_bound_rule": "explicit 'below about 10 wt%' guidance (H13)",
            "reads_follow_up_formulation_row": False,
            "reads_follow_up_hold_results": False,
            "validation_recipe_numeric_values_used_to_generate_grid": False,
            "validation_outcome_included": False,
            "candidate_order_encodes_rank": False,
            "candidate_ids_encode_historical_identity": False,
            "carries_measurement_plan": False,
            "carries_hold_schedule": False,
            "reactive_core_only_option_available": True,
            "n_candidates": len(candidates),
            "claim_boundary": (
                "This space is constructed from pre-result evidence only. The later wet-lab "
                "formulation is not a node of the lattice, so exact composition recovery is "
                "impossible by construction and only region/direction recovery can be scored."
            ),
        },
    }, provenance_rows


def main() -> None:
    p = argparse.ArgumentParser(description="Build the Stage-1 target-blind candidate space")
    p.add_argument(
        "--output", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    p.add_argument(
        "--provenance-csv",
        type=Path,
        default=ROOT / "derived" / "stage1_blind_candidate_provenance.csv",
    )
    args = p.parse_args()

    value, provenance_rows = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with args.provenance_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(provenance_rows[0].keys()))
        writer.writeheader()
        writer.writerows(provenance_rows)

    print(args.output)
    print(args.provenance_csv)
    print(f"n_candidates={len(value['candidates'])}")


if __name__ == "__main__":
    main()
