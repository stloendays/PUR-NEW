from __future__ import annotations

import csv
import json
import math
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from .chemistry_tools import assess_shared_shape_applicability
from .metrics import coefficient_of_variation, hold_stability_index, max_min_ratio
from .scientific_tools import get_state_aware_rheology_summary_v3

ROOT = Path(__file__).resolve().parents[2]
R_GAS = 8.31446261815324


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_formulations() -> list[dict[str, str]]:
    return _read_csv(ROOT / "data" / "formulations.csv")


def load_temperature_sweeps() -> list[dict[str, str]]:
    return _read_csv(ROOT / "data" / "temperature_sweeps.csv")


def load_thermal_hold(*, include_follow_up: bool) -> list[dict[str, str]]:
    rows = _read_csv(ROOT / "data" / "thermal_hold.csv")
    if include_follow_up:
        return rows
    return [r for r in rows if r.get("stage") != "follow_up"]


def load_formulation_priors() -> dict[str, Any]:
    return _read_json(ROOT / "configs" / "formulation_priors.json")


_MORPHOLOGICAL_SUFFIXES = ("ying", "ied", "ier", "ing", "ers", "er", "es", "s", "y")


def _evidence_stem(text: str) -> str:
    """Collapse common English morphology so curated rows are not silently dropped.

    A literal substring match loses whole source rows: "tackifier" does not occur in
    "tackifying resin" or "tackifying agent". Dropping a documented example biases the
    decision toward whichever modifier axis happens to survive retrieval, so the match
    is done on stems instead.
    """
    out = []
    for token in re.split(r"([^a-z0-9]+)", text.lower()):
        if token.isalnum() and len(token) > 4:
            for suffix in _MORPHOLOGICAL_SUFFIXES:
                if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                    token = token[: -len(suffix)]
                    break
        out.append(token)
    return "".join(out)


def query_external_priors(
    *,
    modifier_type: str | None = None,
    candidate_space_role: str | None = None,
    max_rows: int = 20,
) -> list[dict[str, str]]:
    rows = _read_csv(ROOT / "data" / "external_evidence_hints.csv")
    if modifier_type:
        key = _evidence_stem(modifier_type)
        rows = [
            r for r in rows
            if key in _evidence_stem(r.get("resin_modifier_type", ""))
            or key in _evidence_stem(r.get("pattern", ""))
            or key in _evidence_stem(r.get("agent_hint", ""))
        ]
    if candidate_space_role:
        key = candidate_space_role.lower()
        rows = [r for r in rows if key in r.get("candidate_space_role", "").lower()]
    return rows[:max_rows]


def get_candidate_hypothesis() -> dict[str, Any]:
    priors = load_formulation_priors()
    return {
        "historical_status": priors["historical_status"],
        "local_reactive_core_anchor": priors["local_reactive_core_anchor"],
        "candidate_axes": priors["candidate_axes"],
        "stability_hypotheses": priors["stability_hypotheses"],
        "decision_policy": priors.get("decision_policy", {}),
        "claim_boundary": priors["claim_boundary"],
    }


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
        "acrylic_like_fraction": amounts["ac1920"] / total if total else None,
        "tackifier_like_fraction": amounts["tk100"] / total if total else None,
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
    return {
        "formulation_id": formulation_id,
        "runs": out,
        "result_visibility": "full" if include_follow_up else "original_only",
    }


def get_repeatability_risk(formulation_id: str) -> list[dict[str, Any]]:
    rows = [
        r for r in load_temperature_sweeps()
        if r["formulation_id"] == formulation_id and r["retest_after_1d"].lower() != "true"
    ]
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


def _linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    xbar = statistics.fmean(xs)
    ybar = statistics.fmean(ys)
    sxx = sum((x - xbar) ** 2 for x in xs)
    if sxx <= 0:
        raise ValueError("x values have zero variance")
    slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sxx
    intercept = ybar - slope * xbar
    pred = [intercept + slope * x for x in xs]
    sst = sum((y - ybar) ** 2 for y in ys)
    sse = sum((y - p) ** 2 for y, p in zip(ys, pred))
    r2 = 1.0 - sse / sst if sst > 0 else 1.0
    return slope, intercept, r2


def get_state_aware_rheology_summary() -> dict[str, Any]:
    """Recompute the local pre-result state-aware rheology evidence from raw CSV files.

    This action intentionally uses only original temperature sweeps and original hold
    data. It does not inspect the later validation formulation or its outcome.
    """
    rows = load_temperature_sweeps()
    by_run: dict[tuple[str, str, bool], list[tuple[float, float]]] = defaultdict(list)
    for row in rows:
        key = (
            row["formulation_id"],
            row["run_label"],
            row["retest_after_1d"].lower() == "true",
        )
        by_run[key].append((float(row["temperature_c"]), float(row["viscosity_reported"])))

    normalized_by_temp: dict[float, list[float]] = defaultdict(list)
    eta_descriptors: list[dict[str, Any]] = []
    for (formulation_id, run_label, retest), series in sorted(by_run.items()):
        series = sorted(series)
        anchor = next((eta for temp, eta in series if temp == 120.0), None)
        if anchor is None or len(series) < 3:
            continue
        for temp, eta in series:
            normalized_by_temp[temp].append(eta / anchor)
        xs = [1.0 / (temp + 273.15) for temp, _ in series]
        ys = [math.log(eta) for _, eta in series]
        slope, _intercept, r2 = _linear_fit(xs, ys)
        eta_descriptors.append({
            "formulation_id": formulation_id,
            "run_label": run_label,
            "retest_after_1d": retest,
            "apparent_E_eta_kJ_mol": slope * R_GAS / 1000.0,
            "ln_eta_vs_inverse_T_r2": r2,
        })

    collapse = []
    non_anchor_cvs = []
    for temp, values in sorted(normalized_by_temp.items()):
        cv = coefficient_of_variation(values) if len(values) >= 2 else None
        item = {
            "temperature_c": temp,
            "n_realizations": len(values),
            "mean_eta_over_eta120": statistics.fmean(values),
            "cross_realization_cv": cv,
            "min_eta_over_eta120": min(values),
            "max_eta_over_eta120": max(values),
        }
        collapse.append(item)
        if temp != 120.0 and cv is not None:
            non_anchor_cvs.append(cv)

    e_values = [x["apparent_E_eta_kJ_mol"] for x in eta_descriptors]
    r2_values = [x["ln_eta_vs_inverse_T_r2"] for x in eta_descriptors]

    e2_by_temp: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        if row["formulation_id"] == "E2":
            e2_by_temp[float(row["temperature_c"])].append(float(row["viscosity_reported"]))
    e2_spread = [
        {
            "temperature_c": temp,
            "n_realizations": len(values),
            "max_min_ratio": max_min_ratio(values),
        }
        for temp, values in sorted(e2_by_temp.items())
        if len(values) >= 2
    ]

    hold_summary: dict[str, Any] = {}
    for formulation_id in ("E1", "E5"):
        data = get_hold_stability(formulation_id, include_follow_up=False)
        hold_summary[formulation_id] = [
            {
                "run_label": run["run_label"],
                "si_15_to_60": run.get("si_15_to_60"),
                "si_15_to_90": run.get("si_15_to_90"),
            }
            for run in data["runs"]
        ]

    return {
        "source_scope": "original pre-validation local data only",
        "state_shift_evidence": {
            "n_complete_realizations": len(eta_descriptors),
            "e2_matched_temperature_spread": e2_spread,
            "anchor_normalized_collapse": collapse,
            "non_anchor_cv_range": [min(non_anchor_cvs), max(non_anchor_cvs)] if non_anchor_cvs else None,
            "non_anchor_cv_mean": statistics.fmean(non_anchor_cvs) if non_anchor_cvs else None,
        },
        "temperature_sensitivity": {
            "per_realization": eta_descriptors,
            "mean_apparent_E_eta_kJ_mol": statistics.fmean(e_values) if e_values else None,
            "sd_apparent_E_eta_kJ_mol": statistics.stdev(e_values) if len(e_values) >= 2 else None,
            "cv_apparent_E_eta": coefficient_of_variation(e_values) if len(e_values) >= 2 else None,
            "range_apparent_E_eta_kJ_mol": [min(e_values), max(e_values)] if e_values else None,
            "median_ln_eta_inverse_T_r2": statistics.median(r2_values) if r2_values else None,
            "interpretation": "apparent rheological temperature-sensitivity descriptor; not a reaction activation energy",
        },
        "original_hold_failure_evidence": hold_summary,
        "design_theory": [
            "nominal composition alone does not locate the realized viscosity level",
            "within the measured local chemistry family, normalized thermal-response shape is much more conserved than absolute viscosity",
            "process/realization state should remain explicit in the design object",
            "thermal-hold stability should be optimized separately from static viscosity and local thermal-response shape",
        ],
        "claim_boundary": "Local state-shift evidence is not asserted to be universal across reactive-PUR chemistry families.",
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
        "acrylic_like_fraction": amounts["ac1920"] / total if total else None,
        "tackifier_like_fraction": amounts["tk100"] / total if total else None,
        "modifier_fraction": modifier / total if total else None,
        "mdi_fraction": amounts["mdi"] / total if total else None,
        "resin_modified": modifier > 0,
        "amounts": amounts,
    }


def _axis_support(value_pct: float, anchors_pct: list[float], strong: float, moderate: float) -> dict[str, Any]:
    if value_pct == 0:
        return {
            "status": "control_zero",
            "nearest_anchor_pct": None,
            "distance_pct_points": None,
        }
    distance_pairs = [(abs(value_pct - a), a) for a in anchors_pct]
    distance, anchor = min(distance_pairs)
    if distance <= strong:
        status = "strong_analogue_region"
    elif distance <= moderate:
        status = "moderate_analogue_region"
    else:
        status = "weak_analogue_region"
    return {
        "status": status,
        "nearest_anchor_pct": anchor,
        "distance_pct_points": distance,
    }


def compare_candidate_to_priors(candidate: dict[str, Any]) -> dict[str, Any]:
    profile = candidate_profile(candidate)
    priors = load_formulation_priors()
    axes = priors["candidate_axes"]
    thresholds = priors["action_support_thresholds_pct_points"]
    strong = float(thresholds["strong"])
    moderate = float(thresholds["moderate"])

    ac_pct = 100.0 * float(profile["acrylic_like_fraction"] or 0.0)
    tk_pct = 100.0 * float(profile["tackifier_like_fraction"] or 0.0)

    ac_support = _axis_support(
        ac_pct,
        [float(x) for x in axes["acrylic_like_modifier_pct_total"]["direct_evidence_anchors_pct"]],
        strong,
        moderate,
    )
    tk_support = _axis_support(
        tk_pct,
        [float(x) for x in axes["minor_tackifier_like_modifier_pct_total"]["direct_evidence_anchors_pct"]],
        strong,
        moderate,
    )

    active = [x["status"] for x in (ac_support, tk_support) if x["status"] != "control_zero"]
    if not active:
        overall = "baseline_control"
    elif all(x == "strong_analogue_region" for x in active):
        overall = "strong_analogue_region"
    elif any(x == "weak_analogue_region" for x in active):
        overall = "weak_analogue_region"
    else:
        overall = "moderate_analogue_region"

    return {
        "profile": profile,
        "acrylic_axis_support": ac_support,
        "tackifier_axis_support": tk_support,
        "analogue_support": overall,
        "hypothesis": priors["stability_hypotheses"],
        "note": (
            "Analogue support is computed separately for the acrylic-like and tackifier-like axes from independent evidence anchors. "
            "It is not a prediction of the current wet-lab outcome."
        ),
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
    profile = prior["profile"]
    reasons = []
    risk = 0

    total_modifier_pct = 100.0 * float(profile["modifier_fraction"] or 0.0)
    if total_modifier_pct > 35.0:
        risk += 2
        reasons.append("combined modifier fraction is outside the frozen V2 hypothesis grid")

    if prior["analogue_support"] == "weak_analogue_region":
        risk += 1
        reasons.append("one or more active modifier axes are far from the independent evidence anchors")

    if proc["process_history_uncertainty"] == "high":
        risk += 2
        reasons.append("major process-history fields are missing")
    elif proc["process_history_uncertainty"] == "moderate":
        risk += 1
        reasons.append("some process-history fields are missing")

    if not profile["resin_modified"]:
        reasons.append("baseline control does not test the resin-modification hypothesis")

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
    support_points = {
        "strong_analogue_region": 2.0,
        "moderate_analogue_region": 1.0,
        "weak_analogue_region": 0.0,
        "baseline_control": 0.0,
    }
    risk_penalty = {"low": 0.0, "moderate": 1.0, "high": 2.0}

    for candidate in candidates:
        prior = compare_candidate_to_priors(candidate)
        stress = stress_test_candidate(candidate)
        score = support_points[prior["analogue_support"]] - risk_penalty[stress["risk_level"]]
        if prior["profile"]["resin_modified"]:
            score += 1.0
        scored.append({
            "candidate_id": candidate.get("candidate_id"),
            "support_score": score,
            "profile": prior["profile"],
            "analogue_comparison": prior,
            "stress_test": stress,
        })
    return sorted(scored, key=lambda x: (-x["support_score"], str(x["candidate_id"])))


def execute_action(name: str, args: dict[str, Any], *, include_follow_up: bool) -> Any:
    if name == "query_external_priors":
        return query_external_priors(**args)
    if name == "get_candidate_hypothesis":
        return get_candidate_hypothesis()
    if name == "inspect_formulation":
        return inspect_formulation(**args)
    if name == "get_hold_stability":
        return get_hold_stability(include_follow_up=include_follow_up, **args)
    if name == "get_repeatability_risk":
        return get_repeatability_risk(**args)
    if name == "get_temperature_support":
        return get_temperature_support(**args)
    if name == "get_state_aware_rheology_summary":
        return get_state_aware_rheology_summary()
    if name == "get_chemistry_audited_rheology_summary":
        return get_state_aware_rheology_summary_v3()
    if name == "assess_shared_shape_applicability":
        return assess_shared_shape_applicability(**args)
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
