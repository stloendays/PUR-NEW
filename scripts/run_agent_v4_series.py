#!/usr/bin/env python3
"""Drive N independent Agent V4 runs under one frozen series contract.

N is declared and written to the manifest BEFORE the first run starts, together with
SHA-256 hashes of every input that defines the series. Each run is independent: a new
process, a fresh model call chain, the same evidence contract. Every attempted run is
recorded, including failures, so the reported denominator is the declared N.

API settings are read from a local .env and are used, never printed or stored.
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

SERIES_INPUT_FILES = (
    "configs/agent_v4.json",
    "configs/hypothesis_registry.json",
    "configs/measurement_catalog.json",
    "configs/evidence_access_profiles.json",
    "configs/action_catalog.json",
    "configs/formulation_priors.json",
    "configs/workflow.json",
    "src/pur_new/voi.py",
    "scripts/run_agent_v4.py",
    "prompts/agent_v4_planner.txt",
    "prompts/agent_v4_proposer.txt",
    "prompts/agent_v4_skeptic.txt",
    "prompts/agent_v4_robustness.txt",
    "prompts/agent_v4_judge.txt",
)


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
    parser = argparse.ArgumentParser(description="Run an Agent V4 series under a frozen contract")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-runs", type=int, required=True)
    parser.add_argument(
        "--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    parser.add_argument("--evidence-state", type=Path, default=ROOT / "derived" / "evidence_state.json")
    parser.add_argument("--model", default=None, help="override OPENAI_MODEL for this series")
    parser.add_argument("--series-label", default=None)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="continue an interrupted series under its original contract instead of refusing",
    )
    parser.add_argument(
        "--withhold-voi-scores",
        action="store_true",
        help="run the whole series in the ablated arm with the deterministic rule layer withheld",
    )
    parser.add_argument(
        "--rule-order",
        choices=["sufficiency_first", "minimality_first"],
        default=None,
        help="run the whole series under a named deterministic rule ORDER",
    )
    parser.add_argument(
        "--max-new-runs",
        type=int,
        default=None,
        help=(
            "stop after this many NEW runs in this invocation, so a long series can be driven "
            "in bounded chunks and resumed. Does not change the declared N."
        ),
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

    # The contract is written BEFORE the first run, so N cannot be chosen after seeing results.
    manifest: dict[str, Any] = {
        "series_label": args.series_label or output_dir.name,
        "architecture": "PUR_NEW_VOI_GUIDED_EXPERIMENT_SELECTION_AGENT_V4",
        "n_runs_declared": args.n_runs,
        "n_runs_declared_before_first_run": True,
        "declared_utc": utc_now(),
        "model": env["OPENAI_MODEL"],
        "api_base_host": env.get("OPENAI_BASE_URL", "").split("//")[-1].split("/")[0],
        "git_commit": git_commit,
        "candidate_set": str(args.candidate_set),
        "candidate_set_sha256": sha256_file(args.candidate_set.resolve()),
        "evidence_state_sha256": sha256_file(args.evidence_state.resolve()),
        "series_input_hashes": {name: sha256_file(ROOT / name) for name in SERIES_INPUT_FILES},
        "arm": (
            "voi_withheld"
            if args.withhold_voi_scores
            else (f"rule_order_{args.rule_order}" if args.rule_order else "full_v4")
        ),
        "rule_order": args.rule_order,
        "voi_scores_withheld_from_model": bool(args.withhold_voi_scores),
        "reporting_rule": (
            "Every attempted run is reported. The denominator for any rate is n_runs_declared, "
            "not the number of runs that happened to succeed."
        ),
        "runs": [],
    }
    if args.resume and manifest_path.exists():
        # Continue the ORIGINAL contract. N and the input hashes must be unchanged, or the
        # series is no longer the one that was declared and must not be silently extended.
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
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
    completed = {row["run_index"] for row in manifest["runs"] if row["status"] == "ok"}
    if completed:
        print(f"resuming series: {len(completed)} of {args.n_runs} already frozen", flush=True)
    else:
        print(f"series contract frozen: N={args.n_runs} at {manifest['declared_utc']}", flush=True)

    full_env = {**os.environ, **env, "PYTHONPATH": str(ROOT / "src")}
    new_this_invocation = 0
    for index in range(1, args.n_runs + 1):
        if index in completed:
            continue
        if args.max_new_runs is not None and new_this_invocation >= args.max_new_runs:
            print(
                f"chunk limit reached: {new_this_invocation} new runs this invocation; "
                f"{len(completed) + new_this_invocation}/{args.n_runs} frozen. Re-invoke with --resume.",
                flush=True,
            )
            break
        new_this_invocation += 1
        # A previous attempt may have left a partial directory for this index.
        manifest["runs"] = [row for row in manifest["runs"] if row["run_index"] != index]
        run_dir = output_dir / f"run_{index:03d}"
        started = utc_now()
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "run_agent_v4.py"),
            "--candidate-set",
            str(args.candidate_set),
            "--evidence-state",
            str(args.evidence_state),
            "--output-dir",
            str(run_dir),
        ]
        if args.withhold_voi_scores:
            cmd.append("--withhold-voi-scores")
        if args.rule_order:
            cmd.extend(["--rule-order", args.rule_order])
        proc = subprocess.run(cmd, cwd=ROOT, env=full_env, capture_output=True, text=True)
        finished = utc_now()
        frozen = sorted(run_dir.glob("EXP_V4_*/recommendation.json"))
        record = {
            "run_index": index,
            "run_dir": str(run_dir.relative_to(ROOT)),
            "started_utc": started,
            "finished_utc": finished,
            "returncode": proc.returncode,
            "status": "ok" if proc.returncode == 0 and frozen else "failed",
            "frozen_recommendation": str(frozen[0].parent.relative_to(ROOT)) if frozen else None,
        }
        if proc.returncode != 0:
            record["stderr_tail"] = proc.stderr.strip().splitlines()[-8:]
        manifest["runs"].append(record)
        manifest["runs"].sort(key=lambda row: row["run_index"])
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"run {index}/{args.n_runs}: {record['status']}", flush=True)

    manifest["n_ok"] = sum(row["status"] == "ok" for row in manifest["runs"])
    manifest["n_failed"] = sum(row["status"] != "ok" for row in manifest["runs"])
    complete = manifest["n_ok"] == args.n_runs
    if complete:
        # Only a series that actually reached its declared N is marked finished.
        manifest["finished_utc"] = utc_now()
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    state = "series complete" if complete else "series incomplete"
    print(f"{state}: {manifest['n_ok']} ok / {manifest['n_failed']} failed of {args.n_runs} declared")


if __name__ == "__main__":
    main()
