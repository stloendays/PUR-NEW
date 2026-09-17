#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def find_single_recommendation(root: Path) -> Path:
    candidates = sorted(root.rglob("recommendation.json"), key=lambda p: p.stat().st_mtime)
    if not candidates:
        raise RuntimeError(f"no recommendation.json found under {root}")
    return candidates[-1]


def selected_modifier_total(record: dict[str, Any]) -> float | None:
    selected = record.get("selected_candidate")
    if not isinstance(selected, dict):
        return None
    fs = selected.get("formulation_state")
    if not isinstance(fs, dict):
        return None
    if fs.get("modifier_total_pct") is not None:
        return float(fs["modifier_total_pct"])
    return float(fs.get("AC1920", 0.0)) + float(fs.get("TK100", 0.0))


def main() -> None:
    p = argparse.ArgumentParser(
        description="Run PUR-NEW hierarchical Agent: coarse region identification followed by outcome-blind fine refinement."
    )
    p.add_argument("--coarse-candidate-set", type=Path, required=True)
    p.add_argument("--refinement-candidate-set", type=Path, required=True)
    p.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    p.add_argument("--profile", default="blind_pre_result")
    p.add_argument(
        "--inspection-status",
        default="no_results_inspected",
        choices=["no_results_inspected", "some_results_inspected", "unknown"],
    )
    p.add_argument("--output-dir", type=Path, default=ROOT / "records" / "hierarchical_agent")
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    coarse_dir = args.output_dir / "stage1_coarse"
    refinement_dir = args.output_dir / "stage2_refinement"

    base = [
        sys.executable,
        str(ROOT / "scripts" / "run_scientific_agent_v3.py"),
        "--evidence-state", str(args.evidence_state),
        "--profile", args.profile,
        "--inspection-status", args.inspection_status,
        "--ablation", "full",
    ]

    run(base + [
        "--candidate-set", str(args.coarse_candidate_set),
        "--output-dir", str(coarse_dir),
    ])

    coarse_path = find_single_recommendation(coarse_dir)
    coarse_record = read_json(coarse_path)
    modifier_total = selected_modifier_total(coarse_record)
    proceed = modifier_total is not None and modifier_total > 0.0 and coarse_record.get("decision_mode") != "abstain"

    manifest: dict[str, Any] = {
        "workflow": "hierarchical_region_to_refinement",
        "stage1": {
            "candidate_set": str(args.coarse_candidate_set),
            "recommendation": str(coarse_path),
            "selected_modifier_total_pct": modifier_total,
            "entered_resin_modified_region": proceed,
        },
        "stage2": None,
        "historical_claim_boundary": (
            "This current hierarchical runner is a reproducible outcome-blind operationalization. "
            "It is not claimed to be the exact contemporaneous historical freeze algorithm."
        ),
    }

    if proceed:
        run(base + [
            "--candidate-set", str(args.refinement_candidate_set),
            "--output-dir", str(refinement_dir),
        ])
        refinement_path = find_single_recommendation(refinement_dir)
        manifest["stage2"] = {
            "candidate_set": str(args.refinement_candidate_set),
            "recommendation": str(refinement_path),
            "status": "completed",
        }
    else:
        manifest["stage2"] = {
            "status": "not_run",
            "reason": "Stage 1 did not select a resin-modified candidate or abstained."
        }

    (args.output_dir / "hierarchical_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(args.output_dir / "hierarchical_manifest.json")


if __name__ == "__main__":
    main()
