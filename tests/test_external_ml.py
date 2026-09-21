from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from pur_new.external_ml import (
    build_external_thermal_response_report,
    derive_apparent_thermal_targets,
    load_pugar_feature_workbook,
    load_pugar_viscosity_workbook,
)


def _curve(sample, poly, iso, pnco, e_kj, intercept=4.0):
    temps = np.linspace(40, 80, 9)
    inv_t = 1.0 / (temps + 273.15)
    ln_eta = intercept + (e_kj * 1000.0 / 8.314462618) * inv_t
    return pd.DataFrame(
        {
            "sample_id": sample,
            "polyol_code": poly,
            "isocyanate_code": iso,
            "pNCO_pct": pnco,
            "temperature_c": temps,
            "viscosity_pa_s": np.exp(ln_eta),
        }
    )


def test_targets_are_one_per_curve_not_one_per_temperature_point():
    curves = pd.concat(
        [_curve("P_44M_4", "P", "44M", 4, 42.0), _curve("D_44M_4", "D", "44M", 4, 58.0)],
        ignore_index=True,
    )
    target = derive_apparent_thermal_targets(curves)
    assert len(target) == 2
    assert target.set_index("sample_id").loc["P_44M_4", "apparent_E_eta_kJ_mol"] == pytest.approx(42.0, rel=1e-7)


def test_pugar_workbook_parsers(tmp_path):
    curve_path = tmp_path / "ViscTempData.xlsx"
    with pd.ExcelWriter(curve_path) as writer:
        pd.DataFrame({"Temperature (C)": [40, 50, 60], "Viscosity (Pa s)": [30, 20, 12]}).to_excel(
            writer, sheet_name="P_44M_4", index=False
        )
        pd.DataFrame({"Temperature (C)": [40, 50, 60], "Viscosity (Pa s)": [50, 32, 19]}).to_excel(
            writer, sheet_name="D_MLQ_6", index=False
        )
        pd.DataFrame({"note": ["ignore"]}).to_excel(writer, sheet_name="README", index=False)
    curves = load_pugar_viscosity_workbook(curve_path)
    assert set(curves["sample_id"].unique()) == {"P_44M_4", "D_MLQ_6"}

    feature_path = tmp_path / "FeatureSpaces.xlsx"
    with pd.ExcelWriter(feature_path) as writer:
        pd.DataFrame(
            {
                "Iso": ["44M", "MLQ"],
                "Polyol": ["P", "D"],
                "pNCO": [4, 6],
                "PPMW": [5000, 4000],
                "PolyTPSA": [20, 30],
                "IsoISF": [0.001, 0.002],
                "PolyTg": [-80, -70],
            }
        ).to_excel(writer, sheet_name="PhysicochemicalSpace", index=False)
    features = load_pugar_feature_workbook(feature_path)
    assert set(features["sample_id"]) == {"P_44M_4", "D_MLQ_6"}


def test_report_uses_grouped_formulation_family_validation():
    rows = []
    feature_rows = []
    for poly, base_e, tg in [("P", 40.0, -80.0), ("D", 55.0, -70.0), ("C", 65.0, -60.0)]:
        for iso, shift in [("44M", 0.0), ("MLQ", 1.0)]:
            sid = f"{poly}_{iso}_4"
            rows.append(_curve(sid, poly, iso, 4, base_e + shift))
            feature_rows.append(
                {
                    "sample_id": sid,
                    "Polyol": poly,
                    "Iso": iso,
                    "pNCO": 4.0,
                    "PolyTg": tg,
                    "PPMW": 4000.0 + base_e * 10,
                    "PolyTPSA": 20.0 + base_e / 10,
                    "IsoISF": 0.001 if iso == "44M" else 0.002,
                    "PolyLogP": base_e / 100,
                }
            )
    curves = pd.concat(rows, ignore_index=True)
    features = pd.DataFrame(feature_rows)
    report, merged, low_fit = build_external_thermal_response_report(curves, features)
    assert report["n_total_formulations"] == 6
    assert report["n_primary_formulations"] == 6
    assert low_fit.empty
    assert report["models"]["minimal_polyol_state"]["leave_one_isocyanate_family_out"]["n_groups"] == 2
    assert report["models"]["minimal_polyol_state"]["leave_one_polyol_family_out"]["n_groups"] == 3
    assert len(merged) == 6
