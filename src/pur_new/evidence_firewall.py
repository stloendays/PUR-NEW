from __future__ import annotations

import copy
from typing import Any


def filter_evidence_state(
    state: dict[str, Any],
    *,
    policy: dict[str, Any],
    blinded_formulation_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Return an evidence-state copy that obeys the active access profile.

    This function is deliberately structural: forbidden rows are removed before any
    LLM payload is assembled, rather than relying on prompt instructions not to use
    information that is already present.
    """
    blinded_formulation_ids = blinded_formulation_ids or set()
    out = copy.deepcopy(state)

    if not policy.get("allow_original_temperature_sweeps", False):
        out["temperature_response"] = {"runs": [], "nominal_repeat_spread": []}

    hold = out.get("thermal_hold", {})
    if not policy.get("allow_original_hold_data", False):
        out["thermal_hold"] = {"runs": [], "follow_up_mean_profiles": []}
    else:
        runs = list(hold.get("runs", []))
        if not policy.get("allow_follow_up_hold_results", False):
            runs = [row for row in runs if row.get("stage") != "follow_up"]
            hold["follow_up_mean_profiles"] = []
        if not policy.get("allow_follow_up_formulation_identity", False):
            runs = [row for row in runs if row.get("formulation_id") not in blinded_formulation_ids]
            hold["follow_up_mean_profiles"] = [
                row
                for row in hold.get("follow_up_mean_profiles", [])
                if row.get("formulation_id") not in blinded_formulation_ids
            ]
        hold["runs"] = runs
        out["thermal_hold"] = hold

    out["evidence_access_filter"] = {
        "profile_description": policy.get("description"),
        "allow_follow_up_formulation_identity": bool(policy.get("allow_follow_up_formulation_identity", False)),
        "allow_follow_up_hold_results": bool(policy.get("allow_follow_up_hold_results", False)),
        "blinded_formulation_ids": sorted(blinded_formulation_ids),
    }
    return out


def find_blind_payload_violations(
    value: Any,
    *,
    blinded_formulation_ids: set[str] | None = None,
    forbid_follow_up_stage: bool = True,
) -> list[str]:
    """Recursively identify structural blind-payload violations."""
    blinded_formulation_ids = blinded_formulation_ids or set()
    findings: list[str] = []

    def walk(node: Any, path: str) -> None:
        if isinstance(node, dict):
            stage = node.get("stage")
            if forbid_follow_up_stage and stage == "follow_up":
                findings.append(f"{path or '$'} contains stage=follow_up")
            fid = node.get("formulation_id")
            if fid in blinded_formulation_ids:
                findings.append(f"{path or '$'} exposes blinded formulation_id={fid}")
            for key, child in node.items():
                walk(child, f"{path}.{key}" if path else str(key))
        elif isinstance(node, list):
            for i, child in enumerate(node):
                walk(child, f"{path}[{i}]")

    walk(value, "")
    return findings


def assert_blind_payload_clean(
    value: Any,
    *,
    blinded_formulation_ids: set[str] | None = None,
    forbid_follow_up_stage: bool = True,
) -> None:
    findings = find_blind_payload_violations(
        value,
        blinded_formulation_ids=blinded_formulation_ids,
        forbid_follow_up_stage=forbid_follow_up_stage,
    )
    if findings:
        joined = "; ".join(findings[:10])
        raise ValueError(f"blind payload leakage detected: {joined}")
