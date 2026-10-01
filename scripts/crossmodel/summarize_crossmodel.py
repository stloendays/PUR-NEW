#!/usr/bin/env python3
"""Run-level extraction, QC and cumulative statistics for the gpt-5.6-sol replication.

The same extraction is applied to the frozen Luna records and to every Sol replicate, so
the two models are compared on one data structure. The script first recomputes the
published Luna aggregates from the Luna records; a mismatch is reported as a failed
reproduction check. Execution batches are provenance only: every Sol replicate executed
under the protocol is pooled.

Reads frozen records only. Calls no model. Post-freeze scoring (the CRB near-region
endpoint of the naive baseline) reads the held-out composition from
configs/blind_benchmark_v2.json exactly as scripts/score_stage1_replay.py does.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import math
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PROTOCOL = ROOT / "configs" / "crossmodel_sol_v4_protocol.json"
OUT = ROOT / "results" / "multimodel" / "gpt-5_6-sol" / "v4_benchmark"
CANDIDATES = ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
BENCHMARK_V2 = ROOT / "configs" / "blind_benchmark_v2.json"
NEAR_REGION_L1 = 7.5
SUPPORTED_FAMILY = "dual_axis_resin_modified"
LUNA_NAIVE_ATTEMPTED = 10  # results/STAGE1_AI4SCI_REPORT.md section 4b: N=10, 7 valid, 3 invalid outputs not retained

CONDITION_TARGET_MEASUREMENT = {
    "rges_full_v4": "M-HOLD-120",
    "rges_voi_withheld": "M-HOLD-120",
    "rges_rule_order_minimality_first": "M-HOLD-120",
    "cbes_A_drift_V5_NO_GATE": "M-HOLD-120",
    "cbes_A_drift_V5_FULL": "M-HOLD-120",
    "cbes_B_processing_window_V5_NO_GATE": "M-SWEEP",
    "cbes_B_processing_window_V5_FULL": "M-SWEEP",
}

CORRECTNESS_DEFINITION = {
    "naive_direct_llm": "CRB level-3 endpoint: selected candidate within the predeclared 7.5 pp modifier-plane L1 near region of the held-out composition (post-freeze scoring)",
    "rges": "frozen RGES adjudication rule: committed selection whose intervention family (dual-axis resin-modified) AND measurement plan (M-HOLD-120) both match the completed experiment",
    "cbes_A": "committed, chemistry-admissible (no domain violation, no unsupported shortcut) selection of the direct thermal-hold measurement M-HOLD-120",
    "cbes_B": "committed, chemistry-admissible (no domain violation, no unsupported shortcut) selection of the direct temperature sweep M-SWEEP",
}

# Published Luna aggregates (manuscript Fig. 4 / AGENT_V4_REPORT.md / derived/*_summary.json).
LUNA_PUBLISHED = {
    "rges_full_v4": {"n": 10, "supported_family": 9, "target_measurement": 10, "in_tied_top_set": 9, "zero_discrimination": 0,
                     "mean_discrimination": 0.667, "high_severity_objection": 10, "robustness_said_change_experiment": 1, "committed_anyway": 10},
    "rges_voi_withheld": {"n": 5, "supported_family": 0, "target_measurement": 5, "in_tied_top_set": 0, "zero_discrimination": 3,
                          "mean_discrimination": 0.267, "high_severity_objection": 5, "robustness_said_change_experiment": 4, "committed_anyway": 5},
    "rges_rule_order_minimality_first": {"n": 10, "supported_family": 0, "target_measurement": 7, "zero_discrimination": 10,
                                         "mean_discrimination": 0.0, "high_severity_objection": 10, "robustness_said_change_experiment": 5, "committed_anyway": 10},
    "cbes_A_drift_V5_NO_GATE": {"n": 10, "committed": 10, "target_measurement": 10, "chemistry_gate_violation": 0, "unsupported_shortcut": 0, "mean_discrimination": 0.667},
    "cbes_A_drift_V5_FULL": {"n": 10, "committed": 10, "target_measurement": 10, "chemistry_gate_violation": 0, "unsupported_shortcut": 0, "mean_discrimination": 0.667},
    "cbes_B_processing_window_V5_NO_GATE": {"n": 10, "committed": 10, "target_measurement": 10, "chemistry_gate_violation": 0, "unsupported_shortcut": 0, "in_tied_top_set": 0},
    "cbes_B_processing_window_V5_FULL": {"n": 10, "committed": 9, "invalid": 1, "target_measurement": 9, "chemistry_gate_violation": 0, "unsupported_shortcut": 0, "in_tied_top_set": 9},
    "naive_direct_llm": {"n": 10, "valid": 7, "final_decision_correct": 0, "supported_family": 0},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def wilson(successes: int, total: int, z: float = 1.96) -> list[float] | None:
    if total == 0:
        return None
    phat = successes / total
    denom = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def entropy_bits(labels: list[Any]) -> float:
    if not labels:
        return 0.0
    counts = Counter(labels)
    n = len(labels)
    return round(-sum(c / n * math.log2(c / n) for c in counts.values()), 6)


def family_of(cand: dict[str, Any]) -> str:
    fs = cand["formulation_state"]
    ac, tk = float(fs.get("AC1920", 0.0)), float(fs.get("TK100", 0.0))
    if ac > 0 and tk > 0:
        return SUPPORTED_FAMILY
    if ac > 0:
        return "acrylic_only"
    if tk > 0:
        return "tackifier_only"
    return "reactive_core_only"


def coded_tiebreak(tied: list[str], candidates: dict[str, dict[str, Any]]) -> str | None:
    """argmax VOI (the tied set), then lowest total modifier percent, then lexicographic id."""
    if not tied:
        return None

    def burden(exp_id: str) -> tuple[float, str]:
        fs = candidates[exp_id.split("::")[0]]["formulation_state"]
        return (float(fs.get("AC1920", 0.0)) + float(fs.get("TK100", 0.0)), exp_id)

    return min(tied, key=burden)


# ---------------------------------------------------------------- run-level extraction

def audit_deterministic_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    audit = read_json(path)
    audit.pop("selection", None)
    audit.pop("arm", None)
    audit.pop("applicability_gate_enforced", None)
    audit.pop("n_cards_removed_from_selectable_set", None)
    return hashlib.sha256(json.dumps(audit, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def stderr_category(run_dir: Path) -> str | None:
    """Finer failure class from the frozen runner's stderr, for non-ok runs."""
    path = run_dir / "driver_stderr.txt"
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    for needle, label in (
        ("model returned empty content", "empty_model_content"),
        ("JSONDecodeError", "malformed_json"),
        ("did not contain a JSON object", "malformed_json"),
        ("ValidationError", "schema_validation"),
        ("Failed validating", "schema_validation"),
    ):
        if needle in text:
            return label
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return ("other:" + lines[-1][:120]) if lines else None


def agent_row(key: str, model: str, run_id: str, status: str, technical: bool, run_dir: Path,
              candidates: dict[str, dict[str, Any]]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "model": model, "condition_key": key, "run_id": run_id, "status": status,
        "technical_failure": technical, "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
    }
    recs = sorted(run_dir.glob("EXP_V*/recommendation.json"))
    rejected = sorted(run_dir.glob("**/rejected_deliberation.json"))
    if status == "ok" and recs:
        rec_dir = recs[0].parent
        rec = read_json(recs[0])
        de = read_json(rec_dir / "deliberation.json")
    elif rejected:
        rec_dir, rec, de = rejected[0].parent, {}, read_json(rejected[0])
    else:
        row["failure_category"] = "technical_failure" if technical else (stderr_category(run_dir) or "invalid_model_output_no_record")
        return row

    judge = de.get("judge_normalized") or {}
    card = rec.get("experiment_card") or {}
    voi = rec.get("voi") or {}
    gate = (rec.get("chemistry_gate") or {}).get("selection") or {}
    skeptic = de.get("skeptic") or {}
    robust = de.get("robustness_adjudication") or {}
    proposer = de.get("proposer") or {}
    usage = de.get("llm_usage_total") or {}
    trace = de.get("tool_trace") or []
    mode = rec.get("decision_mode") or judge.get("decision_mode")
    committed = mode not in (None, "abstain")
    selected = rec.get("selected_experiment_id") or judge.get("selected_experiment_id")
    measurement = rec.get("selected_measurement_id") or judge.get("selected_measurement_id")
    cand_id = rec.get("selected_candidate_id") or judge.get("selected_candidate_id")
    family = card.get("intervention_family") or (family_of(candidates[cand_id]) if cand_id in candidates else None)
    disc = (card.get("voi_components") or {}).get("hypothesis_discrimination")
    tied = list(voi.get("tied_top_set") or [])
    high = any(o.get("severity") == "high" for o in skeptic.get("objections", []))
    violation = gate.get("chemistry_domain_violation")
    shortcut = gate.get("unsupported_shortcut")
    rejection_class = (de.get("rejection_class") or de.get("rejection_reason")) if rejected and not recs else None
    is_v5 = key.startswith("cbes_")
    # the model's final choice lay outside the deterministic admissible card set: either the
    # freeze stage rejected it (any architecture) or, without enforcement, the gate flags it
    rejected_outside_set = bool(rejection_class) and (
        "inadmissible" in str(rejection_class) or "not an admissible experiment card" in str(rejection_class)
    )
    override_attempt = bool(violation) or rejected_outside_set
    mandatory = de.get("mandatory_local_science_tool_executed")
    if mandatory is None:
        mandatory = any(t.get("name") == "get_state_aware_rheology_summary" and t.get("status") == "ok" for t in trace)
    tool_ok = bool(mandatory) and all(t.get("status") == "ok" for t in trace)
    prov_fields = ["recommendation_id", "model", "git_commit", "prompt_hash", "input_hash", "candidate_set_hash",
                   "hypothesis_registry_hash", "measurement_catalog_hash", "frozen_utc"]
    if is_v5:
        prov_fields.append("pre_enforcement_payload_hash")
    provenance_complete = bool(rec) and all(rec.get(f) for f in prov_fields)
    target = CONDITION_TARGET_MEASUREMENT[key]
    if key.startswith("rges_"):
        correct = committed and family == SUPPORTED_FAMILY and measurement == target
    else:
        correct = committed and measurement == target and not violation and not shortcut
    stage_models = de.get("stage_models") or {}
    coded = coded_tiebreak(tied, candidates)
    row.update({
        "recommendation_id": rec.get("recommendation_id"),
        "decision_mode": mode,
        "committed": committed,
        "selected_experiment_id": selected,
        "selected_candidate_id": cand_id,
        "selected_measurement_id": measurement,
        "intervention_family": family,
        "final_decision_correct": bool(correct) and status == "ok",
        "hypothesis_discrimination": disc,
        "zero_discrimination": (disc == 0.0) if disc is not None else None,
        "voi_score": voi.get("score"),
        "voi_scores_withheld_from_model": bool(voi.get("scores_withheld_from_model", False)),
        "deterministic_tie_present": len(tied) > 1,
        "tie_size": len(tied),
        "tied_top_set": "|".join(tied),
        "selected_in_tied_top_set": voi.get("selected_is_in_tied_top_set"),
        "coded_minimum_burden_tiebreak": coded,
        "matches_coded_tiebreak": (selected == coded) if coded and selected else None,
        "tie_break_justification": proposer.get("tie_break_justification"),
        "proposer_experiment_id": proposer.get("proposed_experiment_id"),
        "proposer_in_tied_top_set": (proposer.get("proposed_experiment_id") in tied) if tied and proposer.get("proposed_experiment_id") else None,
        "proposer_matches_coded_tiebreak": (proposer.get("proposed_experiment_id") == coded) if coded and proposer.get("proposed_experiment_id") else None,
        "final_differs_from_proposer": (selected != proposer.get("proposed_experiment_id")) if selected and proposer.get("proposed_experiment_id") else None,
        "robustness_preferred_experiment_id": robust.get("preferred_experiment_id"),
        "chemistry_applicability_status": gate.get("chemistry_applicability_status"),
        "chemistry_gate_violation": violation,
        "unsupported_shortcut": shortcut,
        "constraint_violation": (bool(violation) or bool(shortcut)) if is_v5 else None,
        "deterministic_rule_override_attempt": override_attempt,
        "rejection_class": rejection_class,
        "high_severity_objection": high,
        "robustness_said_change_experiment": robust.get("skeptic_objection_effect") == "changes_which_experiment_to_run",
        "committed_anyway": high and judge.get("decision_mode") not in (None, "abstain"),
        "robustness_departure_from_deterministic_ranking": robust.get("departure_from_deterministic_ranking"),
        "tool_calls": len(trace),
        "tools_used": "|".join(t.get("name", "") for t in trace),
        "tool_use_correct": tool_ok,
        "provenance_complete": provenance_complete,
        "all_stages_on_model": bool(stage_models) and all(v == model for v in stage_models.values()),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "llm_latency_s": round(float(usage.get("llm_latency_s") or 0.0), 2) if usage else None,
        "prompt_hash": rec.get("prompt_hash"),
        "input_hash": rec.get("input_hash"),
        "candidate_set_hash": rec.get("candidate_set_hash") or de.get("candidate_set_hash"),
        "hypothesis_registry_hash": rec.get("hypothesis_registry_hash"),
        "measurement_catalog_hash": rec.get("measurement_catalog_hash"),
        "pre_enforcement_payload_hash": rec.get("pre_enforcement_payload_hash"),
        "voi_full_ranking_sha256": sha256_file(rec_dir / "voi_full_ranking.json"),
        "experiment_cards_sha256": sha256_file(rec_dir / "experiment_cards.json"),
        # the audit file embeds the per-run `selection` block, so only its deterministic part
        # (every card's admissibility and reason) is comparable across runs and models
        "admissibility_audit_sha256": audit_deterministic_sha256(rec_dir / "admissibility_audit.json"),
        "failure_category": None if status == "ok" else ("selection_outside_admissible_card_set" if rejected_outside_set else (rejection_class or stderr_category(run_dir) or "invalid_model_output")),
    })
    return row


def naive_row(model: str, run_id: str, status: str, technical: bool, run_dir: Path,
              candidates: dict[str, dict[str, Any]], target: dict[str, float]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "model": model, "condition_key": "naive_direct_llm", "run_id": run_id, "status": status,
        "technical_failure": technical, "run_dir": str(run_dir.relative_to(ROOT)).replace("\\", "/"),
    }
    recs = sorted(p for p in run_dir.glob("REC_BASELINE_*.json") if not p.name.endswith(".meta.json"))
    if not recs:
        row["failure_category"] = "technical_failure" if technical else (stderr_category(run_dir) or "invalid_model_output_no_record")
        return row
    rec = read_json(recs[0])
    meta_path = recs[0].with_name(recs[0].stem + ".meta.json")
    meta = read_json(meta_path) if meta_path.exists() else {}
    prov = rec.get("provenance") or {}
    cand_id = (rec.get("selected_candidate") or {}).get("candidate_id")
    mode = rec.get("decision_mode")
    committed = mode != "abstain" and cand_id is not None
    l1 = near = family = None
    if cand_id in candidates:
        fs = candidates[cand_id]["formulation_state"]
        l1 = round(abs(float(fs["AC1920"]) - target["AC1920"]) + abs(float(fs["TK100"]) - target["TK100"]), 4)
        near = l1 <= NEAR_REGION_L1
        family = family_of(candidates[cand_id])
    row.update({
        "recommendation_id": rec.get("recommendation_id"),
        "decision_mode": mode,
        "committed": committed,
        "selected_candidate_id": cand_id,
        "intervention_family": family,
        "modifier_plane_l1_pct_points": l1,
        "near_region_hit": near,
        "final_decision_correct": bool(near) and committed,
        "tool_calls": 0,
        "tool_use_correct": None,
        "provenance_complete": all(prov.get(f) for f in ("git_commit", "input_hash", "model", "prompt_hash", "run_id", "workflow_version")),
        "all_stages_on_model": prov.get("model") == model,
        "prompt_tokens": meta.get("prompt_tokens"),
        "completion_tokens": meta.get("completion_tokens"),
        "total_tokens": meta.get("total_tokens"),
        "llm_latency_s": round(float(meta.get("latency_s") or 0.0), 2) if meta else None,
        "prompt_hash": prov.get("prompt_hash"),
        "input_hash": prov.get("input_hash"),
        "failure_category": None,
    })
    return row


# ---------------------------------------------------------------- collection

def collect_luna(cond: dict[str, Any], candidates, target) -> list[dict[str, Any]]:
    key = cond["condition_key"]
    ref = ROOT / cond["luna_reference"]
    rows = []
    if key == "naive_direct_llm":
        for d in sorted(ref.glob("run_*")):
            rows.append(naive_row("gpt-5.6-luna", d.name, "ok", False, d, candidates, target))
        for i in range(len(rows), LUNA_NAIVE_ATTEMPTED):
            rows.append({"model": "gpt-5.6-luna", "condition_key": key, "run_id": f"unretained_invalid_{i + 1}",
                         "status": "invalid", "technical_failure": False, "failure_category": "invalid_model_output_not_retained"})
        return rows
    manifest = read_json(ref / "series_manifest.json")
    for r in manifest["runs"]:
        status = {"failed": "invalid"}.get(r["status"], r["status"])
        row = agent_row(key, manifest["model"], f"run_{r['run_index']:03d}", status, False,
                        ROOT / r["run_dir"].replace("\\", "/"), candidates)
        tail = " ".join(r.get("stderr_tail") or [])
        if row.get("failure_category") == "invalid_model_output_no_record" and "JSONDecodeError" in tail:
            row["failure_category"] = "malformed_json"
        rows.append(row)
    return rows


def collect_sol(cond: dict[str, Any], candidates, target) -> list[dict[str, Any]]:
    key = cond["condition_key"]
    series = OUT / key
    manifest_path = series / "series_manifest.json"
    if not manifest_path.exists():
        return []
    manifest = read_json(manifest_path)
    rows = []
    for r in manifest["runs"]:
        run_dir = ROOT / r["run_dir"].replace("\\", "/")
        if key == "naive_direct_llm":
            row = naive_row(manifest["model"], r["replicate_id"], r["status"], r["technical_failure"], run_dir, candidates, target)
        else:
            row = agent_row(key, manifest["model"], r["replicate_id"], r["status"], r["technical_failure"], run_dir, candidates)
        row["wall_seconds"] = r.get("wall_seconds")
        rows.append(row)
    return rows


# ---------------------------------------------------------------- aggregation

def count(rows, field) -> int:
    return sum(1 for r in rows if r.get(field) is True)


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    attempted = len(rows)
    technical = sum(1 for r in rows if r.get("technical_failure"))
    sci = [r for r in rows if not r.get("technical_failure")]
    denom = len(sci)
    ok = [r for r in sci if r["status"] == "ok"]
    committed = [r for r in ok if r.get("committed")]
    abstained = [r for r in ok if r.get("decision_mode") == "abstain"]
    discs = [r["hypothesis_discrimination"] for r in committed if r.get("hypothesis_discrimination") is not None]
    tokens = [r["total_tokens"] for r in sci if r.get("total_tokens") is not None]
    lat = [r["llm_latency_s"] for r in sci if r.get("llm_latency_s")]
    tie_rows = [r for r in ok if r.get("deterministic_tie_present")]

    def rate(n: int, d: int = denom) -> dict[str, Any]:
        return {"count": n, "of": d, "rate": round(n / d, 4) if d else None, "wilson_95": wilson(n, d)}

    empty = sum(1 for r in rows if r.get("failure_category") == "empty_model_content")
    out = {
        "sensitivity_empty_content_counted_invalid": {
            "n_empty_model_content": empty,
            "final_decision_correct": {"count": count(sci, "final_decision_correct"), "of": denom + empty},
        },
        "n_attempted": attempted,
        "n_technical_failure": technical,
        "n_scientific_denominator": denom,
        "n_completed": len(ok),
        "n_committed": len(committed),
        "n_abstained": len(abstained),
        "n_invalid": sum(1 for r in sci if r["status"] == "invalid"),
        "final_decision_correct": rate(count(sci, "final_decision_correct")),
        "supported_family_dual_axis": rate(sum(1 for r in committed if r.get("intervention_family") == SUPPORTED_FAMILY)),
        "intervention_family_counts": dict(Counter(r.get("intervention_family") for r in committed).most_common()),
        "measurement_counts": dict(Counter(r.get("selected_measurement_id") for r in committed).most_common()),
        "selected_counts": dict(Counter(r.get("selected_experiment_id") or r.get("selected_candidate_id") for r in committed).most_common()),
        "selection_entropy_bits": entropy_bits([r.get("selected_experiment_id") or r.get("selected_candidate_id") if r.get("committed") else "ABSTAIN" for r in ok]),
        "mean_hypothesis_discrimination": round(sum(discs) / len(discs), 4) if discs else None,
        "zero_discrimination": rate(sum(1 for d in discs if d == 0.0)),
        "selected_in_tied_top_set": rate(count(committed, "selected_in_tied_top_set")),
        "chemistry_gate_violation": rate(count(committed, "chemistry_gate_violation")),
        "unsupported_shortcut": rate(count(committed, "unsupported_shortcut")),
        "constraint_violation": rate(count(committed, "constraint_violation")),
        "deterministic_rule_override_attempt": rate(count(sci, "deterministic_rule_override_attempt")),
        "high_severity_objection": rate(count(ok, "high_severity_objection")),
        "robustness_said_change_experiment": rate(count(ok, "robustness_said_change_experiment")),
        "committed_anyway": rate(count(ok, "committed_anyway")),
        "tie_occurrence": rate(len(tie_rows)),
        "tie_visible_to_model": sum(1 for r in tie_rows if not r.get("voi_scores_withheld_from_model")),
        "tie_break_selected_inside_tied_set": sum(1 for r in tie_rows if r.get("selected_in_tied_top_set")),
        "tie_break_matches_coded_minimum_burden_rule": sum(1 for r in tie_rows if r.get("matches_coded_tiebreak")),
        "proposer_tie_break_inside_tied_set": sum(1 for r in sci if r.get("deterministic_tie_present") and r.get("proposer_in_tied_top_set")),
        "proposer_tie_break_matches_coded_rule": sum(1 for r in sci if r.get("deterministic_tie_present") and r.get("proposer_matches_coded_tiebreak")),
        "n_with_proposer_stage": sum(1 for r in sci if r.get("proposer_experiment_id")),
        "final_decision_differs_from_proposer": sum(1 for r in sci if r.get("final_differs_from_proposer")),
        "tie_break_departures_from_coded_rule": [
            {"run_id": r["run_id"], "selected": r.get("selected_experiment_id"), "coded": r.get("coded_minimum_burden_tiebreak")}
            for r in tie_rows if r.get("matches_coded_tiebreak") is False
        ],
        "tool_use_correct": rate(count(ok, "tool_use_correct"), len(ok)),
        "provenance_complete": rate(count(ok, "provenance_complete"), len(ok)),
        "failure_categories": dict(Counter(r.get("failure_category") for r in rows if r.get("failure_category")).most_common()),
        "total_tokens_mean": round(sum(tokens) / len(tokens)) if tokens else None,
        "total_tokens_sum": sum(tokens) if tokens else None,
        "llm_latency_s_mean": round(sum(lat) / len(lat), 1) if lat else None,
    }
    l1 = [r["modifier_plane_l1_pct_points"] for r in committed if r.get("modifier_plane_l1_pct_points") is not None]
    if l1:
        out["modifier_plane_l1_mean"] = round(sum(l1) / len(l1), 3)
        out["near_region_hit"] = rate(count(committed, "near_region_hit"))
    return out


def luna_reproduction(key: str, agg: dict[str, Any]) -> dict[str, Any]:
    exp = LUNA_PUBLISHED[key]
    got = {
        "n": agg["n_scientific_denominator"],
        "valid": agg["n_completed"],
        "committed": agg["n_committed"],
        "invalid": agg["n_invalid"],
        "supported_family": agg["supported_family_dual_axis"]["count"],
        "target_measurement": sum(v for k, v in agg["measurement_counts"].items() if k == CONDITION_TARGET_MEASUREMENT.get(key)),
        "in_tied_top_set": agg["selected_in_tied_top_set"]["count"],
        "zero_discrimination": agg["zero_discrimination"]["count"],
        "mean_discrimination": agg["mean_hypothesis_discrimination"],
        "high_severity_objection": agg["high_severity_objection"]["count"],
        "robustness_said_change_experiment": agg["robustness_said_change_experiment"]["count"],
        "committed_anyway": agg["committed_anyway"]["count"],
        "chemistry_gate_violation": agg["chemistry_gate_violation"]["count"],
        "unsupported_shortcut": agg["unsupported_shortcut"]["count"],
        "final_decision_correct": agg["final_decision_correct"]["count"],
    }
    mismatches = {}
    for k, v in exp.items():
        g = got[k]
        same = (round(g, 3) == round(v, 3)) if isinstance(v, float) and g is not None else g == v
        if not same:
            mismatches[k] = {"published": v, "recomputed": g}
    return {"pass": not mismatches, "mismatches": mismatches}


# ---------------------------------------------------------------- QC

def qc_sol(rows: list[dict[str, Any]], luna_rows: list[dict[str, Any]], manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    ref_sets = {f: {r.get(f) for r in luna_rows if r.get(f)} for f in (
        "prompt_hash", "candidate_set_hash", "hypothesis_registry_hash", "measurement_catalog_hash",
        "pre_enforcement_payload_hash", "voi_full_ranking_sha256", "experiment_cards_sha256", "admissibility_audit_sha256")}
    naive = bool(rows) and rows[0]["condition_key"] == "naive_direct_llm"
    if naive:
        ref_sets["input_hash"] = {r.get("input_hash") for r in luna_rows if r.get("input_hash")}
    out = []
    for r in rows:
        checks: dict[str, Any] = {"record_present": r["status"] == "ok" and bool(r.get("recommendation_id"))}
        if r["status"] == "ok":
            checks["model_on_every_stage_is_sol"] = r.get("all_stages_on_model")
            for f, ref in ref_sets.items():
                if ref and r.get(f) is not None:
                    checks[f"{f}_equals_luna"] = r.get(f) in ref
            checks["provenance_complete"] = r.get("provenance_complete")
            if not naive:
                checks["tool_use_correct"] = r.get("tool_use_correct")
        out.append({"run_id": r["run_id"], "condition_key": r["condition_key"], "status": r["status"],
                    "technical_failure": r.get("technical_failure"), "checks": checks,
                    "passes_integrity": r["status"] == "ok" and all(v is True for v in checks.values())})
    return out


# ---------------------------------------------------------------- main

def main() -> None:
    protocol = read_json(PROTOCOL)
    cand_list = read_json(CANDIDATES)["candidates"]
    candidates = {c["candidate_id"]: c for c in cand_list}
    target = read_json(BENCHMARK_V2)["controller_only_heldout_target"]["validation_formulation_normalized_pct"]

    all_rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {
        "generated_utc": utc_now(),
        "protocol_id": protocol["protocol_id"],
        "dataset_rule": "all Sol replicates executed under the protocol are pooled; execution batches are provenance only",
        "denominator_rule": "rates use attempted runs minus technical (API/infrastructure) failures; model-output-invalid runs stay in the denominator",
        "final_decision_correct_definition": CORRECTNESS_DEFINITION,
        "conditions": {},
    }
    qc_all: list[dict[str, Any]] = []
    for cond in protocol["conditions"]:
        key = cond["condition_key"]
        luna_rows = collect_luna(cond, candidates, target)
        sol_rows = collect_sol(cond, candidates, target)
        for r in luna_rows + sol_rows:
            if r.get("failure_category") == "empty_model_content" and not r.get("technical_failure"):
                r["technical_failure"] = True
                r["status"] = "technical_failure"
                r["reclassified_by_amendment"] = "1.0.1"
        all_rows += luna_rows + sol_rows
        luna_agg, sol_agg = aggregate(luna_rows), aggregate(sol_rows)
        qc = qc_sol(sol_rows, luna_rows, None)
        qc_all += qc
        valid_sol = [q for q in qc if q["passes_integrity"]]
        summary["conditions"][key] = {
            "role": cond["role"],
            "reader_facing": cond["reader_facing"],
            "luna": luna_agg,
            "luna_reproduction_check": luna_reproduction(key, luna_agg),
            "sol": sol_agg,
            "sol_runs_passing_integrity": len(valid_sol),
            "sol_minus_luna": {
                "final_decision_correct_rate": (
                    round(sol_agg["final_decision_correct"]["rate"] - luna_agg["final_decision_correct"]["rate"], 4)
                    if sol_agg["final_decision_correct"]["rate"] is not None and luna_agg["final_decision_correct"]["rate"] is not None else None
                ),
                "mean_hypothesis_discrimination": (
                    round(sol_agg["mean_hypothesis_discrimination"] - luna_agg["mean_hypothesis_discrimination"], 4)
                    if sol_agg["mean_hypothesis_discrimination"] is not None and luna_agg["mean_hypothesis_discrimination"] is not None else None
                ),
            },
        }

    sol_ids = sorted({r["run_id"] for r in all_rows if r["model"] == "gpt-5.6-sol"})
    summary["sol_replicates"] = sol_ids
    summary["sol_cumulative_n_replicates"] = len(sol_ids)

    columns: list[str] = []
    for r in all_rows:
        for k in r:
            if k not in columns:
                columns.append(k)
    with (OUT / "run_level_rows.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for r in all_rows:
            writer.writerow(r)
    (OUT / "run_level_rows.json").write_text(json.dumps(all_rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "qc_report.json").write_text(json.dumps({
        "generated_utc": utc_now(),
        "n_sol_runs": len(qc_all),
        "n_passing_integrity": sum(q["passes_integrity"] for q in qc_all),
        "n_technical_failure": sum(bool(q["technical_failure"]) for q in qc_all),
        "runs": qc_all,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "cumulative_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    repro = {k: v["luna_reproduction_check"]["pass"] for k, v in summary["conditions"].items()}
    print(f"sol replicates={len(sol_ids)} runs={len(qc_all)} integrity_pass={sum(q['passes_integrity'] for q in qc_all)} luna_repro={repro}")


if __name__ == "__main__":
    main()
