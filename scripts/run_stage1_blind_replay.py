#!/usr/bin/env python3
"""Drive N independent Stage-1 pre-result runs against the real model API.

Arm B (blind)  : the full agent_v3 pipeline over the target-blind candidate space.
Arm A (replay) : the repository's own pre-result replay workflow, unchanged.

Every attempt is recorded, including failures and abstentions. Nothing is retried
silently and nothing is discarded.
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

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def load_dotenv(path: Path) -> dict[str, str]:
    """Read API settings from a local .env. Values are used, never printed or stored."""
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip()
    return env


def run_arm_b(
    run_idx: int,
    out_dir: Path,
    env: dict[str, str],
    candidate_set: Path,
    hide_ranking: bool = False,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_scientific_agent_v3.py"),
        "--candidate-set", str(candidate_set),
        "--evidence-state", str(ROOT / "derived" / "evidence_state.json"),
        "--profile", "blind_pre_result",
        "--inspection-status", "no_results_inspected",
        "--output-dir", str(out_dir),
    ]
    if hide_ranking:
        cmd.append("--hide-deterministic-ranking")
    return _exec(cmd, env, run_idx)


def run_arm_a(run_idx: int, out_dir: Path, env: dict[str, str]) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_pre_result_replay_agent.py"),
        "--selection-mode", "audit",
        "--inspection-status", "no_results_inspected",
        "--output-dir", str(out_dir),
    ]
    return _exec(cmd, env, run_idx)


def _exec(cmd: list[str], env: dict[str, str], run_idx: int) -> dict[str, Any]:
    full_env = {**os.environ, **env, "PYTHONPATH": str(ROOT / "src")}
    started = utc_now()
    t0 = time.perf_counter()
    proc = subprocess.run(cmd, cwd=ROOT, env=full_env, capture_output=True, text=True)
    elapsed = time.perf_counter() - t0
    return {
        "run_index": run_idx,
        "started_utc": started,
        "finished_utc": utc_now(),
        "wall_seconds": round(elapsed, 2),
        "returncode": proc.returncode,
        "status": "ok" if proc.returncode == 0 else "error",
        "stdout": proc.stdout.strip(),
        "stderr": proc.stderr.strip()[-4000:],
    }


def main() -> None:
    p = argparse.ArgumentParser(description="Stage-1 pre-result replay driver")
    p.add_argument("--arm", choices=["A", "B"], required=True)
    p.add_argument("--runs", type=int, default=10)
    p.add_argument("--env-file", type=Path, required=True)
    p.add_argument("--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json")
    p.add_argument("--output-root", type=Path, default=ROOT / "results" / "stage1_blind_replay_v1")
    p.add_argument("--hide-deterministic-ranking", action="store_true")
    p.add_argument(
        "--model",
        default=None,
        help="Override OPENAI_MODEL for this series, so a second model can be run "
             "without copying the credential file.",
    )
    args = p.parse_args()

    env = load_dotenv(args.env_file)
    if args.model:
        env["OPENAI_MODEL"] = args.model
    for required in ("OPENAI_API_KEY", "OPENAI_MODEL"):
        if required not in env:
            raise SystemExit(f"{required} missing from env file")

    arm_dir = args.output_root / ("arm_a_replay" if args.arm == "A" else "arm_b_blind")
    arm_dir.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "arm": args.arm,
        "arm_role": (
            "replay fidelity against the repository's own reconstructed contract"
            if args.arm == "A"
            else "target-blind independent pre-result recovery"
        ),
        "n_runs_requested": args.runs,
        "model": env["OPENAI_MODEL"],
        "api_base_host": env.get("OPENAI_BASE_URL", "").split("//")[-1].split("/")[0],
        "deterministic_ranking_hidden": bool(args.hide_deterministic_ranking),
        "temperature": "not sent; endpoint rejects the temperature parameter (verified). "
                       "Model default sampling retained; stochasticity comes from repeated independent calls.",
        "git_commit": git_commit(),
        "evidence_state_sha256": sha256_file(ROOT / "derived" / "evidence_state.json"),
        "started_utc": utc_now(),
        "runs": [],
    }
    if args.arm == "B":
        manifest["candidate_set"] = str(args.candidate_set)
        manifest["candidate_set_sha256"] = sha256_file(args.candidate_set)
    else:
        manifest["candidate_set"] = str(ROOT / "configs" / "historical_replay_candidate_set.json")
        manifest["candidate_set_sha256"] = sha256_file(ROOT / "configs" / "historical_replay_candidate_set.json")
        manifest["contract_sha256"] = sha256_file(ROOT / "configs" / "pre_result_replay_contract.json")

    for i in range(1, args.runs + 1):
        run_dir = arm_dir / f"run_{i:03d}"
        run_dir.mkdir(parents=True, exist_ok=True)
        print(f"[{utc_now()}] arm {args.arm} run {i}/{args.runs} ...", flush=True)
        record = (
            run_arm_b(i, run_dir, env, args.candidate_set, hide_ranking=args.hide_deterministic_ranking)
            if args.arm == "B"
            else run_arm_a(i, run_dir, env)
        )
        (run_dir / "run_log.json").write_text(
            json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manifest["runs"].append(
            {k: v for k, v in record.items() if k not in ("stdout", "stderr")}
            | {"run_dir": str(run_dir)}
        )
        print(f"    -> {record['status']} ({record['wall_seconds']}s)", flush=True)
        # Persist after every run so a crash cannot lose completed evidence.
        manifest["finished_utc"] = utc_now()
        (arm_dir / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    ok = sum(1 for r in manifest["runs"] if r["status"] == "ok")
    print(f"ARM {args.arm}: {ok}/{args.runs} runs completed")


if __name__ == "__main__":
    main()
