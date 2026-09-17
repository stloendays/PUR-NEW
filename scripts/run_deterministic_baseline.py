#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import validate

from pur_new.actions import rank_candidate_support

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def main() -> None:
    p = argparse.ArgumentParser(description="Run the transparent deterministic PUR-NEW evidence-ranker baseline")
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=ROOT / "records" / "deterministic_baseline")
    args = p.parse_args()

    candidate_set = read_json(args.candidate_set)
    candidate_schema = read_json(ROOT / "schemas" / "candidate_set.schema.json")
    recommendation_schema = read_json(ROOT / "schemas" / "agent_recommendation.schema.json")
    validate(candidate_set, candidate_schema)

    candidates = candidate_set["candidates"]
    by_id = {c["candidate_id"]: c for c in candidates}
    ranking = rank_candidate_support(candidates)
    if not ranking:
        raise SystemExit("candidate set is empty")

    selected_id = ranking[0]["candidate_id"]
    selected = by_id[selected_id]
    alternatives = [
        {
            "candidate_id": item["candidate_id"],
            "relative_reason": f"transparent support_score={item['support_score']}",
            "acquisition_value": None,
        }
        for item in ranking[1:3]
    ]

    created = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    digest = hashlib.sha256(
        json.dumps(ranking, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:10]
    rec_id = f"REC_DET_{created.replace(':', '').replace('-', '')}_{digest}"

    record = {
        "recommendation_id": rec_id,
        "created_utc": created,
        "record_status": "frozen",
        "result_inspection_status_at_creation": "no_results_inspected",
        "decision_mode": "performance_candidate",
        "selected_candidate": {
            "candidate_id": selected_id,
            "formulation_state": selected["formulation_state"],
            "process_state": selected["process_state"],
            "measurement_plan": selected.get("measurement_plan"),
        },
        "alternatives_considered": alternatives,
        "constraints": [],
        "uncertainty": {
            "measurement": {"status": "unknown", "value": None, "unit_or_scale": None, "method": None, "note": "deterministic ranker does not estimate measurement uncertainty"},
            "repeatability": {"status": "unknown", "value": None, "unit_or_scale": None, "method": None, "note": "deterministic ranker does not estimate repeatability uncertainty"},
            "process_history": {"status": "unknown", "value": None, "unit_or_scale": None, "method": None, "note": "process missingness contributes to the transparent stress-test penalty"},
            "extrapolation": {"status": "unknown", "value": None, "unit_or_scale": None, "method": None, "note": "analogue distance is used only as support, not as a property prediction"},
            "evidence_coverage": {"status": "estimated", "value": None, "unit_or_scale": None, "method": "transparent support ranker", "note": "ranking uses the frozen evidence-anchor and stress-test heuristics"},
            "aggregate_penalty": None,
            "aggregation_rule": "rank_candidate_support transparent heuristic",
            "decision_margin": None
        },
        "selection_rationale": "Selected by the deterministic evidence-support baseline using only frozen candidate priors and transparent stress-test penalties; no LLM reasoning or held-out outcome is used.",
        "acceptance_criterion": {
            "claim": "Deterministic evidence-prior baseline selection for architecture comparison.",
            "criterion": "This baseline is not used to define a wet-lab success threshold; it supplies a transparent non-LLM ranking comparator.",
            "measurement_window": None,
            "failure_condition": None
        },
        "provenance": {
            "generated_by": "agent",
            "git_commit": current_git_commit(),
            "run_id": rec_id,
            "model": "deterministic_evidence_ranker",
            "prompt_hash": None,
            "input_hash": digest,
            "workflow_version": "deterministic_evidence_ranker_v1"
        }
    }
    validate(record, recommendation_schema)

    run_dir = args.output_dir / rec_id
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "recommendation.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (run_dir / "ranking.json").write_text(
        json.dumps(ranking, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(run_dir)


if __name__ == "__main__":
    main()
