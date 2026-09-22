#!/usr/bin/env python3
"""Agent V5: chemistry-gated, outcome-blind selection of the next scientific experiment.

V5 is a new prospective runtime. It does not modify, re-run or reinterpret the frozen V4
series. It keeps the five V4 model stages and adds one deterministic scientific layer: a
measurement-admissibility gate that executes the chemistry boundary of the locally
discovered shared thermal-response shape before any value-of-information ranking.

Both primary arms run from this single code path. Under comparison protocol v1.1 the
chemistry applicability audit is computed once, is fully visible to the model in both
arms, and the arms differ only in enforcement:

  * ``V5_NO_GATE``  advice-only: every audited card stays selectable;
  * ``V5_FULL``     the same audit is binding before VOI ranking and again at freeze.

Everything else -- prompts, model endpoint, candidate lattice, hypothesis registry,
measurement catalog, evidence profile, VOI weights -- is identical between the arms, and
the model-visible pre-enforcement payload hash is written into every run so the parity can
be checked on the frozen records rather than asserted in prose.
"""

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

from pur_new.agent_v5 import (  # noqa: E402
    APPLICABILITY_TOOL,
    ARM_ENFORCES_GATE,
    ARMS,
    MANDATORY_LOCAL_SCIENCE_TOOL,
    V5_PLANNER_ACTIONS,
    InadmissibleSelectionError,
    audit_experiment_cards,
    audit_summary,
    build_voi_payload,
    decision_stability,
    ensure_mandatory_tools,
    execute_planned_actions,
    freeze_experiment,
    load_verified_shape_transfer,
    mandatory_tool_executed,
    normalize_judge_output,
    ranked_cards,
    tied_top_set,
)
from pur_new.evidence_firewall import assert_blind_payload_clean, filter_evidence_state  # noqa: E402
from pur_new.conditions import load_condition  # noqa: E402
from pur_new.voi import (  # noqa: E402
    BASE_WEIGHTS,
    VOI_FORMULA,
    build_experiment_cards,
    load_hypothesis_registry,
    load_measurement_catalog,
)

REQUIRED_STAGES = ("planner", "proposer", "skeptic", "robustness_adjudicator", "judge")

EXIT_INVALID_MODEL_OUTPUT = 3


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return sha256_bytes(canonical_json_bytes(value))


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


def main() -> None:
    parser = argparse.ArgumentParser(description="PUR-NEW Agent V5 chemistry-gated experiment selection")
    parser.add_argument("--arm", choices=list(ARMS), required=True)
    parser.add_argument("--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json")
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--inspection-status", default="frozen_pre_result")
    parser.add_argument(
        "--condition",
        default=None,
        help=(
            "named decision condition from configs/decision_conditions.json. It fixes the "
            "hypothesis registry, the measurement catalog and the VOI weights. Both arms of a "
            "comparison must run under the same condition. Defaults to the declared default."
        ),
    )
    args = parser.parse_args()

    gate_enforced = ARM_ENFORCES_GATE[args.arm]

    architecture = read_json(ROOT / "configs" / "agent_v5.json")
    access_profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    profile_name = args.profile or architecture["default_evidence_profile"]
    policy = access_profiles[profile_name]
    workflow = read_json(ROOT / "configs" / "workflow.json")
    action_catalog = read_json(ROOT / "configs" / "action_catalog.json")
    candidate_set = read_json(args.candidate_set)
    raw_evidence = read_json(args.evidence_state)
    condition = load_condition(args.condition)
    registry = condition["registry"]
    catalog = condition["catalog"]
    voi_weights = condition["weights"] or dict(BASE_WEIGHTS)
    verified = load_verified_shape_transfer()
    recommendation_schema = read_json(ROOT / "schemas" / "agent_v5_experiment.schema.json")

    blinded_ids = set(architecture.get("blinded_target_formulation_ids", []))
    evidence = filter_evidence_state(raw_evidence, policy=policy, blinded_formulation_ids=blinded_ids)
    blind_mode = not bool(policy.get("allow_follow_up_hold_results", False))
    blind_identity_ids = blinded_ids if not policy.get("allow_follow_up_formulation_identity", False) else set()

    def guard(payload: dict[str, Any]) -> None:
        if blind_mode:
            assert_blind_payload_clean(
                payload, blinded_formulation_ids=blind_identity_ids, forbid_follow_up_stage=True
            )

    guard(evidence)

    prompts = {
        stage["id"]: (ROOT / stage["prompt"]).read_text(encoding="utf-8")
        for stage in architecture["stages"]
        if "prompt" in stage
    }
    missing = set(REQUIRED_STAGES) - prompts.keys()
    if missing:
        raise SystemExit(f"missing V5 prompts: {sorted(missing)}")
    prompt_hash = canonical_hash({stage: prompts[stage] for stage in sorted(prompts)})

    api_key = os.environ.get("OPENAI_API_KEY")
    base_model = os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not base_model:
        raise SystemExit("OPENAI_API_KEY and OPENAI_MODEL are required")
    stage_models = {
        stage: os.environ.get(f"OPENAI_MODEL_{stage.upper()}", base_model) for stage in REQUIRED_STAGES
    }
    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)
    stage_usage: dict[str, dict[str, Any]] = {}

    # The action inventory is identical in both arms: the control arm can still ask the
    # applicability question. Only enforcement of the answer differs.
    planner_action_specs = sorted(
        (
            {
                "name": action["name"],
                "description": action.get("description"),
                "when_to_use": action.get("when_to_use", []),
                "parameters": action.get("parameters", {"type": "object", "additionalProperties": True}),
            }
            for action in action_catalog["actions"]
            if action["name"] in V5_PLANNER_ACTIONS
        ),
        key=lambda item: item["name"],
    )
    planner_action_schemas = {item["name"]: item["parameters"] for item in planner_action_specs}

    from pur_new.actions import query_external_priors  # noqa: E402

    external_evidence_digest = {
        modifier: query_external_priors(modifier_type=modifier)
        for modifier in ("acrylic_like", "minor_tackifier_like")
    }

    registry_for_model = {
        "registry_id": registry["registry_id"],
        "hypotheses": registry["hypotheses"],
        "reference_observations": registry["reference_observations"],
        "claim_boundary": registry["claim_boundary"],
    }
    catalog_for_model = {
        "catalog_id": catalog["catalog_id"],
        "declared_failure_mode": catalog["declared_failure_mode"],
        "measurements": catalog["measurements"],
    }

    planner_payload = {
        "architecture_version": architecture["version"],
        "unit_of_decision": architecture["unit_of_decision"],
        "workflow_policy": workflow,
        "evidence_profile": profile_name,
        "evidence_policy": policy,
        "allowed_planner_actions": planner_action_specs,
        "mandatory_action": MANDATORY_LOCAL_SCIENCE_TOOL,
        "external_evidence_digest": external_evidence_digest,
        "filtered_evidence_state": evidence,
        "hypothesis_registry": registry_for_model,
        "measurement_catalog": catalog_for_model,
        "candidate_space_summary": candidate_set.get("provenance", {}),
    }
    guard(planner_payload)
    planner, stage_usage["planner"] = call_json(
        client, model=stage_models["planner"], system_prompt=prompts["planner"], payload=planner_payload
    )

    forced_requests = ensure_mandatory_tools(planner.get("action_requests", []))
    tool_trace = execute_planned_actions(
        forced_requests,
        include_follow_up=bool(policy.get("allow_follow_up_hold_results", False)),
        blind_target_formulation_ids=blinded_ids,
        action_schemas=planner_action_schemas,
    )
    if not mandatory_tool_executed(tool_trace):
        raise SystemExit(
            f"mandatory local science tool {MANDATORY_LOCAL_SCIENCE_TOOL} did not execute successfully"
        )

    cards = build_experiment_cards(
        candidate_set["candidates"], registry=registry, catalog=catalog, weights=voi_weights
    )
    audit = audit_experiment_cards(cards, candidates=candidate_set["candidates"], verified=verified)
    gate = audit_summary(audit, enforce=gate_enforced, top_k=args.top_k, weights=voi_weights)
    selectable = ranked_cards(audit, enforce=gate_enforced)
    cards_by_id = {card["experiment_id"]: card for card in audit["cards"]}
    selectable_by_id = {card["experiment_id"]: card for card in selectable}
    tied = tied_top_set(selectable)
    sweep = decision_stability(selectable, base_weights=voi_weights)
    sweep_for_model = {key: value for key, value in sweep.items() if key != "scenarios"}
    voi_for_model = build_voi_payload(
        audit, top_k=args.top_k, enforce=gate_enforced, weights=voi_weights
    )

    shared = {
        "planner": planner,
        "tool_trace": tool_trace,
        "hypothesis_registry": registry_for_model,
        "measurement_catalog": catalog_for_model,
        "voi": voi_for_model["voi"],
        "chemistry_applicability_audit": voi_for_model["chemistry_applicability_audit"],
        "decision_stability": sweep_for_model,
        "evidence_policy": policy,
    }

    proposer_payload = dict(shared)
    guard(proposer_payload)
    proposer, stage_usage["proposer"] = call_json(
        client, model=stage_models["proposer"], system_prompt=prompts["proposer"], payload=proposer_payload
    )

    skeptic_payload = {**shared, "proposer": proposer}
    guard(skeptic_payload)
    skeptic, stage_usage["skeptic"] = call_json(
        client, model=stage_models["skeptic"], system_prompt=prompts["skeptic"], payload=skeptic_payload
    )

    robustness_payload = {**shared, "proposer": proposer, "skeptic": skeptic}
    guard(robustness_payload)
    robustness, stage_usage["robustness_adjudicator"] = call_json(
        client,
        model=stage_models["robustness_adjudicator"],
        system_prompt=prompts["robustness_adjudicator"],
        payload=robustness_payload,
    )

    judge_payload = {**shared, "proposer": proposer, "skeptic": skeptic, "robustness_adjudication": robustness}
    guard(judge_payload)
    judge_raw, stage_usage["judge"] = call_json(
        client, model=stage_models["judge"], system_prompt=prompts["judge"], payload=judge_payload
    )
    judge, judge_normalization = normalize_judge_output(judge_raw)

    hashes = {
        "prompt_hash": prompt_hash,
        "candidate_set_hash": canonical_hash(candidate_set),
        "hypothesis_registry_hash": canonical_hash(registry),
        "measurement_catalog_hash": canonical_hash(catalog),
        "decision_condition_hash": canonical_hash(condition["declared"]),
        "verified_shape_transfer_hash": canonical_hash(verified),
        "input_hash": canonical_hash(
            {
                "architecture": architecture,
                "arm": args.arm,
                "evidence_profile": profile_name,
                "filtered_evidence_state": evidence,
                "candidate_set": candidate_set,
                "hypothesis_registry": registry,
                "measurement_catalog": catalog,
                "verified_shape_transfer": verified,
                "planner": planner,
                "tool_trace": tool_trace,
                "voi": voi_for_model,
                "decision_stability": sweep_for_model,
                "proposer": proposer,
                "skeptic": skeptic,
                "robustness_adjudication": robustness,
            }
        ),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    frozen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = canonical_hash({"judge": judge, "input_hash": hashes["input_hash"], "frozen_utc": frozen_utc})[:10]

    try:
        recommendation = freeze_experiment(
            judge,
            arm=args.arm,
            cards_by_id=cards_by_id,
            selectable_by_id=selectable_by_id,
            tied=tied,
            audit_summary=gate,
            hashes=hashes,
            model=stage_models["judge"],
            workflow_version=workflow["workflow_version"],
            architecture_version=architecture["version"],
            inspection_status=args.inspection_status,
            claim_boundary=architecture["claim_boundary"],
            frozen_utc=frozen_utc,
            recommendation_digest=digest,
            git_commit=current_git_commit(),
            weights=voi_weights,
        )
        validate(recommendation, recommendation_schema)
    except Exception as exc:
        # An invalid model decision is recorded as an invalid RUN. It is never repaired into
        # an admissible neighbour and never silently converted into an abstention.
        inadmissible = isinstance(exc, InadmissibleSelectionError)
        reject_dir = args.output_dir / "REJECTED"
        reject_dir.mkdir(parents=True, exist_ok=True)
        (reject_dir / "rejected_deliberation.json").write_text(
            json.dumps(
                {
                    "arm": args.arm,
                    "gate_enforced": gate_enforced,
                    "rejection_class": "inadmissible_selection" if inadmissible else "contract_violation",
                    "rejection_reason": f"{type(exc).__name__}: {exc}",
                    "planner": planner,
                    "tool_trace": tool_trace,
                    "proposer": proposer,
                    "skeptic": skeptic,
                    "robustness_adjudication": robustness,
                    "judge_raw": judge_raw,
                    "judge_normalized": judge,
                    "judge_normalization": judge_normalization,
                    "chemistry_gate": gate,
                    "llm_usage_by_stage": stage_usage,
                    "llm_usage_total": aggregate_usage(stage_usage),
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"run rejected ({'inadmissible_selection' if inadmissible else 'contract_violation'}): {exc}", file=sys.stderr)
        raise SystemExit(EXIT_INVALID_MODEL_OUTPUT)

    run_dir = args.output_dir / recommendation["recommendation_id"]
    if run_dir.exists():
        raise SystemExit(f"Refusing to overwrite a frozen V5 run: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    (run_dir / "deliberation.json").write_text(
        json.dumps(
            {
                "architecture": architecture,
                "arm": args.arm,
                "gate_enforced": gate_enforced,
                "evidence_profile": profile_name,
                "evidence_policy": policy,
                "filtered_evidence_hash": canonical_hash(evidence),
                "candidate_set_hash": hashes["candidate_set_hash"],
                "stage_models": stage_models,
                "llm_usage_by_stage": stage_usage,
                "llm_usage_total": aggregate_usage(stage_usage),
                "planner": planner,
                "planner_action_requests_after_forcing": forced_requests,
                "tool_trace": tool_trace,
                "mandatory_local_science_tool": MANDATORY_LOCAL_SCIENCE_TOOL,
                "mandatory_local_science_tool_executed": mandatory_tool_executed(tool_trace),
                "applicability_tool": APPLICABILITY_TOOL,
                "chemistry_gate": gate,
                "voi_sent_to_model": voi_for_model,
                "decision_stability_sent_to_model": sweep_for_model,
                "proposer": proposer,
                "skeptic": skeptic,
                "robustness_adjudication": robustness,
                "judge_raw": judge_raw,
                "judge_normalized": judge,
                "judge_normalization": judge_normalization,
                "recommendation_id": recommendation["recommendation_id"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "recommendation.json").write_text(
        json.dumps(recommendation, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "admissibility_audit.json").write_text(
        json.dumps(
            {
                "arm": args.arm,
                "applicability_audit_visible_to_model": True,
                "applicability_gate_enforced": gate_enforced,
                "audit_is_arm_independent": True,
                "gate_id": audit["gate_id"],
                "protocol_version": audit["protocol_version"],
                "rule_text": audit["rule_text"],
                "verified_transfer_registry_version": audit["verified_transfer_registry_version"],
                "verified_shape_transfer_hash": hashes["verified_shape_transfer_hash"],
                "pre_enforcement_payload_sha256": gate["pre_enforcement_payload_sha256"],
                "n_cards_total": audit["n_cards_total"],
                "n_cards_inadmissible": audit["n_cards_inadmissible"],
                "n_cards_removed_from_selectable_set": gate["n_cards_removed_from_selectable_set"],
                "inadmissible_by_rule_id": audit["inadmissible_by_rule_id"],
                "inadmissible_experiment_ids": audit["inadmissible_experiment_ids"],
                "admissible_experiment_ids": audit["admissible_experiment_ids"],
                "candidate_assessments": audit["candidate_assessments"],
                "selection": recommendation["chemistry_gate"]["selection"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "experiment_cards.json").write_text(
        json.dumps(
            {
                "arm": args.arm,
                "applicability_gate_enforced": gate_enforced,
                "decision_condition": condition["condition_id"],
                "weights": voi_weights,
                "formula": VOI_FORMULA,
                "ranked_selectable_experiment_ids": [card["experiment_id"] for card in selectable],
                "cards": audit["cards"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "decision_stability.json").write_text(
        json.dumps(sweep, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(run_dir)


if __name__ == "__main__":
    main()
