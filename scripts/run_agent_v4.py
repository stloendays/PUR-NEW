#!/usr/bin/env python3
"""Agent V4: outcome-blind, VOI-guided selection of the next scientific experiment.

V4 is an independent architecture. It does not modify, re-run or reinterpret V3. The
decision object is an experiment card (formulation candidate x measurement plan), and
value of information is computed by a deterministic scientific tool rather than by an
additional language model.
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

from pur_new.agent_v3 import execute_planned_actions  # noqa: E402
from pur_new.evidence_firewall import assert_blind_payload_clean, filter_evidence_state  # noqa: E402
from pur_new.voi import (  # noqa: E402
    BASE_WEIGHTS,
    TIE_EPSILON,
    VOI_FORMULA,
    build_experiment_cards,
    load_hypothesis_registry,
    load_measurement_catalog,
    voi_robustness_sweep,
)

REQUIRED_STAGES = ("planner", "proposer", "skeptic", "robustness_adjudicator", "judge")
CORE_TOOL = "get_state_aware_rheology_summary"


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


def ensure_core_tool(requests: Any) -> list[dict[str, Any]]:
    """The upstream rheology tool is mandatory before any experiment ranking."""
    items = list(requests) if isinstance(requests, list) else []
    names = {item.get("name") for item in items if isinstance(item, dict)}
    if CORE_TOOL not in names:
        items.insert(
            0,
            {
                "name": CORE_TOOL,
                "args": {},
                "reason": "architecture requires the state-aware rheology summary before experiment ranking",
            },
        )
    return items


def tied_top_set(cards: list[dict[str, Any]]) -> list[str]:
    best = max(card["voi_score"] for card in cards)
    return sorted(card["experiment_id"] for card in cards if abs(card["voi_score"] - best) <= TIE_EPSILON)


def voi_payload(cards: list[dict[str, Any]], *, top_k: int) -> dict[str, Any]:
    """Assemble the VOI evidence given to the model.

    The tied top set is reported explicitly so the model cannot mistake an arbitrary
    alphabetical ordering for a deterministic preference.
    """
    tied = tied_top_set(cards)
    best_per_measurement: dict[str, dict[str, Any]] = {}
    for card in cards:
        best_per_measurement.setdefault(card["measurement_id"], card)
    family_best: dict[str, float] = {}
    for card in cards:
        family_best.setdefault(card["intervention_family"], card["voi_score"])
    return {
        "formula": VOI_FORMULA,
        "weights": BASE_WEIGHTS,
        "is_a_probability": False,
        "is_a_distance_to_any_known_answer": False,
        "n_experiment_cards": len(cards),
        "tied_top_experiment_ids": tied,
        "n_tied_at_top": len(tied),
        "tie_note": (
            "These experiments share an identical component vector. The deterministic tool is "
            "indifferent among them. Any choice within this set must be justified scientifically."
        ),
        "top_cards": cards[:top_k],
        "best_card_per_measurement_plan": {
            key: {
                "experiment_id": value["experiment_id"],
                "voi_score": value["voi_score"],
                "voi_components": value["voi_components"],
            }
            for key, value in best_per_measurement.items()
        },
        "best_voi_per_intervention_family": family_best,
    }


def normalize_judge_output(raw: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Repair the one Judge contract slip V3 documented, and record that it happened.

    A Judge that names a preferred experiment while emitting a null selection is a
    format failure, not scientific indecision. V3 left this unfixed under its freeze
    rule; V4 repairs it deterministically and logs the repair rather than silently
    converting a real decision into an abstention.
    """
    out = dict(raw)
    notes: list[str] = []
    mode = out.get("decision_mode")
    selected = out.get("selected_experiment_id")

    if mode != "abstain" and not selected:
        fallback = out.get("preferred_experiment_id") or out.get("experiment_id")
        if isinstance(fallback, str) and "::" in fallback:
            out["selected_experiment_id"] = fallback
            notes.append(f"selected_experiment_id was null with decision_mode={mode!r}; recovered from {fallback!r}")
            selected = fallback

    if isinstance(selected, str) and "::" in selected:
        candidate_part, measurement_part = selected.split("::", 1)
        if not out.get("selected_candidate_id"):
            out["selected_candidate_id"] = candidate_part
            notes.append("selected_candidate_id derived from selected_experiment_id")
        if not out.get("selected_measurement_id"):
            out["selected_measurement_id"] = measurement_part
            notes.append("selected_measurement_id derived from selected_experiment_id")

    return out, {"applied": bool(notes), "notes": notes}


def freeze_experiment(
    judge: dict[str, Any],
    *,
    cards_by_id: dict[str, dict[str, Any]],
    tied: list[str],
    hashes: dict[str, str],
    model: str,
    workflow_version: str,
    architecture_version: str,
    inspection_status: str,
    claim_boundary: str,
) -> dict[str, Any]:
    allowed = {"committed_experiment", "discriminating_probe", "state_control_experiment", "abstain"}
    mode = judge.get("decision_mode")
    if mode not in allowed:
        raise ValueError(f"invalid decision_mode: {mode!r}")

    experiment_id = judge.get("selected_experiment_id")
    if mode == "abstain":
        if experiment_id is not None:
            raise ValueError("abstain requires selected_experiment_id=null")
        card = None
    else:
        if not isinstance(experiment_id, str):
            raise ValueError(f"decision_mode={mode!r} requires a selected_experiment_id")
        card = cards_by_id.get(experiment_id)
        if card is None:
            raise ValueError(f"selected_experiment_id is not an admissible experiment card: {experiment_id!r}")
        if judge.get("selected_candidate_id") != card["candidate_id"]:
            raise ValueError("selected_candidate_id does not match the selected experiment card")
        if judge.get("selected_measurement_id") != card["measurement_id"]:
            raise ValueError("selected_measurement_id does not match the selected experiment card")
        for required in ("acceptance_criterion", "falsification_criterion"):
            if not judge.get(required):
                raise ValueError(f"a committed experiment requires {required}")

    frozen_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    digest = canonical_hash({"judge": judge, "input_hash": hashes["input_hash"], "frozen_utc": frozen_utc})[:10]

    return {
        "recommendation_id": f"EXP_V4_{frozen_utc.replace('-', '').replace(':', '')}_{digest}",
        "architecture_version": architecture_version,
        "workflow_version": workflow_version,
        "decision_mode": mode,
        "selected_experiment_id": experiment_id,
        "selected_candidate_id": judge.get("selected_candidate_id"),
        "selected_measurement_id": judge.get("selected_measurement_id"),
        "experiment_card": card,
        "primary_observable": judge.get("primary_observable"),
        "hypotheses_addressed": list(judge.get("hypotheses_addressed") or []),
        "hypotheses_left_entangled": list(judge.get("hypotheses_left_entangled") or []),
        "acceptance_criterion": judge.get("acceptance_criterion"),
        "falsification_criterion": judge.get("falsification_criterion"),
        "next_experiment_if_falsified": judge.get("next_experiment_if_falsified"),
        "uncertainty_decomposition": judge.get("uncertainty_decomposition") or {},
        "voi": {
            "score": card["voi_score"] if card else None,
            "components": card["voi_components"] if card else None,
            "weights": BASE_WEIGHTS,
            "tied_top_set": tied,
            "selected_is_in_tied_top_set": (experiment_id in tied) if experiment_id else None,
            "formula": VOI_FORMULA,
        },
        "stage_disagreements_resolved": judge.get("stage_disagreements_resolved"),
        "rationale": judge.get("rationale"),
        "frozen_utc": frozen_utc,
        "model": model,
        "prompt_hash": hashes["prompt_hash"],
        "input_hash": hashes["input_hash"],
        "candidate_set_hash": hashes["candidate_set_hash"],
        "hypothesis_registry_hash": hashes["hypothesis_registry_hash"],
        "measurement_catalog_hash": hashes["measurement_catalog_hash"],
        "git_commit": current_git_commit(),
        "inspection_status": inspection_status,
        "claim_boundary": claim_boundary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="PUR-NEW Agent V4 VOI-guided experiment selection")
    parser.add_argument("--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json")
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--profile", default=None)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--inspection-status", default="frozen_pre_result")
    args = parser.parse_args()

    architecture = read_json(ROOT / "configs" / "agent_v4.json")
    access_profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    profile_name = args.profile or architecture["default_evidence_profile"]
    policy = access_profiles[profile_name]
    workflow = read_json(ROOT / "configs" / "workflow.json")
    action_catalog = read_json(ROOT / "configs" / "action_catalog.json")
    candidate_set = read_json(args.candidate_set)
    raw_evidence = read_json(args.evidence_state)
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    recommendation_schema = read_json(ROOT / "schemas" / "agent_v4_experiment.schema.json")

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
        raise SystemExit(f"missing V4 prompts: {sorted(missing)}")
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

    planner_action_names = {
        "query_external_priors",
        "get_candidate_hypothesis",
        "inspect_formulation",
        "get_hold_stability",
        "get_repeatability_risk",
        "get_temperature_support",
        CORE_TOOL,
    }
    planner_action_specs = sorted(
        (
            {
                "name": action["name"],
                "description": action.get("description"),
                "when_to_use": action.get("when_to_use", []),
                "parameters": action.get("parameters", {"type": "object", "additionalProperties": True}),
            }
            for action in action_catalog["actions"]
            if action["name"] in planner_action_names
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

    tool_trace = execute_planned_actions(
        ensure_core_tool(planner.get("action_requests", [])),
        include_follow_up=bool(policy.get("allow_follow_up_hold_results", False)),
        blind_target_formulation_ids=blinded_ids,
        action_schemas=planner_action_schemas,
    )

    cards = build_experiment_cards(candidate_set["candidates"], registry=registry, catalog=catalog)
    cards_by_id = {card["experiment_id"]: card for card in cards}
    tied = tied_top_set(cards)
    sweep = voi_robustness_sweep(candidate_set["candidates"], registry=registry, catalog=catalog)
    sweep_for_model = {key: value for key, value in sweep.items() if key != "scenarios"}
    voi_for_model = voi_payload(cards, top_k=args.top_k)

    shared = {
        "planner": planner,
        "tool_trace": tool_trace,
        "hypothesis_registry": registry_for_model,
        "measurement_catalog": catalog_for_model,
        "voi": voi_for_model,
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
        "input_hash": canonical_hash(
            {
                "architecture": architecture,
                "evidence_profile": profile_name,
                "filtered_evidence_state": evidence,
                "candidate_set": candidate_set,
                "hypothesis_registry": registry,
                "measurement_catalog": catalog,
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
    try:
        recommendation = freeze_experiment(
            judge,
            cards_by_id=cards_by_id,
            tied=tied,
            hashes=hashes,
            model=stage_models["judge"],
            workflow_version=workflow["workflow_version"],
            architecture_version=architecture["version"],
            inspection_status=args.inspection_status,
            claim_boundary=architecture["claim_boundary"],
        )
        validate(recommendation, recommendation_schema)
    except Exception as exc:
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
                    "robustness_adjudication": robustness,
                    "judge_raw": judge_raw,
                    "judge_normalized": judge,
                    "judge_normalization": judge_normalization,
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
        raise SystemExit(f"Refusing to overwrite frozen V4 run: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=False)

    (run_dir / "deliberation.json").write_text(
        json.dumps(
            {
                "architecture": architecture,
                "evidence_profile": profile_name,
                "evidence_policy": policy,
                "filtered_evidence_hash": canonical_hash(evidence),
                "candidate_set_hash": hashes["candidate_set_hash"],
                "stage_models": stage_models,
                "llm_usage_by_stage": stage_usage,
                "llm_usage_total": aggregate_usage(stage_usage),
                "planner": planner,
                "tool_trace": tool_trace,
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
    (run_dir / "voi_full_ranking.json").write_text(
        json.dumps({"weights": BASE_WEIGHTS, "formula": VOI_FORMULA, "cards": cards}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "decision_stability.json").write_text(
        json.dumps(sweep, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(run_dir)


if __name__ == "__main__":
    main()
