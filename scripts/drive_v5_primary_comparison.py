#!/usr/bin/env python3
"""Drive the two primary Agent V5 arms INTERLEAVED, then write the cross-arm comparison.

One ``V5_NO_GATE`` run, then one ``V5_FULL`` run, repeated N times. Each arm keeps its own
frozen series contract with N declared before its first run; interleaving changes only the
order in which the declared runs are executed.

Running one arm to completion and then the other would confound arm with wall-clock time,
because the model endpoint can drift across an hour. Alternating removes that confound.

This driver is deliberately a plain Python process with no shell dependency, so it can be
launched detached and survive the session that started it. Progress is appended to the log
file given by ``--log``; every chunk is a separate ``run_agent_v5_series.py`` invocation, so
an interrupted driver can simply be restarted and each arm resumes its own contract.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Interleaved driver for the two primary V5 arms")
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--n-runs", type=int, default=10)
    parser.add_argument("--output-root", type=Path, default=ROOT / "results" / "agent_v5")
    parser.add_argument("--log", type=Path, default=None)
    parser.add_argument(
        "--condition",
        default=None,
        help=(
            "named decision condition from configs/decision_conditions.json. Both arms are "
            "driven under this one condition, so the arm contrast stays the enforcement flag."
        ),
    )
    parser.add_argument(
        "--label",
        default=None,
        help="suffix for the series and comparison directory names; defaults to the run count",
    )
    args = parser.parse_args()

    label = args.label or f"n{args.n_runs}"
    arms = {
        "V5_NO_GATE": args.output_root / f"series_no_gate_{label}",
        "V5_FULL": args.output_root / f"series_full_{label}",
    }
    comparison_dir = args.output_root / f"comparison_{label}"
    log_path = args.log or (args.output_root / "drive_v5_primary_comparison.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(message: str) -> None:
        line = f"[{utc_now()}] {message}"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        print(line, flush=True)

    log(
        f"driver started: N={args.n_runs} per arm, interleaved, "
        f"condition={args.condition or '<default>'}"
    )

    for index in range(1, args.n_runs + 1):
        for arm, out_dir in arms.items():
            cmd = [
                sys.executable,
                str(ROOT / "scripts" / "run_agent_v5_series.py"),
                "--arm",
                arm,
                "--env-file",
                str(args.env_file),
                "--n-runs",
                str(args.n_runs),
                "--output-dir",
                str(out_dir),
                "--max-new-runs",
                "1",
            ]
            if args.condition:
                cmd += ["--condition", args.condition]
            if (out_dir / "series_manifest.json").exists():
                cmd.append("--resume")
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
            log(f"block {index}/{args.n_runs} {arm}: rc={proc.returncode} {tail[0]}")
            if proc.returncode != 0:
                # The series runner records a failed run in its own manifest and keeps the
                # declared denominator. A non-zero chunk is reported, not silently retried.
                log(f"block {index}/{args.n_runs} {arm} stderr: {(proc.stderr or '').strip()[-400:]}")

    log("both arms attempted; producing the cross-arm comparison")
    proc = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_agent_v5_comparison.py"),
            "--no-gate-series",
            str(arms["V5_NO_GATE"]),
            "--full-series",
            str(arms["V5_FULL"]),
            "--output-dir",
            str(comparison_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    log(f"comparison: rc={proc.returncode} {(proc.stdout or '').strip()}")
    if proc.returncode != 0:
        log(f"comparison stderr: {(proc.stderr or '').strip()[-600:]}")
    log("driver finished")
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
