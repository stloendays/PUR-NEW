from __future__ import annotations

import math
from collections import Counter
from typing import Any

from jsonschema import Draft202012Validator

from .actions import (
    audit_process_unknowns,
    candidate_profile,
    compare_candidate_to_priors,
    execute_action,
    load_formulation_priors,
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
    """Audit-only distance to the nearest external anchors; never a primary rank objective."""
    total = 0.0
    for key in ("acrylic_axis_support", "tackifier_axis_support"):
        item = prior[key]
        distance = item.get("distance_pct_points")
        if distance is not None:
            total += float(distance)
    return total


def _active_modifier_axis_count(prior: dict[str, Any]) -> int:
    return sum(
        prior[key].get("status") != "control_zero"
        for key in ("acrylic_axis_support", "tackifier_axis_support")
    )


def _supported_active_axis_count(prior: dict[str, Any]) -> int:
    supported = {"strong_analogue_region", "moderate_analogue_region"}
    return sum(
        prior[key].get("status") in supported
        for key in ("acrylic_axis_support", "tackifier_axis_support")
    )


AXIS_PRIOR_KEYS = {
    "acrylic_like": ("acrylic_axis_support", "acrylic_like_modifier_pct_total"),
    "minor_tackifier_like": ("tackifier_axis_support", "minor_tackifier_like_modifier_pct_total"),
}


def independently_supported_axes() -> list[str]:
    """Modifier axes carrying their own pre-result external evidence.

    Read from the curated priors rather than hard-coded, so the set of axes that a
    mitigation experiment is expected to cover follows the evidence base.
    """
    axes_cfg = load_formulation_priors().get("candidate_axes", {})
    out = []
    for axis, (_prior_key, cfg_key) in AXIS_PRIOR_KEYS.items():
        anchors = (axes_cfg.get(cfg_key) or {}).get("direct_evidence_anchors_pct") or []
        if anchors:
            out.append(axis)
    return out


def classify_intervention_coverage(prior: dict[str, Any], supported_axes: list[str]) -> dict[str, Any]:
    """Does this candidate cover every independently supported intervention axis?

    Intervention sufficiency is assessed BEFORE perturbation size. Zeroing an axis
    that pre-result evidence independently supports does not make a candidate a
    cheaper version of the same experiment; it makes it a different, partial one.
    """
    supported_status = {"strong_analogue_region", "moderate_analogue_region"}
    covered, zeroed, unsupported = [], [], []
    for axis in supported_axes:
        status = prior[AXIS_PRIOR_KEYS[axis][0]].get("status")
        if status == "control_zero":
            zeroed.append(axis)
        elif status in supported_status:
            covered.append(axis)
        else:
            unsupported.append(axis)

    if not covered and not unsupported:
        coverage_class = "no_intervention"
    elif zeroed or unsupported:
        coverage_class = "partial_coverage"
    else:
        coverage_class = "full_coverage"

    rank = {"full_coverage": 0, "partial_coverage": 1, "no_intervention": 2}[coverage_class]
    return {
        "coverage_class": coverage_class,
        "coverage_rank": rank,
        "covered_supported_axes": covered,
        "zeroed_supported_axes": zeroed,
        "active_but_unsupported_axes": unsupported,
        "role_if_partial": (
            "partial-coverage / mechanistic control: informative about one axis, but it does not "
            "test the full evidence-supported mitigation strategy"
            if coverage_class != "full_coverage"
            else None
        ),
    }


def build_candidate_cards(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build deterministic, outcome-blind scorecards for every admissible candidate."""
    cards: list[dict[str, Any]] = []
    supported_axes = independently_supported_axes()
    for candidate in candidates:
        profile = candidate_profile(candidate)
        prior = compare_candidate_to_priors(candidate)
        process = audit_process_unknowns(candidate)
        stress = stress_test_candidate(candidate)
        missing_count = len(process["missing_process_fields"])
        total_modifier_pct = 100.0 * float(profile["modifier_fraction"] or 0.0)
        card = {
            "candidate_id": candidate["candidate_id"],
            "profile": profile,
            "analogue_support": prior["analogue_support"],
            "support_value": SUPPORT_VALUE[prior["analogue_support"]],
            "active_modifier_axis_count": _active_modifier_axis_count(prior),
            "supported_active_axis_count": _supported_active_axis_count(prior),
            "total_modifier_pct": total_modifier_pct,
            "active_axis_distance_pct_points": _active_axis_distance(prior),
            "active_axis_distance_role": "audit_only_not_primary_rank_objective",
            "process_history_uncertainty": process["process_history_uncertainty"],
            "process_risk_value": RISK_VALUE[stress["risk_level"]],
            "missing_process_field_count": missing_count,
            "resin_modified": bool(profile["resin_modified"]),
            "stress_reasons": stress["reasons"],
            "intervention_coverage": classify_intervention_coverage(prior, supported_axes),
        }
        card["coverage_rank"] = card["intervention_coverage"]["coverage_rank"]
        card["coverage_class"] = card["intervention_coverage"]["coverage_class"]
        cards.append(card)
    return cards


def _dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """Weight-free Pareto dominance over support, hypothesis coverage, and risk."""
    a_obj = (
        a["support_value"],
        int(a["resin_modified"]),
        a["supported_active_axis_count"],
        -a["process_risk_value"],
        -a["missing_process_field_count"],
        -a["total_modifier_pct"],
    )
    b_obj = (
        b["support_value"],
        int(b["resin_modified"]),
        b["supported_active_axis_count"],
        -b["process_risk_value"],
        -b["missing_process_field_count"],
        -b["total_modifier_pct"],
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
            -card["supported_active_axis_count"],
            card["process_risk_value"],
            card["total_modifier_pct"],
            card["missing_process_field_count"],
            card["candidate_id"],
        )
    if scenario == "robustness_first":
        return (
            card["process_risk_value"],
            card["missing_process_field_count"],
            -card["support_value"],
            -card["supported_active_axis_count"],
            card["total_modifier_pct"],
            card["candidate_id"],
        )
    if scenario == "performance_mitigation":
        # Intervention sufficiency FIRST, perturbation size only as a tie-break among
        # candidates that already cover every independently supported axis. A lower
        # modifier burden obtained by zeroing a supported axis is a different (partial)
        # experiment, not a cheaper version of the same one.
        return (
            card.get("coverage_rank", 0),
            -int(card["resin_modified"]),
            -card["supported_active_axis_count"],
            -card["support_value"],
            card["total_modifier_pct"],
            card["process_risk_value"],
            card["candidate_id"],
        )
    if scenario == "causal_isolation":
        single_axis_penalty = 0 if card["active_modifier_axis_count"] == 1 else 1
        return (
            single_axis_penalty,
            -card["support_value"],
            card["total_modifier_pct"],
            card["process_risk_value"],
            card["candidate_id"],
        )
    raise KeyError(f"unknown scenario: {scenario}")

def robustness_summary(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Rank candidates under several transparent priorities and report stability."""
    supported_axes = independently_supported_axes()
    scenarios = ["evidence_first", "robustness_first", "performance_mitigation", "causal_isolation"]
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

    coverage_groups: dict[str, list[str]] = {}
    for card in sorted(cards, key=lambda c: c["candidate_id"]):
        coverage_groups.setdefault(card.get("coverage_class", "unclassified"), []).append(card["candidate_id"])

    return {
        "pareto_front": pareto_front(cards),
        "scenario_rankings": rankings,
        "scenario_stability": stability,
        "independently_supported_intervention_axes": supported_axes,
        "intervention_coverage_groups": coverage_groups,
        "intervention_sufficiency_rule": (
            "Decision order is: failure mode -> experiment intent -> required intervention-axis "
            "coverage -> evidence-supported candidates -> minimum sufficient intervention. "
            "For performance_mitigation, candidates covering EVERY independently supported axis "
            f"({', '.join(supported_axes)}) are compared first. Minimum sufficient intervention is a "
            "tie-break WITHIN that group only. A candidate that zeroes an independently supported "
            "axis is a partial-coverage / mechanistic control, not the default performance rank-1; "
            "it must not become rank-1 merely because zeroing that axis lowers modifier burden."
        ),
        "note": (
            "These are transparent decision diagnostics, not fitted property predictions. "
            "Exact literature-anchor distance is retained only for audit and is not a primary ranking objective. "
            "Performance-mitigation and causal-isolation scenarios are separated so that single-factor attribution is not the default for every experiment."
        ),
    }


def validate_planner_actions(
    requests: list[dict[str, Any]],
    *,
    action_schemas: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
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
        if action_schemas and name in action_schemas:
            errors = sorted(
                Draft202012Validator(action_schemas[name]).iter_errors(args),
                key=lambda err: list(err.path),
            )
            if errors:
                detail = "; ".join(err.message for err in errors)
                raise ValueError(f"planner action args violate schema for {name}: {detail}")
        normalized.append({"name": name, "args": args, "reason": reason})
    return normalized


def execute_planned_actions(
    requests: list[dict[str, Any]],
    *,
    include_follow_up: bool,
    blind_target_formulation_ids: set[str] | None = None,
    action_schemas: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Execute a planner-selected scientific evidence trace behind the firewall.

    A single malformed action request degrades that one request only. It must not
    abort the whole evidence trace, because losing the external-evidence rows
    silently biases the decision toward whichever axis happens to survive.
    """
    blind_target_formulation_ids = blind_target_formulation_ids or set()
    results: list[dict[str, Any]] = []
    raw_requests = requests if isinstance(requests, list) else []
    for raw_req in raw_requests:
        try:
            req = validate_planner_actions([raw_req], action_schemas=action_schemas)[0]
        except Exception as exc:
            results.append(
                {
                    "name": raw_req.get("name") if isinstance(raw_req, dict) else None,
                    "args": raw_req.get("args") if isinstance(raw_req, dict) else None,
                    "reason": raw_req.get("reason") if isinstance(raw_req, dict) else None,
                    "status": "invalid_arguments",
                    "error": f"{type(exc).__name__}: {exc}",
                    "result": None,
                }
            )
            continue
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
