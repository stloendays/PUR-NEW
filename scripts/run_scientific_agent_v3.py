#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import validate
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import build_candidate_cards, execute_planned_actions, robustness_summary  # noqa: E402
from pur_new.evidence_firewall import assert_blind_payload_clean, filter_evidence_state  # noqa: E402


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
) -> tuple[dict[str, Any], dict[str, Any]]:
    start = time.perf_counter()
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
    elapsed = time.perf_counter() - start
    content = response.choices[0].message.content
    if not content:
        raise ValueError("model returned empty content")
    usage = getattr(response, "usage", None)
    meta = {
        "model": model,
        "latency_s": elapsed,
        "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage is not None else None,
        "completion_tokens": getattr(usage, "completion_tokens", None) if usage is not None else None,
        "total_tokens": getattr(usage, "total_tokens", None) if usage is not None else None,
    }
    return extract_json_object(content), meta


def aggregate_usage(stage_usage: dict[str, dict[str, Any]]) -> dict[str, Any]:
    def total(key: str) -> int | None:
        values = [item.get(key) for item in stage_usage.values() if item.get(key) is not None]
        return int(sum(values)) if values else None

    return {
        "llm_calls": len(stage_usage),
        "prompt_tokens": total("prompt_tokens"),
        "completion_tokens": total("completion_tokens"),
        "total_tokens": total("total_tokens"),
        "llm_latency_s": sum(float(item.get("latency_s", 0.0)) for item in stage_usage.values()),
    }


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
        if not isinstance(alt, dict):
            raise ValueError("each alternative must be an object")
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


# One retrieval per modifier axis, identical in form. Symmetry is the point: if only
# one axis's external rows reach the Proposer, the decision is biased toward that axis
# regardless of what the evidence says.
EXTERNAL_EVIDENCE_AXES = [
    ("acrylic", "Independent external evidence for the acrylic-like modifier axis."),
    ("tackifier", "Independent external evidence for the minor tackifier-like modifier axis."),
]


def ensure_core_scientific_action(action_requests: Any) -> list[dict[str, Any]]:
    """Guarantee the evidence layer the architecture declares as required.

    The Planner requests actions but never sees their results, so a Planner that
    omits or misnames an external-evidence call silently removes that axis from the
    Proposer's evidence. Both modifier axes are therefore retrieved unconditionally.
    """
    requests = list(action_requests) if isinstance(action_requests, list) else []

    for modifier_type, reason in reversed(EXTERNAL_EVIDENCE_AXES):
        already = any(
            isinstance(req, dict)
            and req.get("name") == "query_external_priors"
            and str((req.get("args") or {}).get("modifier_type") or "").lower() == modifier_type
            for req in requests
        )
        if not already:
            requests.insert(0, {
                "name": "query_external_priors",
                "args": {"modifier_type": modifier_type},
                "reason": reason,
            })

    if not any(isinstance(req, dict) and req.get("name") == "get_state_aware_rheology_summary" for req in requests):
        requests.insert(
            0,
            {
                "name": "get_state_aware_rheology_summary",
                "args": {},
                "reason": "Required upstream physical/model evidence before candidate ranking.",
            },
        )
    return requests


def withhold_deterministic_ranking(diagnostics: dict[str, Any]) -> dict[str, Any]:
    """Keep the admissibility gate, remove the precomputed answer.

    The coverage gate, the sufficiency rule and the per-candidate evidence attributes
    are decision INPUT and stay. The scenario orderings and rank-1 stability counts are
    a precomputed ranking: if they are shown, agreement with them cannot be separated
    from the model reading them off. They are withheld here and retained in full in the
    deliberation record for post-hoc attribution.
    """
    out = json.loads(json.dumps(diagnostics))
    rankings = out.pop("scenario_rankings", {})
    out.pop("scenario_stability", None)
    out["admissible_candidates_by_scenario"] = {
        scenario: sorted(ids) for scenario, ids in rankings.items()
    }
    # The Pareto front is a set rather than an order, but on this candidate space its
    # intersection with the full-coverage group is only two candidates, one of which is
    # the deterministic rank-1. Shown alongside the coverage gate it would narrow 36
    # admissible candidates to 2, which is the precomputed answer in another form.
    out.pop("pareto_front", None)
    out["ranking_disclosure"] = (
        "Scenario orderings and rank-1 stability are deliberately withheld. Candidate "
        "identifiers are listed in lexicographic order, which carries no preference. "
        "Select within the evidence-supported admissible set by reasoning from the "
        "candidate evidence attributes and the intervention sufficiency rule; there is "
        "no precomputed best candidate to defer to."
    )
    return out


def normalize_judge_output(raw: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Preserve prose while coercing schema-designated numeric slots to number/null.

    Some OpenAI-compatible models occasionally place explanatory prose in numeric-only
    uncertainty fields. This normalization does not change the decision, candidate,
    rationale, or evidence. It moves that prose into the adjacent note field and records
    every coercion for auditability before schema validation and freeze.
    """
    out = json.loads(json.dumps(raw))
    changes: list[dict[str, Any]] = []

    # --- null selection is an abstention ---------------------------------------
    # The Judge prompt declares "selected_candidate_id": "string or null" for every
    # decision mode, while freeze_recommendation accepts null only for "abstain".
    # A probe that names no candidate IS a refusal to choose one, so it is recorded
    # as an abstention. No selection is invented; the original mode is logged and the
    # untouched judge_raw is retained in the deliberation record.
    if out.get("selected_candidate_id") is None and out.get("decision_mode") not in (None, "abstain"):
        changes.append({
            "path": "decision_mode",
            "original": out.get("decision_mode"),
            "coerced_to": "abstain",
            "basis": "selected_candidate_id was null; a decision naming no candidate is an abstention",
        })
        out["decision_mode"] = "abstain"

    # --- constraint status enum -------------------------------------------------
    # The model reports audit-style verdicts ("qualified", "satisfied") where the
    # record schema allows only pass/fail/unknown. The original wording is preserved
    # in `detail` so no assessment is lost.
    constraints = out.get("constraints")
    if isinstance(constraints, list):
        for item in constraints:
            if not isinstance(item, dict):
                continue
            status = item.get("status")
            if status not in {"pass", "fail", "unknown"}:
                item["detail"] = (
                    f"{item.get('detail')}; model status text: {status}"
                    if item.get("detail")
                    else f"model status text: {status}"
                )
                item["status"] = "unknown"
                changes.append({"path": "constraints[].status", "original": status, "coerced_to": "unknown"})

    # --- alternatives hygiene ---------------------------------------------------
    # Echoing the selected candidate inside alternatives, or repeating one, is a
    # redundancy rather than a different decision. The selection itself is untouched.
    alternatives = out.get("alternatives_considered")
    if isinstance(alternatives, list):
        selected_id = out.get("selected_candidate_id")
        deduped, seen = [], set()
        for alt in alternatives:
            if not isinstance(alt, dict):
                continue
            alt_id = alt.get("candidate_id")
            if selected_id is not None and alt_id == selected_id:
                changes.append({"path": "alternatives_considered", "original": alt_id, "coerced_to": "dropped_selected_echo"})
                continue
            if alt_id in seen:
                changes.append({"path": "alternatives_considered", "original": alt_id, "coerced_to": "dropped_duplicate"})
                continue
            seen.add(alt_id)
            deduped.append(alt)
        out["alternatives_considered"] = deduped

    uncertainty = out.get("uncertainty")
    if not isinstance(uncertainty, dict):
        return out, changes

    for key in ("measurement", "repeatability", "process_history", "extrapolation", "evidence_coverage"):
        item = uncertainty.get(key)
        if not isinstance(item, dict):
            continue
        value = item.get("value")
        if value is None or isinstance(value, (int, float)) and not isinstance(value, bool):
            continue
        prior_note = item.get("note")
        moved = str(value)
        item["value"] = None
        item["note"] = f"{prior_note}; model value text: {moved}" if prior_note else f"model value text: {moved}"
        changes.append({"path": f"uncertainty.{key}.value", "original": value, "coerced_to": None})

    for key in ("aggregate_penalty", "decision_margin"):
        value = uncertainty.get(key)
        if value is None or isinstance(value, (int, float)) and not isinstance(value, bool):
            continue
        uncertainty[key] = None
        changes.append({"path": f"uncertainty.{key}", "original": value, "coerced_to": None})

    return out, changes


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PUR-NEW discovery-to-experiment Agent V3")
    parser.add_argument("--candidate-set", type=Path, required=True)
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--profile", default=None)
    parser.add_argument(
        "--inspection-status",
        required=True,
        choices=["no_results_inspected", "some_results_inspected", "unknown"],
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "records" / "agent_v3")
    parser.add_argument(
        "--hide-deterministic-ranking",
        action="store_true",
        help=(
            "Withhold scenario orderings and rank-1 stability from the model payloads so the "
            "Agent must select within the admissible set itself. The full diagnostics are still "
            "stored in deliberation.json for attribution."
        ),
    )
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
    blind_identity_ids = blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()
    if blind_mode:
        assert_blind_payload_clean(evidence, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)

    prompts: dict[str, str] = {}
    for stage in architecture["stages"]:
        if "prompt" in stage:
            prompts[stage["id"]] = (ROOT / stage["prompt"]).read_text(encoding="utf-8")
    required_prompt_stages = {"planner", "proposer", "skeptic", "robustness_adjudicator", "judge"}
    missing_prompts = required_prompt_stages - prompts.keys()
    if missing_prompts:
        raise SystemExit(f"missing V3 prompts: {sorted(missing_prompts)}")
    prompt_hash = sha256_bytes(canonical_json_bytes({stage: prompts[stage] for stage in sorted(prompts)}))

    api_key = os.environ.get("OPENAI_API_KEY")
    base_model = os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")
    if not base_model:
        raise SystemExit("OPENAI_MODEL is required")

    stage_models = {
        stage: os.environ.get(f"OPENAI_MODEL_{stage.upper()}", base_model)
        for stage in required_prompt_stages
    }
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    stage_usage: dict[str, dict[str, Any]] = {}

    planner_action_names = {
        "query_external_priors",
        "get_candidate_hypothesis",
        "inspect_formulation",
        "get_hold_stability",
        "get_repeatability_risk",
        "get_temperature_support",
        "get_state_aware_rheology_summary",
    }
    planner_action_specs = [
        {
            "name": a["name"],
            "description": a.get("description"),
            "when_to_use": a.get("when_to_use", []),
            "parameters": a.get("parameters", {"type": "object", "additionalProperties": True}),
        }
        for a in action_catalog["actions"]
        if a["name"] in planner_action_names
    ]
    planner_action_specs.sort(key=lambda item: item["name"])
    planner_action_schemas = {item["name"]: item["parameters"] for item in planner_action_specs}
    # The Planner classifies experiment intent but never sees the tool trace, so the
    # external rows for BOTH modifier axes are supplied directly and symmetrically.
    # Retrieval is deterministic and outcome-blind (data/external_evidence_hints.csv).
    from pur_new.actions import query_external_priors as _query_external_priors  # noqa: E402

    external_evidence_digest = {
        modifier_type: _query_external_priors(modifier_type=modifier_type)
        for modifier_type, _reason in EXTERNAL_EVIDENCE_AXES
    }

    planner_payload = {
        "architecture_version": architecture["version"],
        "workflow_policy": workflow,
        "evidence_profile": profile_name,
        "evidence_policy": policy,
        "allowed_planner_actions": planner_action_specs,
        "external_evidence_digest": external_evidence_digest,
        "filtered_evidence_state": evidence,
        "candidate_space_summary": candidate_set.get("provenance", {}),
        "candidate_ids": [c["candidate_id"] for c in candidate_set["candidates"]],
    }
    if blind_mode:
        assert_blind_payload_clean(planner_payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)

    planner, stage_usage["planner"] = call_json(
        client,
        model=stage_models["planner"],
        system_prompt=prompts["planner"],
        payload=planner_payload,
    )

    action_requests = ensure_core_scientific_action(planner.get("action_requests", []))
    tool_trace = execute_planned_actions(
        action_requests,
        include_follow_up=bool(policy.get("allow_follow_up_hold_results", False)),
        blind_target_formulation_ids=blinded_ids,
        action_schemas=planner_action_schemas,
    )
    cards = build_candidate_cards(candidate_set["candidates"])
    deterministic_robustness = robustness_summary(cards)
    deterministic_for_model = (
        withhold_deterministic_ranking(deterministic_robustness)
        if args.hide_deterministic_ranking
        else deterministic_robustness
    )

    proposer_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_set": candidate_set,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_for_model,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(proposer_payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)
    proposer, stage_usage["proposer"] = call_json(
        client,
        model=stage_models["proposer"],
        system_prompt=prompts["proposer"],
        payload=proposer_payload,
    )

    skeptic_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_for_model,
        "proposer": proposer,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(skeptic_payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)
    skeptic, stage_usage["skeptic"] = call_json(
        client,
        model=stage_models["skeptic"],
        system_prompt=prompts["skeptic"],
        payload=skeptic_payload,
    )

    robustness_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_set": candidate_set,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_for_model,
        "proposer": proposer,
        "skeptic": skeptic,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(robustness_payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)
    robustness_adjudication, stage_usage["robustness_adjudicator"] = call_json(
        client,
        model=stage_models["robustness_adjudicator"],
        system_prompt=prompts["robustness_adjudicator"],
        payload=robustness_payload,
    )

    judge_payload = {
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_set": candidate_set,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_for_model,
        "proposer": proposer,
        "skeptic": skeptic,
        "robustness_adjudication": robustness_adjudication,
        "evidence_policy": policy,
    }
    if blind_mode:
        assert_blind_payload_clean(judge_payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True)
    judge_raw, stage_usage["judge"] = call_json(
        client,
        model=stage_models["judge"],
        system_prompt=prompts["judge"],
        payload=judge_payload,
    )
    judge, judge_normalization = normalize_judge_output(judge_raw)

    input_payload = {
        "architecture": architecture,
        "evidence_profile": profile_name,
        "filtered_evidence_state": evidence,
        "candidate_set": candidate_set,
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_for_model,
        "proposer": proposer,
        "skeptic": skeptic,
        "robustness_adjudication": robustness_adjudication,
    }
    input_hash = sha256_bytes(canonical_json_bytes(input_payload))

    try:
        recommendation = freeze_recommendation(
            judge,
            candidate_set=candidate_set,
            inspection_status=args.inspection_status,
            model=stage_models["judge"],
            prompt_hash=prompt_hash,
            input_hash=input_hash,
            workflow_version=workflow["workflow_version"],
            architecture_version=architecture["version"],
        )
        validate(recommendation, recommendation_schema)
    except Exception as exc:
        # An unfreezable Judge output is a real invalid decision and must stay a
        # failure. Its deliberation is still written, so the run can be audited
        # rather than vanishing from the record.
        reject_dir = args.output_dir / "REJECTED"
        reject_dir.mkdir(parents=True, exist_ok=True)
        (reject_dir / "rejected_deliberation.json").write_text(
            json.dumps(
                {
                    "rejection_reason": f"{type(exc).__name__}: {exc}",
                    "planner": planner,
                    "tool_trace": tool_trace,
                    "proposer": proposer,
                    "skeptic": skeptic,
                    "robustness_adjudication": robustness_adjudication,
                    "judge_raw": judge_raw,
                    "judge_normalized": judge,
                    "judge_normalization": judge_normalization,
                    "candidate_ids": [c["candidate_id"] for c in candidate_set["candidates"]],
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        raise

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
        "stage_models": stage_models,
        "llm_usage_by_stage": stage_usage,
        "llm_usage_total": aggregate_usage(stage_usage),
        "planner": planner,
        "tool_trace": tool_trace,
        "candidate_scorecards": cards,
        "deterministic_decision_diagnostics": deterministic_robustness,
        "deterministic_diagnostics_sent_to_model": deterministic_for_model,
        "deterministic_ranking_hidden": bool(args.hide_deterministic_ranking),
        "proposer": proposer,
        "skeptic": skeptic,
        "robustness_adjudication": robustness_adjudication,
        "judge_raw": judge_raw,
        "judge_normalized": judge,
        "judge_normalization": judge_normalization,
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
