from __future__ import annotations

import math
from collections import Counter
from typing import Any

from .actions import (
    audit_process_unknowns,
    candidate_profile,
    compare_candidate_to_priors,
    execute_action,
    stress_test_candidate,
)
from .scientific_tools import get_state_aware_rheology_summary_v3

SUPPORT_VALUE = {
    "strong_analogue_region": 3,
    "moderate_analogue_region": 2,
    "weak_analogue_region": 1,
    "baseline_control": 0,
}
RISK_VALUE = {"low": 0, "moderate": 1, "high": 2}

PLANNER_ACTIONS = {
    "query_external_priors",
    "get_candidate_hypothesis",
    "inspect_formulation",
    "get_hold_stability",
    "get_repeatability_risk",
    "get_temperature_support",
    "get_state_aware_rheology_summary",
}


def _active_axis_distance(prior: dict[str, Any]) -> float:
    total = 0.0
    for key in ("acrylic_axis_support", "tackifier_axis_support"):
        item = prior[key]
        distance = item.get("distance_pct_points")
        if distance is not None:
            total += float(distance)
    return total


def build_candidate_cards(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build deterministic, outcome-blind scorecards for every admissible candidate."""
    cards: list[dict[str, Any]] = []
    for candidate in candidates:
        profile = candidate_profile(candidate)
        prior = compare_candidate_to_priors(candidate)
        process = audit_process_unknowns(candidate)
        stress = stress_test_candidate(candidate)
        missing_count = len(process["missing_process_fields"])
        card = {
            "candidate_id": candidate["candidate_id"],
            "profile": profile,
            "analogue_support": prior["analogue_support"],
            "support_value": SUPPORT_VALUE[prior["analogue_support"]],
            "active_axis_distance_pct_points": _active_axis_distance(prior),
            "process_history_uncertainty": process["process_history_uncertainty"],
            "process_risk_value": RISK_VALUE[stress["risk_level"]],
            "missing_process_field_count": missing_count,
            "resin_modified": bool(profile["resin_modified"]),
            "stress_reasons": stress["reasons"],
        }
        cards.append(card)
    return cards


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Weight-free Pareto dominance over support, hypothesis coverage, and risk."""
    a_obj = (
        a["support_value"],
        int(a["resin_modified"]),
        -a["process_risk_value"],
        -a["missing_process_field_count"],
        -a["active_axis_distance_pct_points"],
    )
    b_obj = (
        b["support_value"],
        int(b["resin_modified"]),
        -b["process_risk_value"],
        -b["missing_process_field_count"],
        -b["active_axis_distance_pct_points"],
    )
    ge = all(x >= y for x, y in zip(a_obj, b_obj))
    gt = any(x > y for x, y in zip(a_obj, b_obj))
    return ge and gt


def pareto_front(cards: list[dict[str, Any]]) -> list[str]:
    front: list[str] = []
    for candidate in cards:
        if not any(
            _dominates(other, candidate)
            for other in cards
            if other["candidate_id"] != candidate["candidate_id"]
        ):
            front.append(candidate["candidate_id"])
    return sorted(front)


def _scenario_key(card: dict[str, Any], scenario: str) -> tuple[Any, ...]:
    if scenario == "evidence_first":
        return (
            -card["support_value"],
            card["active_axis_distance_pct_points"],
            card["process_risk_value"],
            -int(card["resin_modified"]),
            card["candidate_id"],
        )
    if scenario == "robustness_first":
        return (
            card["process_risk_value"],
            card["missing_process_field_count"],
            -card["support_value"],
            -int(card["resin_modified"]),
            card["candidate_id"],
        )
    if scenario == "hypothesis_test_first":
        return (
            -int(card["resin_modified"]),
            -card["support_value"],
            card["process_risk_value"],
            card["active_axis_distance_pct_points"],
            card["candidate_id"],
        )
    raise KeyError(f"unknown scenario: {scenario}")


def robustness_summary(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Rank candidates under several transparent priorities and report stability."""
    scenarios = ["evidence_first", "robustness_first", "hypothesis_test_first"]
    rankings: dict[str, list[str]] = {}
    rank1 = Counter()
    top3 = Counter()
    for scenario in scenarios:
        ordered = sorted(cards, key=lambda c: _scenario_key(c, scenario))
        ids = [c["candidate_id"] for c in ordered]
        rankings[scenario] = ids
        if ids:
            rank1[ids[0]] += 1
        for cid in ids[:3]:
            top3[cid] += 1

    n = len(scenarios)
    stability = []
    for card in cards:
        cid = card["candidate_id"]
        stability.append(
            {
                "candidate_id": cid,
                "rank1_fraction": rank1[cid] / n if n else 0.0,
                "top3_fraction": top3[cid] / n if n else 0.0,
            }
        )
    stability.sort(key=lambda x: (-x["rank1_fraction"], -x["top3_fraction"], x["candidate_id"]))

    return {
        "pareto_front": pareto_front(cards),
        "scenario_rankings": rankings,
        "scenario_stability": stability,
        "note": (
            "These are transparent decision diagnostics, not fitted property predictions. "
            "They are used to avoid selecting a point from one arbitrary scalar score."
        ),
    }


def validate_planner_actions(requests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not isinstance(requests, list):
        raise ValueError("planner action_requests must be a list")
    normalized: list[dict[str, Any]] = []
    for req in requests:
        if not isinstance(req, dict):
            raise ValueError("each planner action request must be an object")
        name = req.get("name")
        args = req.get("args", {})
        reason = req.get("reason")
        if name not in PLANNER_ACTIONS:
            raise ValueError(f"planner requested unsupported action: {name!r}")
        if not isinstance(args, dict):
            raise ValueError("planner action args must be an object")
        normalized.append({"name": name, "args": args, "reason": reason})
    return normalized


def execute_planned_actions(
    requests: list[dict[str, Any]],
    *,
    include_follow_up: bool,
    blind_target_formulation_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Execute a planner-selected scientific evidence trace behind the firewall."""
    blind_target_formulation_ids = blind_target_formulation_ids or set()
    results: list[dict[str, Any]] = []
    for req in validate_planner_actions(requests):
        name = req["name"]
        args = dict(req["args"])
        formulation_id = args.get("formulation_id")
        if not include_follow_up and formulation_id in blind_target_formulation_ids:
            results.append(
                {
                    "name": name,
                    "args": args,
                    "reason": req.get("reason"),
                    "status": "blocked_by_evidence_firewall",
                    "result": None,
                }
            )
            continue
        try:
            if name == "get_state_aware_rheology_summary":
                value = get_state_aware_rheology_summary_v3()
            else:
                value = execute_action(name, args, include_follow_up=include_follow_up)
            results.append(
                {
                    "name": name,
                    "args": args,
                    "reason": req.get("reason"),
                    "status": "ok",
                    "result": value,
                }
            )
        except Exception as exc:
            results.append(
                {
                    "name": name,
                    "args": args,
                    "reason": req.get("reason"),
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "result": None,
                }
            )
    return results


def selection_entropy(candidate_ids: list[str | None]) -> float:
    """Shannon entropy (bits) of repeated final selections; abstention is a category."""
    if not candidate_ids:
        return 0.0
    counts = Counter("__ABSTAIN__" if x is None else x for x in candidate_ids)
    n = sum(counts.values())
    return -sum((count / n) * math.log2(count / n) for count in counts.values())
