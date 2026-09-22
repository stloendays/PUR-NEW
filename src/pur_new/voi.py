"""Deterministic Scientific Value-of-Information (VOI) tool for Agent V4.

This module is a scientific tool, not a second language model. Every quantity it
returns is computed from pre-result evidence by explicit, inspectable rules:

  * the registered mechanistic hypotheses (``configs/hypothesis_registry.json``),
  * the declared measurement plans (``configs/measurement_catalog.json``),
  * the outcome-blind candidate lattice,
  * the curated external formulation priors.

It never reads the held-out validation formulation, its measurements, or any
statistic derived from them. The score is a transparent normalized combination and
is explicitly NOT a posterior probability: the local design contains six audited
realizations and two hold trajectories, which does not support a calibrated
Bayesian expected-information calculation. Weight sensitivity is reported instead
of a fabricated posterior.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Any

from .actions import (
    audit_process_unknowns,
    candidate_profile,
    compare_candidate_to_priors,
    load_formulation_priors,
    stress_test_candidate,
)
from .agent_v3 import classify_intervention_coverage, independently_supported_axes

CONFIG_DIR = Path(__file__).resolve().parents[2] / "configs"

# Prior weight on how unresolved each rheological coordinate currently is, read off
# the measured local design. S_t is least resolved: only two original formulations
# were ever held at temperature and no modifier-bearing composition was measured at
# all. S_T is best resolved: six audited realizations agree to CV 5.77%.
UNRESOLVED_PRIOR = {
    "isothermal time coordinate S_t": 0.90,
    "temperature coordinate S_T": 0.35,
    "realized viscosity level eta_ref": 0.50,
    "realization displacement delta_fr": 0.80,
}

# A composition carrying no modifier re-measures chemistry the local design already
# covers, so its marginal uncertainty reduction is discounted.
NOVEL_CHEMISTRY_FACTOR = {True: 1.0, False: 0.45}

COVERAGE_RELEVANCE = {"full_coverage": 1.0, "partial_coverage": 0.7, "no_intervention": 0.4}
RISK_LEVEL_VALUE = {"low": 0.0, "moderate": 0.5, "high": 1.0}

# Extrapolation beyond the supported region is normalized by roughly one full
# region width, so one region-width of overshoot scores about 1.
EXTRAPOLATION_NORMALIZER_PCT = 12.0

# Two experiments whose VOI differs by less than this are treated as tied. The
# deterministic layer must not manufacture a preference it does not have.
TIE_EPSILON = 1e-9

BASE_WEIGHTS = {
    "hypothesis_discrimination": 0.30,
    "uncertainty_reduction": 0.20,
    "decision_relevance": 0.25,
    "measurement_interpretability": 0.10,
    "extrapolation_risk": 0.10,
    "process_state_risk": 0.05,
}
POSITIVE_TERMS = (
    "hypothesis_discrimination",
    "uncertainty_reduction",
    "decision_relevance",
    "measurement_interpretability",
)
RISK_TERMS = ("extrapolation_risk", "process_state_risk")

VOI_FORMULA = (
    "VOI = w_hyp * hypothesis_discrimination + w_unc * uncertainty_reduction "
    "+ w_dec * decision_relevance + w_int * measurement_interpretability "
    "- w_ext * extrapolation_risk - w_proc * process_state_risk. "
    "Every component is normalized to [0, 1] by construction. This is a transparent "
    "normalized score with reported weight sensitivity, not a Bayesian posterior."
)


def _read(name: str) -> dict[str, Any]:
    return json.loads((CONFIG_DIR / name).read_text(encoding="utf-8"))


def load_hypothesis_registry() -> dict[str, Any]:
    return _read("hypothesis_registry.json")


def load_measurement_catalog() -> dict[str, Any]:
    return _read("measurement_catalog.json")


def reactive_mass_fraction(candidate: dict[str, Any]) -> float:
    """Mass fraction of reaction-capable material (polyols + MDI) in the candidate."""
    state = candidate["formulation_state"]
    reactive = sum(float(state.get(k, 0.0) or 0.0) for k in ("PPG2000", "PDP70", "MDI"))
    modifier = sum(float(state.get(k, 0.0) or 0.0) for k in ("AC1920", "TK100"))
    total = reactive + modifier
    return reactive / total if total else 1.0


def modifier_axes(candidate: dict[str, Any]) -> tuple[float, float]:
    state = candidate["formulation_state"]
    return float(state.get("AC1920", 0.0) or 0.0), float(state.get("TK100", 0.0) or 0.0)


def predict_drift(
    hypothesis: dict[str, Any],
    candidate: dict[str, Any],
    reference_drift_pct: float,
) -> float:
    """Pre-result point prediction of matched-window drift under one hypothesis."""
    phi_r = reactive_mass_fraction(candidate)
    acrylic, tackifier = modifier_axes(candidate)
    linear = reference_drift_pct * phi_r
    rule = hypothesis["prediction_rule"]
    if rule == "linear_dilution":
        return linear
    if rule == "superlinear_suppression":
        # Reduces to the dilution prediction when no resin modifier is present at all.
        if acrylic + tackifier <= 0.0:
            return linear
        return linear * float(hypothesis.get("suppression_factor_vs_linear_max", 0.5))
    if rule == "tackifier_required":
        if tackifier <= 0.0:
            return linear
        return linear * 0.5
    raise KeyError(f"unknown prediction_rule: {rule!r}")


#: Prediction rules whose observable is the realized viscosity LEVEL rather than the
#: matched-window drift. A registry declaring ``discriminating_quantity`` routes here.
LEVEL_PREDICTION_RULES = frozenset(
    {"level_dilution", "level_association", "level_plasticization"}
)


def predict_level_change(
    hypothesis: dict[str, Any],
    candidate: dict[str, Any],
    registry: dict[str, Any],
) -> float:
    """Pre-result point prediction of the relative viscosity LEVEL change, in percent.

    The level is expressed against the unmodified reactive-core composition of the same
    lattice, so an unmodified candidate carries no differential prediction under any of
    the registered level hypotheses and therefore separates none of them.
    """
    reference = registry["reference_observations"]
    exponent = float(reference["dilution_exponent"])
    floor = float(registry.get("prediction_floor_pct", -95.0))
    phi_r = reactive_mass_fraction(candidate)
    acrylic, tackifier = modifier_axes(candidate)
    dilution = 100.0 * (phi_r**exponent - 1.0)
    rule = hypothesis["prediction_rule"]
    if rule == "level_dilution":
        value = dilution
    elif rule == "level_association":
        value = dilution + float(hypothesis["association_gain_pct_per_pct"]) * acrylic
    elif rule == "level_plasticization":
        value = dilution - float(hypothesis["plasticization_drop_pct_per_pct"]) * (
            acrylic + tackifier
        )
    else:
        raise KeyError(f"unknown level prediction_rule: {rule!r}")
    return max(floor, value)


def _separated_pairs(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
    predictions: dict[str, float],
    threshold: float,
) -> list[list[str]]:
    separated = []
    for first, second in pairs:
        left, right = predictions[first["hypothesis_id"]], predictions[second["hypothesis_id"]]
        if abs(left - right) >= threshold:
            separated.append([first["hypothesis_id"], second["hypothesis_id"]])
    return separated


def hypothesis_discrimination(
    candidate: dict[str, Any],
    measurement: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    """Fraction of registered hypothesis pairs this experiment can separate.

    A pair counts as separated only when the two pre-result point predictions differ
    by at least the measurement's declared resolution threshold. Measurements whose
    observable is not the drift coordinate make no differential prediction under this
    registry and score zero. That is the intended scientific result rather than a
    defect: only the matched-window hold measurement observes these mechanisms.
    """
    hypotheses = registry["hypotheses"]
    pairs = list(combinations(hypotheses, 2))
    if not pairs:
        return {"score": 0.0, "separated_pairs": [], "n_pairs": 0}

    quantity = registry.get("discriminating_quantity")
    if quantity is not None:
        # A registry that names the coordinate its hypotheses disagree about is separable
        # only by a measurement that resolves that coordinate. This is the same rule the
        # drift branch below applies; declaring it explicitly makes it apply to any
        # coordinate rather than only to thermal-hold drift.
        if measurement.get("resolves_quantity") != quantity:
            return {
                "score": 0.0,
                "separated_pairs": [],
                "n_pairs": len(pairs),
                "discriminating_quantity": quantity,
                "measurement_resolves_quantity": measurement.get("resolves_quantity"),
                "note": "this measurement does not resolve the coordinate the registry disagrees about",
            }
        threshold = float(measurement["discrimination_threshold_pct"])
        predictions = {
            h["hypothesis_id"]: predict_level_change(h, candidate, registry) for h in hypotheses
        }
        separated = _separated_pairs(pairs, predictions, threshold)
        return {
            "score": len(separated) / len(pairs),
            "separated_pairs": separated,
            "predictions_pct": {key: round(value, 4) for key, value in predictions.items()},
            "resolution_threshold_pct": threshold,
            "n_pairs": len(pairs),
            "discriminating_quantity": quantity,
            "measurement_resolves_quantity": measurement.get("resolves_quantity"),
        }

    if "thermal_hold_drift" not in measurement.get("addresses", []):
        return {
            "score": 0.0,
            "separated_pairs": [],
            "n_pairs": len(pairs),
            "note": "this measurement does not observe the drift coordinate the registry disagrees about",
        }

    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    threshold = float(measurement["discrimination_threshold_pct"])
    predictions = {h["hypothesis_id"]: predict_drift(h, candidate, reference) for h in hypotheses}

    separated = []
    for first, second in pairs:
        left, right = predictions[first["hypothesis_id"]], predictions[second["hypothesis_id"]]
        if abs(left - right) >= threshold:
            separated.append([first["hypothesis_id"], second["hypothesis_id"]])
    return {
        "score": len(separated) / len(pairs),
        "separated_pairs": separated,
        "predictions_pct": {key: round(value, 4) for key, value in predictions.items()},
        "resolution_threshold_pct": threshold,
        "n_pairs": len(pairs),
    }


def catalog_effort_scale(catalog: dict[str, Any]) -> float | None:
    """Largest declared experimental effort in the catalog, or None if none is declared.

    A catalog that declares no ``effort_points`` produces no budget component at all, so
    the drift condition is scored by exactly the terms it was always scored by.
    """
    efforts = [m.get("effort_points") for m in catalog["measurements"]]
    if any(value is None for value in efforts):
        return None
    scale = max(float(value) for value in efforts)
    return scale if scale > 0 else None


def budget_efficiency(measurement: dict[str, Any], effort_scale: float) -> dict[str, Any]:
    """How little of the declared experimental budget this measurement plan consumes.

    Linear in the declared number of viscosity determinations, normalized by the most
    expensive plan in the same catalog. The most expensive plan scores 0.0; the cheapest
    scores 1.0 only in the limit of a free experiment.
    """
    effort = float(measurement["effort_points"])
    return {
        "score": round(max(0.0, 1.0 - effort / effort_scale), 6),
        "effort_points": effort,
        "effort_scale_points": effort_scale,
        "definition": "1 - effort_points / max(effort_points) over the declared catalog",
    }


def extrapolation_risk(candidate: dict[str, Any], priors: dict[str, Any]) -> dict[str, Any]:
    """Normalized distance outside the externally supported modifier regions.

    A zeroed axis carries no extrapolation risk: zero modifier is the original,
    directly measured chemistry, not an extrapolation away from evidence.
    """
    policy = priors["decision_policy"]["evidence_region_policy"]
    acrylic, tackifier = modifier_axes(candidate)
    regions = {
        "acrylic_like": (acrylic, policy["acrylic_like"]["broad_supported_region_pct_total"]),
        "minor_tackifier_like": (
            tackifier,
            policy["minor_tackifier_like"]["repeated_minor_resin_cluster_pct_total"],
        ),
    }
    per_axis = {}
    for axis, (value, bounds) in regions.items():
        low, high = float(bounds[0]), float(bounds[1])
        if value <= 0.0:
            distance = 0.0
        elif value < low:
            distance = low - value
        elif value > high:
            distance = value - high
        else:
            distance = 0.0
        per_axis[axis] = {
            "value_pct": value,
            "supported_region_pct": [low, high],
            "distance_pct": round(distance, 4),
        }
    mean_distance = sum(item["distance_pct"] for item in per_axis.values()) / len(per_axis)
    return {
        "score": min(1.0, mean_distance / EXTRAPOLATION_NORMALIZER_PCT),
        "mean_distance_pct": round(mean_distance, 4),
        "normalizer_pct": EXTRAPOLATION_NORMALIZER_PCT,
        "per_axis": per_axis,
    }


def process_state_risk(candidate: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    """Process/state ambiguity carried into the experiment, after the measurement plan.

    A measurement plan that explicitly controls and records preparation history
    removes most of this risk; that is what a state-control experiment is for.
    """
    stress = stress_test_candidate(candidate)
    process = audit_process_unknowns(candidate)
    missing = len(process["missing_process_fields"])
    known = process.get("known_process_fields") or []
    total_fields = max(1, missing + len(known))
    base = 0.5 * RISK_LEVEL_VALUE[stress["risk_level"]] + 0.5 * (missing / total_fields)
    controls = bool(measurement.get("controls_process_state", False))
    score = base * (0.2 if controls else 1.0)
    return {
        "score": round(min(1.0, max(0.0, score)), 6),
        "base_before_measurement_plan": round(base, 6),
        "measurement_controls_process_state": controls,
        "risk_level": stress["risk_level"],
        "missing_process_fields": missing,
    }


def uncertainty_reduction(candidate: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    """How unresolved the coordinate this measurement resolves currently is."""
    quantity = measurement["resolves_quantity"]
    prior = UNRESOLVED_PRIOR[quantity]
    acrylic, tackifier = modifier_axes(candidate)
    novel = (acrylic + tackifier) > 0.0
    factor = NOVEL_CHEMISTRY_FACTOR[novel]
    return {
        "score": round(prior * factor, 6),
        "resolves_quantity": quantity,
        "unresolved_prior": prior,
        "novel_chemistry": novel,
        "novel_chemistry_factor": factor,
    }


def decision_relevance(
    candidate: dict[str, Any],
    measurement: dict[str, Any],
    supported_axes: list[str],
) -> dict[str, Any]:
    """Relevance of the experiment to the declared failure mode and the pending decision.

    Combines how directly the measurement observes the failure mode with whether the
    composition covers the intervention axes the pre-result evidence supports.
    """
    prior = compare_candidate_to_priors(candidate)
    coverage = classify_intervention_coverage(prior, supported_axes)
    coverage_factor = COVERAGE_RELEVANCE[coverage["coverage_class"]]
    base = float(measurement["decision_relevance"])
    return {
        "score": round(base * coverage_factor, 6),
        "measurement_decision_relevance": base,
        "coverage_class": coverage["coverage_class"],
        "coverage_factor": coverage_factor,
        "covered_supported_axes": coverage["covered_supported_axes"],
        "zeroed_supported_axes": coverage["zeroed_supported_axes"],
    }


def score_components(components: dict[str, float], weights: dict[str, float]) -> float:
    """Weighted sum of the scored components, with the risk terms entering negatively.

    Iterating the declared weights rather than a fixed term list lets a decision condition
    add a positive term of its own - the Condition-B budget term is the only current
    example - without changing the meaning or the value of any existing term. A weight
    with no matching component contributes nothing, so the drift condition scores exactly
    as it did before the budget term existed.
    """
    total = 0.0
    for key, weight in weights.items():
        if key not in components:
            continue
        value = components[key]
        total += -weight * value if key in RISK_TERMS else weight * value
    return total


def _intervention_family(acrylic: float, tackifier: float) -> str:
    if acrylic > 0 and tackifier > 0:
        return "dual_axis_resin_modified"
    if acrylic > 0:
        return "acrylic_only"
    if tackifier > 0:
        return "minor_tackifier_only"
    return "reactive_core_only"


def _level_criteria(
    measurement: dict[str, Any],
    candidate: dict[str, Any],
    registry: dict[str, Any],
) -> tuple[str, str]:
    """Acceptance and falsification text for a registry that adjudicates viscosity level."""
    quantity = registry["discriminating_quantity"]
    if measurement.get("resolves_quantity") != quantity:
        return (
            f"This plan does not return {quantity}, so it cannot accept or reject any registered "
            "level hypothesis. Selecting it leaves the processing-window question open.",
            f"No registered level hypothesis is falsifiable by this plan: it observes "
            f"{measurement.get('resolves_quantity')} rather than {quantity}.",
        )
    predictions = {
        h["hypothesis_id"]: predict_level_change(h, candidate, registry)
        for h in registry["hypotheses"]
    }
    threshold = float(measurement["discrimination_threshold_pct"])
    dilute = predictions["H-LEVEL-DILUTE"]
    assoc = predictions["H-LEVEL-ASSOC"]
    plastic = predictions["H-LEVEL-PLASTIC"]
    accept = (
        f"The measured 120-130 C level change against the unmodified reactive core falls within "
        f"{threshold:.2f}% of exactly one registered prediction: {dilute:.2f}% for H-LEVEL-DILUTE, "
        f"{assoc:.2f}% for H-LEVEL-ASSOC or {plastic:.2f}% for H-LEVEL-PLASTIC. That hypothesis is "
        "accepted for this composition and the processing-window level is reported with it."
    )
    falsify = (
        f"H-LEVEL-ASSOC is falsified if the measured level change is at or below the inert-dilution "
        f"prediction of {dilute:.2f}%. H-LEVEL-PLASTIC is falsified if it is at or above that same "
        f"prediction. H-LEVEL-DILUTE is falsified if the measured level change departs from "
        f"{dilute:.2f}% by more than the {threshold:.2f}% resolution of this plan."
    )
    return accept, falsify


def _acceptance_criterion(
    measurement: dict[str, Any],
    phi_r: float,
    reference: float,
    *,
    registry: dict[str, Any] | None = None,
    candidate: dict[str, Any] | None = None,
) -> str:
    if registry is not None and candidate is not None and registry.get("discriminating_quantity"):
        return _level_criteria(measurement, candidate, registry)[0]
    if "thermal_hold_drift" in measurement.get("addresses", []):
        linear = reference * phi_r
        return (
            f"Matched 15-60 min drift at 120 C stays below {0.5 * linear:.2f}% across at least two "
            f"repeats, i.e. below half the linear-dilution prediction of {linear:.2f}% implied by a "
            f"reactive mass fraction of {phi_r:.4f}. This accepts H-RESIN over H-CORE."
        )
    if measurement["measurement_id"] == "M-SWEEP":
        return (
            "Apparent E_eta of the modified composition lies inside the measured local band "
            "42.05 +/- 2.43 kJ/mol, confirming that modification relocates viscosity level without "
            "changing the local thermal-response shape."
        )
    if measurement["measurement_id"] == "M-ANCHOR":
        return (
            "A single 110 C anchor reconstructs the 120-130 C response of the modified composition "
            "within a multiplicative error of 1.088x, the pooled RMSE measured in the strict holdout."
        )
    return (
        "Three controlled-process preparations of one nominal composition span less than 1.5x in "
        "realized viscosity at matched temperature, against the 2.80-3.57x uncontrolled E2 spread."
    )


def _falsification_criterion(
    measurement: dict[str, Any],
    phi_r: float,
    reference: float,
    tackifier: float,
    *,
    registry: dict[str, Any] | None = None,
    candidate: dict[str, Any] | None = None,
) -> str:
    if registry is not None and candidate is not None and registry.get("discriminating_quantity"):
        return _level_criteria(measurement, candidate, registry)[1]
    if "thermal_hold_drift" in measurement.get("addresses", []):
        linear = reference * phi_r
        threshold = float(measurement["discrimination_threshold_pct"])
        base = (
            f"H-RESIN is falsified if matched 15-60 min drift is at or above the linear-dilution "
            f"prediction of {linear:.2f}%. H-CORE is falsified if drift falls below "
            f"{0.5 * linear:.2f}%, a separation larger than the {threshold:.2f}% resolution threshold."
        )
        if tackifier <= 0.0:
            return (
                base
                + " H-DUAL is falsified if this acrylic-only composition reaches the low-drift regime "
                "with no minor tackifier present."
            )
        return (
            base
            + " This composition carries both axes, so it cannot separate H-RESIN from H-DUAL; an "
            "acrylic-only hold is the follow-up required for that."
        )
    if measurement["measurement_id"] == "M-SWEEP":
        return "The conserved-shape reading is falsified if E_eta moves outside 42.05 +/- 2.43 kJ/mol."
    if measurement["measurement_id"] == "M-ANCHOR":
        return (
            "One-point transferability is falsified if reconstruction error exceeds 1.126x, the upper "
            "bootstrap bound of the strict holdout."
        )
    return (
        "The realization-shift reading is falsified if controlled preparations still span more than "
        "the uncontrolled 2.80x lower bound."
    )


def build_experiment_cards(
    candidates: list[dict[str, Any]],
    *,
    registry: dict[str, Any] | None = None,
    catalog: dict[str, Any] | None = None,
    priors: dict[str, Any] | None = None,
    weights: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    """Cross every candidate formulation with every measurement plan and score VOI.

    The returned card is the unit the Agent selects over: a formulation candidate, a
    measurement plan, the hypothesis set it discriminates, the primary observable, an
    acceptance criterion and a falsification criterion.
    """
    registry = registry or load_hypothesis_registry()
    catalog = catalog or load_measurement_catalog()
    priors = priors or load_formulation_priors()
    weights = weights or dict(BASE_WEIGHTS)
    supported_axes = independently_supported_axes()
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    effort_scale = catalog_effort_scale(catalog)

    cards: list[dict[str, Any]] = []
    for candidate in candidates:
        profile = candidate_profile(candidate)
        phi_r = reactive_mass_fraction(candidate)
        acrylic, tackifier = modifier_axes(candidate)
        for measurement in catalog["measurements"]:
            disc = hypothesis_discrimination(candidate, measurement, registry)
            unc = uncertainty_reduction(candidate, measurement)
            dec = decision_relevance(candidate, measurement, supported_axes)
            ext = extrapolation_risk(candidate, priors)
            proc = process_state_risk(candidate, measurement)
            components = {
                "hypothesis_discrimination": disc["score"],
                "uncertainty_reduction": unc["score"],
                "decision_relevance": dec["score"],
                "measurement_interpretability": float(measurement["interpretability"]),
                "extrapolation_risk": ext["score"],
                "process_state_risk": proc["score"],
            }
            budget = budget_efficiency(measurement, effort_scale) if effort_scale else None
            if budget is not None:
                components["budget_efficiency"] = budget["score"]
            card = {
                "experiment_id": f"{candidate['candidate_id']}::{measurement['measurement_id']}",
                "candidate_id": candidate["candidate_id"],
                "measurement_id": measurement["measurement_id"],
                "intervention_family": _intervention_family(acrylic, tackifier),
                "formulation_state": candidate["formulation_state"],
                "acrylic_like_pct": acrylic,
                "minor_tackifier_like_pct": tackifier,
                "reactive_mass_fraction": round(phi_r, 6),
                "resin_modified": bool(profile["resin_modified"]),
                "measurement_plan": {
                    "measurement_id": measurement["measurement_id"],
                    "name": measurement["name"],
                    "protocol": measurement["protocol"],
                    "primary_observable": measurement["primary_observable"],
                    "sampling_times_min": measurement["sampling_times_min"],
                    "temperature_c": measurement["temperature_c"],
                    "min_repeats": measurement["min_repeats"],
                },
                "scientific_hypotheses_addressed": [h["hypothesis_id"] for h in registry["hypotheses"]],
                "hypothesis_discrimination_detail": disc,
                "uncertainty_reduction_detail": unc,
                "decision_relevance_detail": dec,
                "extrapolation_risk_detail": ext,
                "process_state_risk_detail": proc,
                "voi_components": {key: round(value, 6) for key, value in components.items()},
                "voi_score": round(score_components(components, weights), 6),
                "acceptance_criterion": _acceptance_criterion(
                    measurement, phi_r, reference, registry=registry, candidate=candidate
                ),
                "falsification_criterion": _falsification_criterion(
                    measurement, phi_r, reference, tackifier, registry=registry, candidate=candidate
                ),
            }
            # A catalog that declares no experimental effort produces no budget key at all,
            # so a drift-condition card is byte-identical to the one the frozen V4 and
            # Condition-A series recorded.
            if budget is not None:
                card["budget_efficiency_detail"] = budget
            cards.append(card)
    cards.sort(key=lambda card: (-card["voi_score"], card["experiment_id"]))
    return cards


def _flip_boundary(
    cards: list[dict[str, Any]],
    base_weights: dict[str, float],
    base_top_set: set[str],
) -> dict[str, Any]:
    """Smallest single-term multiplier, per term, that changes the tied top set."""
    boundary: dict[str, Any] = {}
    for term in base_weights:
        flip_low = flip_high = None
        for step in range(1, 61):
            mult = round(0.05 * step, 2)
            weights = dict(base_weights)
            weights[term] = base_weights[term] * mult
            scored = [(score_components(card["voi_components"], weights), card) for card in cards]
            best = max(score for score, _ in scored)
            tied = {card["experiment_id"] for score, card in scored if abs(score - best) <= TIE_EPSILON}
            if tied != base_top_set:
                if mult < 1.0 and flip_low is None:
                    flip_low = mult
                elif mult > 1.0 and flip_high is None:
                    flip_high = mult
        boundary[term] = {
            "flips_when_scaled_below": flip_low,
            "flips_when_scaled_above": flip_high,
            "survives_entire_sweep": flip_low is None and flip_high is None,
        }
    return boundary


COVERAGE_ORDER = {"full_coverage": 0, "partial_coverage": 1, "no_intervention": 2}

RULE_ORDERS = (
    "sufficiency_first",
    "minimality_first",
)


def perturbation_cost(card: dict[str, Any]) -> float:
    """Total modifier burden of a card, as a plain magnitude in percentage points."""
    return card["acrylic_like_pct"] + card["minor_tackifier_like_pct"]


def rule_order_key(card: dict[str, Any], order: str) -> tuple[Any, ...]:
    """Lexicographic decision key under a named rule ORDER.

    The two orders use the same facts, the same candidate space and the same VOI
    components. They differ only in which consideration is allowed to decide first.

    ``sufficiency_first`` asks whether the experiment can answer the open question before
    asking what it costs. ``minimality_first`` inverts that: it minimizes intervention
    burden first and only then looks at whether anything is being tested. The inversion
    is the V2 failure mode of the earlier Stage-1 ladder, reproduced here as a controlled
    arm rather than quoted from a previous series.
    """
    coverage = COVERAGE_ORDER[card["decision_relevance_detail"]["coverage_class"]]
    discrimination = card["voi_components"]["hypothesis_discrimination"]
    relevance = card["voi_components"]["decision_relevance"]
    burden = perturbation_cost(card)
    if order == "sufficiency_first":
        return (coverage, -discrimination, -relevance, burden, card["experiment_id"])
    if order == "minimality_first":
        return (burden, coverage, -discrimination, -relevance, card["experiment_id"])
    raise KeyError(f"unknown rule order: {order!r}")


def rank_by_rule_order(cards: list[dict[str, Any]], order: str) -> dict[str, Any]:
    """Rank experiments under a named rule order and report what it puts first.

    This does not modify the VOI score. It is a separate, explicit statement of decision
    ORDER, so that order can be manipulated while every underlying quantity is held fixed.
    """
    ranked = sorted(cards, key=lambda card: rule_order_key(card, order))
    top = ranked[0]
    return {
        "rule_order": order,
        "order_description": (
            "intervention sufficiency is assessed before perturbation size"
            if order == "sufficiency_first"
            else "perturbation size is minimized before intervention sufficiency is assessed"
        ),
        "ranked_experiment_ids": [card["experiment_id"] for card in ranked],
        "top_experiment_id": top["experiment_id"],
        "top_candidate_id": top["candidate_id"],
        "top_measurement_id": top["measurement_id"],
        "top_intervention_family": top["intervention_family"],
        "top_hypothesis_discrimination": top["voi_components"]["hypothesis_discrimination"],
        "top_total_modifier_pct": perturbation_cost(top),
        "top_voi_score": top["voi_score"],
    }


def voi_robustness_sweep(
    candidates: list[dict[str, Any]],
    *,
    base_weights: dict[str, float] | None = None,
    perturbation: float = 0.5,
    steps: int = 5,
    registry: dict[str, Any] | None = None,
    catalog: dict[str, Any] | None = None,
    priors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Decision stability of the VOI ranking under a weight perturbation sweep.

    Reports how often the top experiment, its intervention family and its measurement
    plan survive a defensible re-weighting. This is decision stability of a transparent
    score. It is not model confidence and not a posterior probability.
    """
    base_weights = base_weights or dict(BASE_WEIGHTS)
    registry = registry or load_hypothesis_registry()
    catalog = catalog or load_measurement_catalog()
    priors = priors or load_formulation_priors()

    cards = build_experiment_cards(
        candidates, registry=registry, catalog=catalog, priors=priors, weights=base_weights
    )

    if steps > 1:
        span = 2 * perturbation / (steps - 1)
        multipliers = [round(1.0 - perturbation + index * span, 6) for index in range(steps)]
    else:
        multipliers = [1.0]

    scenarios: list[dict[str, Any]] = [
        {"scenario_id": "base", "perturbed_term": None, "multiplier": 1.0, "weights": dict(base_weights)}
    ]
    for term in base_weights:
        for mult in multipliers:
            if abs(mult - 1.0) < 1e-12:
                continue
            weights = dict(base_weights)
            weights[term] = round(base_weights[term] * mult, 8)
            scenarios.append(
                {
                    "scenario_id": f"{term}_x{mult:g}",
                    "perturbed_term": term,
                    "multiplier": mult,
                    "weights": weights,
                }
            )

    results = []
    for scenario in scenarios:
        weights = scenario["weights"]
        scored = [(score_components(card["voi_components"], weights), card) for card in cards]
        best = max(score for score, _ in scored)
        tied = sorted(card["experiment_id"] for score, card in scored if abs(score - best) <= TIE_EPSILON)
        representative = next(card for score, card in scored if card["experiment_id"] == tied[0])
        strictly_lower = [score for score, _ in scored if score < best - TIE_EPSILON]
        results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "perturbed_term": scenario["perturbed_term"],
                "multiplier": scenario["multiplier"],
                "top_tied_experiment_ids": tied,
                "n_tied_at_top": len(tied),
                "top_experiment_id_alphabetical_representative": representative["experiment_id"],
                "top_candidate_ids": sorted({eid.split("::")[0] for eid in tied}),
                "top_measurement_ids": sorted({eid.split("::")[1] for eid in tied}),
                "top_intervention_families": sorted(
                    {card["intervention_family"] for score, card in scored if card["experiment_id"] in set(tied)}
                ),
                "top_voi": round(best, 6),
                "margin_to_first_strictly_lower": (
                    round(best - max(strictly_lower), 6) if strictly_lower else None
                ),
            }
        )

    base_result = results[0]
    base_set = set(base_result["top_tied_experiment_ids"])
    total = len(results)

    def _jaccard(other: list[str]) -> float:
        other_set = set(other)
        union = base_set | other_set
        return len(base_set & other_set) / len(union) if union else 1.0

    stability = {
        # Fraction of scenarios whose tied top set is exactly the base tied set. The
        # alphabetical representative is NOT used here: with a genuine tie, reporting
        # stability of one arbitrarily chosen member would overstate the result.
        "top_experiment_set_stability": sum(
            set(row["top_tied_experiment_ids"]) == base_set for row in results
        )
        / total,
        "top_experiment_set_mean_jaccard": sum(
            _jaccard(row["top_tied_experiment_ids"]) for row in results
        )
        / total,
        "intervention_family_stability": sum(
            row["top_intervention_families"] == base_result["top_intervention_families"] for row in results
        )
        / total,
        "measurement_plan_stability": sum(
            row["top_measurement_ids"] == base_result["top_measurement_ids"] for row in results
        )
        / total,
    }
    return {
        "metric_name": "decision_stability",
        "metric_is_not": "model confidence; posterior probability; calibrated expected information",
        "voi_formula": VOI_FORMULA,
        "base_weights": base_weights,
        "perturbation_fraction": perturbation,
        "multipliers": multipliers,
        "n_scenarios": total,
        "tie_epsilon": TIE_EPSILON,
        "base_top_tied_experiment_ids": base_result["top_tied_experiment_ids"],
        "n_tied_at_base_top": base_result["n_tied_at_top"],
        "base_top_intervention_families": base_result["top_intervention_families"],
        "base_margin_to_first_strictly_lower": base_result["margin_to_first_strictly_lower"],
        "tie_interpretation": (
            "The deterministic VOI layer is indifferent among the tied top experiments: they share an "
            "identical component vector. Tie-breaking is therefore a genuine task left to the Agent, and "
            "any selection inside this set cannot have been read off the VOI ranking."
        ),
        "stability": {key: round(value, 6) for key, value in stability.items()},
        "recommendation_flip_boundary": _flip_boundary(cards, base_weights, base_set),
        "flipped_scenarios": [
            row for row in results if set(row["top_tied_experiment_ids"]) != base_set
        ],
        "scenarios": results,
    }
