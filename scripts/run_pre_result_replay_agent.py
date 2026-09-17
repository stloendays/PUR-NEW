#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.replay_contract import evaluate_contract  # noqa: E402


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Run the outcome-excluded historical pre-result replay Agent under a frozen deterministic decision contract. "
            "This is a replay-fidelity workflow, not the target-blind independent-recovery benchmark."
        )
    )
    p.add_argument(
        "--candidate-set",
        type=Path,
        default=ROOT / "configs" / "historical_replay_candidate_set.json",
    )
    p.add_argument(
        "--decision-contract",
        type=Path,
        default=ROOT / "configs" / "pre_result_replay_contract.json",
    )
    p.add_argument(
        "--evidence-state",
        type=Path,
        default=ROOT / "derived" / "evidence_state.json",
    )
    p.add_argument(
        "--selection-mode",
        choices=["strict", "audit"],
        default="strict",
        help=(
            "strict: contract freezes only the deterministic rank-1 admissible candidate before the LLM stages; "
            "audit: all contract-admissible candidates are passed to the LLM to measure agreement with the contract."
        ),
    )
    p.add_argument(
        "--inspection-status",
        choices=["no_results_inspected", "some_results_inspected", "unknown"],
        default="no_results_inspected",
    )
    p.add_argument("--output-dir", type=Path, default=ROOT / "records" / "pre_result_replay")
    args = p.parse_args()

    full_set = read_json(args.candidate_set)
    contract = read_json(args.decision_contract)
    if contract.get("required_evidence_profile") != "blind_pre_result":
        raise SystemExit("pre-result replay contract must require the blind_pre_result evidence profile")

    diagnostics = evaluate_contract(full_set, contract)
    if diagnostics["abstain_required"]:
        raise SystemExit("Replay contract found no admissible candidate; refusing to run the API Agent")

    by_id = {c["candidate_id"]: c for c in full_set["candidates"]}
    ranked = diagnostics["contract_ranked_candidate_ids"]
    if args.selection_mode == "strict":
        chosen_ids = ranked[:1]
    else:
        chosen_ids = ranked

    constrained_candidates = []
    for rank, cid in enumerate(chosen_ids, start=1):
        candidate = json.loads(json.dumps(by_id[cid]))
        notes = list(candidate.get("constraint_notes", []))
        notes.append(
            f"Pre-result replay contract admissible; deterministic contract priority rank={rank}. "
            "This rank is derived from frozen pre-result replay rules, not from the later wet-lab outcome."
        )
        candidate["constraint_notes"] = notes
        constrained_candidates.append(candidate)

    constrained_set = {
        "candidate_set_id": f"{full_set['candidate_set_id']}__{args.selection_mode.upper()}",
        "decision_context": (
            "Contract-constrained historical pre-result replay. Later validation measurements and post-result labels are excluded. "
            "Strict mode assesses replay fidelity; audit mode assesses LLM agreement among all contract-admissible candidates."
        ),
        "candidates": constrained_candidates,
        "provenance": {
            **full_set.get("provenance", {}),
            "replay_contract_id": contract["contract_id"],
            "replay_contract_hash": canonical_hash(contract),
            "selection_mode": args.selection_mode,
            "full_shortlist_hash": canonical_hash(full_set),
            "contract_selected_candidate_id": diagnostics["contract_selected_candidate_id"],
            "target_blind_independent_benchmark": False,
            "validation_outcome_included": False,
            "claim_boundary": contract["claim_boundary"],
        },
    }

    run_root = args.output_dir / f"{contract['contract_id']}__{args.selection_mode}"
    run_root.mkdir(parents=True, exist_ok=True)
    constrained_path = run_root / "contract_constrained_candidate_set.json"
    constrained_path.write_text(json.dumps(constrained_set, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    diagnostics_path = run_root / "contract_diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_scientific_agent_v3.py"),
        "--candidate-set",
        str(constrained_path),
        "--evidence-state",
        str(args.evidence_state),
        "--profile",
        "blind_pre_result",
        "--inspection-status",
        args.inspection_status,
        "--output-dir",
        str(run_root / "agent_runs"),
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)

    manifest = {
        "workflow": "historical_pre_result_replay",
        "selection_mode": args.selection_mode,
        "decision_contract": str(args.decision_contract),
        "decision_contract_hash": canonical_hash(contract),
        "full_reconstructed_shortlist": str(args.candidate_set),
        "full_reconstructed_shortlist_hash": canonical_hash(full_set),
        "contract_selected_candidate_id": diagnostics["contract_selected_candidate_id"],
        "eligible_candidate_ids": diagnostics["eligible_candidate_ids"],
        "constrained_candidate_ids_passed_to_api": chosen_ids,
        "evidence_profile": "blind_pre_result",
        "later_validation_outcome_available_to_agent": False,
        "interpretation": (
            "Strict mode tests deterministic replay fidelity under a reconstructed pre-result decision contract. "
            "Audit mode tests whether the LLM agrees with the contract among all admissible candidates. "
            "Neither mode is the independent target-blind benchmark."
        ),
    }
    (run_root / "replay_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(run_root)


if __name__ == "__main__":
    main()
