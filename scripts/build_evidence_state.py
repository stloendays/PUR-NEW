#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.metrics import (  # noqa: E402
    andrade_fit,
    coefficient_of_variation,
    hold_stability_index,
    max_min_ratio,
    mean_profile_si,
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def build_temperature_state(rows: list[dict[str, str]]) -> dict:
    by_run: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row["formulation_id"], row["run_label"], row["retest_after_1d"])
        by_run[key].append(row)

    runs = []
    for (formulation_id, run_label, retest), group in sorted(by_run.items()):
        group = sorted(group, key=lambda r: float(r["temperature_c"]))
        temps = [float(r["temperature_c"]) for r in group]
        values = [float(r["viscosity_reported"]) for r in group]
        fit = andrade_fit(temps, values) if len(group) >= 3 else None
        runs.append(
            {
                "formulation_id": formulation_id,
                "run_label": run_label,
                "retest_after_1d": retest.lower() == "true",
                "temperature_support_C": [min(temps), max(temps)],
                "n_points": len(group),
                "monotonic_decrease_with_temperature": all(
                    later < earlier for earlier, later in zip(values, values[1:])
                ),
                "andrade_descriptive_fit": fit,
            }
        )

    # Descriptive spread across nominal non-retest realizations.
    by_form_temp: dict[tuple[str, float], list[float]] = defaultdict(list)
    for row in rows:
        if row["retest_after_1d"].lower() == "true":
            continue
        by_form_temp[(row["formulation_id"], float(row["temperature_c"]))].append(
            float(row["viscosity_reported"])
        )

    spread = []
    for (formulation_id, temperature_c), values in sorted(by_form_temp.items()):
        if len(values) < 2:
            continue
        spread.append(
            {
                "formulation_id": formulation_id,
                "temperature_c": temperature_c,
                "n_runs": len(values),
                "mean": statistics.fmean(values),
                "sample_cv": coefficient_of_variation(values),
                "max_min_ratio": max_min_ratio(values),
                "interpretation": "descriptive run spread; run labels are not assigned a meaning here",
            }
        )

    return {"runs": runs, "nominal_repeat_spread": spread}


def build_hold_state(rows: list[dict[str, str]]) -> dict:
    by_run: dict[tuple[str, str, str, float], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            row["formulation_id"],
            row["stage"],
            row["run_label"],
            float(row["temperature_c"]),
        )
        by_run[key].append(row)

    runs = []
    for (formulation_id, stage, run_label, temperature_c), group in sorted(by_run.items()):
        measurements = {float(r["time_min"]): float(r["viscosity_reported"]) for r in group}
        entry = {
            "formulation_id": formulation_id,
            "stage": stage,
            "run_label": run_label,
            "temperature_c": temperature_c,
            "time_support_min": [min(measurements), max(measurements)],
            "n_points": len(measurements),
            "si": {},
        }
        if 15.0 in measurements and 60.0 in measurements:
            entry["si"]["15_to_60"] = hold_stability_index(
                measurements[15.0], measurements[60.0]
            )
        if 15.0 in measurements and 90.0 in measurements:
            entry["si"]["15_to_90"] = hold_stability_index(
                measurements[15.0], measurements[90.0]
            )
        runs.append(entry)

    # Mean-profile SI only when multiple runs share the exact start/end window.
    follow_up_groups: dict[tuple[str, float], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if row["stage"] == "follow_up":
            follow_up_groups[(row["formulation_id"], float(row["temperature_c"]))].append(row)

    mean_profiles = []
    for (formulation_id, temperature_c), group in sorted(follow_up_groups.items()):
        by_label: dict[str, dict[float, float]] = defaultdict(dict)
        for row in group:
            by_label[row["run_label"]][float(row["time_min"])] = float(row["viscosity_reported"])
        eligible = [series for series in by_label.values() if 15.0 in series and 60.0 in series]
        if len(eligible) >= 2:
            mean_profiles.append(
                {
                    "formulation_id": formulation_id,
                    "temperature_c": temperature_c,
                    "n_runs": len(eligible),
                    "si_15_to_60_mean_profile": mean_profile_si(
                        [series[15.0] for series in eligible],
                        [series[60.0] for series in eligible],
                    ),
                }
            )

    return {"runs": runs, "follow_up_mean_profiles": mean_profiles}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build deterministic PUR-NEW evidence state")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "derived" / "evidence_state.json",
        help="Output JSON path",
    )
    args = parser.parse_args()

    temp_rows = read_csv(ROOT / "data" / "temperature_sweeps.csv")
    hold_rows = read_csv(ROOT / "data" / "thermal_hold.csv")

    state = {
        "workflow": "PUR_NEW_CLOSED_LOOP_V1",
        "source_files": [
            "data/formulations.csv",
            "data/temperature_sweeps.csv",
            "data/thermal_hold.csv",
        ],
        "viscosity_unit": None,
        "temperature_response": build_temperature_state(temp_rows),
        "thermal_hold": build_hold_state(hold_rows),
        "claim_boundary": {
            "measured_vs_derived_kept_separate": True,
            "run_labels_not_interpreted": True,
            "unknown_viscosity_unit_not_invented": True,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
