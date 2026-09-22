#!/usr/bin/env python3
"""Drive N independent Agent V5 runs of ONE arm under a frozen series contract.

N is declared and written to the manifest BEFORE the first run starts, together with
SHA-256 hashes of every input that defines the series. Each run is independent: a new
process, a fresh model call chain, the same evidence contract.

Every attempted run is recorded with its outcome class, so the reported denominator is
the declared N and never the number of runs that happened to succeed:

  ``ok``       the run froze a recommendation (committed or abstained);
  ``invalid``  the model violated the output contract, including naming an experiment the
               chemistry-domain gate had removed;
  ``failed``   the run did not complete for an infrastructure or API reason.

A failed or invalid run is never silently replaced by a rerun. API settings are read from
a local .env and are used, never printed or stored.
"""

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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v5 import (  # noqa: E402
    ARM_ENFORCES_GATE,
    ARMS,
    audit_experiment_cards,
    load_verified_shape_transfer,
    pre_enforcement_payload_hash,
)
from pur_new.conditions import load_condition  # noqa: E402
from pur_new.voi import BASE_WEIGHTS, build_experiment_cards  # noqa: E402

EXIT_INVALID_MODEL_OUTPUT = 3

#: Inputs every series hashes regardless of condition. The condition contributes its own
#: registry, catalog and protocol on top of these, so a Condition-B contract cannot be
#: satisfied by a Condition-A input set and vice versa.
SERIES_INPUT_FILES = (
    "configs/agent_v5.json",
    "configs/decision_conditions.json",
    "configs/verified_shape_transfer.json",
    "configs/evidence_access_profiles.json",
    "configs/action_catalog.json",
    "configs/formulation_priors.json",
    "configs/workflow.json",
    "schemas/agent_v5_experiment.schema.json",
    "src/pur_new/voi.py",
    "src/pur_new/agent_v5.py",
    "src/pur_new/chemistry_tools.py",
    "scripts/run_agent_v5.py",
    "prompts/agent_v5_planner.txt",
    "prompts/agent_v5_proposer.txt",
    "prompts/agent_v5_skeptic.txt",
    "prompts/agent_v5_robustness.txt",
    "prompts/agent_v5_judge.txt",
)

#: Files whose hashes must be IDENTICAL between the two primary arms. The arm flag is the
#: only declared difference, so anything on this list differing across arms invalidates the
#: controlled comparison.
def series_input_files(condition: dict[str, Any]) -> tuple[str, ...]:
    """Shared inputs plus the files the chosen condition declares."""
    declared = condition["declared"]
    extra = [declared["hypothesis_registry"], declared["measurement_catalog"]]
    protocol = declared.get("protocol")
    if protocol:
        extra.append(protocol)
    return tuple(SERIES_INPUT_FILES) + tuple(sorted(set(extra)))


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_dotenv(path: Path) -> dict[str, str]:
    """Read API settings from a local .env. Values are used, never printed or stored."""
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one Agent V5 arm under a frozen series contract")
    parser.add_argument("--arm", choices=list(ARMS), required=True)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-runs", type=int, default=10)
    parser.add_argument(
        "--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--model", default=None, help="override OPENAI_MODEL for this series")
    parser.add_argument("--series-label", default=None)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument(
        "--condition",
        default=None,
        help="named decision condition; both arms of a comparison must declare the same one",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="continue an interrupted series under its original contract instead of refusing",
    )
    parser.add_argument(
        "--max-new-runs",
        type=int,
        default=None,
        help="stop after this many NEW runs in this invocation. Does not change the declared N.",
    )
    args = parser.parse_args()

    env = load_dotenv(args.env_file)
    if args.model:
        env["OPENAI_MODEL"] = args.model
    for required in ("OPENAI_API_KEY", "OPENAI_MODEL"):
        if required not in env:
            raise SystemExit(f"{required} missing from env file")

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "series_manifest.json"
    if manifest_path.exists() and not args.resume:
        raise SystemExit(
            f"Refusing to overwrite an existing series manifest: {manifest_path}. "
            "Pass --resume to continue an interrupted series."
        )

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        git_commit = None

    # Protocol v1.1 information-parity evidence: the model-visible pre-enforcement payload
    # is arm-independent by construction, and its hash is frozen into the contract so the
    # two arms can be compared on the record rather than on a claim.
    condition = load_condition(args.condition)
    voi_weights = condition["weights"] or dict(BASE_WEIGHTS)
    input_files = series_input_files(condition)
    candidates = json.loads(args.candidate_set.read_text(encoding="utf-8"))["candidates"]
    audit = audit_experiment_cards(
        build_experiment_cards(
            candidates,
            registry=condition["registry"],
            catalog=condition["catalog"],
            weights=voi_weights,
        ),
        candidates=candidates,
        verified=load_verified_shape_transfer(),
    )
    parity_hash = pre_enforcement_payload_hash(audit, top_k=args.top_k, weights=voi_weights)

    # The contract is written BEFORE the first run, so N cannot be chosen after seeing results.
    manifest: dict[str, Any] = {
        "series_label": args.series_label or output_dir.name,
        "architecture": "PUR_NEW_CHEMISTRY_GATED_EXPERIMENT_SELECTION_AGENT_V5",
        "protocol_version": "1.1.0",
        "arm": args.arm,
        "decision_condition": condition["condition_id"],
        "decision_condition_protocol": condition["protocol"],
        "decision_question": condition["decision_question"],
        "voi_weights": voi_weights,
        "applicability_audit_visible_to_model": True,
        "applicability_gate_enforced": ARM_ENFORCES_GATE[args.arm],
        "pre_enforcement_payload_sha256": parity_hash,
        "n_cards_total": audit["n_cards_total"],
        "n_cards_inadmissible": audit["n_cards_inadmissible"],
        "n_runs_declared": args.n_runs,
        "n_runs_declared_before_first_run": True,
        "declared_utc": utc_now(),
        "model": env["OPENAI_MODEL"],
        "api_base_host": env.get("OPENAI_BASE_URL", "").split("//")[-1].split("/")[0],
        "git_commit": git_commit,
        "top_k": args.top_k,
        "candidate_set": str(args.candidate_set),
        "candidate_set_sha256": sha256_file(args.candidate_set.resolve()),
        "evidence_state_sha256": sha256_file(args.evidence_state.resolve()),
        "series_input_hashes": {name: sha256_file(ROOT / name) for name in input_files},
        "arm_parity_files": list(input_files),
        "reporting_rule": (
            "Every attempted run is reported with its outcome class. The denominator for any rate "
            "is n_runs_declared, not the number of runs that happened to succeed. A failed or "
            "invalid run is never silently replaced."
        ),
        "runs": [],
    }
    if args.resume and manifest_path.exists():
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        if existing.get("arm") != args.arm:
            raise SystemExit(f"resume refused: manifest declares arm {existing.get('arm')!r}, invoked with {args.arm!r}")
        if existing.get("decision_condition") != condition["condition_id"]:
            raise SystemExit(
                f"resume refused: manifest declares condition {existing.get('decision_condition')!r}, "
                f"invoked with {condition['condition_id']!r}"
            )
        if existing["n_runs_declared"] != args.n_runs:
            raise SystemExit(
                f"resume refused: manifest declares N={existing['n_runs_declared']}, invoked with N={args.n_runs}"
            )
        changed = [
            name
            for name, digest in existing["series_input_hashes"].items()
            if manifest["series_input_hashes"].get(name) != digest
        ]
        if changed:
            raise SystemExit(f"resume refused: series inputs changed since the contract was frozen: {changed}")
        existing.setdefault("resumed_utc", []).append(utc_now())
        manifest = existing
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    attempted = {row["run_index"] for row in manifest["runs"]}
    if attempted:
        print(f"resuming series: {len(attempted)} of {args.n_runs} already attempted", flush=True)
    else:
        print(f"series contract frozen: arm={args.arm} N={args.n_runs} at {manifest['declared_utc']}", flush=True)

    full_env = {**os.environ, **env, "PYTHONPATH": str(ROOT / "src")}
    new_this_invocation = 0
    for index in range(1, args.n_runs + 1):
        if index in attempted:
            continue
        if args.max_new_runs is not None and new_this_invocation >= args.max_new_runs:
            print(
                f"chunk limit reached: {new_this_invocation} new runs this invocation; "
                f"{len(attempted) + new_this_invocation}/{args.n_runs} attempted. Re-invoke with --resume.",
                flush=True,
            )
            break
        new_this_invocation += 1
        run_dir = output_dir / f"run_{index:03d}"
        started = utc_now()
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "run_agent_v5.py"),
            "--arm",
            args.arm,
            "--candidate-set",
            str(args.candidate_set),
            "--evidence-state",
            str(args.evidence_state),
            "--top-k",
            str(args.top_k),
            "--condition",
            condition["condition_id"],
            "--output-dir",
            str(run_dir),
        ]
        proc = subprocess.run(cmd, cwd=ROOT, env=full_env, capture_output=True, text=True)
        finished = utc_now()
        frozen = sorted(run_dir.glob("EXP_V5_*/recommendation.json"))
        if proc.returncode == 0 and frozen:
            status = "ok"
        elif proc.returncode == EXIT_INVALID_MODEL_OUTPUT:
            status = "invalid"
        else:
            status = "failed"
        record = {
            "run_index": index,
            "run_dir": str(run_dir.relative_to(ROOT)),
            "started_utc": started,
            "finished_utc": finished,
            "returncode": proc.returncode,
            "status": status,
            "frozen_recommendation": str(frozen[0].parent.relative_to(ROOT)) if frozen else None,
        }
        if status != "ok":
            record["stderr_tail"] = proc.stderr.strip().splitlines()[-8:]
        manifest["runs"].append(record)
        manifest["runs"].sort(key=lambda row: row["run_index"])
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"run {index}/{args.n_runs}: {status}", flush=True)

    manifest["n_attempted"] = len(manifest["runs"])
    manifest["n_ok"] = sum(row["status"] == "ok" for row in manifest["runs"])
    manifest["n_invalid"] = sum(row["status"] == "invalid" for row in manifest["runs"])
    manifest["n_failed"] = sum(row["status"] == "failed" for row in manifest["runs"])
    if manifest["n_attempted"] == args.n_runs:
        manifest["finished_utc"] = utc_now()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"arm {args.arm}: {manifest['n_ok']} ok / {manifest['n_invalid']} invalid / "
        f"{manifest['n_failed']} failed of {args.n_runs} declared"
    )


if __name__ == "__main__":
    main()
