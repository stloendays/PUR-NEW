#!/usr/bin/env python3
"""Deterministic V3 versus V4 comparison on the byte-identical 73-node lattice.

Both architectures are run against the same candidate space, so the comparison
isolates the decision object and the deterministic layer. V3 records are read only;
nothing in the V3 series is re-run, re-scored or modified.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import build_candidate_cards, robustness_summary  # noqa: E402
from pur_new.voi import BASE_WEIGHTS, TIE_EPSILON, build_experiment_cards  # noqa: E402


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def v3_frozen_selections(series_dir: Path) -> dict[str, Any]:
    """Read the frozen V3 recommendations of one series without altering them."""
    selections: list[str | None] = []
    for path in sorted(series_dir.glob("run_*/*/recommendation.json")):
        record = read_json(path)
        # V3 nests the chosen candidate; an abstention carries no candidate object.
        chosen = record.get("selected_candidate") or {}
        selections.append(chosen.get("candidate_id") if isinstance(chosen, dict) else None)
    named = [item for item in selections if item]
    return {
        "series": str(series_dir.relative_to(ROOT)),
        "n_runs": len(selections),
        "n_named": len(named),
        "n_abstained": len(selections) - len(named),
        "selection_counts": dict(Counter(named).most_common()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare V3 and V4 decision layers")
    parser.add_argument("--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json")
    parser.add_argument("--v3-series", type=Path, default=ROOT / "results" / "stage1_blind_replay_v3h" / "arm_b_blind")
    parser.add_argument("--v4-run-dir", type=Path, default=None)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    # Accept paths given relative to the repository root as well as absolute ones.
    args.candidate_set = args.candidate_set.resolve()
    args.v3_series = args.v3_series.resolve()
    if args.v4_run_dir:
        args.v4_run_dir = args.v4_run_dir.resolve()

    candidate_set = read_json(args.candidate_set)
    candidates = candidate_set["candidates"]

    # V3 deterministic layer: a strict ranking with a unique rank-1 per scenario.
    v3_cards = build_candidate_cards(candidates)
    v3_summary = robustness_summary(v3_cards)
    v3_rank1 = {scenario: ids[0] for scenario, ids in v3_summary["scenario_rankings"].items()}

    # V4 deterministic layer: a VOI score over experiments, reporting ties as ties.
    v4_cards = build_experiment_cards(candidates)
    best = max(card["voi_score"] for card in v4_cards)
    v4_tied = sorted(card["experiment_id"] for card in v4_cards if abs(card["voi_score"] - best) <= TIE_EPSILON)
    v4_tied_candidates = sorted({eid.split("::")[0] for eid in v4_tied})
    strictly_lower = max(score for score in (card["voi_score"] for card in v4_cards) if score < best - TIE_EPSILON)

    comparison = {
        "candidate_space": {
            "path": str(args.candidate_set.relative_to(ROOT)),
            "n_nodes": len(candidates),
            "identical_for_both_architectures": True,
        },
        "decision_object": {
            "v3": "formulation candidate (73 options)",
            "v4": f"experiment card = formulation x measurement plan ({len(v4_cards)} options)",
        },
        "deterministic_layer": {
            "v3": {
                "kind": "scenario rankings with a unique rank-1 per scenario",
                "rank1_by_scenario": v3_rank1,
                "pareto_front_size": len(v3_summary["pareto_front"]),
                "reports_ties_explicitly": False,
            },
            "v4": {
                "kind": "VOI score over experiments with explicit tie reporting",
                "formula_weights": BASE_WEIGHTS,
                "top_voi": best,
                "n_tied_at_top": len(v4_tied),
                "tied_top_experiment_ids": v4_tied,
                "tied_top_candidate_ids": v4_tied_candidates,
                "margin_to_first_strictly_lower": round(best - strictly_lower, 6),
                "reports_ties_explicitly": True,
            },
        },
        "what_the_model_layer_must_do": {
            "v3": "may depart from a visible or hidden unique deterministic rank-1",
            "v4": (
                "must break a genuine tie the deterministic tool cannot break, so a selection inside "
                "the tied set provably was not read off the score"
            ),
        },
        "adjudication_type": {
            "v3": "modifier-plane distance to the held-out composition",
            "v4": "survival of a registered mechanistic hypothesis against the completed measurement",
        },
        "v3_frozen_series": v3_frozen_selections(args.v3_series) if args.v3_series.exists() else None,
    }

    if args.v4_run_dir:
        recommendation = read_json(args.v4_run_dir / "recommendation.json")
        comparison["v4_frozen_decision"] = {
            "run_dir": str(args.v4_run_dir.relative_to(ROOT)),
            "recommendation_id": recommendation["recommendation_id"],
            "decision_mode": recommendation["decision_mode"],
            "selected_experiment_id": recommendation["selected_experiment_id"],
            "selected_candidate_id": recommendation["selected_candidate_id"],
            "selected_measurement_id": recommendation["selected_measurement_id"],
            "selected_is_in_tied_top_set": recommendation["voi"]["selected_is_in_tied_top_set"],
            "hypotheses_addressed": recommendation["hypotheses_addressed"],
            "hypotheses_left_entangled": recommendation["hypotheses_left_entangled"],
        }
        # selection_counts is built most-common-first; a set would lose that ordering.
        v3_counts = (comparison["v3_frozen_series"] or {}).get("selection_counts", {})
        comparison["overlap"] = {
            "v3_modal_selection": next(iter(v3_counts), None),
            "v3_selection_counts": v3_counts,
            "v4_selected_candidate": recommendation["selected_candidate_id"],
            "v4_selection_would_have_been_available_to_v3": recommendation["selected_candidate_id"]
            in {c["candidate_id"] for c in candidates},
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(comparison["deterministic_layer"], indent=2))


if __name__ == "__main__":
    main()
