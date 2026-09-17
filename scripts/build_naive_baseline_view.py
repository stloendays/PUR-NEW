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


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def numeric_or_none(value: str | None):
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return value


def main() -> None:
    p = argparse.ArgumentParser(
        description="Build a deliberately simple, leakage-safe baseline view from original local data only."
    )
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    formulations = [
        row for row in read_csv(ROOT / "data" / "formulations.csv")
        if row.get("stage") != "follow_up" and row.get("formulation_id") != "F1"
    ]
    temperature = [
        row for row in read_csv(ROOT / "data" / "temperature_sweeps.csv")
        if row.get("formulation_id") != "F1"
    ]
    hold = [
        row for row in read_csv(ROOT / "data" / "thermal_hold.csv")
        if row.get("stage") != "follow_up" and row.get("formulation_id") != "F1"
    ]

    candidate_set = read_json(args.candidate_set)
    candidates = []
    for c in candidate_set["candidates"]:
        fs = c.get("formulation_state", {})
        candidates.append(
            {
                "candidate_id": c["candidate_id"],
                "formulation_state": {
                    key: fs.get(key)
                    for key in (
                        "PPG2000",
                        "PDP70",
                        "AC1920",
                        "TK100",
                        "MDI",
                        "acrylic_like_modifier_pct",
                        "minor_tackifier_like_modifier_pct",
                        "modifier_total_pct",
                    )
                    if key in fs
                },
            }
        )

    view = {
        "baseline_id": "NAIVE_LOCAL_ONLY_V1",
        "task": (
            "Choose one candidate for a 120 C thermal-hold validation experiment. "
            "Use only the original local measurements and the candidate compositions shown here."
        ),
        "information_budget": {
            "raw_original_local_measurements_only": True,
            "state_aware_theory_summary": False,
            "external_database_or_literature": False,
            "scientific_actions": False,
            "candidate_space_rationale": False,
            "planner_or_skeptic": False,
            "hidden_validation_identity_or_outcome": False,
        },
        "original_formulations": [
            {
                "formulation_id": r.get("formulation_id"),
                "nco_oh": numeric_or_none(r.get("nco_oh")),
                "ppg2000": numeric_or_none(r.get("ppg2000")),
                "pdp70": numeric_or_none(r.get("pdp70")),
                "mdi": numeric_or_none(r.get("mdi")),
            }
            for r in formulations
        ],
        "raw_temperature_measurements": [
            {
                "formulation_id": r.get("formulation_id"),
                "run_label": r.get("run_label"),
                "retest_after_1d": r.get("retest_after_1d"),
                "temperature_c": numeric_or_none(r.get("temperature_c")),
                "viscosity_reported": numeric_or_none(r.get("viscosity_reported")),
            }
            for r in temperature
        ],
        "raw_thermal_hold_measurements": [
            {
                "formulation_id": r.get("formulation_id"),
                "run_label": r.get("run_label"),
                "temperature_c": numeric_or_none(r.get("temperature_c")),
                "time_min": numeric_or_none(r.get("time_min")),
                "viscosity_reported": numeric_or_none(r.get("viscosity_reported")),
            }
            for r in hold
        ],
        "candidates": candidates,
        "rules": [
            "Do not assume literature or database knowledge not supplied in this payload.",
            "Do not infer or invent the hidden validation result.",
            "This baseline has no tools and no state-aware model summary."
        ],
    }

    text = json.dumps(view, indent=2, sort_keys=True) + "\n"
    if '"F1"' in text or '"stage": "follow_up"' in text:
        raise RuntimeError("naive baseline view contains forbidden follow-up information")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
