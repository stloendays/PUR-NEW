#!/usr/bin/env python3
"""Measure what the deterministic rule layer contributes, by controlled ablation.

Two arms, identical in every respect except one: the model, the prompts, the hypothesis
registry, the measurement catalog, the evidence contract, the tool trace and all 292
experiment cards are the same. Only the deterministic value-of-information score is
withheld in the ablated arm.

The comparison is reported per decision axis, because the rule layer does not contribute
uniformly: the measurement plan and the composition are separable choices and the score
turns out to matter for one and not the other.
"""

from __future__ import annotations

import argparse
import glob
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.voi import (  # noqa: E402
    build_experiment_cards,
    rank_by_rule_order,
    hypothesis_discrimination,
    load_hypothesis_registry,
    load_measurement_catalog,
)

SUPPORTED_FAMILY = "dual_axis_resin_modified"
FAILURE_MODE_MEASUREMENT = "M-HOLD-120"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if total == 0:
        return None
    phat = successes / total
    denom = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def load_arm(
    series_dir: Path,
    label: str,
    discrimination: dict[str, float],
    *,
    run_range: tuple[int, int] | None = None,
) -> dict[str, Any]:
    manifest = read_json(series_dir / "series_manifest.json")
    paths = sorted(glob.glob(str(series_dir / "run_*" / "EXP_V4_*" / "recommendation.json")))
    if run_range is not None:
        low, high = run_range
        paths = [
            path
            for path in paths
            if low <= int(Path(path).parent.parent.name.split("_")[-1]) <= high
        ]
    records = [read_json(Path(path)) for path in paths]
    declared = (run_range[1] - run_range[0] + 1) if run_range else manifest.get(
        "n_runs_after_extension", manifest["n_runs_declared"]
    )

    # Did the internal critique stages see the defect, and did the decision change?
    critique = {"high_severity_objection": 0, "robustness_said_change_experiment": 0, "committed_anyway": 0}
    delib_paths = sorted(glob.glob(str(series_dir / "run_*" / "EXP_V4_*" / "deliberation.json")))
    if run_range is not None:
        low, high = run_range
        delib_paths = [
            path
            for path in delib_paths
            if low <= int(Path(path).parent.parent.name.split("_")[-1]) <= high
        ]
    for path in delib_paths:
        deliberation = read_json(Path(path))
        skeptic = deliberation.get("skeptic") or {}
        robustness = deliberation.get("robustness_adjudication") or {}
        judge = deliberation.get("judge_normalized") or {}
        high = any(item.get("severity") == "high" for item in skeptic.get("objections", []))
        change = robustness.get("skeptic_objection_effect") == "changes_which_experiment_to_run"
        critique["high_severity_objection"] += int(high)
        critique["robustness_said_change_experiment"] += int(change)
        if high and judge.get("decision_mode") != "abstain":
            critique["committed_anyway"] += 1

    families, measurements, candidates, modes, vois, in_tied, discs = [], [], [], [], [], [], []
    for record in records:
        card = record.get("experiment_card") or {}
        families.append(card.get("intervention_family"))
        measurements.append(record.get("selected_measurement_id"))
        candidates.append(record.get("selected_candidate_id"))
        modes.append(record["decision_mode"])
        if record["voi"]["score"] is not None:
            vois.append(record["voi"]["score"])
            in_tied.append(bool(record["voi"]["selected_is_in_tied_top_set"]))
        if record.get("selected_experiment_id"):
            discs.append(discrimination.get(record["selected_experiment_id"], 0.0))

    n_supported = sum(item == SUPPORTED_FAMILY for item in families)
    n_measurement = sum(item == FAILURE_MODE_MEASUREMENT for item in measurements)
    n_tied = sum(in_tied)
    n_zero_disc = sum(1 for value in discs if value == 0.0)

    return {
        "label": label,
        "series": str(series_dir.relative_to(ROOT)),
        "arm": manifest.get("arm"),
        "voi_scores_withheld_from_model": manifest.get("voi_scores_withheld_from_model", False),
        "model": manifest["model"],
        "n_runs_declared": declared,
        "n_runs_completed": len(records),
        "run_range": list(run_range) if run_range else None,
        "n_runs_declared_originally": manifest.get("n_runs_declared_originally", manifest["n_runs_declared"]),
        "extensions": manifest.get("extensions"),
        "decision_modes": dict(Counter(modes).most_common()),
        "intervention_family_counts": dict(Counter(families).most_common()),
        "measurement_counts": dict(Counter(measurements).most_common()),
        "candidate_counts": dict(Counter(candidates).most_common()),
        "supported_family_recovery": {
            "count": n_supported,
            "of_declared": declared,
            "wilson_95": wilson(n_supported, declared),
        },
        "failure_mode_measurement_selection": {
            "count": n_measurement,
            "of_declared": declared,
            "wilson_95": wilson(n_measurement, declared),
        },
        "selection_inside_deterministic_tied_top_set": {
            "count": n_tied,
            "of_scored": len(in_tied),
            "wilson_95": wilson(n_tied, len(in_tied)),
        },
        "post_hoc_voi_of_selection": {
            "mean": round(sum(vois) / len(vois), 6) if vois else None,
            "min": min(vois) if vois else None,
            "max": max(vois) if vois else None,
        },
        "hypothesis_discrimination_of_selection": {
            "mean": round(sum(discs) / len(discs), 6) if discs else None,
            "n_with_zero_discrimination": n_zero_disc,
            "of_completed": len(discs),
        },
        "internal_critique": {
            **critique,
            "of_completed": len(records),
            "note": (
                "A high-severity Skeptic objection that does not change the frozen decision shows "
                "the critique stage detecting a defect the decision policy then overrides."
            ),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare the full and rule-ablated V4 arms")
    parser.add_argument("--full-series", type=Path, default=ROOT / "results" / "agent_v4_voi" / "series_n10")
    parser.add_argument(
        "--ablated-series",
        type=Path,
        default=ROOT / "results" / "agent_v4_voi" / "series_ablation_voi_withheld_n5",
    )
    parser.add_argument(
        "--order-series",
        type=Path,
        default=ROOT / "results" / "agent_v4_voi" / "series_ablation_rule_order_minimality_first_n5",
    )
    parser.add_argument(
        "--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    candidates = read_json(args.candidate_set.resolve())["candidates"]
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    by_measurement = {item["measurement_id"]: item for item in catalog["measurements"]}
    by_candidate = {item["candidate_id"]: item for item in candidates}

    cards = build_experiment_cards(candidates, registry=registry, catalog=catalog)
    discrimination = {
        card["experiment_id"]: hypothesis_discrimination(
            by_candidate[card["candidate_id"]], by_measurement[card["measurement_id"]], registry
        )["score"]
        for card in cards
    }

    full = load_arm(args.full_series.resolve(), "full_v4_rule_layer_supplied", discrimination)
    ablated = load_arm(args.ablated_series.resolve(), "ablated_voi_scores_withheld", discrimination)
    order_dir = args.order_series.resolve()
    has_order = (order_dir / "series_manifest.json").exists()
    order_arm = load_arm(order_dir, "rule_order_minimality_first", discrimination) if has_order else None
    order_manifest = read_json(order_dir / "series_manifest.json") if has_order else {}
    original_n = order_manifest.get("n_runs_declared_originally", order_manifest.get("n_runs_declared"))
    order_blocks = None
    if has_order and order_manifest.get("extensions"):
        # An extension decided after observing the first block is not the same thing as a
        # single pre-declared N. Both blocks are reported separately so a reader can check
        # that the extension did not change the conclusion.
        order_blocks = {
            "pre_declared_block": load_arm(
                order_dir, "rule_order_minimality_first_runs_1_to_%d" % original_n, discrimination,
                run_range=(1, original_n),
            ),
            "extension_block": load_arm(
                order_dir,
                "rule_order_minimality_first_extension",
                discrimination,
                run_range=(original_n + 1, order_manifest["n_runs_after_extension"]),
            ),
            "extension_provenance": order_manifest["extensions"],
        }
    order_predictions = {
        name: rank_by_rule_order(cards, name) for name in ("sufficiency_first", "minimality_first")
    }

    report = {
        "question": (
            "Same model, same prompts, same hypothesis registry, same measurement catalog, same "
            "evidence contract, same 292 experiment cards. Only the deterministic value-of-"
            "information score is withheld. What changes?"
        ),
        "controlled": [
            "model and decoding endpoint",
            "all five stage prompts",
            "hypothesis registry and its prediction rules",
            "measurement catalog and declared resolutions",
            "evidence access profile and structural firewall",
            "candidate lattice (73 nodes) and the full 292-card experiment inventory",
        ],
        "manipulated": [
            "deterministic VOI score, component vector, ranking and tie set",
            "the decision-stability sweep, which would reveal the tie set",
            "the tool-generated acceptance and falsification criteria",
        ],
        "arms": {
            key: value
            for key, value in (("full", full), ("ablated", ablated), ("rule_order_inverted", order_arm))
            if value is not None
        },
        "rule_order_blocks": order_blocks,
        "deterministic_rule_order_predictions": {
            name: {
                "top_experiment_id": value["top_experiment_id"],
                "top_intervention_family": value["top_intervention_family"],
                "top_hypothesis_discrimination": value["top_hypothesis_discrimination"],
                "top_total_modifier_pct": value["top_total_modifier_pct"],
                "top_voi_score": value["top_voi_score"],
            }
            for name, value in order_predictions.items()
        },
        "effect_of_the_rule_layer": {
            "supported_family_recovery": (
                f"{full['supported_family_recovery']['count']}/{full['n_runs_declared']} "
                f"-> {ablated['supported_family_recovery']['count']}/{ablated['n_runs_declared']}"
            ),
            "failure_mode_measurement_selection": (
                f"{full['failure_mode_measurement_selection']['count']}/{full['n_runs_declared']} "
                f"-> {ablated['failure_mode_measurement_selection']['count']}/{ablated['n_runs_declared']}"
            ),
            "mean_post_hoc_voi": (
                round(
                    (full["post_hoc_voi_of_selection"]["mean"] or 0.0)
                    - (ablated["post_hoc_voi_of_selection"]["mean"] or 0.0),
                    6,
                )
            ),
            "mean_hypothesis_discrimination": (
                round(
                    (full["hypothesis_discrimination_of_selection"]["mean"] or 0.0)
                    - (ablated["hypothesis_discrimination_of_selection"]["mean"] or 0.0),
                    6,
                )
            ),
        },
        "reading": (
            "The rule layer does not contribute uniformly across the decision. The measurement "
            "plan is recovered in both arms, so that choice follows from the hypothesis registry "
            "and the declared failure mode rather than from the score. The composition choice "
            "does not survive the ablation: without the score the runs fall back to compositions "
            "that cannot separate any registered hypothesis. Specifying the right rule is what "
            "converts a capable model into a correct decision."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report["effect_of_the_rule_layer"], indent=2))
    for arm in [item for item in (full, ablated, order_arm) if item is not None]:
        print(
            f"\n{arm['label']}: families={arm['intervention_family_counts']} "
            f"zero-discrimination selections={arm['hypothesis_discrimination_of_selection']['n_with_zero_discrimination']}"
            f"/{arm['hypothesis_discrimination_of_selection']['of_completed']}"
        )


if __name__ == "__main__":
    main()
