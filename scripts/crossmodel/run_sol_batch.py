#!/usr/bin/env python3
"""Run the next execution batch of gpt-5.6-sol replicates under the frozen Luna matrix.

A replicate `sol_rNNN` is one independent execution of every condition declared in
configs/crossmodel_sol_v4_protocol.json. Conditions are interleaved inside a replicate so
that condition is not confounded with wall-clock time. Each run executes the per-run script
of the condition's verified replay tree (scripts/crossmodel/build_replay_trees.py), so the
pinned inputs are byte-identical to the Luna series and only the model differs.

Rules enforced here:
- replicate numbering continues from the highest existing sol_rNNN; nothing is overwritten;
- every attempted run is recorded; no run is re-run or dropped because of its outcome;
- API/infrastructure failures are marked technical_failure = true and kept;
- before the first model call of a series, the replay tree must reproduce the Luna input
  hashes and, for V5, the Luna pre-enforcement payload hash; otherwise the batch aborts.

API settings are read from a local .env and are used, never printed or stored.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL_PATH = ROOT / "configs" / "crossmodel_sol_v4_protocol.json"
REL_OUT = Path("results") / "multimodel" / "gpt-5_6-sol" / "v4_benchmark"
OUT = ROOT / REL_OUT
REPLAY_TREES = OUT / "replay_trees.json"
CUMULATIVE = OUT / "cumulative_manifest.json"
EXIT_INVALID_MODEL_OUTPUT = 3

TECHNICAL_PATTERNS = re.compile(
    r"APIConnectionError|APITimeoutError|InternalServerError|RateLimitError|ServiceUnavailable|"
    r"BadGateway|GatewayTimeout|Connection error|ConnectError|ReadTimeout|RemoteProtocolError|"
    r"Error code: 5\d\d|Error code: 429|Error code: 401|Error code: 403|api_yes_proxy_error|"
    r"timed out|ConnectionResetError|No API key|OPENAI_API_KEY",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def load_dotenv(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        env[key.strip()] = value.strip()
    return env


def sync_dir(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def log_line(message: str) -> None:
    line = f"[{utc_now()}] {message}"
    with (OUT / "driver.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
    print(line, flush=True)


def verify_tree(tree_entry: dict[str, Any]) -> list[str]:
    """Re-hash every pin in a replay tree; return the paths that no longer match."""
    tree = Path(tree_entry["tree"])
    bad = []
    for pin in tree_entry["pins"]:
        if "sha256" in pin and sha256_file(tree / pin["path"]) != pin["sha256"]:
            bad.append(pin["path"])
    return bad


def series_dir(key: str) -> Path:
    return REL_OUT / key


def declare_series(cond: dict[str, Any], tree: Path, env_file: Path, model: str, n_declared: int) -> dict[str, Any]:
    """Freeze the series contract in the replay tree without any model call."""
    key = cond["condition_key"]
    out_rel = series_dir(key)
    tree_out = tree / out_rel
    if key == "naive_direct_llm":
        manifest = {
            "series_label": f"sol_{key}",
            "baseline": "naive_direct_llm",
            "architecture": "naive_direct_llm_baseline_v1",
            "n_runs_declared": n_declared,
            "n_runs_declared_before_first_run": True,
            "declared_utc": utc_now(),
            "model": model,
            "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tree, text=True).strip(),
            "candidate_set": "derived/stage1_blind_candidate_space_v1.json",
            "candidate_set_sha256": sha256_file(tree / "derived" / "stage1_blind_candidate_space_v1.json"),
            "prompt_hash": cond["luna_reference_prompt_hash"],
            "input_hash": cond["luna_reference_input_hash"],
            "reporting_rule": (
                "Every attempted run is reported. The denominator for any rate is the number of "
                "attempted runs excluding technical failures, not the number of valid outputs."
            ),
            "runs": [],
        }
        write_json(tree_out / "series_manifest.json", manifest)
        return manifest
    cmd = [
        sys.executable,
        str(tree / cond["declaration_runner"]),
        "--env-file", str(env_file),
        "--output-dir", str(tree_out),
        "--n-runs", str(n_declared),
        "--model", model,
        "--series-label", f"sol_{key}",
        "--max-new-runs", "0",
    ]
    # the series runners take the same condition flags as the per-run scripts
    cmd += list(cond["runner_flags"])
    proc = subprocess.run(cmd, cwd=tree, capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"declaration failed for {key}: {proc.stderr.strip()[-800:]}")
    return read_json(tree_out / "series_manifest.json")


def check_declaration(cond: dict[str, Any], manifest: dict[str, Any]) -> dict[str, bool]:
    if cond["condition_key"] == "naive_direct_llm":
        return {"declared": True}
    luna = read_json(ROOT / cond["luna_reference"] / "series_manifest.json")
    checks = {
        "series_input_hashes_equal_luna": manifest["series_input_hashes"] == luna["series_input_hashes"],
        "candidate_set_sha256_equal_luna": manifest["candidate_set_sha256"] == luna["candidate_set_sha256"],
        "evidence_state_sha256_equal_luna": manifest["evidence_state_sha256"] == luna["evidence_state_sha256"],
        "arm_equal_luna": manifest.get("arm") == luna.get("arm"),
        "model_is_sol": manifest["model"] == "gpt-5.6-sol",
    }
    if "luna_pre_enforcement_payload_sha256" in cond:
        checks["pre_enforcement_payload_sha256_equal_luna"] = (
            manifest.get("pre_enforcement_payload_sha256") == cond["luna_pre_enforcement_payload_sha256"]
        )
        checks["n_cards_inadmissible_equal_luna"] = manifest.get("n_cards_inadmissible") == luna.get("n_cards_inadmissible")
        checks["decision_condition_equal_luna"] = manifest.get("decision_condition") == luna.get("decision_condition")
    if "rule_order" in luna:
        checks["rule_order_equal_luna"] = manifest.get("rule_order") == luna.get("rule_order")
    if "voi_scores_withheld_from_model" in luna:
        checks["voi_withheld_flag_equal_luna"] = (
            manifest.get("voi_scores_withheld_from_model") == luna.get("voi_scores_withheld_from_model")
        )
    return checks


def run_command(cond: dict[str, Any], tree: Path, run_dir: Path) -> list[str]:
    runner = str(tree / cond["runner"])
    if cond["condition_key"] == "naive_direct_llm":
        return [
            sys.executable, runner,
            "--candidate-set", str(tree / "derived" / "stage1_blind_candidate_space_v1.json"),
            "--naive-view", str(tree / "derived" / "naive_baseline_view.json"),
            "--output-dir", str(run_dir),
        ]
    cmd = [sys.executable, runner]
    flags = list(cond["runner_flags"])
    if cond["runner"].endswith("run_agent_v5.py"):
        cmd += flags
    cmd += [
        "--candidate-set", str(tree / "derived" / "stage1_blind_candidate_space_v1.json"),
        "--evidence-state", str(tree / "derived" / "evidence_state.json"),
        "--output-dir", str(run_dir),
    ]
    if cond["runner"].endswith("run_agent_v4.py"):
        cmd += flags
    return cmd


def frozen_outputs(cond: dict[str, Any], run_dir: Path) -> list[Path]:
    if cond["condition_key"] == "naive_direct_llm":
        return sorted(p for p in run_dir.glob("REC_BASELINE_*.json") if not p.name.endswith(".meta.json"))
    pattern = "EXP_V5_*/recommendation.json" if cond["runner"].endswith("run_agent_v5.py") else "EXP_V4_*/recommendation.json"
    return sorted(run_dir.glob(pattern))


def classify(cond: dict[str, Any], returncode: int, frozen: list[Path], stderr: str) -> tuple[str, bool]:
    if returncode == 0 and frozen:
        return "ok", False
    if TECHNICAL_PATTERNS.search(stderr or "") or "model returned empty content" in (stderr or ""):
        # protocol amendment 1.0.1: an empty HTTP-200 body is an endpoint failure, not model output
        return "technical_failure", True
    # anything else is a model-output failure (unparseable or contract-violating JSON); it stays
    # in the denominator. QC reviews every non-ok stderr tail by hand.
    return "invalid", False


def wait_for_quota(env: dict[str, str], model: str) -> None:
    """One-token probe before each run. On a router usage limit, sleep until the reset so that
    quota exhaustion never consumes a replicate slot. The probe is not part of any run."""
    from openai import OpenAI, RateLimitError

    client = OpenAI(api_key=env["OPENAI_API_KEY"], base_url=env["OPENAI_BASE_URL"])
    transient = 0
    while True:
        try:
            client.chat.completions.create(model=model, messages=[{"role": "user", "content": "Reply with: ok"}])
            return
        except RateLimitError as exc:
            match = re.search(r"resets_in_seconds\W*(\d+)", str(exc))
            wait = int(match.group(1)) + 90 if match else 600
            log_line(f"quota probe: usage limit, sleeping {wait}s before the next run")
            time.sleep(wait)
        except Exception as exc:  # connection/5xx: back off, give up after 30 min
            transient += 1
            if transient > 30:
                raise SystemExit(f"quota probe failed repeatedly: {type(exc).__name__}")
            log_line(f"quota probe: {type(exc).__name__}, retrying in 60s")
            time.sleep(60)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", type=Path, required=True)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--declare-only", action="store_true")
    parser.add_argument("--resume-batch", action="store_true", help="complete unattempted pairs of the last batch")
    args = parser.parse_args()

    protocol = read_json(PROTOCOL_PATH)
    model = protocol["model"]
    n_declared = protocol["replicate_design"]["n_runs_declared_in_series_manifests"]
    trees = read_json(REPLAY_TREES)["trees"]
    env = load_dotenv(args.env_file)
    env["OPENAI_MODEL"] = model
    for required in ("OPENAI_API_KEY", "OPENAI_BASE_URL"):
        if required not in env:
            raise SystemExit(f"{required} missing from env file")
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. replay trees still byte-exact
    for key, entry in trees.items():
        if not entry["accepted"]:
            raise SystemExit(f"replay tree {key} was not accepted")
        bad = verify_tree(entry)
        if bad:
            raise SystemExit(f"replay tree {key} drifted since it was built: {bad}")

    cumulative = read_json(CUMULATIVE) if CUMULATIVE.exists() else {
        "protocol_id": protocol["protocol_id"],
        "model": model,
        "created_utc": utc_now(),
        "series": {},
        "batches": [],
        "replicates": [],
    }

    # 2. declare (or restore) each series and check it against Luna before any model call
    for cond in protocol["conditions"]:
        key = cond["condition_key"]
        tree = Path(trees[key]["tree"])
        main_manifest = ROOT / series_dir(key) / "series_manifest.json"
        tree_series = tree / series_dir(key)
        if main_manifest.exists():
            if not (tree_series / "series_manifest.json").exists():
                sync_dir(ROOT / series_dir(key), tree_series)
            manifest = read_json(main_manifest)
        else:
            manifest = declare_series(cond, tree, args.env_file, model, n_declared)
            sync_dir(tree_series, ROOT / series_dir(key))
            log_line(f"declared series {key}: N={n_declared} (no model call)")
        checks = check_declaration(cond, manifest)
        cumulative["series"][key] = {
            "series_dir": str(series_dir(key)).replace("\\", "/"),
            "replay_tree": str(tree),
            "replay_base_commit": trees[key]["base_commit"],
            "luna_reference": cond["luna_reference"],
            "declaration_checks": checks,
        }
        if not all(checks.values()):
            write_json(CUMULATIVE, cumulative)
            raise SystemExit(f"declaration check failed for {key}: {checks}")
    write_json(CUMULATIVE, cumulative)
    log_line("all series declared and verified against the Luna contracts")
    if args.declare_only:
        return 0

    # 3. replicate ids: resume the last batch's unattempted pairs, or open a new batch
    if args.resume_batch:
        if not cumulative["batches"]:
            raise SystemExit("--resume-batch: no batch to resume")
        batch = cumulative["batches"][-1]
        batch_id, ids = batch["batch_id"], batch["replicate_ids"]
        batch.setdefault("resumed", []).append({
            "utc": utc_now(), "driver_sha256": sha256_file(Path(__file__)), "protocol_sha256": sha256_file(PROTOCOL_PATH),
        })
        batch.pop("finished_utc", None)
        log_line(f"{batch_id}: resuming unattempted pairs of {ids[0]}..{ids[-1]}")
    else:
        existing = {row["replicate_id"] for row in cumulative["replicates"]}
        for cond in protocol["conditions"]:
            for d in (ROOT / series_dir(cond["condition_key"])).glob("sol_r*"):
                existing.add(d.name)
        start = max((int(r[5:]) for r in existing), default=0) + 1
        ids = [f"sol_r{i:03d}" for i in range(start, start + args.batch_size)]
        batch_id = f"batch_{len(cumulative['batches']) + 1:02d}"
        batch = {
            "batch_id": batch_id,
            "role": "execution batch (provenance only, not an explanatory variable)",
            "replicate_ids": ids,
            "started_utc": utc_now(),
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "openai_package": importlib.metadata.version("openai"),
            "driver_sha256": sha256_file(Path(__file__)),
            "protocol_sha256": sha256_file(PROTOCOL_PATH),
            "main_tree_git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        }
        cumulative["batches"].append(batch)
        log_line(f"{batch_id}: replicates {ids[0]}..{ids[-1]}")
    write_json(CUMULATIVE, cumulative)

    # 4. replicates, conditions interleaved; an attempted pair is never run again
    for rep in ids:
        rep_row = next((r for r in cumulative["replicates"] if r["replicate_id"] == rep), None)
        if rep_row is None:
            rep_row = {"replicate_id": rep, "batch_id": batch_id, "started_utc": utc_now(), "conditions": {}}
            cumulative["replicates"].append(rep_row)
        for cond in protocol["conditions"]:
            key = cond["condition_key"]
            if key in rep_row["conditions"]:
                continue
            tree = Path(trees[key]["tree"])
            tree_series = tree / series_dir(key)
            run_dir = tree_series / rep
            if run_dir.exists() or (ROOT / series_dir(key) / rep).exists():
                raise SystemExit(f"refusing to overwrite existing run directory {key}/{rep}")
            wait_for_quota(env, model)
            run_dir.mkdir(parents=True)
            full_env = {**os.environ, **env, "PYTHONPATH": str(tree / "src")}
            started = utc_now()
            t0 = time.perf_counter()
            proc = subprocess.run(run_command(cond, tree, run_dir), cwd=tree, env=full_env, capture_output=True, text=True)
            wall = round(time.perf_counter() - t0, 2)
            (run_dir / "driver_stdout.txt").write_text(proc.stdout or "", encoding="utf-8")
            (run_dir / "driver_stderr.txt").write_text(proc.stderr or "", encoding="utf-8")
            frozen = frozen_outputs(cond, run_dir)
            status, technical = classify(cond, proc.returncode, frozen, proc.stderr)
            record = {
                "run_index": int(rep[5:]),
                "replicate_id": rep,
                "run_dir": str(series_dir(key) / rep),
                "started_utc": started,
                "finished_utc": utc_now(),
                "wall_seconds": wall,
                "returncode": proc.returncode,
                "status": status,
                "technical_failure": technical,
                "frozen_recommendation": (
                    str(series_dir(key) / rep / frozen[0].relative_to(run_dir)) if frozen else None
                ),
            }
            if status != "ok":
                record["stderr_tail"] = (proc.stderr or "").strip().splitlines()[-8:]
            manifest_path = tree_series / "series_manifest.json"
            manifest = read_json(manifest_path)
            manifest["runs"].append(record)
            manifest["runs"].sort(key=lambda row: row["run_index"])
            manifest["n_attempted"] = len(manifest["runs"])
            manifest["n_ok"] = sum(r["status"] == "ok" for r in manifest["runs"])
            manifest["n_invalid"] = sum(r["status"] == "invalid" for r in manifest["runs"])
            manifest["n_technical_failure"] = sum(bool(r.get("technical_failure")) for r in manifest["runs"])
            write_json(manifest_path, manifest)
            sync_dir(run_dir, ROOT / series_dir(key) / rep)
            shutil.copy2(manifest_path, ROOT / series_dir(key) / "series_manifest.json")
            rep_row["conditions"][key] = {k: record[k] for k in ("status", "technical_failure", "run_dir", "wall_seconds", "returncode")}
            write_json(CUMULATIVE, cumulative)
            log_line(f"{rep} {key}: {status} ({wall}s)")
        rep_row["finished_utc"] = utc_now()
        write_json(CUMULATIVE, cumulative)

    batch["finished_utc"] = utc_now()
    write_json(CUMULATIVE, cumulative)
    log_line(f"{batch_id} finished")
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "crossmodel" / "summarize_crossmodel.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    log_line(f"summary rc={proc.returncode} {(proc.stdout or '').strip()[-300:]} {(proc.stderr or '').strip()[-500:]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
