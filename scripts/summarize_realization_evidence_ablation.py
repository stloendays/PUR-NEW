#!/usr/bin/env python3
"""Summarize the Realization-Aware Evidence Integration (RAEI) diagnostic."""

from __future__ import annotations

import argparse
import json
import statistics
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("NOMINAL_ONLY", "REALIZATION_AWARE")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def summarize_arm(
    arm: str,
    records: list[dict[str, Any]],
    protocol: dict[str, Any],
) -> dict[str, Any]:
    declared = int(protocol["run_design"]["diagnostic_runs_per_arm"])
    policy_measurement = protocol["predeclared_evidence_consistent_policy"][arm][
        "measurement_id"
    ]

    arm_rows = [r for r in records if r.get("arm") == arm]
    ok = [r for r in arm_rows if r.get("status") == "ok"]
    committed = [r for r in ok if r.get("decision_mode") == "commit"]
    abstained = [r for r in ok if r.get("decision_mode") == "abstain"]
    invalid = [r for r in arm_rows if r.get("status") == "invalid"]
    failed = [r for r in arm_rows if r.get("status") == "failed"]

    selected = [r.get("selected_measurement_id") for r in committed]
    distribution = Counter(str(x) for x in selected if x is not None)
    effort = [float(r["effort_points"]) for r in committed if r.get("effort_points") is not None]

    policy_matches = sum(
        r.get("selected_measurement_id") == policy_measurement for r in committed
    )
    anchor = sum(r.get("selected_measurement_id") == "M-ANCHOR" for r in committed)
    reversals = sum(bool(r.get("proposer_to_judge_reversal")) for r in ok)

    out = {
        "declared_runs": declared,
        "attempted_runs": len(arm_rows),
        "completed_valid_runs": len(ok),
        "committed_runs": len(committed),
        "abstained_runs": len(abstained),
        "invalid_runs": len(invalid),
        "failed_runs": len(failed),
        "measurement_selection_distribution": dict(sorted(distribution.items())),
        "anchor_selection_rate_of_declared": anchor / declared,
        "evidence_consistent_policy_measurement": policy_measurement,
        "evidence_consistent_policy_match_rate_of_declared": policy_matches / declared,
        "mean_effort_points_among_committed": (
            statistics.fmean(effort) if effort else None
        ),
        "proposer_to_judge_reversal_rate_of_completed_valid": (
            reversals / len(ok) if ok else None
        ),
    }

    if arm == "NOMINAL_ONLY":
        out["unsupported_anchor_count"] = anchor
        out["unsupported_anchor_rate_of_declared"] = anchor / declared
        out["unsupported_anchor_definition"] = (
            "M-ANCHOR was selected even though this arm supplied no model-visible "
            "cross-temperature realization structure or validated one-anchor transfer."
        )
    else:
        over = sum(
            r.get("selected_measurement_id") not in (None, "M-ANCHOR")
            for r in committed
        )
        out["overmeasurement_count"] = over
        out["overmeasurement_rate_of_declared"] = over / declared
        out["overmeasurement_definition"] = (
            "A committed plan used more measurement burden than M-ANCHOR after this arm "
            "supplied the in-domain E2 anchor validation. This is a diagnostic efficiency "
            "metric, not a statement that the direct measurement is scientifically invalid."
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Summarize the RAEI diagnostic")
    p.add_argument("--series-dir", type=Path, required=True)
    p.add_argument(
        "--output",
        type=Path,
        default=ROOT / "derived" / "realization_evidence_ablation_summary.json",
    )
    p.add_argument("--report", type=Path, default=None)
    args = p.parse_args()

    protocol = read_json(ROOT / "configs" / "realization_evidence_ablation_v1.json")
    manifest = read_json(args.series_dir / "series_manifest.json")
    records = [
        read_json(path)
        for path in sorted(args.series_dir.glob("run_*_*.json"))
        if path.name != "series_manifest.json"
    ]

    arms = {
        arm: summarize_arm(arm, records, protocol)
        for arm in ARMS
    }
    n_effort = arms["NOMINAL_ONLY"]["mean_effort_points_among_committed"]
    a_effort = arms["REALIZATION_AWARE"]["mean_effort_points_among_committed"]
    effort_delta = (
        a_effort - n_effort
        if a_effort is not None and n_effort is not None
        else None
    )

    summary = {
        "analysis_id": "RAEI_DIAGNOSTIC_SUMMARY_V1",
        "reader_facing_name": protocol["reader_facing_name"],
        "acronym": protocol["acronym"],
        "protocol_id": protocol["protocol_id"],
        "series_git_commit": manifest.get("git_commit"),
        "model": manifest.get("model"),
        "scientific_question": protocol["scientific_question"],
        "arms": arms,
        "descriptive_contrast": {
            "mean_effort_points_REALIZATION_AWARE_minus_NOMINAL_ONLY": effort_delta,
            "interpretation": (
                "Negative values mean the realization-aware representation led to a lower "
                "declared measurement burden on average among committed decisions."
                if effort_delta is not None
                else "Not estimable because at least one arm had no committed valid decision."
            ),
        },
        "preexisting_material_evidence": {
            "formulation_only_multiplicative_rmse": 1.8244156992081213,
            "one_anchor_multiplicative_rmse": 1.086317254261679,
            "log_rmse_reduction_fraction": 0.8623002671298862,
            "role": (
                "This is the already completed same-formulation E2 materials analysis used "
                "only in the REALIZATION_AWARE evidence arm; it is not a new material replicate."
            ),
        },
        "claim_boundary": protocol["claim_boundaries"],
        "reporting_note": (
            "This N=5-per-arm series is a diagnostic evidence-representation experiment. "
            "It is not pooled with CRB, RGES or CBES and is not inserted into the canonical "
            "manuscript until audited and explicitly frozen."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    report_path = args.report or args.series_dir / "RAEI_REPORT.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    def pct(x: float | None) -> str:
        return "NA" if x is None else f"{100*x:.1f}%"

    n = arms["NOMINAL_ONLY"]
    a = arms["REALIZATION_AWARE"]
    lines = [
        "# Realization-Aware Evidence Integration diagnostic",
        "",
        "## Question",
        "",
        protocol["scientific_question"],
        "",
        "## Pre-existing materials result",
        "",
        "Within repeated E2 realizations, formulation-only prediction gave a "
        "1.824x multiplicative RMSE, while one 110 C state-anchor calibration gave "
        "1.086x, corresponding to an 86.2% reduction in log-RMSE. This statistic "
        "comes from the already completed materials analysis and is not a new wet-lab result.",
        "",
        "## Agent diagnostic",
        "",
        "| Metric | Nominal-only | Realization-aware |",
        "|---|---:|---:|",
        f"| Declared runs | {n['declared_runs']} | {a['declared_runs']} |",
        f"| Valid completed | {n['completed_valid_runs']} | {a['completed_valid_runs']} |",
        f"| Committed | {n['committed_runs']} | {a['committed_runs']} |",
        f"| Abstained | {n['abstained_runs']} | {a['abstained_runs']} |",
        f"| Invalid | {n['invalid_runs']} | {a['invalid_runs']} |",
        f"| Failed | {n['failed_runs']} | {a['failed_runs']} |",
        f"| M-ANCHOR rate / declared | {pct(n['anchor_selection_rate_of_declared'])} | {pct(a['anchor_selection_rate_of_declared'])} |",
        f"| Evidence-consistent policy match / declared | {pct(n['evidence_consistent_policy_match_rate_of_declared'])} | {pct(a['evidence_consistent_policy_match_rate_of_declared'])} |",
        f"| Mean effort points among committed | {n['mean_effort_points_among_committed']} | {a['mean_effort_points_among_committed']} |",
        "",
        "Selection distributions:",
        "",
        f"- NOMINAL_ONLY: {json.dumps(n['measurement_selection_distribution'], sort_keys=True)}",
        f"- REALIZATION_AWARE: {json.dumps(a['measurement_selection_distribution'], sort_keys=True)}",
        "",
        "## Interpretation boundary",
        "",
        "This diagnostic asks whether preserving realization structure changes downstream "
        "measurement choice for a future in-domain E2 realization. It does not test a new "
        "material, does not authorize one-point transfer after a chemistry shift, and does "
        "not replace the existing chemistry-domain gate.",
        "",
        "The result must be reported even if the two arms behave identically.",
        "",
    ]
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(args.output)
    print(report_path)


if __name__ == "__main__":
    main()
