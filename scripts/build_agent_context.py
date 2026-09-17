#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.actions import (  # noqa: E402
    audit_process_unknowns,
    candidate_profile,
    compare_candidate_to_priors,
    get_hold_stability,
    get_repeatability_risk,
    get_temperature_support,
    query_external_priors,
    rank_candidate_support,
    stress_test_candidate,
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    p = argparse.ArgumentParser(description="Build an action-enriched Agent context with explicit evidence-access control")
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--profile", choices=["blind_pre_result", "closed_loop_design", "literature_only_sanity"], default="blind_pre_result")
    p.add_argument("--output", type=Path, default=ROOT / "derived" / "agent_context.json")
    args = p.parse_args()

    profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    policy = profiles[args.profile]
    candidate_set = read_json(args.candidate_set)
    candidates = candidate_set["candidates"]

    include_follow_up = bool(policy["allow_follow_up_hold_results"])
    local: dict = {}
    if policy["allow_original_hold_data"]:
        local["original_hold_E1"] = get_hold_stability("E1", include_follow_up=False)
        local["original_hold_E5"] = get_hold_stability("E5", include_follow_up=False)
    if policy["allow_original_temperature_sweeps"]:
        local["repeatability_E2"] = get_repeatability_risk("E2")
        local["temperature_support_E1"] = get_temperature_support("E1")
        local["temperature_support_E2"] = get_temperature_support("E2")
        local["temperature_support_E3"] = get_temperature_support("E3")
    if include_follow_up:
        local["follow_up_hold"] = get_hold_stability("F1", include_follow_up=True)

    priors = query_external_priors(max_rows=100) if policy["allow_external_evidence_hints"] else []
    candidate_actions = []
    for c in candidates:
        candidate_actions.append({
            "candidate_id": c["candidate_id"],
            "profile": candidate_profile(c),
            "analogue_comparison": compare_candidate_to_priors(c) if priors else None,
            "process_audit": audit_process_unknowns(c),
            "stress_test": stress_test_candidate(c) if priors else None,
        })

    context = {
        "evidence_access_profile": args.profile,
        "profile_policy": policy,
        "local_failure_evidence": local,
        "external_prior_hints": priors,
        "candidate_action_outputs": candidate_actions,
        "support_ranking": rank_candidate_support(candidates) if priors else [],
        "interpretation_rules": [
            "External prior hints are analogies, not current-system outcomes.",
            "In blind_pre_result mode, follow-up thermal-hold results are intentionally absent.",
            "High original-system hold drift should be treated as a robustness failure that justifies formulation-family changes, not only stoichiometric micro-tuning.",
            "A candidate near a repeatedly documented resin-modifier region receives prior support only if it remains chemically/operationally admissible.",
            "Process-history missingness remains uncertainty even when a candidate has strong literature analogue support."
        ]
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(context, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
