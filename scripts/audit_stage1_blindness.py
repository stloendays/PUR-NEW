#!/usr/bin/env python3
"""Hard structural blindness audit for the Stage-1 pre-result replay test.

This is a programmatic firewall, not a prompt instruction. It inspects every
artifact the Agent runtime can actually reach and refuses to certify a candidate
set whose payloads carry post-result knowledge.

It audits:
  1. the candidate set (posterior coordinates, measurement plans, hold schedules)
  2. the filtered evidence state under the active access profile
  3. the deterministic action layer (including blocked follow-up inspection)
  4. the five stage prompts
  5. every config file the runner reads at runtime

Usage:
    python scripts/audit_stage1_blindness.py --candidate-set <path> [--label ARM_B]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import build_candidate_cards, execute_planned_actions  # noqa: E402
from pur_new.evidence_firewall import (  # noqa: E402
    filter_evidence_state,
    find_blind_payload_violations,
)

# --- Post-result knowledge that must never reach a Stage-1 runtime payload ----

# Measured F1 thermal-hold viscosities (data/thermal_hold.csv, stage=follow_up).
FORBIDDEN_NUMERIC_STRINGS = [
    "1230", "1189", "1203", "1228",  # repeat_1
    "1281", "1260", "1289", "1320",  # repeat_2
]

# Post-result derived statistics and adjudication language.
FORBIDDEN_RESULT_STRINGS = [
    "-0.1626", "0.1626", "3.0445", "1.6035", "1.4735",
    "strong support", "strong_support",
    "successful validation", "successful_candidate", "validated_candidate",
    "target_candidate", "ground_truth_formula", "ground_truth",
    "F1_success", "best_after_experiment",
    "post_result_adjudication", "post-result adjudication",
]

# Exact normalized coordinates of the later wet-lab formulation.
HELD_OUT_AC_PCT = 14.00444847
HELD_OUT_TK_PCT = 4.11895543
EXACT_COORD_TOL = 0.01  # percentage points

BLINDED_FORMULATION_IDS = {"F1"}

RUNTIME_CONFIGS = [
    "configs/agent_v3.json",
    "configs/evidence_access_profiles.json",
    "configs/workflow.json",
    "configs/action_catalog.json",
    "configs/formulation_priors.json",
]
PROMPTS = [
    "prompts/agent_v3_planner.txt",
    "prompts/agent_v3_proposer.txt",
    "prompts/agent_v3_skeptic.txt",
    "prompts/agent_v3_robustness.txt",
    "prompts/agent_v3_judge.txt",
]

# Every allowed planner action, exercised against every formulation the Agent
# could name, so that a blocked path is proven rather than assumed.
PROBE_ACTIONS = [
    {"name": "get_state_aware_rheology_summary", "args": {}},
    {"name": "get_candidate_hypothesis", "args": {}},
    {"name": "query_external_priors", "args": {}},
] + [
    {"name": name, "args": {"formulation_id": fid}}
    for fid in ["E1", "E2", "E3", "E4", "E5", "F1"]
    for name in ["inspect_formulation", "get_hold_stability", "get_repeatability_risk", "get_temperature_support"]
]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# Control-flag / schema-key names that legitimately contain post-result wording
# because they are the switches that KEEP that information out. Their presence is
# not leakage; their VALUE is checked separately by audit_gate_values().
CONTROL_FLAG_NAMES = [
    "allow_post_result_adjudication",
    "post_result_criteria_rewrite_allowed",
    "post_result_record",
    "forbid_adjudication_labels_in_agent_payload",
    "adjudication_is_separate_record",
]


def scan_text(text: str, where: str) -> list[dict[str, str]]:
    findings = []
    for flag in CONTROL_FLAG_NAMES:
        text = text.replace(flag, "<control_flag>")
    lowered = text.lower()
    for token in FORBIDDEN_NUMERIC_STRINGS:
        # Digit boundaries, so a coincidental substring inside a longer number
        # (e.g. "1189" inside "4.11895543") is not misreported as a viscosity value.
        if re.search(rf"(?<![\d.]){token}(?![\d])", text):
            findings.append({"severity": "critical", "where": where, "issue": f"post-result viscosity value {token!r} present"})
    for token in FORBIDDEN_RESULT_STRINGS:
        if token.lower() in lowered:
            findings.append({"severity": "critical", "where": where, "issue": f"post-result label/statistic {token!r} present"})
    return findings


def audit_candidate_set(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    cs = json.loads(path.read_text(encoding="utf-8"))
    findings: list[dict[str, Any]] = []
    exact_hits, plan_hits, hold_hits = [], [], []

    for c in cs["candidates"]:
        fs = c.get("formulation_state", {})
        ac = float(fs.get("AC1920", fs.get("ac1920", 0.0)) or 0.0)
        tk = float(fs.get("TK100", fs.get("tk100", 0.0)) or 0.0)
        if abs(ac - HELD_OUT_AC_PCT) <= EXACT_COORD_TOL and abs(tk - HELD_OUT_TK_PCT) <= EXACT_COORD_TOL:
            exact_hits.append(c["candidate_id"])
        if c.get("measurement_plan"):
            plan_hits.append(c["candidate_id"])
        ps = c.get("process_state", {})
        if ps.get("hold_temperature_c") is not None or ps.get("hold_time_min") is not None:
            hold_hits.append(c["candidate_id"])

    if exact_hits:
        findings.append({
            "severity": "critical",
            "where": str(path),
            "issue": (
                f"candidate(s) {exact_hits} encode the exact held-out normalized coordinates "
                f"(AC={HELD_OUT_AC_PCT}, TK={HELD_OUT_TK_PCT}); selection cannot be called independent discovery"
            ),
        })
    if plan_hits:
        findings.append({
            "severity": "high",
            "where": str(path),
            "issue": f"candidate(s) {plan_hits} carry a pre-specified measurement_plan, which encodes the intended experiment",
        })
    if hold_hits:
        findings.append({
            "severity": "moderate",
            "where": str(path),
            "issue": (
                f"{len(hold_hits)} candidate(s) carry a pre-specified hold temperature/time; this tells the Agent "
                "the experiment is a thermal-hold test and weakens Level-1 (failure-mode) recovery"
            ),
        })
    findings += scan_text(json.dumps(cs, ensure_ascii=False), str(path))

    summary = {
        "candidate_set_id": cs.get("candidate_set_id"),
        "n_candidates": len(cs["candidates"]),
        "sha256": sha256_file(path),
        "exact_heldout_coordinate_candidates": exact_hits,
        "candidates_with_measurement_plan": plan_hits,
        "candidates_with_hold_schedule": len(hold_hits),
        "resin_modified_options": sum(
            1 for c in cs["candidates"]
            if float(c["formulation_state"].get("AC1920", 0) or 0) + float(c["formulation_state"].get("TK100", 0) or 0) > 0
        ),
        "reactive_core_only_options": sum(
            1 for c in cs["candidates"]
            if float(c["formulation_state"].get("AC1920", 0) or 0) + float(c["formulation_state"].get("TK100", 0) or 0) == 0
        ),
    }
    return findings, summary


def audit_evidence(profile_name: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw = json.loads((ROOT / "derived" / "evidence_state.json").read_text(encoding="utf-8"))
    policy = json.loads((ROOT / "configs" / "evidence_access_profiles.json").read_text(encoding="utf-8"))["profiles"][profile_name]
    filtered = filter_evidence_state(raw, policy=policy, blinded_formulation_ids=BLINDED_FORMULATION_IDS)

    findings = scan_text(json.dumps(filtered, ensure_ascii=False), "filtered_evidence_state")
    structural = find_blind_payload_violations(filtered, blinded_formulation_ids=BLINDED_FORMULATION_IDS)
    for item in structural:
        findings.append({"severity": "critical", "where": "filtered_evidence_state", "issue": item})

    hold_ids = sorted({r.get("formulation_id") for r in filtered["thermal_hold"]["runs"]})
    stages = sorted({r.get("stage") for r in filtered["thermal_hold"]["runs"]})
    info = {
        "profile": profile_name,
        "hold_formulations_visible": hold_ids,
        "hold_stages_visible": stages,
        "follow_up_mean_profiles": filtered["thermal_hold"]["follow_up_mean_profiles"],
        "residual_metadata_disclosure": filtered.get("evidence_access_filter", {}).get("blinded_formulation_ids"),
    }
    return findings, info


def audit_actions() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    trace = execute_planned_actions(
        PROBE_ACTIONS,
        include_follow_up=False,
        blind_target_formulation_ids=BLINDED_FORMULATION_IDS,
    )
    findings = scan_text(json.dumps(trace, ensure_ascii=False, default=str), "action_layer_probe")

    for item in trace:
        fid = item["args"].get("formulation_id")
        if fid in BLINDED_FORMULATION_IDS and item["status"] == "ok":
            findings.append({
                "severity": "critical",
                "where": "action_layer_probe",
                "issue": f"action {item['name']}({fid}) returned data instead of being blocked by the firewall",
            })
    status = [
        {"action": i["name"], "formulation_id": i["args"].get("formulation_id"), "status": i["status"]}
        for i in trace
    ]
    return findings, status


def audit_gate_values(profile_name: str) -> list[dict[str, Any]]:
    """Assert that the post-result gates are actually closed for this profile."""
    findings: list[dict[str, Any]] = []
    policy = json.loads(
        (ROOT / "configs" / "evidence_access_profiles.json").read_text(encoding="utf-8")
    )["profiles"][profile_name]
    for gate in (
        "allow_follow_up_formulation_identity",
        "allow_follow_up_hold_results",
        "allow_post_result_adjudication",
    ):
        if policy.get(gate, False):
            findings.append({
                "severity": "critical",
                "where": f"evidence_access_profiles.json::{profile_name}",
                "issue": f"post-result gate {gate} is OPEN",
            })
    workflow = json.loads((ROOT / "configs" / "workflow.json").read_text(encoding="utf-8"))
    if workflow["hard_rules"].get("post_result_criteria_rewrite_allowed", False):
        findings.append({
            "severity": "critical",
            "where": "workflow.json",
            "issue": "post_result_criteria_rewrite_allowed is TRUE; frozen criteria could be rewritten after unblinding",
        })
    return findings


def audit_static_files() -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for rel in PROMPTS + RUNTIME_CONFIGS:
        path = ROOT / rel
        findings += scan_text(path.read_text(encoding="utf-8"), rel)
    return findings


def main() -> None:
    p = argparse.ArgumentParser(description="Stage-1 blindness audit")
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--profile", default="blind_pre_result")
    p.add_argument("--label", default="ARM")
    p.add_argument("--output", type=Path, default=None)
    args = p.parse_args()

    findings: list[dict[str, Any]] = []
    cs_findings, cs_summary = audit_candidate_set(args.candidate_set)
    ev_findings, ev_info = audit_evidence(args.profile)
    ac_findings, ac_status = audit_actions()
    st_findings = audit_static_files()
    gate_findings = audit_gate_values(args.profile)
    findings += cs_findings + ev_findings + ac_findings + st_findings + gate_findings

    critical = [f for f in findings if f["severity"] == "critical"]
    high = [f for f in findings if f["severity"] == "high"]
    verdict = "FAIL" if critical else ("CONDITIONAL" if high else "PASS")

    report = {
        "audit_id": f"STAGE1_BLINDNESS_AUDIT__{args.label}",
        "verdict": verdict,
        "candidate_set": str(args.candidate_set),
        "candidate_set_summary": cs_summary,
        "evidence_firewall": ev_info,
        "action_layer_probe": ac_status,
        "findings": findings,
        "n_critical": len(critical),
        "n_high": len(high),
        "interpretation": {
            "PASS": "No post-result knowledge reachable; independent-discovery scoring is admissible.",
            "CONDITIONAL": "No outcome values leak, but the payload pre-specifies part of the intended experiment.",
            "FAIL": "Post-result knowledge is reachable; results must not be reported as independent discovery.",
        }[verdict],
    }

    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    print(f"VERDICT[{args.label}] = {verdict}  (critical={len(critical)}, high={len(high)})")


if __name__ == "__main__":
    main()
