from __future__ import annotations

from typing import Any


_LOCAL_REACTIVE_COMPONENTS = {"ppg2000", "pdp70", "mdi"}
_MODIFIER_ALIASES = {"ac1920", "tk100"}


def _canonical_formulation_state(candidate: dict[str, Any]) -> dict[str, float]:
    fs = candidate.get("formulation_state", candidate)
    aliases = {
        "ppg2000": ("ppg2000", "PPG2000"),
        "pdp70": ("pdp70", "PDP70", "STEPANPOL PDP-70", "stepanpol_pdp70"),
        "ac1920": ("ac1920", "AC1920"),
        "tk100": ("tk100", "TK100"),
        "mdi": ("mdi", "MDI", "4,4'-MDI", "44MDI"),
    }
    out: dict[str, float] = {}
    for canonical, keys in aliases.items():
        raw = next((fs[k] for k in keys if k in fs and fs[k] is not None), 0.0)
        out[canonical] = float(raw or 0.0)
    return out


def assess_shared_shape_applicability(candidate: dict[str, Any]) -> dict[str, Any]:
    """Check whether the local shared thermal-response shape may be used as an interpolation prior.

    This is a scientific-boundary tool, not a property predictor. The shared shape was
    established only for the unmodified PPG2000/PDP70/MDI local family. Any active resin
    modifier moves the candidate outside that validated chemistry family and therefore
    requires direct verification before the local curve shape can be reused.
    """
    amounts = _canonical_formulation_state(candidate)
    total = sum(amounts.values())
    if total <= 0:
        return {
            "status": "insufficient_composition",
            "shared_shape_use": "not_allowed",
            "reason": "No recognized PPG2000/PDP70/MDI/AC1920/TK100 composition was supplied.",
            "recommended_measurement": "M-SWEEP",
        }

    active = {name for name, value in amounts.items() if value > 0}
    modifier_fraction = (amounts["ac1920"] + amounts["tk100"]) / total
    core_fraction = (amounts["ppg2000"] + amounts["pdp70"] + amounts["mdi"]) / total

    if active & _MODIFIER_ALIASES:
        return {
            "status": "modified_chemistry_unvalidated",
            "shared_shape_use": "verification_only",
            "reason": (
                "The local shared thermal-response shape was measured only in the unmodified "
                "PPG2000/PDP70/MDI family. Resin-modified chemistry is outside that validated support."
            ),
            "modifier_fraction": modifier_fraction,
            "reactive_core_fraction": core_fraction,
            "recommended_measurement": "M-SWEEP",
            "allowed_shortcut": (
                "A one-point anchor may be used only as a provisional prediction if the prediction is "
                "then checked against at least one additional directly measured temperature."
            ),
        }

    if active <= _LOCAL_REACTIVE_COMPONENTS and amounts["ppg2000"] > 0 and amounts["pdp70"] > 0 and amounts["mdi"] > 0:
        return {
            "status": "local_family_interpolation",
            "shared_shape_use": "allowed_with_state_anchor",
            "reason": (
                "Candidate remains inside the measured unmodified PPG2000/PDP70/MDI chemistry family. "
                "A state-specific viscosity anchor is therefore an evidence-supported local interpolation prior."
            ),
            "modifier_fraction": 0.0,
            "reactive_core_fraction": 1.0,
            "recommended_measurement": "M-ANCHOR",
        }

    return {
        "status": "chemistry_support_unknown",
        "shared_shape_use": "not_allowed",
        "reason": "Recognized composition does not map cleanly to the measured local chemistry family.",
        "modifier_fraction": modifier_fraction,
        "reactive_core_fraction": core_fraction,
        "recommended_measurement": "M-SWEEP",
    }
