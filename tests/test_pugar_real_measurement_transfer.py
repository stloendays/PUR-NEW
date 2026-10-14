"""Submission guardrails for real measured-point external PUR transfer.

The published Pugar input remains in its pinned source workbook; only
the derived independent source-workbook execution report is checked here.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_raw_pugar_summary_reports_matched_chemistry_and_true_readouts() -> None:
    p = ROOT / "analysis/results/generality_20261014/pur_raw_anchor/summary.json"
    report = json.loads(p.read_text(encoding="utf-8"))
    assert report["n_raw_curves"] == 39
    assert report["n_raw_measurements"] == 4559
    assert report["n_raw_polyol_families"] == 3
    assert report["paired_train_curve_count_per_scope"] == 2
    assert report["source_workbook_sha256"] == (
        "bbec41da4ff3cae1231686e5d219ec217ac53d85e0f5fc561e408e78fdaf7085"
    )
    assert report["excluded_no_60C_anchor_within_half_degree"] == ["D_I_9", "D_W_9"]
    pair = report["paired_10C_comparison"]
    assert pair["n_held_curves"] == 34
    assert pair["n_predictions"] == 68
    assert abs(pair["same_polyol_multiplicative_error"] - 1.0764488569123007) < 1e-9
    assert abs(pair["cross_polyol_multiplicative_error"] - 1.2384142784076282) < 1e-9
    assert pair["difference_log_rmse_bootstrap_ci95"][0] > 0
    pNCO = report["pNCO_proximity_sensitivity_10C"]
    assert (pNCO["n_held_curves"], pNCO["n_predictions"]) == (22, 44)
    assert pNCO["same_polyol_multiplicative_rmse"] < pNCO["cross_polyol_multiplicative_rmse"]


def test_canonical_manuscript_distinguishes_raw_and_interpolated_anchors() -> None:
    main = (ROOT / "manuscript/MAIN_TEXT_V5.md").read_text(encoding="utf-8")
    si = (ROOT / "manuscript/SUPPLEMENTARY_INFORMATION_V5.md").read_text(encoding="utf-8")
    for t in (main, si):
        for token in ("1.076×", "1.238×", "1.057×", "1.166×"):
            assert token in t
        assert "raw" in t.lower()
    assert "grid-level reconstruction" in si.lower()
    assert "scripts/external_pur_raw_anchor.py" in si
    assert "one-measurement calibration" in main.lower()
