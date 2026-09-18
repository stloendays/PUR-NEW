from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_audit_module():
    path = ROOT / "scripts" / "analysis_audit_v1.py"
    spec = importlib.util.spec_from_file_location("analysis_audit_v1", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_bounded_local_formulation_temperature_extrapolation_reproduces_frozen_result():
    audit = _load_audit_module()
    _all_rows, audited = audit.prepare_local(
        ROOT / "data" / "temperature_sweeps.csv",
        ROOT / "data" / "realization_metadata.csv",
    )

    detail, summary, overall = audit.bounded_formulation_temperature_extrapolation(
        audited,
        anchor_temp_c=110.0,
        target_temps_c=(120.0, 130.0),
        bootstrap_reps=1000,
        bootstrap_seed=20260918,
    )

    assert len(detail) == 12
    assert detail["held_formulation"].nunique() == 3
    assert detail["held_realization"].nunique() == 6

    assert abs(overall["multiplicative_rmse"] - 1.088219628209339) < 1e-10
    assert abs(overall["median_absolute_percentage_error"] - 0.05684603125436871) < 1e-10

    by_temp = summary[summary["scope"] == "target_temperature_c"].set_index("group")
    assert abs(by_temp.loc["120", "multiplicative_rmse"] - 1.0870339321849665) < 1e-10
    assert abs(by_temp.loc["130", "multiplicative_rmse"] - 1.0893914970085157) < 1e-10

    low, high = overall["bootstrap_multiplicative_rmse_ci95"]
    assert 1.03 < low < 1.06
    assert 1.11 < high < 1.14

    assert "Short-range" in overall["claim_boundary"]
    assert "not cross-family" in overall["claim_boundary"]
