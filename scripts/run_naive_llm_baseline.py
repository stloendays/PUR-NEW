#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import time
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
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
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


def candidate_map(candidate_set: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {c["candidate_id"]: c for c in candidate_set["candidates"]}


def freeze(raw: dict[str, Any], *, candidate_set: dict[str, Any], model: str, prompt_hash: str, input_hash: str) -> dict[str, Any]:
    candidates = candidate_map(candidate_set)
    mode = raw.get("decision_mode")
    if mode not in {"performance_candidate", "abstain"}:
        raise ValueError(f"invalid baseline decision_mode: {mode!r}")
    selected_id = raw.get("selected_candidate_id")
    if mode == "abstain":
        if selected_id is not None:
            raise ValueError("abstain requires selected_candidate_id=null")
        selected = None
    else:
        if selected_id not in candidates:
            raise ValueError("selected candidate not in candidate set")
        c = candidates[selected_id]
        selected = {
            "candidate_id": selected_id,
            "formulation_state": c.get("formulation_state"),
            "process_state": c.get("process_state"),
            "measurement_plan": c.get("measurement_plan"),
        }

    alternatives = raw.get("alternatives_considered", [])
    if not isinstance(alternatives, list):
        raise ValueError("alternatives_considered must be a list")
    seen: set[str] = set()
    for alt in alternatives:
        cid = alt.get("candidate_id") if isinstance(alt, dict) else None
        if cid not in candidates:
            raise ValueError(f"baseline alternative not in candidate set: {cid!r}")
        if cid == selected_id or cid in seen:
            raise ValueError("baseline alternatives must be unique and exclude selected candidate")
        seen.add(cid)
    if mode != "abstain" and len(candidates) >= 3 and len(alternatives) < 2:
        raise ValueError("baseline recommendation requires at least two alternatives")

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    rec_seed = canonical_json_bytes({"created_utc": created, "selected_candidate_id": selected_id, "input_hash": input_hash, "model": model})
    recommendation_id = f"REC_BASELINE_{created.replace(':', '').replace('-', '')}_{sha256_bytes(rec_seed)[:10]}"
    return {
        "recommendation_id": recommendation_id,
        "created_utc": created,
        "record_status": "frozen",
        "result_inspection_status_at_creation": "no_results_inspected",
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
            "workflow_version": "naive_direct_llm_baseline_v1",
        },
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Run the deliberately simple direct-LLM PUR baseline")
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--naive-view", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    candidate_set = read_json(args.candidate_set)
    naive_view = read_json(args.naive_view)
    if naive_view.get("information_budget", {}).get("state_aware_theory_summary") is not False:
        raise SystemExit("naive view unexpectedly contains state-aware theory")
    if naive_view.get("information_budget", {}).get("external_database_or_literature") is not False:
        raise SystemExit("naive view unexpectedly contains external evidence")

    validate(candidate_set, read_json(ROOT / "schemas" / "candidate_set.schema.json"))
    recommendation_schema = read_json(ROOT / "schemas" / "agent_recommendation.schema.json")
    prompt_text = (ROOT / "prompts" / "baseline_direct_llm.txt").read_text(encoding="utf-8")
    prompt_hash = sha256_bytes(prompt_text.encode("utf-8"))
    input_hash = sha256_bytes(canonical_json_bytes(naive_view))

    api_key = os.environ.get("OPENAI_API_KEY")
    model = os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not model:
        raise SystemExit("OPENAI_API_KEY and OPENAI_MODEL are required")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": prompt_text},
            {"role": "user", "content": json.dumps(naive_view, ensure_ascii=False, sort_keys=True)},
        ],
    )
    latency = time.perf_counter() - start
    content = response.choices[0].message.content
    if not content:
        raise SystemExit("model returned empty content")
    raw = extract_json_object(content)
    record = freeze(raw, candidate_set=candidate_set, model=model, prompt_hash=prompt_hash, input_hash=input_hash)
    validate(record, recommendation_schema)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out = args.output_dir / f"{record['recommendation_id']}.json"
    out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    usage = getattr(response, "usage", None)
    meta = {
        "baseline": "naive_direct_llm",
        "latency_s": latency,
        "prompt_tokens": getattr(usage, "prompt_tokens", None) if usage else None,
        "completion_tokens": getattr(usage, "completion_tokens", None) if usage else None,
        "total_tokens": getattr(usage, "total_tokens", None) if usage else None,
    }
    out.with_name(f"{out.stem}.meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
