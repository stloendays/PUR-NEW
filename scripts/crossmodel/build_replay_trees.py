#!/usr/bin/env python3
"""Build one byte-exact replay tree per Luna condition for the gpt-5.6-sol replication.

A replay tree is a detached git worktree at the commit a Luna series was declared at. Every
file pinned in that series manifest is overwritten with the historical bytes whose sha256
equals the pin, searched across all of git history in raw, LF and CRLF form. The tree is
accepted only if it then reproduces every pinned hash plus the candidate-set and
evidence-state hashes. Nothing in the main working tree is modified.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "configs" / "crossmodel_sol_v4_protocol.json"
DEFAULT_TREES = Path("D:/Research/_purnew_wt/sol_replay")
DEFAULT_OUT = ROOT / "results" / "multimodel" / "gpt-5_6-sol" / "v4_benchmark" / "replay_trees.json"
CANDIDATE_SET = "derived/stage1_blind_candidate_space_v1.json"
EVIDENCE_STATE = "derived/evidence_state.json"
NAIVE_VIEW = "derived/naive_baseline_view.json"
NAIVE_PROMPT = "prompts/baseline_direct_llm.txt"
LF = b"\n"
CRLF = b"\r\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str, cwd: Path = ROOT) -> str:
    return subprocess.check_output(["git", *args], cwd=cwd, text=True).strip()


def git_bytes(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT, stderr=subprocess.DEVNULL)


def to_crlf(blob: bytes) -> bytes:
    """Bytes as an autocrlf=true checkout writes them."""
    return blob.replace(CRLF, LF).replace(LF, CRLF)


def historical_bytes(path: str, digest: str) -> tuple[bytes, str, str] | None:
    """Find bytes for `path` anywhere in history whose sha256 is `digest`."""
    commits = git("log", "--all", "--format=%H", "--", path).split()
    for commit in commits:
        try:
            blob = git_bytes("show", f"{commit}:{path}")
        except subprocess.CalledProcessError:
            continue
        lf = blob.replace(CRLF, LF)
        for form, data in (("raw", blob), ("lf", lf), ("crlf", to_crlf(blob))):
            if sha256_bytes(data) == digest:
                return data, commit, form
    return None


def ensure_worktree(tree: Path, commit: str) -> None:
    if tree.exists():
        head = git("rev-parse", "HEAD", cwd=tree)
        if head != commit:
            raise SystemExit(f"{tree} exists at {head}, expected {commit}")
        return
    tree.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call(["git", "worktree", "add", "--detach", str(tree), commit], cwd=ROOT)


def base_checkout_sha256(base: str, path: str) -> str | None:
    """sha256 of `path` as a plain autocrlf checkout of `base` would write it."""
    try:
        return sha256_bytes(to_crlf(git_bytes("show", f"{base}:{path}")))
    except subprocess.CalledProcessError:
        return None


def pin_file(tree: Path, base: str, path: str, digest: str) -> dict[str, Any]:
    target = tree / path
    source = "checkout" if base_checkout_sha256(base, path) == digest else "overlay"
    if source == "checkout" and target.exists() and sha256_bytes(target.read_bytes()) == digest:
        return {"path": path, "sha256": digest, "source": source}
    found = historical_bytes(path, digest)
    if found is None:
        raise SystemExit(f"no historical bytes reproduce {path} sha256={digest}")
    data, commit, form = found
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or sha256_bytes(target.read_bytes()) != digest:
        target.write_bytes(data)
    return {"path": path, "sha256": digest, "source": source, "from_commit": commit, "form": form}


def overlay_from_commit(tree: Path, commit: str, path: str) -> dict[str, Any]:
    """Unpinned orchestration/support file taken from a named commit, recorded by hash."""
    source = git("rev-parse", commit)
    data = to_crlf(git_bytes("show", f"{source}:{path}"))
    (tree / path).write_bytes(data)
    return {"path": path, "from_commit": source, "sha256": sha256_bytes(data)}


def provenance_hashes(tree: Path) -> dict[str, str]:
    files = sorted((tree / "src" / "pur_new").glob("*.py")) + sorted((tree / "scripts").glob("run_*.py"))
    return {str(p.relative_to(tree)).replace("\\", "/"): sha256_bytes(p.read_bytes()) for p in files}


def canonical_hash(value: Any) -> str:
    return sha256_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )


def pin_view_by_canonical_hash(tree: Path, base: str, path: str, digest: str) -> dict[str, Any]:
    """The naive runner hashes the parsed view, so match on canonical JSON, not bytes."""
    target = tree / path
    try:
        base_view = json.loads(git_bytes("show", f"{base}:{path}").decode("utf-8"))
        source = "checkout" if canonical_hash(base_view) == digest else "overlay"
    except subprocess.CalledProcessError:
        source = "overlay"
    for commit in git("log", "--all", "--format=%H", "--", path).split():
        data = git_bytes("show", f"{commit}:{path}")
        if canonical_hash(json.loads(data.decode("utf-8"))) == digest:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            return {"path": path, "canonical_sha256": digest, "source": source, "from_commit": commit, "form": "raw"}
    raise SystemExit(f"no historical {path} reproduces canonical sha256={digest}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trees-root", type=Path, default=DEFAULT_TREES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
    report: dict[str, Any] = {"built_utc": utc_now(), "protocol_id": protocol["protocol_id"], "trees": {}}

    for cond in protocol["conditions"]:
        key = cond["condition_key"]
        tree = args.trees_root / key
        entry: dict[str, Any] = {"tree": str(tree), "luna_reference": cond["luna_reference"]}
        if key == "naive_direct_llm":
            commit = cond["luna_reference_git_commit"]
            ensure_worktree(tree, commit)
            pins = [pin_view_by_canonical_hash(tree, commit, NAIVE_VIEW, cond["luna_reference_input_hash"])]
            pins.append(pin_file(tree, commit, CANDIDATE_SET, cond["candidate_set_sha256"]))
            prompt_hash = sha256_bytes((tree / NAIVE_PROMPT).read_text(encoding="utf-8").encode("utf-8"))
            input_hash = canonical_hash(json.loads((tree / NAIVE_VIEW).read_text(encoding="utf-8")))
            checks = {
                "prompt_hash_matches_luna": prompt_hash == cond["luna_reference_prompt_hash"],
                "input_hash_matches_luna": input_hash == cond["luna_reference_input_hash"],
                "candidate_set_reproduced": sha256_bytes((tree / CANDIDATE_SET).read_bytes()) == cond["candidate_set_sha256"],
            }
            entry.update({"base_commit": commit, "pins": pins, "checks": checks})
        else:
            manifest = json.loads((ROOT / cond["luna_reference"] / "series_manifest.json").read_text(encoding="utf-8"))
            commit = manifest["git_commit"]
            ensure_worktree(tree, commit)
            pins = [pin_file(tree, commit, path, digest) for path, digest in sorted(manifest["series_input_hashes"].items())]
            if cond.get("declaration_runner_from_commit"):
                entry["declaration_runner_overlay"] = overlay_from_commit(
                    tree, cond["declaration_runner_from_commit"], cond["declaration_runner"]
                )
            for support in cond.get("support_files", []):
                entry.setdefault("support_file_overlays", []).append(
                    overlay_from_commit(tree, support["from_commit"], support["path"])
                )
            pins.append(pin_file(tree, commit, CANDIDATE_SET, manifest["candidate_set_sha256"]))
            pins.append(pin_file(tree, commit, EVIDENCE_STATE, manifest["evidence_state_sha256"]))
            checks = {
                "all_pins_reproduced": all(
                    sha256_bytes((tree / p["path"]).read_bytes()) == p["sha256"] for p in pins
                )
            }
            entry.update({"base_commit": commit, "pins": pins, "checks": checks})
        entry["unpinned_code_sha256"] = provenance_hashes(tree)
        entry["accepted"] = all(entry["checks"].values())
        report["trees"][key] = entry
        state = "ACCEPTED" if entry["accepted"] else "REJECTED"
        overlays = sum(p.get("source") == "overlay" for p in entry["pins"])
        print(f"{key}: {state} base={entry['base_commit'][:9]} overlays={overlays} checks={entry['checks']}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if not all(t["accepted"] for t in report["trees"].values()):
        raise SystemExit("at least one replay tree failed verification")


if __name__ == "__main__":
    main()
