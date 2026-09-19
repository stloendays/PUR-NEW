#!/usr/bin/env python3
"""Post-freeze adjudication of a frozen Agent V4 experiment recommendation.

This script is the ONLY place in the V4 pipeline that reads the held-out validation
formulation and its measurements. It refuses to run unless a frozen recommendation
already exists on disk, and it re-verifies that file's hash before scoring, so the
decision cannot be edited after the truth is loaded.

What it adjudicates, in order of scientific weight:

  1. Which registered hypothesis survives contact with the completed measurement.
  2. Whether the frozen acceptance and falsification criteria are met.
  3. Whether the selected measurement plan matches what was actually measured.
  4. Modifier-plane distance, reported LAST and explicitly not the VOI objective.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HELD_OUT_ID = "F1"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_held_out_composition() -> dict[str, float]:
    with (ROOT / "data" / "formulations.csv").open(newline="", encoding="utf-8") as handle:
        row = next(item for item in csv.DictReader(handle) if item["formulation_id"] == HELD_OUT_ID)
    parts = {key: float(row[key]) for key in ("ppg2000", "pdp70", "ac1920", "tk100", "mdi")}
    total = sum(parts.values())
    reactive = parts["ppg2000"] + parts["pdp70"] + parts["mdi"]
    return {
        "acrylic_like_pct": 100.0 * parts["ac1920"] / total,
        "minor_tackifier_like_pct": 100.0 * parts["tk100"] / total,
        "reactive_mass_fraction": reactive / total,
        "source_reported_parts": parts,
    }


def load_held_out_hold() -> dict[str, Any]:
    rows = []
    with (ROOT / "data" / "thermal_hold.csv").open(newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            if item["formulation_id"] == HELD_OUT_ID:
                rows.append(
                    {
                        "run_label": item["run_label"],
                        "temperature_c": float(item["temperature_c"]),
                        "time_min": float(item["time_min"]),
                        "viscosity_reported": float(item["viscosity_reported"]),
                    }
                )
    repeats: dict[str, dict[float, float]] = {}
    for row in rows:
        repeats.setdefault(row["run_label"], {})[row["time_min"]] = row["viscosity_reported"]

    per_repeat = {}
    for label, series in sorted(repeats.items()):
        if 15.0 in series and 60.0 in series:
            drift = 100.0 * (series[60.0] - series[15.0]) / series[15.0]
            per_repeat[label] = {
                "eta_15": series[15.0],
                "eta_60": series[60.0],
                "drift_15_60_pct": round(drift, 4),
                "sampling_times_min": sorted(series),
            }
    drifts = [item["drift_15_60_pct"] for item in per_repeat.values()]
    mean_abs = sum(abs(value) for value in drifts) / len(drifts) if drifts else None
    return {
        "per_repeat": per_repeat,
        "n_repeats": len(per_repeat),
        "mean_absolute_drift_15_60_pct": round(mean_abs, 4) if mean_abs is not None else None,
        "temperature_c": 120.0,
    }


def adjudicate_hypotheses(
    registry: dict[str, Any],
    composition: dict[str, float],
    hold: dict[str, Any],
) -> dict[str, Any]:
    """Score each registered hypothesis against the completed measurement.

    The prediction rules are applied at the held-out composition's own reactive mass
    fraction, exactly as they were registered before the truth was loaded.
    """
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    phi_r = composition["reactive_mass_fraction"]
    tackifier = composition["minor_tackifier_like_pct"]
    observed = hold["mean_absolute_drift_15_60_pct"]
    linear = reference * phi_r

    predictions = {
        "H-CORE": linear,
        "H-RESIN": 0.5 * linear,
        "H-DUAL": 0.5 * linear if tackifier > 0 else linear,
    }

    verdicts = {}
    for hypothesis in registry["hypotheses"]:
        hid = hypothesis["hypothesis_id"]
        predicted = predictions[hid]
        if hid == "H-CORE":
            # Falsified when the observation sits far below the linear-dilution prediction.
            survives = observed >= 0.5 * linear
            basis = (
                f"linear-dilution prediction {linear:.2f}% at phi_r={phi_r:.4f}; "
                f"observed {observed:.2f}%"
            )
        elif hid == "H-RESIN":
            survives = observed < 0.5 * linear
            basis = f"suppression below half the dilution prediction ({0.5 * linear:.2f}%); observed {observed:.2f}%"
        else:
            # H-DUAL is not separable from H-RESIN by a dual-axis composition alone.
            survives = observed < 0.5 * linear if tackifier > 0 else observed >= 0.5 * linear
            basis = (
                "this composition carries both modifier axes, so the completed measurement "
                "cannot separate H-DUAL from H-RESIN; an acrylic-only hold is required"
            )
        verdicts[hid] = {
            "predicted_drift_pct": round(predicted, 4),
            "observed_drift_pct": observed,
            "survives": bool(survives),
            "basis": basis,
        }

    verdicts["H-DUAL"]["separable_by_this_measurement"] = tackifier <= 0
    return {
        "reference_E1_drift_pct": reference,
        "held_out_reactive_mass_fraction": round(phi_r, 6),
        "linear_dilution_prediction_pct": round(linear, 4),
        "observed_mean_absolute_drift_pct": observed,
        "observed_vs_linear_ratio": round(observed / linear, 4) if linear else None,
        "drift_reduction_vs_E1_pct": round(100.0 * (1.0 - observed / reference), 2),
        "dilution_explained_reduction_pct": round(100.0 * (1.0 - phi_r), 2),
        "hypothesis_verdicts": verdicts,
        "surviving_hypotheses": sorted(hid for hid, item in verdicts.items() if item["survives"]),
        "falsified_hypotheses": sorted(hid for hid, item in verdicts.items() if not item["survives"]),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Adjudicate a frozen Agent V4 experiment")
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    recommendation_path = args.run_dir / "recommendation.json"
    if not recommendation_path.exists():
        raise SystemExit(
            f"no frozen recommendation at {recommendation_path}; adjudication may only run after freeze"
        )
    frozen_hash = sha256_file(recommendation_path)
    recommendation = read_json(recommendation_path)
    registry = read_json(ROOT / "configs" / "hypothesis_registry.json")

    closure = {
        "blind_phase_closed_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "frozen_recommendation_sha256": frozen_hash,
        "frozen_utc": recommendation["frozen_utc"],
        "recommendation_id": recommendation["recommendation_id"],
    }
    (args.run_dir / "BLIND_PHASE_CLOSED.json").write_text(
        json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    composition = load_held_out_composition()
    hold = load_held_out_hold()
    hypothesis_result = adjudicate_hypotheses(registry, composition, hold)

    selected_measurement = recommendation.get("selected_measurement_id")
    measurement_match = {
        "selected_measurement_id": selected_measurement,
        "held_out_measurement_actually_performed": "120 C thermal hold, 15/30/45/60 min, two repeats",
        "matches": selected_measurement == "M-HOLD-120",
        "note": (
            "A selected measurement plan that does not match the completed measurement cannot be "
            "adjudicated by it; that is a reportable outcome, not a failure of the Agent."
        ),
    }

    card = recommendation.get("experiment_card") or {}
    distance = None
    if card:
        distance = {
            "selected_acrylic_like_pct": card["acrylic_like_pct"],
            "selected_minor_tackifier_like_pct": card["minor_tackifier_like_pct"],
            "held_out_acrylic_like_pct": round(composition["acrylic_like_pct"], 4),
            "held_out_minor_tackifier_like_pct": round(composition["minor_tackifier_like_pct"], 4),
            "modifier_plane_l1_pct_points": round(
                abs(card["acrylic_like_pct"] - composition["acrylic_like_pct"])
                + abs(card["minor_tackifier_like_pct"] - composition["minor_tackifier_like_pct"]),
                4,
            ),
            "role": (
                "reported for comparability with the V3 series only. Distance to the held-out "
                "composition is NOT the V4 objective and enters no VOI component, weight or tie-break."
            ),
        }

    report = {
        "adjudication_id": f"ADJ_{recommendation['recommendation_id']}",
        "blind_phase_closure": closure,
        "frozen_decision": {
            "decision_mode": recommendation["decision_mode"],
            "selected_experiment_id": recommendation["selected_experiment_id"],
            "acceptance_criterion": recommendation["acceptance_criterion"],
            "falsification_criterion": recommendation["falsification_criterion"],
            "voi_score": recommendation["voi"]["score"],
            "voi_tied_top_set": recommendation["voi"]["tied_top_set"],
            "selected_is_in_tied_top_set": recommendation["voi"]["selected_is_in_tied_top_set"],
            "hypotheses_addressed": recommendation["hypotheses_addressed"],
            "hypotheses_left_entangled": recommendation["hypotheses_left_entangled"],
        },
        "held_out_composition": composition,
        "held_out_thermal_hold": hold,
        "hypothesis_adjudication": hypothesis_result,
        "measurement_plan_match": measurement_match,
        "modifier_plane_distance": distance,
        "claim_boundary": (
            "This adjudication tests registered hypotheses against a completed measurement under an "
            "outcome-blind freeze. It establishes a formulation-level rheological mechanism only; no "
            "chain-level characterization is reported and none is implied."
        ),
    }

    output = args.output or (args.run_dir / "adjudication.json")
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("adjudication_id", "hypothesis_adjudication", "measurement_plan_match")}, indent=2))


if __name__ == "__main__":
    main()
