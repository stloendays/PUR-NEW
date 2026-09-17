from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from .metrics import coefficient_of_variation, hold_stability_index, max_min_ratio

ROOT = Path(__file__).resolve().parents[2]


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_formulations() -> list[dict[str, str]]:
    return _read_csv(ROOT / "data" / "formulations.csv")


def load_temperature_sweeps() -> list[dict[str, str]]:
    return _read_csv(ROOT / "data" / "temperature_sweeps.csv")


def load_thermal_hold(*, include_follow_up: bool) -> list[dict[str, str]]:
    rows = _read_csv(ROOT / "data" / "thermal_hold.csv")
    if include_follow_up:
        return rows
    return [r for r in rows if r.get("stage") != "follow_up"]


def query_external_priors(
    *,
    modifier_type: str | None = None,
    max_rows: int = 20,
) -> list[dict[str, str]]:
    rows = _read_csv(ROOT / "data" / "external_evidence_hints.csv")
    if modifier_type:
        key = modifier_type.lower()
        rows = [
            r for r in rows
            if key in r.get("resin_modifier_type", "").lower()
            or key in r.get("pattern", "").lower()
            or key in r.get("agent_hint", "").lower()
        ]
    return rows[:max_rows]


def inspect_formulation(formulation_id: str) -> dict[str, Any]:
    row = next((r for r in load_formulations() if r["formulation_id"] == formulation_id), None)
    if row is None:
        raise KeyError(formulation_id)
    numeric_keys = ["ppg2000", "pdp70", "ac1920", "tk100", "mdi"]
    amounts = {k: float(row[k]) if row.get(k) else 0.0 for k in numeric_keys}
    total = sum(amounts.values())
    modifier = amounts["ac1920"] + amounts["tk100"]
    polyol = amounts["ppg2000"] + amounts["pdp70"]
    return {
        "formulation_id": formulation_id,
        "stage": row.get("stage"),
        "amount_basis": row.get("amount_basis"),
        "nco_oh": float(row["nco_oh"]) if row.get("nco_oh") else None,
        "amounts": amounts,
        "total_reported_amount": total,
        "polyol_fraction": polyol / total if total else None,
        "modifier_fraction": modifier / total if total else None,
        "mdi_fraction": amounts["mdi"] / total if total else None,
        "resin_modified": modifier > 0,
    }


def get_hold_stability(formulation_id: str, *, include_follow_up: bool) -> dict[str, Any]:
    rows = [r for r in load_thermal_hold(include_follow_up=include_follow_up) if r["formulation_id"] == formulation_id]
    by_run: dict[str, dict[float, float]] = defaultdict(dict)
    for row in rows:
        by_run[row["run_label"]][float(row["time_min"])] = float(row["viscosity_reported"])
    out = []
    for run_label, series in sorted(by_run.items()):
        item: dict[str, Any] = {"run_label": run_label, "measurements": dict(sorted(series.items()))}
        if 15.0 in series and 60.0 in series:
            item["si_15_to_60"] = hold_stability_index(series[15.0], series[60.0])
        if 15.0 in series and 90.0 in series:
            item["si_15_to_90"] = hold_stability_index(series[15.0], series[90.0])
        out.append(item)
    return {"formulation_id": formulation_id, "runs": out, "result_visibility": "full" if include_follow_up else "original_only"}


def get_repeatability_risk(formulation_id: str) -> list[dict[str, Any]]:
    rows = [r for r in load_temperature_sweeps() if r["formulation_id"] == formulation_id and r["retest_after_1d"].lower() != "true"]
    by_temp: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        by_temp[float(row["temperature_c"])].append(float(row["viscosity_reported"]))
    out = []
    for temp, vals in sorted(by_temp.items()):
        if len(vals) < 2:
            continue
        out.append({
            "temperature_c": temp,
            "n_runs": len(vals),
            "sample_cv": coefficient_of_variation(vals),
            "max_min_ratio": max_min_ratio(vals),
        })
    return out


def get_temperature_support(formulation_id: str) -> dict[str, Any]:
    rows = [r for r in load_temperature_sweeps() if r["formulation_id"] == formulation_id]
    temps = sorted({float(r["temperature_c"]) for r in rows})
    return {
        "formulation_id": formulation_id,
        "temperature_support_c": [min(temps), max(temps)] if temps else None,
        "n_points": len(rows),
    }


def candidate_profile(candidate: dict[str, Any]) -> dict[str, Any]:
    fs = candidate.get("formulation_state", {})
    aliases = {
        "ppg2000": ["ppg2000", "PPG2000"],
        "pdp70": ["pdp70", "PDP70"],
        "ac1920": ["ac1920", "AC1920"],
        "tk100": ["tk100", "TK100"],
        "mdi": ["mdi", "MDI"],
    }
    amounts: dict[str, float] = {}
    for canonical, keys in aliases.items():
        val = next((fs[k] for k in keys if k in fs and fs[k] is not None), 0.0)
        amounts[canonical] = float(val)
    total = sum(amounts.values())
    modifier = amounts["ac1920"] + amounts["tk100"]
    polyol = amounts["ppg2000"] + amounts["pdp70"]
    return {
        "candidate_id": candidate.get("candidate_id"),
        "total_reported_amount": total,
        "polyol_fraction": polyol / total if total else None,
        "modifier_fraction": modifier / total if total else None,
        "mdi_fraction": amounts["mdi"] / total if total else None,
        "resin_modified": modifier > 0,
        "amounts": amounts,
    }


def compare_candidate_to_priors(candidate: dict[str, Any]) -> dict[str, Any]:
    profile = candidate_profile(candidate)
    frac = profile["modifier_fraction"]
    priors = query_external_priors(max_rows=100)
    prior_fracs = []
    for r in priors:
        raw = r.get("resin_modifier_fraction_pct")
        if raw:
            try:
                prior_fracs.append(float(raw) / 100.0)
            except ValueError:
                pass
    if not prior_fracs or frac is None:
        return {"profile": profile, "analogue_support": "unknown", "nearest_modifier_fraction_distance": None}
    d = min(abs(frac - p) for p in prior_fracs)
    if d <= 0.03:
        support = "strong_analogue_region"
    elif d <= 0.08:
        support = "moderate_analogue_region"
    else:
        support = "weak_analogue_region"
    return {
        "profile": profile,
        "analogue_support": support,
        "nearest_modifier_fraction_distance": d,
        "prior_modifier_fraction_range": [min(prior_fracs), max(prior_fracs)],
        "note": "Analogue support is a literature/database prior, not a prediction of current wet-lab performance.",
    }


def audit_process_unknowns(candidate: dict[str, Any]) -> dict[str, Any]:
    ps = candidate.get("process_state", {})
    fields = [
        "reaction_temperature_c",
        "reaction_time_min",
        "mixing_history",
        "sample_age",
        "hold_temperature_c",
        "hold_time_min",
    ]
    missing = [f for f in fields if ps.get(f) in (None, "", [])]
    return {
        "candidate_id": candidate.get("candidate_id"),
        "missing_process_fields": missing,
        "process_history_uncertainty": "high" if len(missing) >= 4 else "moderate" if missing else "low",
    }


def stress_test_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    prior = compare_candidate_to_priors(candidate)
    proc = audit_process_unknowns(candidate)
    reasons = []
    risk = 0
    if prior["profile"]["modifier_fraction"] is not None and prior["profile"]["modifier_fraction"] > 0.35:
        risk += 2
        reasons.append("modifier fraction is far above the curated external analogue region")
    if prior["analogue_support"] == "weak_analogue_region":
        risk += 1
        reasons.append("weak external analogue support")
    if proc["process_history_uncertainty"] == "high":
        risk += 2
        reasons.append("major process-history fields are missing")
    elif proc["process_history_uncertainty"] == "moderate":
        risk += 1
        reasons.append("some process-history fields are missing")
    if not prior["profile"]["resin_modified"]:
        reasons.append("unmodified candidate does not directly address the resin-modification design hypothesis")
    label = "low" if risk <= 1 else "moderate" if risk <= 3 else "high"
    return {
        "candidate_id": candidate.get("candidate_id"),
        "risk_level": label,
        "reasons": reasons,
        "analogue_support": prior["analogue_support"],
        "process_history_uncertainty": proc["process_history_uncertainty"],
    }


def rank_candidate_support(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored = []
    for candidate in candidates:
        prior = compare_candidate_to_priors(candidate)
        stress = stress_test_candidate(candidate)
        score = 0.0
        if prior["profile"]["resin_modified"]:
            score += 2.0
        score += {"strong_analogue_region": 2.0, "moderate_analogue_region": 1.0, "weak_analogue_region": 0.0, "unknown": 0.0}[prior["analogue_support"]]
        score -= {"low": 0.0, "moderate": 1.0, "high": 2.0}[stress["risk_level"]]
        scored.append({"candidate_id": candidate.get("candidate_id"), "support_score": score, "profile": prior["profile"], "stress_test": stress})
    return sorted(scored, key=lambda x: (-x["support_score"], str(x["candidate_id"])))


def execute_action(name: str, args: dict[str, Any], *, include_follow_up: bool) -> Any:
    if name == "query_external_priors":
        return query_external_priors(**args)
    if name == "inspect_formulation":
        return inspect_formulation(**args)
    if name == "get_hold_stability":
        return get_hold_stability(include_follow_up=include_follow_up, **args)
    if name == "get_repeatability_risk":
        return get_repeatability_risk(**args)
    if name == "get_temperature_support":
        return get_temperature_support(**args)
    if name == "candidate_profile":
        return candidate_profile(**args)
    if name == "compare_candidate_to_priors":
        return compare_candidate_to_priors(**args)
    if name == "audit_process_unknowns":
        return audit_process_unknowns(**args)
    if name == "stress_test_candidate":
        return stress_test_candidate(**args)
    if name == "rank_candidate_support":
        return rank_candidate_support(**args)
    raise KeyError(f"unknown action: {name}")
