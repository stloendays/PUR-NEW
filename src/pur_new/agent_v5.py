"""Agent V5 chemistry-domain admissibility layer (comparison protocol v1.1).

V5 adds no language-model role. It adds one deterministic scientific layer between the
tool trace and the value-of-information ranking: a *measurement* admissibility audit that
executes the chemistry boundary of the locally discovered shared thermal-response shape.

The scientific order this module implements is fixed::

    measured rheology
      -> discovered local regularity
      -> external domain test (assess_shared_shape_applicability)
      -> deterministic applicability rule
      -> experiment-card admissibility audit
      -> [enforcement, in V5_FULL only]
      -> VOI over the selectable set
      -> model-mediated selection
      -> freeze

Protocol v1.1 fixes what separates the two primary arms. The audit is **identical and
fully model-visible in both arms**; only enforcement differs:

* ``V5_NO_GATE``  advice-only. Every pre-gate card stays selectable and a committed card is
  never rejected for chemistry-domain inadmissibility alone.
* ``V5_FULL``     the same audit becomes hard admissibility before VOI and again at freeze.

Everything the model can see before the enforcement step is therefore byte-identical
between arms by construction: :func:`build_pre_enforcement_payload` takes no arm argument.

The module does not modify ``voi.py``, ``actions.py`` or anything the frozen V3/V4 series
hashed into its contract. It reads the same deterministic VOI cards and annotates them.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from .actions import execute_action
# ``_canonical_formulation_state`` is the single alias map for the recognized components.
# Re-deriving it here would let the gate and the applicability tool drift apart.
from .chemistry_tools import _canonical_formulation_state, assess_shared_shape_applicability
from .voi import BASE_WEIGHTS, TIE_EPSILON, VOI_FORMULA, _flip_boundary, score_components

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"

ARMS = ("V5_NO_GATE", "V5_FULL")
GATE_ID = "PUR_NEW_CHEMISTRY_DOMAIN_GATE_V1"
PROTOCOL_VERSION = "1.1.0"

#: Enforcement is the only declared difference between the two primary arms.
ARM_ENFORCES_GATE = {"V5_NO_GATE": False, "V5_FULL": True}

MANDATORY_LOCAL_SCIENCE_TOOL = "get_chemistry_audited_rheology_summary"
APPLICABILITY_TOOL = "assess_shared_shape_applicability"

#: Planner actions V5 exposes. The predecessor ``get_state_aware_rheology_summary`` is
#: deliberately absent: in V5 the chemistry-provenance-audited summary is the single
#: upstream local-science tool, so the two cannot be silently interchanged mid-series.
V5_PLANNER_ACTIONS = frozenset(
    {
        "query_external_priors",
        "get_candidate_hypothesis",
        "inspect_formulation",
        "get_hold_stability",
        "get_repeatability_risk",
        "get_temperature_support",
        MANDATORY_LOCAL_SCIENCE_TOOL,
        APPLICABILITY_TOOL,
    }
)

#: Measurement plans whose primary observable is only interpretable through the shared
#: thermal-response shape. Everything else observes its quantity directly.
SHAPE_DEPENDENT_MEASUREMENTS = frozenset({"M-ANCHOR"})

SHARED_SHAPE_SUPPORTED = "allowed_with_state_anchor"

SHAPE_INDEPENDENT_BASIS = {
    "M-HOLD-120": (
        "admissible_direct_drift_measurement",
        "The matched-window 120 C hold observes thermal-hold drift directly and does not "
        "reuse the shared thermal-response shape, so it stays admissible outside the "
        "validated chemistry family.",
    ),
    "M-REPEAT": (
        "admissible_direct_state_control_measurement",
        "The repeatability experiment observes between-preparation spread directly and "
        "does not reuse the shared thermal-response shape.",
    ),
    "M-SWEEP": (
        "admissible_direct_shape_verification_measurement",
        "The 80-130 C sweep is the direct verification measurement that establishes the "
        "thermal-response shape for a chemistry-shifted candidate.",
    ),
}

GATE_RULE_TEXT = [
    "Scope: measurement admissibility, not formulation admissibility.",
    "M-HOLD-120, M-REPEAT and M-SWEEP observe their quantity directly and remain admissible.",
    "M-ANCHOR is admissible only when assess_shared_shape_applicability returns "
    f"shared_shape_use == {SHARED_SHAPE_SUPPORTED!r}, or when a versioned prior direct sweep "
    "has verified transferability for the same chemistry family.",
    "Otherwise M-ANCHOR is inadmissible_before_shape_verification: the one-point anchor would "
    "reconstruct 120-130 C viscosity through a shape that has never been measured for that "
    "chemistry.",
    "This audit is a deterministic scientific rule, not a VOI penalty and not a model opinion. "
    "Whether it is binding in this run is stated by the enforcement field.",
]


class InadmissibleSelectionError(ValueError):
    """A model stage named an experiment the enforced gate had removed."""


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def load_architecture(path: Path | None = None) -> dict[str, Any]:
    return read_json(path or CONFIG_DIR / "agent_v5.json")


def load_verified_shape_transfer(path: Path | None = None) -> dict[str, Any]:
    """Versioned record of chemistry families with a completed direct sweep.

    This registry is the only exemption path from the M-ANCHOR rule. It is a repository
    file, so an exemption is a reviewable change rather than a runtime argument.
    """
    return read_json(path or CONFIG_DIR / "verified_shape_transfer.json")


def chemistry_family(candidate: dict[str, Any]) -> str:
    """Stable key for the chemistry family a candidate belongs to."""
    amounts = _canonical_formulation_state(candidate)
    if sum(amounts.values()) <= 0:
        return "unrecognized_composition"
    modifiers = [name for name in ("ac1920", "tk100") if amounts[name] > 0]
    if modifiers:
        return "resin_modified:" + "+".join(sorted(modifiers))
    core = [name for name in ("ppg2000", "pdp70", "mdi") if amounts[name] > 0]
    if len(core) == 3:
        return "unmodified_ppg2000_pdp70_mdi"
    return "partial_core:" + "+".join(sorted(core))


def find_verified_transfer(family: str, verified: dict[str, Any] | None) -> dict[str, Any] | None:
    """Return the versioned verification record for this chemistry family, if any."""
    if not verified:
        return None
    for entry in verified.get("verified_chemistry_families", []):
        if entry.get("chemistry_family") == family:
            return entry
    return None


def assess_candidate(candidate: dict[str, Any], *, verified: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run the domain tool for one candidate and attach its verification status."""
    applicability = assess_shared_shape_applicability(candidate)
    family = chemistry_family(candidate)
    record = find_verified_transfer(family, verified)
    return {
        "candidate_id": candidate.get("candidate_id"),
        "tool": APPLICABILITY_TOOL,
        "chemistry_family": family,
        "chemistry_applicability_status": applicability["status"],
        "shared_shape_use": applicability["shared_shape_use"],
        "applicability_reason": applicability["reason"],
        "recommended_measurement": applicability.get("recommended_measurement"),
        "modifier_fraction": applicability.get("modifier_fraction"),
        "reactive_core_fraction": applicability.get("reactive_core_fraction"),
        "prior_verified_shape_transfer": record,
        "has_prior_verified_shape_transfer": record is not None,
    }


def measurement_admissibility(measurement_id: str, assessment: dict[str, Any]) -> dict[str, Any]:
    """Deterministic admissibility of one measurement plan for one assessed candidate."""
    if measurement_id not in SHAPE_DEPENDENT_MEASUREMENTS:
        rule_id, reason = SHAPE_INDEPENDENT_BASIS.get(
            measurement_id,
            (
                "admissible_not_shape_dependent",
                "The measurement does not reuse the shared thermal-response shape.",
            ),
        )
        return {
            "measurement_admissible": True,
            "admissibility_rule_id": rule_id,
            "admissibility_reason": reason,
            "required_precondition": None,
        }

    if assessment["shared_shape_use"] == SHARED_SHAPE_SUPPORTED:
        return {
            "measurement_admissible": True,
            "admissibility_rule_id": "admissible_shared_shape_supported",
            "admissibility_reason": (
                "The candidate stays inside the measured unmodified PPG2000/PDP70/MDI family, so a "
                "state anchor on the shared thermal-response shape is an evidence-supported local "
                "interpolation prior."
            ),
            "required_precondition": None,
        }

    record = assessment.get("prior_verified_shape_transfer")
    if record is not None:
        return {
            "measurement_admissible": True,
            "admissibility_rule_id": "admissible_prior_verified_shape_transfer",
            "admissibility_reason": (
                "A versioned prior direct sweep verified shared-shape transferability for chemistry "
                f"family {assessment['chemistry_family']}."
            ),
            "required_precondition": None,
            "verification_record": record,
        }

    return {
        "measurement_admissible": False,
        "admissibility_rule_id": "inadmissible_before_shape_verification",
        "admissibility_reason": (
            "M-ANCHOR reconstructs the 120-130 C response through the shared thermal-response shape. "
            f"That shape has not been measured for chemistry family {assessment['chemistry_family']} "
            f"(applicability status {assessment['chemistry_applicability_status']}), and no versioned "
            "prior direct sweep has verified its transfer."
        ),
        "required_precondition": (
            "a completed direct M-SWEEP on this chemistry family, recorded in "
            "configs/verified_shape_transfer.json"
        ),
    }


#: Audit fields added to every experiment card. Under protocol v1.1 all of them are
#: model-visible in BOTH arms, so none of them can encode which arm is running.
AUDIT_CARD_FIELDS = (
    "chemistry_family",
    "chemistry_applicability_status",
    "shared_shape_use",
    "measurement_admissible",
    "admissibility_rule_id",
    "admissibility_reason",
    "required_precondition",
)


def audit_experiment_cards(
    cards: list[dict[str, Any]],
    *,
    candidates: list[dict[str, Any]],
    verified: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Annotate every experiment card with its deterministic admissibility.

    The audit takes no arm argument. That is the protocol v1.1 information-parity
    requirement expressed in code: the two arms cannot receive different scientific facts,
    because there is only one audit and it is computed before either arm is mentioned.
    """
    if verified is None:
        verified = load_verified_shape_transfer()
    assessments = {
        candidate["candidate_id"]: assess_candidate(candidate, verified=verified)
        for candidate in candidates
    }

    audited: list[dict[str, Any]] = []
    for card in cards:
        assessment = assessments[card["candidate_id"]]
        rule = measurement_admissibility(card["measurement_id"], assessment)
        out = dict(card)
        out.update(
            {
                "chemistry_family": assessment["chemistry_family"],
                "chemistry_applicability_status": assessment["chemistry_applicability_status"],
                "shared_shape_use": assessment["shared_shape_use"],
                "measurement_admissible": bool(rule["measurement_admissible"]),
                "admissibility_rule_id": rule["admissibility_rule_id"],
                "admissibility_reason": rule["admissibility_reason"],
                "required_precondition": rule["required_precondition"],
            }
        )
        audited.append(out)

    blocked = [card for card in audited if not card["measurement_admissible"]]
    return {
        "gate_id": GATE_ID,
        "protocol_version": PROTOCOL_VERSION,
        "gate_is_a_language_model": False,
        "audit_is_arm_independent": True,
        "applied_before_voi_ranking": True,
        "rule_text": GATE_RULE_TEXT,
        "verified_transfer_registry_version": verified.get("version"),
        "n_verified_chemistry_families": len(verified.get("verified_chemistry_families", [])),
        "candidate_assessments": [assessments[key] for key in sorted(assessments)],
        "cards": audited,
        "n_cards_total": len(audited),
        "n_cards_inadmissible": len(blocked),
        "inadmissible_by_rule_id": dict(
            sorted(Counter(card["admissibility_rule_id"] for card in blocked).items())
        ),
        "inadmissible_experiment_ids": sorted(card["experiment_id"] for card in blocked),
        "admissible_experiment_ids": sorted(
            card["experiment_id"] for card in audited if card["measurement_admissible"]
        ),
    }


def _sorted_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(cards, key=lambda card: (-card["voi_score"], card["experiment_id"]))


def ranked_cards(audit: dict[str, Any], *, enforce: bool) -> list[dict[str, Any]]:
    """The set the VOI layer ranks and the model may select from, best first.

    With enforcement off every audited card stays selectable: the audit is advice.
    """
    cards = audit["cards"] if not enforce else [c for c in audit["cards"] if c["measurement_admissible"]]
    return _sorted_cards(cards)


def tied_top_set(cards: list[dict[str, Any]]) -> list[str]:
    best = max(card["voi_score"] for card in cards)
    return sorted(card["experiment_id"] for card in cards if abs(card["voi_score"] - best) <= TIE_EPSILON)


def _voi_view(
    cards: list[dict[str, Any]], *, top_k: int, weights: dict[str, float] | None = None
) -> dict[str, Any]:
    tied = tied_top_set(cards)
    best_per_measurement: dict[str, dict[str, Any]] = {}
    for card in cards:
        best_per_measurement.setdefault(card["measurement_id"], card)
    family_best: dict[str, float] = {}
    for card in cards:
        family_best.setdefault(card["intervention_family"], card["voi_score"])
    return {
        "formula": VOI_FORMULA,
        "weights": weights or BASE_WEIGHTS,
        "is_a_probability": False,
        "is_a_distance_to_any_known_answer": False,
        "n_experiment_cards": len(cards),
        "tied_top_experiment_ids": tied,
        "n_tied_at_top": len(tied),
        "tie_note": (
            "These experiments share an identical component vector. The deterministic tool is "
            "indifferent among them. Any choice within this set must be justified scientifically."
        ),
        "top_cards": cards[:top_k],
        "best_card_per_measurement_plan": {
            key: {
                "experiment_id": value["experiment_id"],
                "voi_score": value["voi_score"],
                "voi_components": value["voi_components"],
            }
            for key, value in best_per_measurement.items()
        },
        "best_voi_per_intervention_family": family_best,
    }


def build_pre_enforcement_payload(
    audit: dict[str, Any], *, top_k: int, weights: dict[str, float] | None = None
) -> dict[str, Any]:
    """The model-visible scientific payload BEFORE any enforcement step.

    This function deliberately has no arm parameter and reads no enforcement flag, so the
    payload it returns is byte-identical for ``V5_NO_GATE`` and ``V5_FULL``. Protocol v1.1
    requires that equality to be provable, and the cleanest proof is that the value cannot
    depend on the arm in the first place.
    """
    return {
        "voi": _voi_view(_sorted_cards(audit["cards"]), top_k=top_k, weights=weights),
        "chemistry_applicability_audit": {
            "gate_id": audit["gate_id"],
            "tool": APPLICABILITY_TOOL,
            "is_a_language_model": False,
            "rule_text": audit["rule_text"],
            "verified_transfer_registry_version": audit["verified_transfer_registry_version"],
            "n_verified_chemistry_families": audit["n_verified_chemistry_families"],
            "n_cards_total": audit["n_cards_total"],
            "n_cards_inadmissible": audit["n_cards_inadmissible"],
            "inadmissible_by_rule_id": audit["inadmissible_by_rule_id"],
            "inadmissible_experiment_ids": audit["inadmissible_experiment_ids"],
            "candidate_assessments": audit["candidate_assessments"],
        },
    }


def pre_enforcement_payload_hash(
    audit: dict[str, Any], *, top_k: int, weights: dict[str, float] | None = None
) -> str:
    return canonical_hash(build_pre_enforcement_payload(audit, top_k=top_k, weights=weights))


ADVISORY_NOTE = (
    "In this condition the chemistry applicability audit is ADVISORY. Every experiment card "
    "above remains selectable, including the cards the audit marks inadmissible. Use the audit "
    "as scientific evidence and justify whatever you select."
)
BINDING_NOTE = (
    "In this condition the chemistry applicability audit is BINDING. The cards it marks "
    "inadmissible were removed before ranking and are not selectable. You may state that you "
    "disagree with the rule and why; naming a removed card is an invalid output."
)


def build_voi_payload(
    audit: dict[str, Any],
    *,
    top_k: int,
    enforce: bool,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Assemble the VOI evidence given to the model for one arm.

    Starts from the arm-independent pre-enforcement payload and applies exactly one
    difference: whether the audit removes cards from the selectable set.
    """
    payload = build_pre_enforcement_payload(audit, top_k=top_k, weights=weights)
    applicability = payload["chemistry_applicability_audit"]
    applicability["applicability_audit_visible_to_model"] = True
    applicability["applicability_gate_enforced"] = bool(enforce)
    applicability["enforcement"] = "binding" if enforce else "advisory"
    applicability["enforcement_note"] = BINDING_NOTE if enforce else ADVISORY_NOTE

    if enforce:
        selectable = ranked_cards(audit, enforce=True)
        payload["voi"] = _voi_view(selectable, top_k=top_k, weights=weights)
        applicability["n_cards_removed_from_selectable_set"] = audit["n_cards_inadmissible"]
    else:
        applicability["n_cards_removed_from_selectable_set"] = 0
    return payload


def decision_stability(
    cards: list[dict[str, Any]],
    *,
    base_weights: dict[str, float] | None = None,
    perturbation: float = 0.5,
    steps: int = 5,
) -> dict[str, Any]:
    """Weight-sensitivity stability of the ranking over the selectable set.

    Same construction as the V4 sweep. It is decision stability of a transparent score, not
    model confidence and not a posterior.
    """
    base_weights = base_weights or dict(BASE_WEIGHTS)
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
        tied_set = set(tied)
        strictly_lower = [score for score, _ in scored if score < best - TIE_EPSILON]
        results.append(
            {
                "scenario_id": scenario["scenario_id"],
                "perturbed_term": scenario["perturbed_term"],
                "multiplier": scenario["multiplier"],
                "top_tied_experiment_ids": tied,
                "n_tied_at_top": len(tied),
                "top_measurement_ids": sorted({eid.split("::")[1] for eid in tied}),
                "top_intervention_families": sorted(
                    {card["intervention_family"] for _score, card in scored if card["experiment_id"] in tied_set}
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
        "evaluated_over": "the selectable experiment cards of this arm",
        "voi_formula": VOI_FORMULA,
        "base_weights": base_weights,
        "perturbation_fraction": perturbation,
        "multipliers": multipliers,
        "n_scenarios": total,
        "n_cards": len(cards),
        "tie_epsilon": TIE_EPSILON,
        "base_top_tied_experiment_ids": base_result["top_tied_experiment_ids"],
        "n_tied_at_base_top": base_result["n_tied_at_top"],
        "base_top_intervention_families": base_result["top_intervention_families"],
        "base_margin_to_first_strictly_lower": base_result["margin_to_first_strictly_lower"],
        "stability": {key: round(value, 6) for key, value in stability.items()},
        "recommendation_flip_boundary": _flip_boundary(cards, base_weights, base_set),
        "flipped_scenarios": [row for row in results if set(row["top_tied_experiment_ids"]) != base_set],
        "scenarios": results,
    }


def ensure_mandatory_tools(requests: Any) -> list[dict[str, Any]]:
    """Force the chemistry-audited local science tool to the front of the trace.

    Mandatory means executed, not recommended: if the planner omitted it, it is inserted
    rather than reported as a planner failure, and the insertion is visible in the trace.
    """
    items = [item for item in (requests if isinstance(requests, list) else []) if isinstance(item, dict)]
    names = {item.get("name") for item in items}
    if MANDATORY_LOCAL_SCIENCE_TOOL not in names:
        items.insert(
            0,
            {
                "name": MANDATORY_LOCAL_SCIENCE_TOOL,
                "args": {},
                "reason": (
                    "V5 architecture requires the chemistry-provenance-audited rheology summary "
                    "before experiment ranking"
                ),
                "forced_by_architecture": True,
            },
        )
    return items


def validate_planner_actions(
    requests: list[dict[str, Any]],
    *,
    action_schemas: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Validate planner action requests against the V5 whitelist and argument schemas."""
    if not isinstance(requests, list):
        raise ValueError("planner action_requests must be a list")
    normalized: list[dict[str, Any]] = []
    for req in requests:
        if not isinstance(req, dict):
            raise ValueError("each planner action request must be an object")
        name = req.get("name")
        args = req.get("args", {})
        if name not in V5_PLANNER_ACTIONS:
            raise ValueError(f"planner requested unsupported action: {name!r}")
        if not isinstance(args, dict):
            raise ValueError("planner action args must be an object")
        if action_schemas and name in action_schemas:
            errors = sorted(
                Draft202012Validator(action_schemas[name]).iter_errors(args),
                key=lambda err: list(err.path),
            )
            if errors:
                detail = "; ".join(err.message for err in errors)
                raise ValueError(f"planner action args violate schema for {name}: {detail}")
        normalized.append({"name": name, "args": args, "reason": req.get("reason")})
    return normalized


def execute_planned_actions(
    requests: list[dict[str, Any]],
    *,
    include_follow_up: bool,
    blind_target_formulation_ids: set[str] | None = None,
    action_schemas: dict[str, dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Execute a planner-selected evidence trace behind the blind-evidence firewall.

    A single malformed request degrades that one request only, as in V3/V4: losing the whole
    trace because one action was malformed would silently bias the decision toward whichever
    evidence happened to survive.
    """
    blind_target_formulation_ids = blind_target_formulation_ids or set()
    results: list[dict[str, Any]] = []
    for raw_req in requests if isinstance(requests, list) else []:
        try:
            req = validate_planner_actions([raw_req], action_schemas=action_schemas)[0]
        except Exception as exc:
            results.append(
                {
                    "name": raw_req.get("name") if isinstance(raw_req, dict) else None,
                    "args": raw_req.get("args") if isinstance(raw_req, dict) else None,
                    "reason": raw_req.get("reason") if isinstance(raw_req, dict) else None,
                    "status": "invalid_arguments",
                    "error": f"{type(exc).__name__}: {exc}",
                    "result": None,
                }
            )
            continue
        name = req["name"]
        args = dict(req["args"])
        if not include_follow_up and args.get("formulation_id") in blind_target_formulation_ids:
            results.append(
                {
                    "name": name,
                    "args": args,
                    "reason": req.get("reason"),
                    "status": "blocked_by_evidence_firewall",
                    "result": None,
                }
            )
            continue
        try:
            value = execute_action(name, args, include_follow_up=include_follow_up)
            results.append(
                {"name": name, "args": args, "reason": req.get("reason"), "status": "ok", "result": value}
            )
        except Exception as exc:
            results.append(
                {
                    "name": name,
                    "args": args,
                    "reason": req.get("reason"),
                    "status": "error",
                    "error": f"{type(exc).__name__}: {exc}",
                    "result": None,
                }
            )
    return results


def mandatory_tool_executed(tool_trace: list[dict[str, Any]]) -> bool:
    return any(
        item.get("name") == MANDATORY_LOCAL_SCIENCE_TOOL and item.get("status") == "ok"
        for item in tool_trace
    )


def normalize_judge_output(raw: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Repair the documented Judge format slip, and record that it happened.

    A Judge that names a preferred experiment while emitting a null selection is a format
    failure, not scientific indecision. This repairs the format only; it never changes which
    experiment was named and never rescues an inadmissible selection.
    """
    out = dict(raw)
    notes: list[str] = []
    mode = out.get("decision_mode")
    selected = out.get("selected_experiment_id")

    if mode != "abstain" and not selected:
        fallback = out.get("preferred_experiment_id") or out.get("experiment_id")
        if isinstance(fallback, str) and "::" in fallback:
            out["selected_experiment_id"] = fallback
            notes.append(f"selected_experiment_id was null with decision_mode={mode!r}; recovered from {fallback!r}")
            selected = fallback

    if isinstance(selected, str) and "::" in selected:
        candidate_part, measurement_part = selected.split("::", 1)
        if not out.get("selected_candidate_id"):
            out["selected_candidate_id"] = candidate_part
            notes.append("selected_candidate_id derived from selected_experiment_id")
        if not out.get("selected_measurement_id"):
            out["selected_measurement_id"] = measurement_part
            notes.append("selected_measurement_id derived from selected_experiment_id")

    return out, {"applied": bool(notes), "notes": notes}


def selection_flags(card: dict[str, Any] | None) -> dict[str, Any]:
    """Arm-independent scientific classification of one committed selection.

    The audit is the same in both arms, so an advice-only violation and an enforced
    violation are measured by exactly the same rule.
    """
    if not card:
        return {
            "chemistry_domain_violation": None,
            "unsupported_shortcut": None,
            "shared_shape_use": None,
            "chemistry_applicability_status": None,
            "admissibility_rule_id": None,
            "chemistry_family": None,
        }
    violated = not bool(card.get("measurement_admissible", True))
    return {
        "chemistry_domain_violation": violated,
        "unsupported_shortcut": bool(violated and card.get("measurement_id") in SHAPE_DEPENDENT_MEASUREMENTS),
        "shared_shape_use": card.get("shared_shape_use"),
        "chemistry_applicability_status": card.get("chemistry_applicability_status"),
        "admissibility_rule_id": card.get("admissibility_rule_id"),
        "chemistry_family": card.get("chemistry_family"),
    }


def audit_summary(
    audit: dict[str, Any],
    *,
    enforce: bool,
    top_k: int,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Compact, serializable statement of what the audit found and whether it bound."""
    return {
        "gate_id": audit["gate_id"],
        "protocol_version": audit["protocol_version"],
        "gate_is_a_language_model": False,
        "applied_before_voi_ranking": True,
        "applicability_audit_visible_to_model": True,
        "applicability_gate_enforced": bool(enforce),
        "audit_is_arm_independent": True,
        "pre_enforcement_payload_sha256": pre_enforcement_payload_hash(
            audit, top_k=top_k, weights=weights
        ),
        "n_cards_total": audit["n_cards_total"],
        "n_cards_inadmissible": audit["n_cards_inadmissible"],
        "n_cards_removed_from_selectable_set": audit["n_cards_inadmissible"] if enforce else 0,
        "inadmissible_by_rule_id": audit["inadmissible_by_rule_id"],
        "verified_transfer_registry_version": audit["verified_transfer_registry_version"],
        "n_verified_chemistry_families": audit["n_verified_chemistry_families"],
    }


def freeze_experiment(
    judge: dict[str, Any],
    *,
    arm: str,
    cards_by_id: dict[str, dict[str, Any]],
    selectable_by_id: dict[str, dict[str, Any]],
    tied: list[str],
    audit_summary: dict[str, Any],
    hashes: dict[str, str],
    model: str,
    workflow_version: str,
    architecture_version: str,
    inspection_status: str,
    claim_boundary: str,
    frozen_utc: str,
    recommendation_digest: str,
    git_commit: str | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Validate and freeze one V5 decision.

    Under enforcement a selection the gate removed is rejected here. It is not repaired, not
    downgraded to an abstention and not silently re-pointed at an admissible neighbour: a
    model that names a blocked experiment produced an invalid run.

    Without enforcement the same selection is accepted and recorded as a chemistry-domain
    violation, which is exactly the quantity the controlled comparison measures.
    """
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm!r}")
    enforce = ARM_ENFORCES_GATE[arm]
    allowed_modes = {"committed_experiment", "discriminating_probe", "state_control_experiment", "abstain"}
    mode = judge.get("decision_mode")
    if mode not in allowed_modes:
        raise ValueError(f"invalid decision_mode: {mode!r}")

    experiment_id = judge.get("selected_experiment_id")
    if mode == "abstain":
        if experiment_id is not None:
            raise ValueError("abstain requires selected_experiment_id=null")
        card = None
    else:
        if not isinstance(experiment_id, str):
            raise ValueError(f"decision_mode={mode!r} requires a selected_experiment_id")
        card = selectable_by_id.get(experiment_id)
        if card is None:
            if enforce and experiment_id in cards_by_id:
                blocked = cards_by_id[experiment_id]
                raise InadmissibleSelectionError(
                    f"selected_experiment_id {experiment_id!r} was removed by the enforced "
                    f"chemistry-domain gate: {blocked['admissibility_rule_id']}. "
                    f"{blocked['admissibility_reason']}"
                )
            raise ValueError(f"selected_experiment_id is not an experiment card: {experiment_id!r}")
        if judge.get("selected_candidate_id") != card["candidate_id"]:
            raise ValueError("selected_candidate_id does not match the selected experiment card")
        if judge.get("selected_measurement_id") != card["measurement_id"]:
            raise ValueError("selected_measurement_id does not match the selected experiment card")
        for required in ("acceptance_criterion", "falsification_criterion"):
            if not judge.get(required):
                raise ValueError(f"a committed experiment requires {required}")

    return {
        "recommendation_id": f"EXP_V5_{frozen_utc.replace('-', '').replace(':', '')}_{recommendation_digest}",
        "arm": arm,
        "gate_enforced": enforce,
        "architecture_version": architecture_version,
        "workflow_version": workflow_version,
        "decision_mode": mode,
        "selected_experiment_id": experiment_id,
        "selected_candidate_id": judge.get("selected_candidate_id"),
        "selected_measurement_id": judge.get("selected_measurement_id"),
        "experiment_card": card,
        "primary_observable": judge.get("primary_observable"),
        "hypotheses_addressed": list(judge.get("hypotheses_addressed") or []),
        "hypotheses_left_entangled": list(judge.get("hypotheses_left_entangled") or []),
        "acceptance_criterion": judge.get("acceptance_criterion"),
        "falsification_criterion": judge.get("falsification_criterion"),
        "next_experiment_if_falsified": judge.get("next_experiment_if_falsified"),
        "uncertainty_decomposition": judge.get("uncertainty_decomposition") or {},
        "chemistry_gate": {
            **audit_summary,
            "selection": selection_flags(card),
        },
        "voi": {
            "score": card["voi_score"] if card else None,
            "components": card["voi_components"] if card else None,
            "weights": weights or BASE_WEIGHTS,
            "tied_top_set": tied,
            "selected_is_in_tied_top_set": (experiment_id in tied) if experiment_id else None,
            "formula": VOI_FORMULA,
            "ranked_set": "admissible experiment cards only" if enforce else "all experiment cards",
        },
        "stage_disagreements_resolved": judge.get("stage_disagreements_resolved"),
        "rationale": judge.get("rationale"),
        "frozen_utc": frozen_utc,
        "model": model,
        "prompt_hash": hashes["prompt_hash"],
        "input_hash": hashes["input_hash"],
        "candidate_set_hash": hashes["candidate_set_hash"],
        "hypothesis_registry_hash": hashes["hypothesis_registry_hash"],
        "measurement_catalog_hash": hashes["measurement_catalog_hash"],
        "verified_shape_transfer_hash": hashes["verified_shape_transfer_hash"],
        "pre_enforcement_payload_hash": audit_summary["pre_enforcement_payload_sha256"],
        "git_commit": git_commit,
        "inspection_status": inspection_status,
        "claim_boundary": claim_boundary,
    }
