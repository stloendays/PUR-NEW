from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import LeaveOneGroupOut, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

R_GAS = 8.314462618
PRIMARY_CURVE_R2_THRESHOLD = 0.98
MINIMAL_FEATURES = ("PolyTg", "pNCO")
LITERATURE_INFORMED_FEATURES = ("PPMW", "PolyTPSA", "IsoISF", "pNCO", "PolyTg")


def _clean_name(value: Any) -> str:
    return str(value).strip().replace("%", "pct").replace(" ", "_")


def _find_column(columns: Iterable[Any], tokens: tuple[str, ...]) -> str | None:
    names = {str(c): re.sub(r"[^a-z0-9]+", "", str(c).lower()) for c in columns}
    for original, normalized in names.items():
        if all(token in normalized for token in tokens):
            return original
    return None


def parse_pugar_sample_id(sample_id: str) -> tuple[str, str, float]:
    match = re.match(r"^([^_]+)_([^_]+)_([0-9]+(?:\.[0-9]+)?)$", str(sample_id).strip())
    if not match:
        raise ValueError(f"Cannot parse Pugar sample id: {sample_id!r}")
    return match.group(1), match.group(2), float(match.group(3))


def _sheet_to_curve(sheet: str, frame: pd.DataFrame) -> pd.DataFrame | None:
    try:
        polyol, iso, pnco = parse_pugar_sample_id(sheet)
    except ValueError:
        return None

    if frame.empty:
        return None
    frame = frame.copy()
    frame.columns = [str(c).strip() for c in frame.columns]
    temp_col = _find_column(frame.columns, ("temp",))
    visc_col = _find_column(frame.columns, ("visc",))

    if temp_col is None or visc_col is None:
        numeric = {c: pd.to_numeric(frame[c], errors="coerce") for c in frame.columns}
        candidates = []
        for c, s in numeric.items():
            valid = s.dropna()
            if len(valid) < 3:
                continue
            frac_temp_range = float(((valid >= 20) & (valid <= 200)).mean())
            positive_fraction = float((valid > 0).mean())
            candidates.append((c, frac_temp_range, positive_fraction, float(valid.median())))
        if temp_col is None:
            temp_options = [x for x in candidates if x[1] >= 0.8]
            if temp_options:
                temp_col = max(temp_options, key=lambda x: x[1])[0]
        if visc_col is None:
            visc_options = [x for x in candidates if x[0] != temp_col and x[2] >= 0.95]
            if visc_options:
                visc_col = max(visc_options, key=lambda x: x[3])[0]

    if temp_col is None or visc_col is None:
        return None

    out = pd.DataFrame(
        {
            "temperature_c": pd.to_numeric(frame[temp_col], errors="coerce"),
            "viscosity_pa_s": pd.to_numeric(frame[visc_col], errors="coerce"),
        }
    ).dropna()
    out = out[(out["temperature_c"] >= 20) & (out["temperature_c"] <= 200) & (out["viscosity_pa_s"] > 0)]
    if len(out) < 3:
        return None
    out = out.sort_values("temperature_c").reset_index(drop=True)
    out.insert(0, "sample_id", sheet)
    out["polyol_code"] = polyol
    out["isocyanate_code"] = iso
    out["pNCO_pct"] = pnco
    return out


def load_pugar_viscosity_workbook(path: str | Path) -> pd.DataFrame:
    """Normalize the public Pugar viscosity workbook to one long table."""
    xls = pd.ExcelFile(path)
    frames: list[pd.DataFrame] = []
    for sheet in xls.sheet_names:
        frame = pd.read_excel(path, sheet_name=sheet)
        parsed = _sheet_to_curve(sheet, frame)
        if parsed is not None:
            frames.append(parsed)
    if not frames:
        raise ValueError("No Pugar-style viscosity curve sheets were detected")
    out = pd.concat(frames, ignore_index=True)
    if out["sample_id"].nunique() < 2:
        raise ValueError("Expected multiple formulation curves")
    return out


def load_pugar_feature_workbook(path: str | Path) -> pd.DataFrame:
    """Load the physicochemical feature space and derive an explicit formulation key."""
    xls = pd.ExcelFile(path)
    candidates = [s for s in xls.sheet_names if "phys" in s.lower()]
    if not candidates:
        candidates = list(xls.sheet_names)

    chosen: pd.DataFrame | None = None
    for sheet in candidates:
        frame = pd.read_excel(path, sheet_name=sheet)
        frame.columns = [str(c).strip() for c in frame.columns]
        lower = {re.sub(r"[^a-z0-9]+", "", c.lower()): c for c in frame.columns}
        if {"polyol", "iso", "pnco"} <= set(lower):
            chosen = frame.rename(
                columns={lower["polyol"]: "Polyol", lower["iso"]: "Iso", lower["pnco"]: "pNCO"}
            )
            break
    if chosen is None:
        raise ValueError("Could not find a physicochemical sheet with Polyol/Iso/pNCO columns")

    chosen = chosen.copy()
    chosen["Polyol"] = chosen["Polyol"].astype(str).str.strip()
    chosen["Iso"] = chosen["Iso"].astype(str).str.strip()
    chosen["pNCO"] = pd.to_numeric(chosen["pNCO"], errors="raise")

    def key(row: pd.Series) -> str:
        p = float(row["pNCO"])
        p_text = str(int(p)) if p.is_integer() else ("%g" % p)
        return f"{row['Polyol']}_{row['Iso']}_{p_text}"

    chosen["sample_id"] = chosen.apply(key, axis=1)
    for col in chosen.columns:
        if col in {"sample_id", "Polyol", "Iso"}:
            continue
        chosen[col] = pd.to_numeric(chosen[col], errors="coerce")
    if chosen["sample_id"].duplicated().any():
        dup = chosen.loc[chosen["sample_id"].duplicated(), "sample_id"].tolist()
        raise ValueError(f"Duplicate feature rows for samples: {dup}")
    return chosen


def derive_apparent_thermal_targets(curves: pd.DataFrame) -> pd.DataFrame:
    """Derive one apparent rheological E_eta target per complete formulation curve."""
    required = {"sample_id", "polyol_code", "isocyanate_code", "pNCO_pct", "temperature_c", "viscosity_pa_s"}
    missing = required - set(curves.columns)
    if missing:
        raise ValueError(f"Missing curve columns: {sorted(missing)}")

    rows: list[dict[str, Any]] = []
    for sample_id, group in curves.groupby("sample_id", sort=True):
        group = group.dropna(subset=["temperature_c", "viscosity_pa_s"]).sort_values("temperature_c")
        if len(group) < 3:
            continue
        x = 1.0 / (group["temperature_c"].to_numpy(dtype=float) + 273.15)
        y = np.log(group["viscosity_pa_s"].to_numpy(dtype=float))
        fit = stats.linregress(x, y)
        rows.append(
            {
                "sample_id": sample_id,
                "polyol_code": str(group["polyol_code"].iloc[0]),
                "isocyanate_code": str(group["isocyanate_code"].iloc[0]),
                "pNCO_pct": float(group["pNCO_pct"].iloc[0]),
                "n_curve_points": int(len(group)),
                "temperature_min_c": float(group["temperature_c"].min()),
                "temperature_max_c": float(group["temperature_c"].max()),
                "apparent_E_eta_kJ_mol": float(fit.slope * R_GAS / 1000.0),
                "ln_eta_inverse_T_r2": float(fit.rvalue**2),
            }
        )
    return pd.DataFrame(rows)


def _grouped_cv_metrics(frame: pd.DataFrame, features: list[str], group_column: str) -> dict[str, Any]:
    use = frame.dropna(subset=features + ["apparent_E_eta_kJ_mol", group_column]).copy()
    groups = use[group_column].astype(str).to_numpy()
    if len(set(groups)) < 2:
        raise ValueError(f"Need at least two groups for {group_column}")
    model = Pipeline([("scale", StandardScaler()), ("ridge", Ridge(alpha=1.0))])
    pred = cross_val_predict(
        model,
        use[features].astype(float),
        use["apparent_E_eta_kJ_mol"].to_numpy(dtype=float),
        groups=groups,
        cv=LeaveOneGroupOut(),
    )
    obs = use["apparent_E_eta_kJ_mol"].to_numpy(dtype=float)
    return {
        "group_column": group_column,
        "n_samples": int(len(use)),
        "n_groups": int(len(set(groups))),
        "r2": float(r2_score(obs, pred)),
        "rmse_kJ_mol": float(math.sqrt(mean_squared_error(obs, pred))),
        "mae_kJ_mol": float(mean_absolute_error(obs, pred)),
    }


def _standardized_coefficients(frame: pd.DataFrame, features: list[str]) -> list[dict[str, float | str]]:
    use = frame.dropna(subset=features + ["apparent_E_eta_kJ_mol"])
    scaler = StandardScaler()
    x = scaler.fit_transform(use[features].astype(float))
    y = use["apparent_E_eta_kJ_mol"].to_numpy(dtype=float)
    model = Ridge(alpha=1.0).fit(x, y)
    return [
        {"feature": feature, "standardized_ridge_coefficient": float(coef)}
        for feature, coef in zip(features, model.coef_)
    ]


def build_external_thermal_response_report(
    curves: pd.DataFrame,
    features: pd.DataFrame,
    *,
    curve_r2_threshold: float = PRIMARY_CURVE_R2_THRESHOLD,
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    targets = derive_apparent_thermal_targets(curves)
    merged = targets.merge(features, on="sample_id", how="inner", validate="one_to_one")
    merged["quality_pass"] = merged["ln_eta_inverse_T_r2"] >= curve_r2_threshold
    primary = merged[merged["quality_pass"]].copy()

    report: dict[str, Any] = {
        "target_definition": (
            "apparent rheological E_eta from slope of ln(viscosity) versus 1/T; descriptor only, not a chemical reaction activation energy"
        ),
        "curve_fit_quality_threshold_r2": float(curve_r2_threshold),
        "n_total_formulations": int(len(merged)),
        "n_primary_formulations": int(len(primary)),
        "n_low_fit_sensitivity_only": int((~merged["quality_pass"]).sum()),
        "target_range_all_kJ_mol": [
            float(merged["apparent_E_eta_kJ_mol"].min()),
            float(merged["apparent_E_eta_kJ_mol"].max()),
        ],
        "median_curve_r2_all": float(merged["ln_eta_inverse_T_r2"].median()),
        "models": {},
        "feature_associations_primary": {},
        "interpretation_boundary": (
            "Grouped validation is formulation-family validation. Row-level random splits of temperature points are not used because they would leak the same formulation curve across train and test."
        ),
    }

    for name, requested in {
        "minimal_polyol_state": list(MINIMAL_FEATURES),
        "literature_informed_ridge": list(LITERATURE_INFORMED_FEATURES),
    }.items():
        available = [f for f in requested if f in primary.columns and primary[f].notna().all()]
        if len(available) != len(requested):
            report["models"][name] = {"status": "unavailable", "requested_features": requested, "available": available}
            continue
        report["models"][name] = {
            "status": "fit",
            "features": available,
            "ridge_alpha": 1.0,
            "leave_one_isocyanate_family_out": _grouped_cv_metrics(primary, available, "isocyanate_code"),
            "leave_one_polyol_family_out": _grouped_cv_metrics(primary, available, "polyol_code"),
            "full_primary_standardized_coefficients": _standardized_coefficients(primary, available),
        }

    association_candidates = ["PolyTg", "PolyTPSA", "PolyLogP", "PPMW", "IsoISF", "pNCO"]
    for feature in association_candidates:
        if feature not in primary.columns:
            continue
        use = primary[[feature, "apparent_E_eta_kJ_mol"]].dropna()
        if len(use) < 3:
            continue
        if use[feature].nunique() < 2 or use["apparent_E_eta_kJ_mol"].nunique() < 2:
            report["feature_associations_primary"][feature] = {
                "spearman_rho": None,
                "pvalue_descriptive_only": None,
                "n": int(len(use)),
                "causal_interpretation": False,
                "status": "constant_input",
            }
            continue
        rho, pvalue = stats.spearmanr(use[feature], use["apparent_E_eta_kJ_mol"])
        report["feature_associations_primary"][feature] = {
            "spearman_rho": float(rho),
            "pvalue_descriptive_only": float(pvalue),
            "n": int(len(use)),
            "causal_interpretation": False,
            "status": "descriptive_only",
        }

    low_fit = merged.loc[~merged["quality_pass"], ["sample_id", "ln_eta_inverse_T_r2", "apparent_E_eta_kJ_mol"]].copy()
    return report, merged, low_fit
