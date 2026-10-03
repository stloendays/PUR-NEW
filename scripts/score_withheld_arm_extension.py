#!/usr/bin/env python3
"""Combine the score-withheld RGES arm (runs 1-5) with its five-run extension (runs 6-10).

The extension series (results/agent_v4_voi/series_ablation_voi_withheld_extension_n5) was
declared as its own N=5 contract after the first block had been observed, and was executed
from the rges_voi_withheld replay tree, whose 14 series inputs, evidence state and candidate
set are byte-identical to the original series (same model, gpt-5.6-luna). Both blocks are
scored with the metric definitions of scripts/compare_rule_layer_arms.py and reported
separately and combined.

Outputs go to analysis/results/upgrades_20261003/score_withheld_extension/.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis" / "results" / "upgrades_20261003" / "score_withheld_extension"
ORIGINAL = ROOT / "results" / "agent_v4_voi" / "series_ablation_voi_withheld_n5"
EXTENSION = ROOT / "results" / "agent_v4_voi" / "series_ablation_voi_withheld_extension_n5"
FULL = ROOT / "results" / "agent_v4_voi" / "series_n10"

spec = importlib.util.spec_from_file_location("compare_rule_layer_arms", ROOT / "scripts" / "compare_rule_layer_arms.py")
arms = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arms)


def discrimination_table() -> dict[str, float]:
    candidates = arms.read_json(ROOT / "derived" / "stage1_blind_candidate_space_v1.json")["candidates"]
    registry = arms.load_hypothesis_registry()
    catalog = arms.load_measurement_catalog()
    by_measurement = {item["measurement_id"]: item for item in catalog["measurements"]}
    by_candidate = {item["candidate_id"]: item for item in candidates}
    cards = arms.build_experiment_cards(candidates, registry=registry, catalog=catalog)
    return {
        card["experiment_id"]: arms.hypothesis_discrimination(
            by_candidate[card["candidate_id"]], by_measurement[card["measurement_id"]], registry
        )["score"]
        for card in cards
    }


def combine(blocks: list[dict]) -> dict:
    declared = sum(b["n_runs_declared"] for b in blocks)
    completed = sum(b["n_runs_completed"] for b in blocks)
    sup = sum(b["supported_family_recovery"]["count"] for b in blocks)
    meas = sum(b["failure_mode_measurement_selection"]["count"] for b in blocks)
    tied = sum(b["selection_inside_deterministic_tied_top_set"]["count"] for b in blocks)
    scored = sum(b["selection_inside_deterministic_tied_top_set"]["of_scored"] for b in blocks)
    disc_n = sum(b["hypothesis_discrimination_of_selection"]["of_completed"] for b in blocks)
    disc_sum = sum((b["hypothesis_discrimination_of_selection"]["mean"] or 0) * b["hypothesis_discrimination_of_selection"]["of_completed"] for b in blocks)
    zero = sum(b["hypothesis_discrimination_of_selection"]["n_with_zero_discrimination"] for b in blocks)
    fam, mes, cand = Counter(), Counter(), Counter()
    for b in blocks:
        fam.update(b["intervention_family_counts"])
        mes.update(b["measurement_counts"])
        cand.update(b["candidate_counts"])
    return {
        "n_runs_declared": declared,
        "n_runs_completed": completed,
        "intervention_family_counts": dict(fam.most_common()),
        "measurement_counts": dict(mes.most_common()),
        "candidate_counts": dict(cand.most_common()),
        "supported_family_recovery": {"count": sup, "of_declared": declared, "wilson_95": arms.wilson(sup, declared)},
        "failure_mode_measurement_selection": {"count": meas, "of_declared": declared, "wilson_95": arms.wilson(meas, declared)},
        "selection_inside_deterministic_tied_top_set": {"count": tied, "of_scored": scored, "wilson_95": arms.wilson(tied, scored)},
        "hypothesis_discrimination_of_selection": {"mean": round(disc_sum / disc_n, 6) if disc_n else None,
                                                   "n_with_zero_discrimination": zero, "of_completed": disc_n},
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    disc = discrimination_table()
    original = arms.load_arm(ORIGINAL, "score_withheld_runs_1_to_5", disc)
    extension = arms.load_arm(EXTENSION, "score_withheld_runs_6_to_10", disc)
    full = arms.load_arm(FULL, "rule_complete", disc)
    ext_manifest = arms.read_json(EXTENSION / "series_manifest.json")
    summary = {
        "original_block": original,
        "extension_block": extension,
        "combined_n10": combine([original, extension]),
        "rule_complete_reference": {k: full[k] for k in ("n_runs_declared", "supported_family_recovery",
                                                           "failure_mode_measurement_selection",
                                                           "hypothesis_discrimination_of_selection",
                                                           "intervention_family_counts")},
        "extension_provenance": {
            "declared_utc": ext_manifest.get("declared_utc"),
            "decided_after_observing_the_earlier_block": True,
            "executed_from": "replay tree rges_voi_withheld (commit 71bf7d9); 14/14 series input hashes, evidence state "
                             "and candidate set byte-identical to series_ablation_voi_withheld_n5",
            "model": ext_manifest.get("model"),
            "realization_codes": "public run records use R01-R03; see private_artifacts_index.json in the series directory",
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    for name in ("original_block", "extension_block", "combined_n10"):
        b = summary[name]
        print(name, b["supported_family_recovery"], b["failure_mode_measurement_selection"]["count"],
              b["hypothesis_discrimination_of_selection"], b["intervention_family_counts"], b["candidate_counts"])
    print("rule-complete", summary["rule_complete_reference"]["hypothesis_discrimination_of_selection"])


if __name__ == "__main__":
    main()
