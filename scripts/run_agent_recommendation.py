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
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("model output did not contain a JSON object")
        value = json.loads(stripped[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("model output must be a JSON object")
    return value


def candidate_map(candidate_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["candidate_id"]: c for c in candidate_set["candidates"]}


def normalize_agent_decision(
    raw: dict[str, Any],
    *,
    candidate_set: dict[str, Any],
    inspection_status: str,
    model: str,
    prompt_hash: str,
    input_hash: str,
    workflow_version: str,
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
    for alt in alternatives:
        alt_id = alt.get("candidate_id")
        if alt_id not in candidates:
            raise ValueError(f"alternative candidate not in candidate set: {alt_id!r}")

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rec_seed = canonical_json_bytes(
        {
            "created_utc": created,
            "selected_candidate_id": selected_id,
            "input_hash": input_hash,
            "model": model,
        }
    )
    recommendation_id = f"REC_{created.replace(':', '').replace('-', '')}_{sha256_bytes(rec_seed)[:10]}"

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
            "workflow_version": workflow_version,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run and freeze a PUR-NEW Agent recommendation")
    parser.add_argument("--candidate-set", type=Path, required=True)
    parser.add_argument(
        "--evidence-state",
        type=Path,
        default=ROOT / "derived" / "evidence_state.json",
    )
    parser.add_argument(
        "--inspection-status",
        required=True,
        choices=["no_results_inspected", "some_results_inspected", "unknown"],
        help="Chronology at recommendation creation; must be supplied explicitly.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "records" / "recommendations",
    )
    args = parser.parse_args()

    if not args.evidence_state.exists():
        raise SystemExit(
            f"Evidence state not found: {args.evidence_state}. Run scripts/build_evidence_state.py first."
        )

    workflow = read_json(ROOT / "configs" / "workflow.json")
    evidence = read_json(args.evidence_state)
    candidates = read_json(args.candidate_set)
    candidate_schema = read_json(ROOT / "schemas" / "candidate_set.schema.json")
    recommendation_schema = read_json(ROOT / "schemas" / "agent_recommendation.schema.json")
    validate(candidates, candidate_schema)

    prompt_path = ROOT / "prompts" / "agent_system.txt"
    prompt_text = prompt_path.read_text(encoding="utf-8")
    prompt_hash = sha256_bytes(prompt_text.encode("utf-8"))

    input_payload = {
        "workflow_policy": workflow,
        "evidence_state": evidence,
        "candidate_set": candidates,
    }
    input_hash = sha256_bytes(canonical_json_bytes(input_payload))

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise SystemExit("OPENAI_API_KEY is required")
    if not model:
        raise SystemExit("OPENAI_MODEL is required")

    client_kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    user_message = (
        "Choose from the supplied candidate set or abstain. Return JSON only.\n\n"
        + json.dumps(input_payload, ensure_ascii=False, sort_keys=True)
    )
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": user_message},
        ],
    )
    content = response.choices[0].message.content
    if not content:
        raise SystemExit("model returned empty content")
    raw_decision = extract_json_object(content)

    record = normalize_agent_decision(
        raw_decision,
        candidate_set=candidates,
        inspection_status=args.inspection_status,
        model=model,
        prompt_hash=prompt_hash,
        input_hash=input_hash,
        workflow_version=workflow["workflow_version"],
    )
    validate(record, recommendation_schema)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / f"{record['recommendation_id']}.json"
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite frozen recommendation: {output_path}")
    output_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
