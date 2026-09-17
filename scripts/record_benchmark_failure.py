#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    p = argparse.ArgumentParser(description="Record a failed PUR-NEW benchmark attempt instead of silently dropping it")
    p.add_argument("--condition", required=True)
    p.add_argument("--run-index", required=True, type=int)
    p.add_argument("--failure-type", default="runner_error")
    p.add_argument("--exit-code", type=int, default=None)
    p.add_argument("--log-file", type=Path, default=None)
    p.add_argument("--output-dir", type=Path, required=True)
    args = p.parse_args()

    log_text = None
    if args.log_file is not None and args.log_file.exists():
        log_text = args.log_file.read_text(encoding="utf-8", errors="replace")
        if len(log_text) > 20000:
            log_text = log_text[-20000:]

    record = {
        "record_type": "benchmark_failure",
        "condition": args.condition,
        "run_index": args.run_index,
        "failure_type": args.failure_type,
        "exit_code": args.exit_code,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "log_tail": log_text,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    path = args.output_dir / f"failure_{args.run_index:04d}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
