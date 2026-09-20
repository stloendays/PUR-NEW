#!/usr/bin/env python3
"""Two-phase summary and adjudication of an Agent V4 series.

Phase 1 (blind): read every frozen recommendation and write `blind_summary.json`.
                 No held-out data is touched.
Phase 2 (close): write `BLIND_PHASE_CLOSED.json` recording the hash of every frozen
                 recommendation in the series.
Phase 3 (adjudicate): load the held-out composition and measurements for the first
                 time, re-verify each frozen hash, and score the registered hypotheses.

The phases run in that order in one invocation, and the closure record fixes what was
frozen before the truth was read.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_adjudicator():
    spec = importlib.util.spec_from_file_location("adj_v4", ROOT / "scripts" / "adjudicate_agent_v4.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    """95% Wilson score interval. Returns None when the denominator is zero."""
    if total == 0:
        return None
    phat = successes / total
    denom = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def collect_runs(series_dir: Path) -> list[dict[str, Any]]:
    manifest = read_json(series_dir / "series_manifest.json")
    runs = []
    for row in manifest["runs"]:
        entry = {"run_index": row["run_index"], "status": row["status"], "record": None}
        if row.get("frozen_recommendation"):
            rec_dir = ROOT / row["frozen_recommendation"]
            rec_path = rec_dir / "recommendation.json"
            entry["record"] = read_json(rec_path)
            entry["record_dir"] = rec_dir
            entry["recommendation_sha256"] = sha256_file(rec_path)
            deliberation = read_json(rec_dir / "deliberation.json")
            entry["proposer"] = deliberation.get("proposer", {})
            entry["skeptic"] = deliberation.get("skeptic", {})
            entry["robustness"] = deliberation.get("robustness_adjudication", {})
            entry["judge_normalization"] = deliberation.get("judge_normalization", {})
            entry["llm_usage_total"] = deliberation.get("llm_usage_total", {})
        runs.append(entry)
    return manifest, runs


def blind_summary(manifest: dict[str, Any], runs: list[dict[str, Any]]) -> dict[str, Any]:
    declared = manifest["n_runs_declared"]
    records = [row["record"] for row in runs if row["record"]]
    committed = [rec for rec in records if rec["decision_mode"] != "abstain"]
    abstained = [rec for rec in records if rec["decision_mode"] == "abstain"]

    selections = Counter(rec["selected_experiment_id"] for rec in committed)
    candidates = Counter(rec["selected_candidate_id"] for rec in committed)
    measurements = Counter(rec["selected_measurement_id"] for rec in committed)
    modes = Counter(rec["decision_mode"] for rec in records)

    in_tied = sum(bool(rec["voi"]["selected_is_in_tied_top_set"]) for rec in committed)
    declared_entangled = sum(bool(rec.get("hypotheses_left_entangled")) for rec in committed)
    judge_repairs = sum(bool(row.get("judge_normalization", {}).get("applied")) for row in runs if row["record"])

    tokens = sum(int(row.get("llm_usage_total", {}).get("total_tokens") or 0) for row in runs if row["record"])
    calls = sum(int(row.get("llm_usage_total", {}).get("llm_calls") or 0) for row in runs if row["record"])

    return {
        "phase": "blind",
        "summarized_utc": utc_now(),
        "series_label": manifest["series_label"],
        "model": manifest["model"],
        "git_commit": manifest.get("git_commit"),
        "n_runs_declared": declared,
        "n_runs_completed": len(records),
        "n_committed": len(committed),
        "n_abstained": len(abstained),
        "decision_modes": dict(modes.most_common()),
        "selected_experiment_counts": dict(selections.most_common()),
        "selected_candidate_counts": dict(candidates.most_common()),
        "selected_measurement_counts": dict(measurements.most_common()),
        "selection_inside_deterministic_tied_top_set": {
            "count": in_tied,
            "of_committed": len(committed),
            "rate_wilson_95": wilson(in_tied, len(committed)),
        },
        "committed_runs_declaring_an_entangled_hypothesis_pair": {
            "count": declared_entangled,
            "of_committed": len(committed),
        },
        "judge_output_contract_repairs": judge_repairs,
        "llm_calls_total": calls,
        "llm_tokens_total": tokens,
        "tie_break_justifications": [
            {
                "run_index": row["run_index"],
                "selected": row["record"]["selected_experiment_id"],
                "justification": (row.get("proposer") or {}).get("tie_break_justification"),
            }
            for row in runs
            if row["record"] and row["record"]["decision_mode"] != "abstain"
        ],
        "reporting_rule": manifest["reporting_rule"],
        "no_held_out_data_read_in_this_phase": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize and adjudicate an Agent V4 series")
    parser.add_argument("--series-dir", type=Path, required=True)
    args = parser.parse_args()
    series_dir = args.series_dir.resolve()

    manifest, runs = collect_runs(series_dir)

    # Phase 1 - blind.
    summary = blind_summary(manifest, runs)
    (series_dir / "blind_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Phase 2 - closure. Hashes are fixed before any held-out value is read.
    closure = {
        "blind_phase_closed_utc": utc_now(),
        "series_label": manifest["series_label"],
        "n_runs_declared": manifest["n_runs_declared"],
        "frozen_recommendation_hashes": {
            f"run_{row['run_index']:03d}": row["recommendation_sha256"]
            for row in runs
            if row["record"]
        },
    }
    (series_dir / "BLIND_PHASE_CLOSED.json").write_text(
        json.dumps(closure, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Phase 3 - adjudication. This is the first read of held-out data in this script.
    adj = _load_adjudicator()
    registry = read_json(ROOT / "configs" / "hypothesis_registry.json")
    composition = adj.load_held_out_composition()
    hold = adj.load_held_out_hold()
    hypothesis_result = adj.adjudicate_hypotheses(registry, composition, hold)

    per_run = []
    for row in runs:
        record = row["record"]
        if not record:
            per_run.append({"run_index": row["run_index"], "status": row["status"], "adjudicable": False})
            continue
        rec_path = row["record_dir"] / "recommendation.json"
        if sha256_file(rec_path) != closure["frozen_recommendation_hashes"][f"run_{row['run_index']:03d}"]:
            raise SystemExit(f"frozen recommendation changed after closure: {rec_path}")
        card = record.get("experiment_card") or {}
        plan_matches = record.get("selected_measurement_id") == "M-HOLD-120"
        # The completed wet-lab experiment used a DUAL-AXIS composition. A run that selected
        # an acrylic-only or reactive-core-only composition chose an experiment that was never
        # performed: its frozen criteria cannot be checked against this measurement, even
        # though its measurement plan matches. Reporting it as adjudicated would be false.
        family_matches = card.get("intervention_family") == "dual_axis_resin_modified"
        entry = {
            "run_index": row["run_index"],
            "status": row["status"],
            "decision_mode": record["decision_mode"],
            "selected_experiment_id": record["selected_experiment_id"],
            "selected_intervention_family": card.get("intervention_family"),
            "measurement_plan_matches_completed_measurement": plan_matches,
            "intervention_family_matches_completed_experiment": family_matches,
            "adjudicable": bool(card) and plan_matches and family_matches,
            "not_adjudicable_reason": (
                None
                if (bool(card) and plan_matches and family_matches)
                else (
                    "the selected composition is not the one that was synthesised, so its frozen "
                    "acceptance and falsification criteria cannot be checked against this measurement"
                    if plan_matches
                    else "the selected measurement plan is not the measurement that was performed"
                )
            ),
            "hypotheses_left_entangled": record.get("hypotheses_left_entangled"),
        }
        if card:
            entry["modifier_plane_l1_pct_points"] = round(
                abs(card["acrylic_like_pct"] - composition["acrylic_like_pct"])
                + abs(card["minor_tackifier_like_pct"] - composition["minor_tackifier_like_pct"]),
                4,
            )
        per_run.append(entry)

    adjudicable = [row for row in per_run if row.get("adjudicable")]
    distances = [row["modifier_plane_l1_pct_points"] for row in adjudicable]

    adjudication = {
        "phase": "adjudicated",
        "adjudicated_utc": utc_now(),
        "blind_phase_closure": closure,
        "series_label": manifest["series_label"],
        "n_runs_declared": manifest["n_runs_declared"],
        "held_out_composition": composition,
        "held_out_thermal_hold": hold,
        "hypothesis_adjudication": hypothesis_result,
        "adjudication_note": (
            "The hypothesis verdict is a property of the completed measurement and the registered "
            "prediction rules, so it is identical for every run that selected the matched-window "
            "hold. What varies across runs is which experiment was chosen and what the Agent "
            "declared it could not separate."
        ),
        "per_run": per_run,
        "n_adjudicable": len(adjudicable),
        "n_not_adjudicable": len(per_run) - len(adjudicable),
        "measurement_plan_match_rate": {
            "count": sum(row.get("measurement_plan_matches_completed_measurement", False) for row in per_run),
            "of_declared": manifest["n_runs_declared"],
            "wilson_95": wilson(
                sum(row.get("measurement_plan_matches_completed_measurement", False) for row in per_run),
                manifest["n_runs_declared"],
            ),
        },
        "adjudicable_rate": {
            "count": len(adjudicable),
            "of_declared": manifest["n_runs_declared"],
            "wilson_95": wilson(len(adjudicable), manifest["n_runs_declared"]),
            "note": (
                "A run is adjudicable only when BOTH its measurement plan and its intervention "
                "family match the completed experiment. A run that deliberately chose a different "
                "composition to close a different hypothesis pair is reported here as not "
                "adjudicable, which is a property of the completed experiment, not a failure."
            ),
        },
        "modifier_plane_l1_pct_points": {
            "role": (
                "reported for comparability with the V3 series only. Distance to the held-out "
                "composition is not the V4 objective and enters no VOI component, weight or tie-break."
            ),
            "values": distances,
            "min": min(distances) if distances else None,
            "median": sorted(distances)[len(distances) // 2] if distances else None,
            "mean": round(sum(distances) / len(distances), 4) if distances else None,
            "max": max(distances) if distances else None,
        },
    }
    (series_dir / "adjudication_summary.json").write_text(
        json.dumps(adjudication, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(json.dumps({"blind": summary, "adjudicated": {
        "hypothesis_adjudication": hypothesis_result,
        "n_adjudicable": adjudication["n_adjudicable"],
        "modifier_plane_l1_pct_points": adjudication["modifier_plane_l1_pct_points"],
    }}, indent=2))


if __name__ == "__main__":
    main()
