from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "analysis" / "results"


def _read_csv(name: str) -> list[dict[str, str]]:
    with (RESULTS / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _read_json(name: str) -> dict[str, Any]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def _float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def get_state_aware_rheology_summary_v3() -> dict[str, Any]:
    """Return the paper's upstream rheology findings as an auditable scientific tool.

    The output is intentionally restricted to patterns derived from the original local
    temperature sweeps and original E1/E5 hold trajectories. The validation formulation
    F1 and its outcome are never returned.
    """
    model_rows = {r["model"]: r for r in _read_csv("local_model_comparison.csv")}
    validation_rows = _read_csv("local_validation.csv")
    thermal_rows = _read_csv("local_thermal_curve_fits.csv")
    hold_rows = [
        r for r in _read_csv("local_hold_dynamics.csv")
        if r["formulation_id"] in {"E1", "E5"}
    ]

    m0 = model_rows["M0_formulation_only"]
    m2q = model_rows["M2q_state_intercept_shared_quadratic"]

    loo_temp = {
        r["model"]: r
        for r in validation_rows
        if r["validation_type"] == "leave_one_temperature_out"
    }
    anchor_rows = [
        r for r in validation_rows
        if r["validation_type"] == "leave_one_realization_out_one_point_anchor"
    ]

    thermal_E = [_float(r, "apparent_E_kJ_mol") for r in thermal_rows]
    thermal_r2 = [_float(r, "r2") for r in thermal_rows]
    mean_E = sum(thermal_E) / len(thermal_E)
    if len(thermal_E) > 1:
        mean_sq = sum((x - mean_E) ** 2 for x in thermal_E) / (len(thermal_E) - 1)
        sd_E = mean_sq ** 0.5
    else:
        sd_E = 0.0

    hold = {
        r["formulation_id"]: {
            "linear_lneta_slope_per_h": _float(r, "linear_lneta_slope_per_h"),
            "linear_lneta_r2": _float(r, "linear_lneta_r2"),
            "endpoint_si": _float(r, "SI_endpoint"),
            "time_start_min": _float(r, "time_start_min"),
            "time_end_min": _float(r, "time_end_min"),
        }
        for r in hold_rows
    }
    drift_ratio = (
        hold["E5"]["linear_lneta_slope_per_h"]
        / hold["E1"]["linear_lneta_slope_per_h"]
    )

    anchor_factors = [_float(r, "multiplicative_error_factor") for r in anchor_rows]
    best_anchor = min(anchor_rows, key=lambda r: _float(r, "multiplicative_error_factor"))

    formulation_cv = _float(loo_temp["M0_formulation_only"], "multiplicative_error_factor")
    state_cv = _float(loo_temp["M2q_state_intercept_shared_quadratic"], "multiplicative_error_factor")

    return {
        "tool_name": "get_state_aware_rheology_summary",
        "tool_version": "3.2",
        "source_scope": "original pre-validation local measurements and derived analyses only",
        "validation_formulation_visible": False,
        "discovered_patterns": {
            "state_shift_master_curve": {
                "formulation_only_r2": _float(m0, "r2"),
                "state_aware_shared_shape_r2": _float(m2q, "r2"),
                "held_temperature_formulation_only_error_factor": formulation_cv,
                "held_temperature_state_aware_error_factor": state_cv,
                "held_temperature_log_rmse_reduction_fraction": 1.0
                - _float(loo_temp["M2q_state_intercept_shared_quadratic"], "rmse_log")
                / _float(loo_temp["M0_formulation_only"], "rmse_log"),
                "positive_model": "ln(eta_r(T)) = alpha_r + g(T) + epsilon",
                "interpretation": (
                    "Within the measured local chemistry family, realization/process state primarily shifts the viscosity scale while a common thermal-response shape remains transferable."
                ),
            },
            "one_point_state_calibration": {
                "multiplicative_error_factor_range": [min(anchor_factors), max(anchor_factors)],
                "best_observed_anchor_temperature_c": _float(best_anchor, "anchor_temperature_c"),
                "best_observed_error_factor": _float(best_anchor, "multiplicative_error_factor"),
                "interpretation": (
                    "A single state-specific viscosity anchor can calibrate the remaining measured temperature curve to roughly 6-9% multiplicative error in the current local dataset."
                ),
            },
            "thermal_coordinate": {
                "mean_apparent_E_eta_kJ_mol": mean_E,
                "sd_apparent_E_eta_kJ_mol": sd_E,
                "cv_apparent_E_eta": sd_E / mean_E if mean_E else None,
                "median_like_curve_fit_quality": sorted(thermal_r2)[len(thermal_r2) // 2],
                "interpretation": (
                    "The apparent temperature-sensitivity descriptor is comparatively concentrated within the local chemistry family; it is not a molecular reaction activation energy."
                ),
            },
            "temporal_stability_coordinate": {
                "E1": hold["E1"],
                "E5": hold["E5"],
                "E5_to_E1_drift_coefficient_ratio": drift_ratio,
                "interpretation": (
                    "Thermal-hold viscosity drift is strongly formulation dependent and should be treated as a distinct design response rather than inferred from static viscosity alone."
                ),
            },
        },
        "design_rules": [
            "Represent a candidate as formulation plus process/realization state, not composition alone.",
            "Use one state-specific anchor measurement to locate a new realization on the transferable local temperature-response shape when the chemistry remains inside the supported local family.",
            "Treat static viscosity, temperature response and thermal-hold stability as separate decision variables.",
            "When the failure mode is hot-hold drift, prefer experiment points that directly test drift rather than only matching one nominal viscosity value.",
            "Use external resin/tackifier evidence to define chemically plausible directions, but do not convert analogue proximity into a predicted local outcome.",
        ],
        "experiment_design_implications": {
            "state_anchor": (
                "For efficient temperature-curve calibration, the current leave-one-realization analysis found its smallest error at 110 C; 120 C remains operationally useful because it aligns with the hold-stability experiment."
            ),
            "hold_window": (
                "For the current local study, 120 C and a matched 15-60 min window directly interrogate the design failure mode and allow comparison with original references."
            ),
            "selection_target": (
                "Choose a formulation-process point that is scientifically informative about the observed instability, not merely the numerically closest static-viscosity candidate."
            ),
        },
        "claim_boundaries": [
            "The state-shift structure is established only for the measured local chemistry family.",
            "The apparent E_eta descriptor is rheological, not a chemical reaction activation energy.",
            "E1/E5 hold trajectories establish a large effect size but do not by themselves identify a molecular mechanism.",
            "No validation-formulation result is used in this tool output.",
        ],
    }
