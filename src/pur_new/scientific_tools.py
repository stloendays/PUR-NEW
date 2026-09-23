from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
R_GAS = 8.314462618
T_REF_K = 393.15


def _rmse(values) -> float:
    arr = np.asarray(values, dtype=float)
    return float(np.sqrt(np.mean(arr * arr)))


def _prepare_audited_temperature_data() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "temperature_sweeps.csv")
    meta = pd.read_csv(ROOT / "data" / "realization_metadata.csv")
    df["temperature_c"] = pd.to_numeric(df["temperature_c"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["retest_after_1d"] = df["retest_after_1d"].astype(str).str.lower().map({"true": True, "false": False})
    if df["retest_after_1d"].isna().any():
        raise ValueError("Unexpected retest_after_1d value")
    df["dx"] = 1000.0 / (df["temperature_c"] + 273.15) - 1000.0 / T_REF_K
    df["ln_eta"] = np.log(df["viscosity_reported"])
    df["realization_id"] = df.apply(
        lambda r: f"{r['formulation_id']}__{r['run_label']}__day1_{int(r['retest_after_1d'])}", axis=1
    )
    df = df.merge(
        meta[["realization_id", "analysis_role", "chemistry_comparability"]],
        on="realization_id",
        how="left",
        validate="many_to_one",
    )
    if df["analysis_role"].isna().any():
        missing = sorted(df.loc[df["analysis_role"].isna(), "realization_id"].unique())
        raise ValueError(f"Missing realization metadata: {missing}")
    primary_roles = {"primary", "primary_with_caveat"}
    return df[df["analysis_role"].isin(primary_roles)].copy()


def _model_and_cv(df: pd.DataFrame, formula: str) -> dict[str, float]:
    model = smf.ols(formula, df).fit()
    observed, predicted = [], []
    for temp in sorted(df["temperature_c"].unique()):
        train = df[df["temperature_c"] != temp]
        test = df[df["temperature_c"] == temp]
        fitted = smf.ols(formula, train).fit()
        observed.extend(test["ln_eta"].tolist())
        predicted.extend(fitted.predict(test).tolist())
    cv_rmse = _rmse(np.asarray(observed) - np.asarray(predicted))
    return {
        "r2": float(model.rsquared),
        "aic": float(model.aic),
        "bic": float(model.bic),
        "held_temperature_multiplicative_error": math.exp(cv_rmse),
    }


def _leave_one_formulation_one_point(df: pd.DataFrame) -> tuple[list[dict[str, Any]], list[float]]:
    rows: list[dict[str, Any]] = []
    all_errors_by_anchor: dict[float, list[float]] = {float(t): [] for t in sorted(df["temperature_c"].unique())}
    for held_formulation in sorted(df["formulation_id"].unique()):
        train = df[df["formulation_id"] != held_formulation]
        held_all = df[df["formulation_id"] == held_formulation]
        shape = smf.ols("ln_eta ~ C(realization_id) + dx + I(dx**2)", train).fit()
        beta1 = float(shape.params["dx"])
        beta2 = float(shape.params["I(dx ** 2)"])
        for anchor_temp in sorted(df["temperature_c"].unique()):
            errors = []
            n_realizations = 0
            for _rid, held in held_all.groupby("realization_id"):
                anchor = held[held["temperature_c"] == anchor_temp].iloc[0]
                test = held[held["temperature_c"] != anchor_temp]
                prediction = (
                    anchor["ln_eta"]
                    + beta1 * (test["dx"] - anchor["dx"])
                    + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
                )
                err = test["ln_eta"].to_numpy() - prediction.to_numpy()
                errors.extend(err.tolist())
                all_errors_by_anchor[float(anchor_temp)].extend(err.tolist())
                n_realizations += 1
            rows.append(
                {
                    "held_formulation": held_formulation,
                    "anchor_temperature_c": float(anchor_temp),
                    "n_held_realizations": n_realizations,
                    "multiplicative_error": math.exp(_rmse(errors)),
                }
            )
    pooled = [math.exp(_rmse(all_errors_by_anchor[t])) for t in sorted(all_errors_by_anchor)]
    return rows, pooled


def _same_formulation_anchor_gain(
    df: pd.DataFrame,
    anchor_temperature_c: float = 110.0,
    target_temperatures_c: tuple[float, ...] = (120.0, 130.0),
) -> dict[str, Any]:
    """Quantify information gained from one state anchor within repeated E2 realizations.

    This is deliberately a same-formulation holdout: E2 is the only audited nominal
    formulation with multiple realizations, so formulation identity is known from the
    remaining data while the held realization state is unknown.
    """
    formulation_id = "E2"
    held_ids = sorted(
        df.loc[df["formulation_id"] == formulation_id, "realization_id"].unique()
    )
    baseline_errors: list[float] = []
    anchor_errors: list[float] = []
    per_realization: list[dict[str, Any]] = []

    for held_id in held_ids:
        train = df[df["realization_id"] != held_id].copy()
        held = df[df["realization_id"] == held_id].copy()

        formulation_only = smf.ols(
            "ln_eta ~ C(formulation_id) + dx + I(dx**2)", data=train
        ).fit()
        state_shape = smf.ols(
            "ln_eta ~ C(realization_id) + dx + I(dx**2)", data=train
        ).fit()
        beta1 = float(state_shape.params["dx"])
        beta2 = float(state_shape.params["I(dx ** 2)"])

        anchor = held.loc[held["temperature_c"] == anchor_temperature_c].iloc[0]
        test = held[held["temperature_c"].isin(target_temperatures_c)].copy()
        baseline_pred = formulation_only.predict(test).to_numpy()
        state_pred = (
            anchor["ln_eta"]
            + beta1 * (test["dx"] - anchor["dx"])
            + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
        ).to_numpy()

        baseline_err = baseline_pred - test["ln_eta"].to_numpy()
        anchor_err = state_pred - test["ln_eta"].to_numpy()
        baseline_errors.extend(baseline_err.tolist())
        anchor_errors.extend(anchor_err.tolist())

        b = _rmse(baseline_err)
        a = _rmse(anchor_err)
        per_realization.append(
            {
                "held_realization": held_id,
                "formulation_only_multiplicative_error": math.exp(b),
                "one_anchor_multiplicative_error": math.exp(a),
                "log_rmse_reduction_fraction": 1.0 - a / b,
            }
        )

    baseline_rmse = _rmse(baseline_errors)
    anchor_rmse = _rmse(anchor_errors)
    return {
        "validation_scheme": (
            "leave one E2 realization out; formulation-only baseline uses the same "
            "quadratic thermal basis; one 110 C anchor supplies held-state information "
            "and predicts 120 and 130 C"
        ),
        "anchor_temperature_c": float(anchor_temperature_c),
        "target_temperatures_c": [float(x) for x in target_temperatures_c],
        "n_held_realizations": len(held_ids),
        "n_predictions": len(anchor_errors),
        "formulation_only_multiplicative_error": math.exp(baseline_rmse),
        "one_anchor_multiplicative_error": math.exp(anchor_rmse),
        "log_rmse_reduction_fraction": 1.0 - anchor_rmse / baseline_rmse,
        "per_realization": per_realization,
        "interpretation": (
            "Within repeated E2 realizations, formulation identity alone does not locate "
            "the realized viscosity level reliably. A single in-domain anchor supplies "
            "state information that sharply improves short-range reconstruction."
        ),
        "agent_implication": (
            "M-ANCHOR has measured value inside validated shared-shape support, but this "
            "result does not authorize the shortcut after a chemistry shift. Resin-modified "
            "or otherwise shifted chemistry requires direct M-SWEEP verification first."
        ),
    }


def _model_free_state_shift(df: pd.DataFrame) -> dict[str, Any]:
    matrix = df.pivot(index="realization_id", columns="temperature_c", values="ln_eta").dropna()
    x = matrix.to_numpy(dtype=float)
    x = x - x.mean(axis=0, keepdims=True)
    _u, s, vt = np.linalg.svd(x, full_matrices=False)
    variance = s * s
    explained = variance / variance.sum()
    pc1 = vt[0]
    constant = np.ones_like(pc1) / np.sqrt(len(pc1))
    cosine = abs(float(np.dot(pc1, constant) / (np.linalg.norm(pc1) * np.linalg.norm(constant))))
    return {
        "pc1_explained_between_realization_variance_fraction": float(explained[0]),
        "pc1_constant_vertical_shift_cosine_similarity": cosine,
        "n_complete_realizations": int(matrix.shape[0]),
    }


def _thermal_descriptor(df: pd.DataFrame) -> dict[str, Any]:
    values, fit_r2 = [], []
    for _rid, group in df.groupby("realization_id"):
        fit = stats.linregress(1.0 / (group["temperature_c"].to_numpy() + 273.15), group["ln_eta"].to_numpy())
        values.append(float(fit.slope * R_GAS / 1000.0))
        fit_r2.append(float(fit.rvalue**2))
    return {
        "mean_apparent_E_eta_kJ_mol": float(np.mean(values)),
        "sd_apparent_E_eta_kJ_mol": float(np.std(values, ddof=1)),
        "cv_apparent_E_eta": float(np.std(values, ddof=1) / np.mean(values)),
        "median_curve_r2": float(np.median(fit_r2)),
        "n_realizations": len(values),
    }


def _phosphoric_acid_perturbation(
    primary_df: pd.DataFrame, thermal_summary: dict[str, Any]
) -> dict[str, Any]:
    """Quantify the verified E1 +P perturbation without mixing it into the primary fit."""
    sweeps = pd.read_csv(ROOT / "data" / "temperature_sweeps.csv")
    sweeps["temperature_c"] = pd.to_numeric(sweeps["temperature_c"], errors="raise")
    sweeps["viscosity_reported"] = pd.to_numeric(sweeps["viscosity_reported"], errors="raise")
    sweeps["retest_after_1d"] = sweeps["retest_after_1d"].astype(str).str.lower().map(
        {"true": True, "false": False}
    )
    sweeps["dx"] = 1000.0 / (sweeps["temperature_c"] + 273.15) - 1000.0 / T_REF_K
    sweeps["ln_eta"] = np.log(sweeps["viscosity_reported"])

    plus_p = sweeps[
        (sweeps["formulation_id"] == "E1") & (sweeps["run_label"] == "+P")
    ].sort_values("temperature_c").copy()
    if len(plus_p) != 6:
        raise ValueError("Expected six temperatures for E1 +P perturbation")

    perturb = pd.read_csv(ROOT / "data" / "experimental_perturbations.csv")
    prow = perturb.loc[perturb["realization_id"] == "E1__+P__day1_0"].iloc[0]

    fit = stats.linregress(
        1.0 / (plus_p["temperature_c"].to_numpy() + 273.15),
        plus_p["ln_eta"].to_numpy(),
    )
    e_eta = float(fit.slope * R_GAS / 1000.0)

    shape = smf.ols("ln_eta ~ C(realization_id) + dx + I(dx**2)", primary_df).fit()
    beta1 = float(shape.params["dx"])
    beta2 = float(shape.params["I(dx ** 2)"])

    intercept = float(
        np.mean(
            plus_p["ln_eta"].to_numpy()
            - beta1 * plus_p["dx"].to_numpy()
            - beta2 * plus_p["dx"].to_numpy() ** 2
        )
    )
    pred = intercept + beta1 * plus_p["dx"].to_numpy() + beta2 * plus_p["dx"].to_numpy() ** 2
    intercept_only_error = math.exp(_rmse(plus_p["ln_eta"].to_numpy() - pred))

    anchor = plus_p.loc[plus_p["temperature_c"] == 120.0].iloc[0]
    test = plus_p.loc[plus_p["temperature_c"] != 120.0]
    anchor_pred = (
        anchor["ln_eta"]
        + beta1 * (test["dx"] - anchor["dx"])
        + beta2 * (test["dx"] ** 2 - anchor["dx"] ** 2)
    )
    anchor_error = math.exp(_rmse(test["ln_eta"].to_numpy() - anchor_pred.to_numpy()))

    comparator = sweeps[
        (sweeps["formulation_id"] == "E1")
        & (sweeps["run_label"] == "R01")
        & (sweeps["retest_after_1d"] == True)  # noqa: E712
    ][["temperature_c", "viscosity_reported"]].rename(
        columns={"viscosity_reported": "comparator_viscosity"}
    )
    comparison = plus_p[["temperature_c", "viscosity_reported"]].merge(
        comparator, on="temperature_c", how="inner", validate="one_to_one"
    )
    ratios = comparison["viscosity_reported"].to_numpy() / comparison[
        "comparator_viscosity"
    ].to_numpy()
    pct = (ratios - 1.0) * 100.0

    return {
        "condition": {
            "additive": str(prow["additive"]),
            "standard_solution_concentration_mol_L": float(prow["solution_concentration_mol_L"]),
            "amount_mmol": float(prow["amount_mmol"]),
            "calculated_solution_volume_mL": float(prow["calculated_solution_volume_mL"]),
            "calculated_neat_additive_mass_mg": float(prow["calculated_neat_additive_mass_mg"]),
            "addition_stage": str(prow["addition_stage"]),
        },
        "apparent_E_eta_kJ_mol": e_eta,
        "ln_eta_vs_invT_r2": float(fit.rvalue**2),
        "primary_E_eta_mean_kJ_mol": float(thermal_summary["mean_apparent_E_eta_kJ_mol"]),
        "primary_E_eta_sd_kJ_mol": float(thermal_summary["sd_apparent_E_eta_kJ_mol"]),
        "standardized_E_eta_delta_from_primary_mean": float(
            (e_eta - thermal_summary["mean_apparent_E_eta_kJ_mol"])
            / thermal_summary["sd_apparent_E_eta_kJ_mol"]
        ),
        "shared_shape_intercept_only_multiplicative_error": intercept_only_error,
        "anchor_120c_predict_remaining_temperatures_multiplicative_error": anchor_error,
        "observational_E1_GJJ_day1_comparator": {
            "geometric_mean_viscosity_ratio": float(np.exp(np.mean(np.log(ratios)))),
            "percent_difference_range": [float(np.min(pct)), float(np.max(pct))],
            "mean_absolute_percent_difference": float(np.mean(np.abs(pct))),
            "interpretation_boundary": (
                "Observational reference only; the compact record does not establish a paired "
                "parent-batch relationship between E1 +P and E1 GJJ day-1."
            ),
        },
        "interpretation": (
            "The verified low-dose H3PO4 perturbation shifts the observed viscosity level while "
            "remaining closely compatible with the local shared thermal-response geometry. "
            "It is a separate chemical-perturbation check and is not pooled into the primary "
            "same-composition state model."
        ),
    }


def _original_hold() -> dict[str, Any]:
    df = pd.read_csv(ROOT / "data" / "thermal_hold.csv")
    df = df[(df["stage"] == "original") & (df["formulation_id"].isin(["E1", "E5"]))].copy()
    df["time_min"] = pd.to_numeric(df["time_min"], errors="raise")
    df["viscosity_reported"] = pd.to_numeric(df["viscosity_reported"], errors="raise")
    df["time_h"] = df["time_min"] / 60.0
    df["ln_eta"] = np.log(df["viscosity_reported"])
    out: dict[str, Any] = {}
    for formulation_id, group in df.groupby("formulation_id"):
        group = group.sort_values("time_min")
        fit = stats.linregress(group["time_h"], group["ln_eta"])
        eta15 = float(group.loc[group["time_min"] == 15, "viscosity_reported"].iloc[0])
        eta60 = float(group.loc[group["time_min"] == 60, "viscosity_reported"].iloc[0])
        eta90 = float(group.loc[group["time_min"] == 90, "viscosity_reported"].iloc[0])
        out[formulation_id] = {
            "linear_lneta_slope_per_h": float(fit.slope),
            "linear_lneta_r2": float(fit.rvalue**2),
            "si_15_to_60": (eta60 - eta15) / eta15,
            "si_15_to_90": (eta90 - eta15) / eta15,
        }
    out["E5_to_E1_drift_coefficient_ratio"] = (
        out["E5"]["linear_lneta_slope_per_h"] / out["E1"]["linear_lneta_slope_per_h"]
    )
    return out


def get_state_aware_rheology_summary_v3() -> dict[str, Any]:
    """Return provenance-audited upstream rheology findings for blind Agent use.

    Only original/pre-validation measurements are used. The validation formulation and
    its wet-lab outcome are neither loaded nor returned.
    """
    df = _prepare_audited_temperature_data()
    formulation = _model_and_cv(df, "ln_eta ~ C(formulation_id) + dx + I(dx**2)")
    state = _model_and_cv(df, "ln_eta ~ C(realization_id) + dx + I(dx**2)")
    lofo_rows, pooled_anchor_errors = _leave_one_formulation_one_point(df)
    lofo_120 = [row for row in lofo_rows if row["anchor_temperature_c"] == 120.0]
    pca = _model_free_state_shift(df)
    thermal = _thermal_descriptor(df)
    hold = _original_hold()
    perturbation = _phosphoric_acid_perturbation(df, thermal)
    same_formulation_anchor_gain = _same_formulation_anchor_gain(df)

    return {
        "tool_name": "get_state_aware_rheology_summary",
        "tool_version": "3.6-state-anchor-bridge",
        "source_scope": "original pre-validation local measurements with chemistry-comparability audit",
        "validation_formulation_visible": False,
        "provenance_audit": {
            "excluded_from_primary_state_model": ["E1__+P__day1_0"],
            "reason": (
                "E1 +P is a verified chemical perturbation: 0.025 mmol H3PO4 from a 0.1 mol/L "
                "standard solution was added during dehydration. It is excluded from the "
                "same-composition primary state model and exposed separately as a perturbation check."
            ),
            "same_operator_labels": ["R01", "R02", "R03"],
            "day1_parent_sample_relation": "unknown in compact source metadata",
        },
        "discovered_patterns": {
            "state_shift_master_curve": {
                "n_points": int(len(df)),
                "n_realizations": int(df["realization_id"].nunique()),
                "n_formulations": int(df["formulation_id"].nunique()),
                "formulation_only_r2": formulation["r2"],
                "state_aware_shared_shape_r2": state["r2"],
                "held_temperature_formulation_only_error_factor": formulation[
                    "held_temperature_multiplicative_error"
                ],
                "held_temperature_state_aware_error_factor": state[
                    "held_temperature_multiplicative_error"
                ],
                "positive_model": "ln(eta_fr(T)) = a_fr + beta1*z(T) + beta2*z(T)^2 + epsilon",
                "model_free_check": pca,
                "interpretation": (
                    "Within the chemistry-audited local family, a realization-specific viscosity-scale intercept plus a shared quadratic inverse-temperature response closes the data far better than a formulation-level intercept using the same thermal basis."
                ),
            },
            "one_point_state_calibration": {
                "validation_scheme": "leave one nominal formulation out; fit shared shape on the remaining formulations; use one anchor from the held formulation",
                "pooled_multiplicative_error_factor_range": [
                    float(min(pooled_anchor_errors)),
                    float(max(pooled_anchor_errors)),
                ],
                "at_120c_by_held_formulation": lofo_120,
                "interpretation": (
                    "Within the tested local chemistry family, one state-specific viscosity anchor can locate a previously held-out nominal formulation on the shared thermal-response shape to roughly 6-10% pooled multiplicative error."
                ),
            },
            "same_formulation_anchor_information_gain": same_formulation_anchor_gain,
            "thermal_coordinate": {
                **thermal,
                "interpretation": (
                    "The apparent temperature-sensitivity descriptor remains comparatively concentrated after chemistry auditing; it is a rheological descriptor, not a molecular reaction activation energy."
                ),
            },
            "temporal_stability_coordinate": {
                **hold,
                "interpretation": (
                    "Original E1 and E5 hold trajectories show that thermal-hold viscosity drift is strongly formulation dependent and should be treated separately from static viscosity."
                ),
            },
            "chemical_perturbation_check": perturbation,
        },
        "design_rules": [
            "Represent a candidate as formulation plus process/realization state, not composition alone.",
            "Use one state-specific anchor measurement to locate a new realization or nearby local formulation on the transferable thermal-response shape when it remains inside the supported local chemistry family.",
            "Within repeated E2 realizations, a 110 C anchor reduced 120-130 C pooled multiplicative error from about 1.824x for formulation identity alone to about 1.086x; treat this as measured value of state information, not as permission to extrapolate the shortcut across chemistry.",
            "Treat static viscosity, temperature response and thermal-hold stability as separate decision variables.",
            "When the failure mode is hot-hold drift, choose an experiment and measurement window that directly test drift rather than only matching one nominal viscosity value.",
            "Use external resin/tackifier evidence to define chemically plausible directions, but do not convert analogue proximity into a predicted local outcome.",
            "Keep deliberately chemistry-perturbed curves outside same-composition fitting, but use them to test whether an intervention shifts viscosity scale, thermal-response shape, or both.",
        ],
        "experiment_design_implications": {
            "state_anchor": (
                "A single in-range anchor has directly measured information value within repeated E2 realizations: a 110 C anchor reduced pooled 120-130 C multiplicative error from about 1.824x to about 1.086x. The shortcut is allowed only inside validated shared-shape support; chemistry-shifted candidates require direct sweep verification first."
            ),
            "hold_window": (
                "For the current local study, 120 C and the common 15-60 min window directly interrogate the observed instability while matching the available validation window."
            ),
            "selection_target": (
                "Select a formulation-process point that is informative about the observed instability and state uncertainty, not merely the closest static-viscosity value."
            ),
            "verified_acid_perturbation": (
                "E1 +P received 0.025 mmol H3PO4 from a 0.1 mol/L standard solution during dehydration. "
                "Its close agreement with the primary shared thermal shape makes it useful as a defined "
                "scale-versus-shape perturbation check, not as another nominal E1 realization."
            ),
        },
        "claim_boundaries": [
            "The shared-shape/state-shift structure is established only within the measured local chemistry family.",
            "The apparent E_eta descriptor is rheological, not a chemical reaction activation energy.",
            "The E1/E5 hold contrast does not identify a unique molecular mechanism.",
            "The verified E1 +P phosphoric-acid perturbation is excluded from the primary same-composition fit and is interpreted separately as a chemical-perturbation check.",
            "No validation-formulation identity or outcome is used by this tool.",
        ],
    }
