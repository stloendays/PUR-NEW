"""One-shot source patch: add condition-aware scoring seams to src/pur_new/voi.py.

Kept in the repository as provenance for exactly what changed when Condition B was
added. Every replacement is anchored and asserted, so a silent partial patch is
impossible. Re-running it on an already patched tree fails loudly rather than
double-applying.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "src" / "pur_new" / "voi.py"

source = TARGET.read_text(encoding="utf-8")
before = len(source)


def sub(old: str, new: str, label: str) -> None:
    global source
    found = source.count(old)
    if found != 1:
        raise SystemExit(f"ANCHOR FAIL [{label}]: found {found} occurrences, expected 1")
    source = source.replace(old, new)
    print(f"ok  {label}")


# ------------------------------------------------------------------ 1. score_components
sub(
    '''def score_components(components: dict[str, float], weights: dict[str, float]) -> float:
    positive = sum(weights[key] * components[key] for key in POSITIVE_TERMS)
    penalty = sum(weights[key] * components[key] for key in RISK_TERMS)
    return positive - penalty''',
    '''def score_components(components: dict[str, float], weights: dict[str, float]) -> float:
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
    return total''',
    "score_components",
)

# ------------------------------------------------------------- 2. level prediction rules
sub(
    "def hypothesis_discrimination(",
    '''#: Prediction rules whose observable is the realized viscosity LEVEL rather than the
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


def hypothesis_discrimination(''',
    "level prediction helpers",
)

# --------------------------------------------------- 3. quantity-aware discrimination body
sub(
    '''    hypotheses = registry["hypotheses"]
    pairs = list(combinations(hypotheses, 2))
    if not pairs:
        return {"score": 0.0, "separated_pairs": [], "n_pairs": 0}

    if "thermal_hold_drift" not in measurement.get("addresses", []):''',
    '''    hypotheses = registry["hypotheses"]
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

    if "thermal_hold_drift" not in measurement.get("addresses", []):''',
    "quantity-aware discrimination",
)

# ------------------------------------------------------------------ 4. budget efficiency
sub(
    "def extrapolation_risk(candidate: dict[str, Any], priors: dict[str, Any]) -> dict[str, Any]:",
    '''def catalog_effort_scale(catalog: dict[str, Any]) -> float | None:
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


def extrapolation_risk(candidate: dict[str, Any], priors: dict[str, Any]) -> dict[str, Any]:''',
    "budget efficiency",
)

# ------------------------------------------------- 5. wire budget into card construction
sub(
    '''    supported_axes = independently_supported_axes()
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])''',
    '''    supported_axes = independently_supported_axes()
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    effort_scale = catalog_effort_scale(catalog)''',
    "effort scale",
)

sub(
    '''            components = {
                "hypothesis_discrimination": disc["score"],
                "uncertainty_reduction": unc["score"],
                "decision_relevance": dec["score"],
                "measurement_interpretability": float(measurement["interpretability"]),
                "extrapolation_risk": ext["score"],
                "process_state_risk": proc["score"],
            }''',
    '''            components = {
                "hypothesis_discrimination": disc["score"],
                "uncertainty_reduction": unc["score"],
                "decision_relevance": dec["score"],
                "measurement_interpretability": float(measurement["interpretability"]),
                "extrapolation_risk": ext["score"],
                "process_state_risk": proc["score"],
            }
            budget = budget_efficiency(measurement, effort_scale) if effort_scale else None
            if budget is not None:
                components["budget_efficiency"] = budget["score"]''',
    "budget component",
)

sub(
    '''                    "extrapolation_risk_detail": ext,
                    "process_state_risk_detail": proc,''',
    '''                    "extrapolation_risk_detail": ext,
                    "process_state_risk_detail": proc,
                    "budget_efficiency_detail": budget,''',
    "budget detail",
)

# --------------------------------------------------------- 6. condition-aware criteria
sub(
    '''                    "acceptance_criterion": _acceptance_criterion(measurement, phi_r, reference),
                    "falsification_criterion": _falsification_criterion(
                        measurement, phi_r, reference, tackifier
                    ),''',
    '''                    "acceptance_criterion": _acceptance_criterion(
                        measurement, phi_r, reference, registry=registry, candidate=candidate
                    ),
                    "falsification_criterion": _falsification_criterion(
                        measurement, phi_r, reference, tackifier, registry=registry, candidate=candidate
                    ),''',
    "criteria call",
)

TARGET.write_text(source, encoding="utf-8")
print(f"voi.py patched: {before} -> {len(source)} bytes")
