#!/usr/bin/env python3
"""Deterministic baseline for the V4 tie-break, and the measurable model-layer departure.

The V4 Proposer broke the five-way VOI tie on "smallest supported total modifier burden".
That rule is NOT an independent inference: near-identical wording is present in
`configs/formulation_priors.json` under `MINIMUM_SUFFICIENT_INTERVENTION_V1`, and that
text verifiably reaches the model through the tool trace. A run that applies it is
therefore applying a supplied policy correctly, which is a competence result and not an
autonomy result.

This script codes that policy as a deterministic baseline so the model-layer contribution
can be measured rather than asserted:

    baseline = argmax VOI, ties broken by lowest total modifier percent, then by id.

Any frozen run matching the baseline is explained by the supplied policy. Only runs that
depart from it require the model layer as an explanation.
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

from pur_new.voi import TIE_EPSILON, build_experiment_cards  # noqa: E402

POLICY_SOURCE = "configs/formulation_priors.json"
POLICY_ID = "MINIMUM_SUFFICIENT_INTERVENTION_V1"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def policy_text_available_to_model(run_dir: Path) -> dict[str, Any]:
    """Was the minimum-burden policy actually inside the payload the model saw?"""
    deliberation = read_json(run_dir / "deliberation.json")
    needle = "smallest sufficient total modifier burden"
    found_in = [
        key
        for key in ("planner", "tool_trace", "voi_sent_to_model", "decision_stability_sent_to_model")
        if needle in json.dumps(deliberation.get(key), ensure_ascii=False)
    ]
    return {
        "policy_source": POLICY_SOURCE,
        "policy_id": POLICY_ID,
        "payload_sections_containing_the_policy": found_in,
        "policy_was_supplied_to_the_model": bool(found_in),
    }


def deterministic_tiebreak_baseline(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    cards = build_experiment_cards(candidates)
    best = max(card["voi_score"] for card in cards)
    tied = [card for card in cards if abs(card["voi_score"] - best) <= TIE_EPSILON]
    chosen = min(
        tied,
        key=lambda card: (
            card["acrylic_like_pct"] + card["minor_tackifier_like_pct"],
            card["experiment_id"],
        ),
    )
    return {
        "rule": "argmax VOI, then lowest total modifier percent, then lexicographic id",
        "rule_is_supplied_not_inferred": True,
        "top_voi": best,
        "tied_top_experiment_ids": sorted(card["experiment_id"] for card in tied),
        "baseline_experiment_id": chosen["experiment_id"],
        "baseline_total_modifier_pct": chosen["acrylic_like_pct"] + chosen["minor_tackifier_like_pct"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the V4 model-layer departure from a coded tie-break")
    parser.add_argument("--series-dir", type=Path, required=True)
    parser.add_argument(
        "--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    series_dir = args.series_dir.resolve()
    candidates = read_json(args.candidate_set.resolve())["candidates"]
    baseline = deterministic_tiebreak_baseline(candidates)

    manifest = read_json(series_dir / "series_manifest.json")
    rows = []
    for row in manifest["runs"]:
        if not row.get("frozen_recommendation"):
            continue
        run_dir = ROOT / row["frozen_recommendation"]
        record = read_json(run_dir / "recommendation.json")
        selected = record["selected_experiment_id"]
        card = record.get("experiment_card") or {}
        rows.append(
            {
                "run_index": row["run_index"],
                "selected_experiment_id": selected,
                "decision_mode": record["decision_mode"],
                "matches_coded_baseline": selected == baseline["baseline_experiment_id"],
                "voi_of_selection": record["voi"]["score"],
                "voi_deficit_vs_top": (
                    round(baseline["top_voi"] - record["voi"]["score"], 6)
                    if record["voi"]["score"] is not None
                    else None
                ),
                "intervention_family": card.get("intervention_family"),
            }
        )

    matched = [row for row in rows if row["matches_coded_baseline"]]
    departed = [row for row in rows if not row["matches_coded_baseline"]]

    report = {
        "question": (
            "How much of the frozen series is explained by a coded tie-break using a policy the "
            "model was given, and how much requires the model layer?"
        ),
        "policy_provenance": policy_text_available_to_model(
            ROOT / manifest["runs"][0]["frozen_recommendation"]
        ),
        "coded_baseline": baseline,
        "n_runs": len(rows),
        "n_matching_coded_baseline": len(matched),
        "n_departing_from_coded_baseline": len(departed),
        "model_layer_departure_rate": f"{len(departed)}/{len(rows)}",
        "departures": departed,
        "per_run": rows,
        "interpretation": (
            "Runs matching the coded baseline are consistent with correct application of a supplied "
            "policy and are not evidence of independent model reasoning. Only the departing runs "
            "require the model layer as an explanation, and they must be reported at that rate."
        ),
    }

    output = args.output or (series_dir / "tiebreak_baseline.json")
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "policy_provenance", "coded_baseline", "n_runs",
        "n_matching_coded_baseline", "model_layer_departure_rate", "departures",
    )}, indent=2))


if __name__ == "__main__":
    main()
