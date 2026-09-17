#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import selection_entropy  # noqa: E402
from pur_new.evidence_firewall import find_blind_payload_violations  # noqa: E402


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_recommendations(path: Path) -> list[Path]:
    files: list[Path] = []
    if path.is_file():
        return [path]
    files.extend(path.rglob("recommendation.json"))
    files.extend(
        p for p in path.rglob("REC_*.json")
        if p.name != "recommendation.json" and not p.name.endswith(".meta.json")
    )
    return sorted(set(files))


def discover_failures(path: Path) -> list[Path]:
    if path.is_file():
        return []
    return sorted(path.rglob("failure_*.json"))


def parse_condition(text: str) -> tuple[str, Path]:
    if "=" not in text:
        raise argparse.ArgumentTypeError("condition must be NAME=PATH")
    name, raw = text.split("=", 1)
    if not name or not raw:
        raise argparse.ArgumentTypeError("condition must be NAME=PATH")
    return name, Path(raw)


def ranking_from_record(record: dict[str, Any]) -> list[str]:
    out: list[str] = []
    selected = record.get("selected_candidate")
    if isinstance(selected, dict) and selected.get("candidate_id"):
        out.append(str(selected["candidate_id"]))
    for alt in record.get("alternatives_considered", []):
        cid = alt.get("candidate_id") if isinstance(alt, dict) else None
        if cid and cid not in out:
            out.append(str(cid))
    return out


def candidate_axes(candidate_set: dict[str, Any]) -> dict[str, tuple[float, float]]:
    out: dict[str, tuple[float, float]] = {}
    for c in candidate_set["candidates"]:
        fs = c["formulation_state"]
        ac = float(fs.get("acrylic_like_modifier_pct", fs.get("AC1920", 0.0)))
        tk = float(fs.get("minor_tackifier_like_modifier_pct", fs.get("TK100", 0.0)))
        out[c["candidate_id"]] = (ac, tk)
    return out


def l1_distance(point: tuple[float, float], target: tuple[float, float]) -> float:
    return abs(point[0] - target[0]) + abs(point[1] - target[1])


def load_deliberation_for_recommendation(path: Path) -> dict[str, Any] | None:
    sibling = path.parent / "deliberation.json"
    if sibling.exists():
        return read_json(sibling)
    return None


def load_runtime_meta(path: Path, deliberation: dict[str, Any] | None) -> dict[str, Any]:
    if deliberation is not None:
        total = deliberation.get("llm_usage_total")
        if isinstance(total, dict):
            return total
    if path.name != "recommendation.json":
        meta_path = path.with_name(f"{path.stem}.meta.json")
        if meta_path.exists():
            meta = read_json(meta_path)
            return {
                "llm_calls": 1,
                "prompt_tokens": meta.get("prompt_tokens"),
                "completion_tokens": meta.get("completion_tokens"),
                "total_tokens": meta.get("total_tokens"),
                "llm_latency_s": meta.get("latency_s"),
            }
    return {}


def controller_target(target_cfg: dict[str, Any]) -> dict[str, float]:
    for key in ("validation_formulation_normalized_pct", "follow_up_normalized_pct"):
        value = target_cfg.get(key)
        if isinstance(value, dict):
            return value
    raise KeyError(
        "controller_only_heldout_target must contain validation_formulation_normalized_pct "
        "or legacy follow_up_normalized_pct"
    )


def summarize_condition(
    name: str,
    files: list[Path],
    failure_files: list[Path],
    *,
    axes: dict[str, tuple[float, float]],
    nearest_candidate_id: str,
    target: tuple[float, float],
    blinded_ids: set[str],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    failures = [read_json(path) for path in failure_files]
    selections: list[str | None] = []

    for path in files:
        record = read_json(path)
        ranking = ranking_from_record(record)
        mode = record.get("decision_mode")
        selected_id = ranking[0] if ranking else None
        selections.append(selected_id)

        top1_dist = l1_distance(axes[selected_id], target) if selected_id in axes else None
        top3_ids = ranking[:3]
        top3_distances = [l1_distance(axes[cid], target) for cid in top3_ids if cid in axes]
        best_top3 = min(top3_distances) if top3_distances else None

        deliberation = load_deliberation_for_recommendation(path)
        runtime = load_runtime_meta(path, deliberation)
        tool_calls = None
        tool_ok_fraction = None
        leakage_findings = 0
        skeptic_boundary = None
        skeptic_leakage = None
        ablation = None
        if deliberation is not None:
            ablation = deliberation.get("ablation")
            trace = deliberation.get("tool_trace", [])
            tool_calls = len(trace)
            if trace:
                tool_ok_fraction = sum(1 for x in trace if x.get("status") == "ok") / len(trace)
            leakage_findings = len(
                find_blind_payload_violations(
                    deliberation,
                    blinded_formulation_ids=blinded_ids,
                    forbid_follow_up_stage=True,
                )
            )
            skeptic = deliberation.get("skeptic", {})
            if isinstance(skeptic, dict):
                if isinstance(skeptic.get("scientific_boundary_check"), dict):
                    skeptic_boundary = skeptic["scientific_boundary_check"].get("status")
                if isinstance(skeptic.get("leakage_check"), dict):
                    skeptic_leakage = skeptic["leakage_check"].get("status")

        rows.append(
            {
                "condition": name,
                "file": str(path),
                "ablation": ablation,
                "decision_mode": mode,
                "selected_candidate_id": selected_id,
                "nearest_candidate_rank": (ranking.index(nearest_candidate_id) + 1) if nearest_candidate_id in ranking else None,
                "nearest_candidate_top1": selected_id == nearest_candidate_id,
                "nearest_candidate_top3": nearest_candidate_id in top3_ids,
                "top1_l1_distance": top1_dist,
                "best_top3_l1_distance": best_top3,
                "tool_calls": tool_calls,
                "tool_ok_fraction": tool_ok_fraction,
                "llm_calls": runtime.get("llm_calls"),
                "prompt_tokens": runtime.get("prompt_tokens"),
                "completion_tokens": runtime.get("completion_tokens"),
                "total_tokens": runtime.get("total_tokens"),
                "llm_latency_s": runtime.get("llm_latency_s"),
                "structural_leakage_findings": leakage_findings,
                "skeptic_boundary_check": skeptic_boundary,
                "skeptic_leakage_check": skeptic_leakage,
            }
        )

    valid = [r for r in rows if r["selected_candidate_id"] is not None]
    n_completed = len(rows)
    n_failed = len(failures)
    n_attempted = n_completed + n_failed
    selected_counts = Counter(r["selected_candidate_id"] or "__ABSTAIN__" for r in rows)

    def mean_numeric(key: str, subset: list[dict[str, Any]] = rows) -> float | None:
        values = [float(r[key]) for r in subset if r.get(key) is not None]
        return sum(values) / len(values) if values else None

    summary = {
        "condition": name,
        "n_attempted": n_attempted,
        "n_completed": n_completed,
        "n_failed": n_failed,
        "failure_rate": n_failed / n_attempted if n_attempted else None,
        "n_nonabstaining": len(valid),
        "abstention_rate_among_completed": (n_completed - len(valid)) / n_completed if n_completed else None,
        "selection_entropy_bits": selection_entropy(selections),
        "selection_distribution": dict(sorted(selected_counts.items())),
        "nearest_candidate_top1_rate": (
            sum(bool(r["nearest_candidate_top1"]) for r in valid) / len(valid) if valid else None
        ),
        "nearest_candidate_top3_rate": (
            sum(bool(r["nearest_candidate_top3"]) for r in valid) / len(valid) if valid else None
        ),
        "mean_top1_l1_distance": mean_numeric("top1_l1_distance", valid),
        "mean_best_top3_l1_distance": mean_numeric("best_top3_l1_distance", valid),
        "mean_tool_calls": mean_numeric("tool_calls"),
        "mean_tool_ok_fraction": mean_numeric("tool_ok_fraction"),
        "mean_llm_calls": mean_numeric("llm_calls"),
        "mean_prompt_tokens": mean_numeric("prompt_tokens"),
        "mean_completion_tokens": mean_numeric("completion_tokens"),
        "mean_total_tokens": mean_numeric("total_tokens"),
        "mean_llm_latency_s": mean_numeric("llm_latency_s"),
        "runs_with_structural_leakage": sum(r["structural_leakage_findings"] > 0 for r in rows),
        "skeptic_boundary_failures": sum(r["skeptic_boundary_check"] == "fail" for r in rows),
        "skeptic_leakage_failures": sum(r["skeptic_leakage_check"] == "fail" for r in rows),
        "failure_types": dict(sorted(Counter(str(f.get("failure_type", "unknown")) for f in failures).items())),
    }
    return summary, rows, failures


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize PUR-NEW Agent benchmark conditions")
    p.add_argument("--condition", action="append", required=True, type=parse_condition, help="NAME=PATH; repeat for each condition")
    p.add_argument("--candidate-set", type=Path, required=True)
    p.add_argument("--benchmark-config", type=Path, default=ROOT / "configs" / "blind_benchmark_v2.json")
    p.add_argument("--output-dir", type=Path, default=ROOT / "records" / "benchmarks" / "agent_v3_summary")
    args = p.parse_args()

    candidate_set = read_json(args.candidate_set)
    benchmark = read_json(args.benchmark_config)
    axes = candidate_axes(candidate_set)
    target_cfg = benchmark["controller_only_heldout_target"]
    target_pct = controller_target(target_cfg)
    target = (float(target_pct["AC1920"]), float(target_pct["TK100"]))
    nearest_candidate_id = str(target_cfg["nearest_candidate_id"])
    architecture = read_json(ROOT / "configs" / "agent_v3.json")
    blinded_ids = set(architecture.get("blinded_target_formulation_ids", []))

    summaries = []
    all_rows: list[dict[str, Any]] = []
    all_failures: list[dict[str, Any]] = []
    for name, path in args.condition:
        files = discover_recommendations(path)
        failure_files = discover_failures(path)
        summary, rows, failures = summarize_condition(
            name,
            files,
            failure_files,
            axes=axes,
            nearest_candidate_id=nearest_candidate_id,
            target=target,
            blinded_ids=blinded_ids,
        )
        summaries.append(summary)
        all_rows.extend(rows)
        for failure in failures:
            item = dict(failure)
            item.setdefault("condition", name)
            all_failures.append(item)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "heldout_target_used_controller_side_only": {
            "nearest_candidate_id": nearest_candidate_id,
            "target_acrylic_pct": target[0],
            "target_tackifier_pct": target[1],
        },
        "conditions": summaries,
        "interpretation": (
            "This scorer is controller-side only. Held-out target coordinates must never be included in Agent payloads. "
            "Failed attempts are retained and counted. Token/latency metrics are reported so any V3 gain can be interpreted against extra inference cost. "
            "Architecture advantage should be claimed only if the full Agent improves recovery/robustness without increasing failure, leakage, or scientific-boundary violations beyond an acceptable trade-off."
        ),
    }
    (args.output_dir / "benchmark_summary.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    fieldnames = [
        "condition",
        "file",
        "ablation",
        "decision_mode",
        "selected_candidate_id",
        "nearest_candidate_rank",
        "nearest_candidate_top1",
        "nearest_candidate_top3",
        "top1_l1_distance",
        "best_top3_l1_distance",
        "tool_calls",
        "tool_ok_fraction",
        "llm_calls",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "llm_latency_s",
        "structural_leakage_findings",
        "skeptic_boundary_check",
        "skeptic_leakage_check",
    ]
    with (args.output_dir / "benchmark_runs.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    (args.output_dir / "benchmark_failures.json").write_text(
        json.dumps(all_failures, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(args.output_dir)


if __name__ == "__main__":
    main()
