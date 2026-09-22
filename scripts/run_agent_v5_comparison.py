#!/usr/bin/env python3
"""Deterministic cross-arm comparison of the two primary Agent V5 arms.

The comparison is ``V5_NO_GATE`` versus ``V5_FULL``: same runtime, same prompts, same model
endpoint, same candidate lattice, same hypothesis registry, same measurement catalog, same
evidence profile, same VOI weights and -- under protocol v1.1 -- the same model-visible
chemistry applicability audit. The only declared difference is whether that identical audit
is enforced as hard experiment-card admissibility, which the parity check verifies through
the arm-independent pre-enforcement payload hash.

This script reads two frozen arm series and writes the machine-readable comparison. It
calls no model and computes no metric that contains held-out wet-lab information. Every
rate is reported with its numerator and both denominators -- committed selections and
declared runs -- because a rate over an unstated denominator is not a result.

Frozen V4 is historical architecture context and is deliberately not pooled into this
table: V4 differs from V5 in more than the gate, so it cannot isolate the gate effect.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v3 import selection_entropy  # noqa: E402
from pur_new.agent_v5 import ARMS  # noqa: E402

# The parity file list is read from the series manifests rather than imported from the
# runner. Each series froze the list it actually hashed, and different decision conditions
# legitimately hash different registry and catalog files. Comparing against a module
# constant would silently check the wrong list for any condition but the default.

CSV_COLUMNS = [
    "arm",
    "run_index",
    "status",
    "model",
    "decision_mode",
    "selected_candidate_id",
    "selected_measurement_id",
    "selected_experiment_id",
    "intervention_family",
    "chemistry_applicability_status",
    "shared_shape_use",
    "admissibility_rule_id",
    "chemistry_domain_violation",
    "unsupported_shortcut",
    "hypothesis_discrimination",
    "voi_score",
    "selected_is_in_tied_top_set",
    "n_cards_removed_by_gate",
    "tool_calls",
    "mandatory_tool_executed",
    "prompt_tokens",
    "completion_tokens",
    "total_tokens",
    "llm_latency_s",
    "recommendation_id",
    "pre_enforcement_payload_hash",
    "input_hash",
    "prompt_hash",
    "candidate_set_hash",
    "run_dir",
]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    """Wilson score interval. Returns None when the denominator is zero."""
    if total == 0:
        return None
    phat = successes / total
    denom = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def rate(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": round(numerator / denominator, 6) if denominator else None,
        "wilson_95ci": wilson(numerator, denominator),
    }


def load_run_row(arm: str, record: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {column: None for column in CSV_COLUMNS}
    row.update(
        {
            "arm": arm,
            "run_index": record["run_index"],
            "status": record["status"],
            "model": manifest.get("model"),
            "run_dir": record.get("run_dir"),
        }
    )

    frozen = record.get("frozen_recommendation")
    if record["status"] == "ok" and frozen:
        run_dir = ROOT / frozen
        recommendation = read_json(run_dir / "recommendation.json")
        deliberation = read_json(run_dir / "deliberation.json")
        card = recommendation.get("experiment_card") or {}
        gate = recommendation.get("chemistry_gate") or {}
        selection = gate.get("selection") or {}
        usage = deliberation.get("llm_usage_total") or {}
        discrimination = (card.get("voi_components") or {}).get("hypothesis_discrimination")
        row.update(
            {
                "decision_mode": recommendation.get("decision_mode"),
                "selected_candidate_id": recommendation.get("selected_candidate_id"),
                "selected_measurement_id": recommendation.get("selected_measurement_id"),
                "selected_experiment_id": recommendation.get("selected_experiment_id"),
                "intervention_family": card.get("intervention_family"),
                "chemistry_applicability_status": selection.get("chemistry_applicability_status"),
                "shared_shape_use": selection.get("shared_shape_use"),
                "admissibility_rule_id": selection.get("admissibility_rule_id"),
                "chemistry_domain_violation": selection.get("chemistry_domain_violation"),
                "unsupported_shortcut": selection.get("unsupported_shortcut"),
                "hypothesis_discrimination": discrimination,
                "voi_score": (recommendation.get("voi") or {}).get("score"),
                "selected_is_in_tied_top_set": (recommendation.get("voi") or {}).get(
                    "selected_is_in_tied_top_set"
                ),
                "n_cards_removed_by_gate": gate.get("n_cards_removed_from_selectable_set"),
                "tool_calls": len(deliberation.get("tool_trace") or []),
                "mandatory_tool_executed": deliberation.get("mandatory_local_science_tool_executed"),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "llm_latency_s": round(float(usage.get("llm_latency_s") or 0.0), 3),
                "recommendation_id": recommendation.get("recommendation_id"),
                "pre_enforcement_payload_hash": recommendation.get("pre_enforcement_payload_hash"),
                "input_hash": recommendation.get("input_hash"),
                "prompt_hash": recommendation.get("prompt_hash"),
                "candidate_set_hash": recommendation.get("candidate_set_hash"),
            }
        )
        return row

    rejected = ROOT / (record.get("run_dir") or "") / "REJECTED" / "rejected_deliberation.json"
    if rejected.exists():
        payload = read_json(rejected)
        usage = payload.get("llm_usage_total") or {}
        judge = payload.get("judge_normalized") or {}
        row.update(
            {
                "decision_mode": judge.get("decision_mode"),
                "selected_experiment_id": judge.get("selected_experiment_id"),
                "selected_candidate_id": judge.get("selected_candidate_id"),
                "selected_measurement_id": judge.get("selected_measurement_id"),
                "admissibility_rule_id": payload.get("rejection_class"),
                "tool_calls": len(payload.get("tool_trace") or []),
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "total_tokens": usage.get("total_tokens"),
                "llm_latency_s": round(float(usage.get("llm_latency_s") or 0.0), 3),
            }
        )
    return row


def summarize_arm(arm: str, manifest: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    declared = int(manifest["n_runs_declared"])
    attempted = len(rows)
    completed = [row for row in rows if row["status"] == "ok"]
    invalid = [row for row in rows if row["status"] == "invalid"]
    failed = [row for row in rows if row["status"] == "failed"]
    abstained = [row for row in completed if row["decision_mode"] == "abstain"]
    committed = [row for row in completed if row["decision_mode"] not in (None, "abstain")]

    violations = sum(1 for row in committed if row["chemistry_domain_violation"])
    shortcuts = sum(1 for row in committed if row["unsupported_shortcut"])
    discs = [row["hypothesis_discrimination"] for row in committed if row["hypothesis_discrimination"] is not None]
    vois = [row["voi_score"] for row in committed if row["voi_score"] is not None]
    tokens = [row["total_tokens"] for row in rows if row["total_tokens"] is not None]
    latencies = [row["llm_latency_s"] for row in rows if row["llm_latency_s"] is not None]

    return {
        "arm": arm,
        "series": manifest.get("series_label"),
        "applicability_gate_enforced": manifest.get("applicability_gate_enforced"),
        "applicability_audit_visible_to_model": manifest.get("applicability_audit_visible_to_model"),
        "pre_enforcement_payload_sha256": manifest.get("pre_enforcement_payload_sha256"),
        "model": manifest.get("model"),
        "counts": {
            "declared": declared,
            "attempted": attempted,
            "completed": len(completed),
            "committed": len(committed),
            "abstained": len(abstained),
            "invalid": len(invalid),
            "failed": len(failed),
        },
        "counts_note": (
            "attempted/completed/committed/abstained/invalid/failed are reported separately and no "
            "failed or invalid run was replaced."
        ),
        "primary_metrics": {
            "unsupported_shortcut_rate_over_committed": rate(shortcuts, len(committed)),
            "unsupported_shortcut_rate_over_declared": rate(shortcuts, declared),
            "chemistry_domain_violation_rate_over_committed": rate(violations, len(committed)),
            "chemistry_domain_violation_rate_over_declared": rate(violations, declared),
            "measurement_validity_rate_over_committed": rate(len(committed) - violations, len(committed)),
            "hypothesis_discrimination_mean_over_committed": (
                round(sum(discs) / len(discs), 6) if discs else None
            ),
            "hypothesis_discrimination_n": len(discs),
            "selection_entropy_bits": round(
                selection_entropy(
                    [None if row["decision_mode"] == "abstain" else row["selected_experiment_id"] for row in completed]
                ),
                6,
            ),
            "selection_entropy_note": "abstention is its own category; computed over completed runs",
        },
        "secondary_metrics": {
            "measurement_plan_frequency": dict(
                sorted(Counter(row["selected_measurement_id"] for row in committed).items(), key=lambda kv: str(kv[0]))
            ),
            "intervention_family_frequency": dict(
                sorted(Counter(row["intervention_family"] for row in committed).items(), key=lambda kv: str(kv[0]))
            ),
            "candidate_frequency": dict(
                sorted(Counter(row["selected_candidate_id"] for row in committed).items(), key=lambda kv: str(kv[0]))
            ),
            "voi_of_committed_card_mean": round(sum(vois) / len(vois), 6) if vois else None,
            "selected_in_tied_top_set": sum(1 for row in committed if row["selected_is_in_tied_top_set"]),
            "mandatory_tool_executed_in_all_completed_runs": all(
                bool(row["mandatory_tool_executed"]) for row in completed
            )
            if completed
            else None,
            "n_cards_removed_by_gate": sorted({row["n_cards_removed_by_gate"] for row in completed if row["n_cards_removed_by_gate"] is not None}),
            "total_tokens_sum": sum(tokens) if tokens else None,
            "llm_latency_s_sum": round(sum(latencies), 3) if latencies else None,
        },
    }


def check_parity(manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Verify that the two arms differ only by the declared arm flag."""
    no_gate, full = manifests["V5_NO_GATE"], manifests["V5_FULL"]
    differences: list[str] = []

    declared_left = list(no_gate.get("arm_parity_files") or [])
    declared_right = list(full.get("arm_parity_files") or [])
    if declared_left != declared_right:
        differences.append("arms declared different parity file lists")
    parity_files = sorted(set(declared_left) | set(declared_right))
    if not parity_files:
        differences.append("neither arm declared a parity file list")

    for name in parity_files:
        left = (no_gate.get("series_input_hashes") or {}).get(name)
        right = (full.get("series_input_hashes") or {}).get(name)
        if left is None or right is None:
            differences.append(f"series input not hashed by both arms: {name}")
        elif left != right:
            differences.append(f"series input differs between arms: {name}")

    for key in (
        "model",
        "candidate_set_sha256",
        "evidence_state_sha256",
        "n_runs_declared",
        "top_k",
        "api_base_host",
        "pre_enforcement_payload_sha256",
        "decision_condition",
        "voi_weights",
    ):
        if no_gate.get(key) != full.get(key):
            differences.append(f"series setting differs between arms: {key}")

    if (
        no_gate.get("applicability_gate_enforced") is not False
        or full.get("applicability_gate_enforced") is not True
    ):
        differences.append("arm enforcement flags are not the declared control/treatment pair")

    for arm, manifest in (("V5_NO_GATE", no_gate), ("V5_FULL", full)):
        if manifest.get("applicability_audit_visible_to_model") is not True:
            differences.append(f"{arm} did not expose the applicability audit to the model")

    return {
        "parity_ok": not differences,
        "differences": differences,
        "checked_files": parity_files,
        "decision_condition": no_gate.get("decision_condition"),
        "information_parity_rule": (
            "protocol v1.1: both arms must receive the same model-visible applicability facts. "
            "The pre-enforcement payload hash is the machine-checkable form of that requirement."
        ),
        "pre_enforcement_payload_sha256": {
            "V5_NO_GATE": no_gate.get("pre_enforcement_payload_sha256"),
            "V5_FULL": full.get("pre_enforcement_payload_sha256"),
        },
        "only_intended_difference": (
            "whether the identical chemistry-domain applicability audit is enforced as hard "
            "experiment-card admissibility before VOI and at freeze"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Cross-arm comparison of the two primary Agent V5 arms")
    parser.add_argument("--no-gate-series", type=Path, required=True)
    parser.add_argument("--full-series", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    series_dirs = {"V5_NO_GATE": args.no_gate_series, "V5_FULL": args.full_series}
    manifests: dict[str, dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []
    arm_summaries = []

    for arm in ARMS:
        manifest = read_json(series_dirs[arm] / "series_manifest.json")
        if manifest.get("arm") != arm:
            raise SystemExit(f"{series_dirs[arm]} declares arm {manifest.get('arm')!r}, expected {arm!r}")
        manifests[arm] = manifest
        arm_rows = [load_run_row(arm, record, manifest) for record in manifest.get("runs", [])]
        arm_rows.sort(key=lambda row: row["run_index"])
        rows.extend(arm_rows)
        arm_summaries.append(summarize_arm(arm, manifest, arm_rows))

    parity = check_parity(manifests)
    completed_counts = {item["arm"]: item["counts"]["completed"] for item in arm_summaries}
    comparison_status = (
        "runs_present" if all(count > 0 for count in completed_counts.values()) else "insufficient_runs"
    )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    runs_csv = args.output_dir / "cross_arm_runs.csv"
    with runs_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    summary = {
        "comparison_id": "PUR_NEW_AGENT_V5_CHEMISTRY_GATE_COMPARISON_V1",
        "protocol": "configs/agent_v5_comparison_protocol.json",
        "primary_comparison": "V5_NO_GATE vs V5_FULL",
        "comparison_status": comparison_status,
        "arms": arm_summaries,
        "arms_are_not_pooled": True,
        "parity": parity,
        "interpretation_rule": (
            "This table reports what each arm did. It does not by itself establish that the gated "
            "runtime is better: a difference is interpretable only when the parity check passes, both "
            "denominators are reported, and the arms are not pooled. Frozen V4 is historical "
            "architecture context and is not a same-condition causal comparison for the gate."
        ),
        "forbidden_metrics_not_computed": [
            "distance to the held-out validation formulation",
            "post-result closeness to S1C39 or S1C41",
            "any metric containing held-out wet-lab outcome information",
        ],
    }
    (args.output_dir / "cross_arm_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for item in arm_summaries:
        (args.output_dir / f"arm_summary_{item['arm']}.json").write_text(
            json.dumps(item, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    manifest_out = {
        "comparison_id": summary["comparison_id"],
        "generated_by": "scripts/run_agent_v5_comparison.py",
        "series": {arm: str(path) for arm, path in series_dirs.items()},
        "series_manifest_sha256": {
            arm: sha256_file(series_dirs[arm] / "series_manifest.json") for arm in ARMS
        },
        "series_input_hashes": {arm: manifests[arm].get("series_input_hashes") for arm in ARMS},
        "models": {arm: manifests[arm].get("model") for arm in ARMS},
        "n_runs_declared": {arm: manifests[arm].get("n_runs_declared") for arm in ARMS},
        "counts": {item["arm"]: item["counts"] for item in arm_summaries},
        "parity": parity,
        "rows_written": len(rows),
        "outputs": [
            "cross_arm_runs.csv",
            "cross_arm_summary.json",
            "comparison_manifest.json",
            "arm_summary_V5_NO_GATE.json",
            "arm_summary_V5_FULL.json",
        ],
    }
    (args.output_dir / "comparison_manifest.json").write_text(
        json.dumps(manifest_out, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"wrote {runs_csv} ({len(rows)} rows); parity_ok={parity['parity_ok']}; status={comparison_status}")


if __name__ == "__main__":
    main()
