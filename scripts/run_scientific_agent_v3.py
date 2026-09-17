#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import validate
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import (  # noqa: E402
    build_candidate_cards,
    execute_planned_actions,
    robustness_summary,
)
from pur_new.evidence_firewall import (  # noqa: E402
    assert_blind_payload_clean,
    filter_evidence_state,
)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start, end = stripped.find("{"), stripped.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model output did not contain a JSON object")
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("model output must be a JSON object")
    return value


def call_json(
    client: OpenAI,
    *,
    model: str,
    system_prompt: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Use only the supplied payload and return JSON only.\n\n"
                + json.dumps(payload, ensure_ascii=False, sort_keys=True),
            },
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise ValueError("model returned empty content")
    return extract_json_object(content)


def candidate_map(candidate_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["candidate_id"]: c for c in candidate_set["candidates"]}


def freeze_recommendation(
    raw: dict[str, Any],
    *,
    candidate_set: dict[str, Any],
    inspection_status: str,
    model: str,
    prompt_hash: str,
    input_hash: str,
    workflow_version: str,
    architecture_version: str,
) -> dict[str, Any]:
    allowed_modes = {"performance_candidate", "robustness_probe", "uncertainty_probe", "abstain"}
    mode = raw.get("decision_mode")
    if mode not in allowed_modes:
        raise ValueError(f"invalid decision_mode: {mode!r}")

    candidates = candidate_map(candidate_set)
    selected_id = raw.get("selected_candidate_id")
    if mode == "abstain":
        if selected_id is not None:
            raise ValueError("abstain requires selected_candidate_id=null")
        selected = None
    else:
        if selected_id not in candidates:
            raise ValueError("selected_candidate_id must be present in candidate set")
        c = candidates[selected_id]
        selected = {
            "candidate_id": selected_id,
            "formulation_state": c["formulation_state"],
            "process_state": c["process_state"],
            "measurement_plan": c.get("measurement_plan"),
        }

    alternatives = raw.get("alternatives_considered", [])
    if not isinstance(alternatives, list):
        raise ValueError("alternatives_considered must be a list")
    seen: set[str] = set()
    for alt in alternatives:
        alt_id = alt.get("candidate_id")
        if alt_id not in candidates:
            raise ValueError(f"alternative not in candidate set: {alt_id!r}")
        if selected_id is not None and alt_id == selected_id:
            raise ValueError("selected candidate repeated in alternatives")
        if alt_id in seen:
            raise ValueError(f"duplicate alternative: {alt_id!r}")
        seen.add(alt_id)
    if mode != "abstain" and len(candidates) >= 3 and len(alternatives) < 2:
        raise ValueError("non-abstaining recommendation requires at least two alternatives")

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rec_seed = canonical_json_bytes(
        {
            "created_utc": created,
            "selected_candidate_id": selected_id,
            "input_hash": input_hash,
            "model": model,
            "architecture_version": architecture_version,
        }
    )
    recommendation_id = f"REC_V3_{created.replace(':', '').replace('-', '')}_{sha256_bytes(rec_seed)[:10]}"

    return {
        "recommendation_id": recommendation_id,
        "created_utc": created,
        "record_status": "frozen",
        "result_inspection_status_at_creation": inspection_status,
        "decision_mode": mode,
        "selected_candidate": selected,
        "alternatives_considered": alternatives,
        "constraints": raw.get("constraints", []),
        "uncertainty": raw["uncertainty"],
        "selection_rationale": raw["selection_rationale"],
        "acceptance_criterion": raw["acceptance_criterion"],
        "provenance": {
            "generated_by": "agent",
            "git_commit": current_git_commit(),
            "run_id": recommendation_id,
            "model": model,
            "prompt_hash": prompt_hash,
            "input_hash": input_hash,
            "workflow_version": f"{workflow_version};agent_v3={architecture_version}",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PUR-NEW multi-stage scientific decision Agent V3")
    parser.add_argument("--candidate-set", type=Path, required=True)
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--profile", default=None)
    parser.add_argument(
        "--inspection-status",
        required=True,
        choices=["no_results_inspected", "some_results_inspected", "unknown"],
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "records" / "agent_v3")
    args = parser.parse_args()

    architecture = read_json(ROOT / "configs" / "agent_v3.json")
    profile_name = args.profile or architecture["default_evidence_profile"]
    access_profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    if profile_name not in access_profiles:
        raise SystemExit(f"unknown evidence profile: {profile_name}")
    policy = access_profiles[profile_name]

    workflow = read_json(ROOT / "configs" / "workflow.json")
    action_catalog = read_json(ROOT / "configs" / "action_catalog.json")
    candidate_set = read_json(args.candidate_set)
    raw_evidence = read_json(args.evidence_state)
    candidate_schema = read_json(ROOT / "schemas" / "candidate_set.schema.json")
    recommendation_schema = read_json(ROOT / "schemas" / "agent_recommendation.schema.json")
    validate(candidate_set, candidate_schema)

    blinded_ids = set(architecture.get("blinded_target_formulation_ids", []))
    evidence = filter_evidence_state(raw_evidence, policy=policy, blinded_formulation_ids=blinded_ids)

    blind_mode = not bool(policy.get("allow_follow_up_hold_results", False))
    if blind_mode:
        assert_blind_payload_clean(
            evidence,
            blinded_formulation_ids=(
                blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()
            ),
            forbid_follow_up_stage=True,
        )

    prompts: dict[str, str] = {}
    for stage in architecture["stages"]:
        if "prompt" in stage:
            path = ROOT / stage["prompt"]
            prompts[stage["id"]] = path.read_text(encoding="utf-8")
    prompt_hash = sha256_bytes(
        canonical_json_bytes({stage: prompts[stage] for stage in sorted(prompts)})
    )

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")
    if not model:
        raise SystemExit("OPENAI_MODEL is required")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)

    planner_action_names = {
        "query_external_priors",
        "get_candidate_hypothesis",
        "inspect_formulation",
        "get_hold_stability",
        "get_repeatability_risk",
        "get_temperature_support",
        "get_state_aware_rheology_summary",
    }
    planner_payload = {
        "architecture_version": architecture["version"],
        "workflow_policy": workflow,
        "evidence_profile": profile_name,
        "evidence_policy": policy,
        "allowed_planner_actions": sorted(
            [a["name"] for a in action_catalog["actions"] if a["name"] in planner_action_names]
        ),
        "filtered_evidence_state": evidence,
        "candidate_space_summary": candidate_set.get("provenance", {}),
        "candidate_ids": [c["candidate_id"] for c in candidate_set["candidates"]],
    }
    if blind_mode:
        assert_blind_payload_clean(
            planner_payload,
            blinded_formulation_ids=(
                blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()
            ),
            forbid_follow_up_stage=True,
        )

    planner = call_json(client, model=model, system_prompt=prompts["planner"], payload=planner_payload)
    tool_trace = execute_planned_actions(
        planner.get("action_requests", []),
        include_follow_up=bool(policy.get("allow_follow_up_hold_results", False)),
        blind_target_formulation_ids=blinded_ids,
    )

    cards = build_candidate_cards(candidate_set["candidates"])
    robustness = robustness_summary(cards)

    proposer_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_set": candidate_set,
        "candidate_scorecards": cards,
        "deterministic_robustness": robustness,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(
            proposer_payload,
            blinded_formulation_ids=(
                blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()
            ),
            forbid_follow_up_stage=True,
        )
    proposer = call_json(client, model=model, system_prompt=prompts["proposer"], payload=proposer_payload)

    skeptic_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_robustness": robustness,
        "proposer": proposer,
        "evidence_policy": policy,
    }
    skeptic = call_json(client, model=model, system_prompt=prompts["skeptic"], payload=skeptic_payload)

    judge_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_set": candidate_set,
        "candidate_scorecards": cards,
        "deterministic_robustness": robustness,
        "proposer": proposer,
        "skeptic": skeptic,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(
            judge_payload,
            blinded_formulation_ids=(
                blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()
            ),
            forbid_follow_up_stage=True,
        )
    judge = call_json(client, model=model, system_prompt=prompts["judge"], payload=judge_payload)

    input_payload = {
        "architecture": architecture,
        "evidence_profile": profile_name,
        "filtered_evidence_state": evidence,
        "candidate_set": candidate_set,
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_robustness": robustness,
        "proposer": proposer,
        "skeptic": skeptic,
    }
    input_hash = sha256_bytes(canonical_json_bytes(input_payload))

    recommendation = freeze_recommendation(
        judge,
        candidate_set=candidate_set,
        inspection_status=args.inspection_status,
        model=model,
        prompt_hash=prompt_hash,
        input_hash=input_hash,
        workflow_version=workflow["workflow_version"],
        architecture_version=architecture["version"],
    )
    validate(recommendation, recommendation_schema)

    run_dir = args.output_dir / recommendation["recommendation_id"]
    if run_dir.exists():
        raise SystemExit(f"Refusing to overwrite frozen V3 run: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    deliberation = {
        "architecture": architecture,
        "evidence_profile": profile_name,
        "evidence_policy": policy,
        "filtered_evidence_hash": sha256_bytes(canonical_json_bytes(evidence)),
        "candidate_set_hash": sha256_bytes(canonical_json_bytes(candidate_set)),
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_robustness": robustness,
        "proposer": proposer,
        "skeptic": skeptic,
        "judge_raw": judge,
        "recommendation_id": recommendation["recommendation_id"],
    }
    (run_dir / "deliberation.json").write_text(
        json.dumps(deliberation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "recommendation.json").write_text(
        json.dumps(recommendation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(run_dir)


if __name__ == "__main__":
    main()
