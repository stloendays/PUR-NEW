from __future__ import annotations

from typing import Any

from .actions import candidate_profile


def _axes(candidate: dict[str, Any]) -> dict[str, float | bool | str]:
    profile = candidate_profile(candidate)
    ac = 100.0 * float(profile.get("acrylic_like_fraction") or 0.0)
    tk = 100.0 * float(profile.get("tackifier_like_fraction") or 0.0)
    total = 100.0 * float(profile.get("modifier_fraction") or 0.0)
    return {
        "candidate_id": str(candidate.get("candidate_id")),
        "acrylic_pct_total": ac,
        "tackifier_pct_total": tk,
        "total_modifier_pct_total": total,
        "resin_modified": bool(profile.get("resin_modified")),
    }


def evaluate_candidate(candidate: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    axes = _axes(candidate)
    c = contract["hard_candidate_constraints"]
    failures: list[str] = []

    if c.get("require_resin_modified") and not axes["resin_modified"]:
        failures.append("resin_modified_required")
    if c.get("require_acrylic_like_modifier") and float(axes["acrylic_pct_total"]) <= 0.0:
        failures.append("acrylic_like_modifier_required")
    if c.get("require_minor_tackifier_like_modifier") and float(axes["tackifier_pct_total"]) <= 0.0:
        failures.append("minor_tackifier_like_modifier_required")

    ac = float(axes["acrylic_pct_total"])
    tk = float(axes["tackifier_pct_total"])
    total = float(axes["total_modifier_pct_total"])

    if c.get("acrylic_pct_total_min") is not None and ac < float(c["acrylic_pct_total_min"]):
        failures.append("acrylic_below_min")
    if c.get("acrylic_pct_total_max") is not None and ac > float(c["acrylic_pct_total_max"]):
        failures.append("acrylic_above_max")
    if c.get("tackifier_pct_total_min") is not None and tk < float(c["tackifier_pct_total_min"]):
        failures.append("tackifier_below_min")
    if c.get("tackifier_pct_total_max") is not None and tk > float(c["tackifier_pct_total_max"]):
        failures.append("tackifier_above_max")
    if c.get("total_modifier_pct_total_max") is not None and total > float(c["total_modifier_pct_total_max"]):
        failures.append("total_modifier_above_max")

    priority = (
        total,
        abs(ac - 15.0),
        abs(tk - 5.0),
        str(axes["candidate_id"]),
    )
    return {
        **axes,
        "contract_admissible": not failures,
        "contract_failures": failures,
        "priority_tuple": list(priority),
    }


def evaluate_contract(candidate_set: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    rows = [evaluate_candidate(c, contract) for c in candidate_set["candidates"]]
    eligible = [r for r in rows if r["contract_admissible"]]
    eligible.sort(key=lambda r: tuple(r["priority_tuple"]))
    return {
        "contract_id": contract["contract_id"],
        "mode": contract["mode"],
        "selection_authority": contract["selection_authority"],
        "candidate_audit": rows,
        "eligible_candidate_ids": [r["candidate_id"] for r in eligible],
        "contract_ranked_candidate_ids": [r["candidate_id"] for r in eligible],
        "contract_selected_candidate_id": eligible[0]["candidate_id"] if eligible else None,
        "abstain_required": not eligible,
        "tie_break": contract["deterministic_tie_break"],
        "claim_boundary": contract["claim_boundary"],
    }


def enforce_contract_on_judge(
    judge: dict[str, Any],
    diagnostics: dict[str, Any],
    contract: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply the frozen replay contract after LLM adjudication.

    The LLM still performs planning, evidence integration, proposing, skepticism and
    adjudication. In strict historical replay, the final candidate identity is bounded
    by the deterministic pre-result contract so stochastic language-model preference
    cannot change the replayed experimental decision.
    """
    out = dict(judge)
    model_selected = out.get("selected_candidate_id")
    contract_selected = diagnostics.get("contract_selected_candidate_id")

    audit = {
        "model_selected_candidate_id": model_selected,
        "contract_selected_candidate_id": contract_selected,
        "contract_override_applied": False,
        "reason": None,
    }

    if diagnostics.get("abstain_required"):
        out["decision_mode"] = "abstain"
        out["selected_candidate_id"] = None
        audit["contract_override_applied"] = model_selected is not None
        audit["reason"] = "No candidate satisfied the frozen hard replay constraints."
        return out, audit

    if contract.get("selection_authority") != "hybrid_contract_constrained":
        return out, audit

    if model_selected != contract_selected:
        out["decision_mode"] = "performance_candidate"
        out["selected_candidate_id"] = contract_selected
        existing = str(out.get("selection_rationale") or "")
        out["selection_rationale"] = (
            "Frozen replay contract selected the highest-priority admissible candidate under the "
            "pre-result minimum-intervention rules. The LLM deliberation remains stored separately. "
            + existing
        ).strip()
        audit["contract_override_applied"] = True
        audit["reason"] = (
            "Strict replay uses a deterministic final tie-break after LLM scientific adjudication "
            "to remove stochastic model drift."
        )

    return out, audit
