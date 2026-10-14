"""Submission-critical evidence and frozen decision-rule guardrails.

Do not edit or replace the 2026-09-20 frozen prospective source here.
Changes to the scientific interpretation must preserve the source hierarchy.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_s1c39_hypothesis_verdict_keeps_frozen_indeterminate_region() -> None:
    frozen = (ROOT / "experiments/prospective/S1C39_M-HOLD-120_20260920.md").read_text(
        encoding="utf-8"
    )
    si = (ROOT / "manuscript/SUPPLEMENTARY_INFORMATION_V5.md").read_text(
        encoding="utf-8"
    )
    main = (ROOT / "manuscript/MAIN_TEXT_V5.md").read_text(encoding="utf-8")
    note = (
        ROOT
        / "experiments/supplementary_20261004/INTERPRETATION_RECONCILIATION_20261014.md"
    ).read_text(encoding="utf-8")

    for threshold in ("4.04%", "6.08%", "3.80%"):
        assert threshold in frozen
        assert threshold in si
        assert threshold in main
        assert threshold in note
    for text in (si, main, note):
        assert "S1C41" in text
        assert "H-DUAL" in text
    for text in (si, note):
        assert "unresolved" in text.lower()
        assert "contemporaneous" in text.lower()
    assert "at or above 4.04% supports H-DUAL" not in si
    assert "at or above 4.04% supports H-DUAL" not in main
    assert "not automatically reset" in note.replace("**", "")
    assert "not automatically updated" in si


def test_spe_raw_predictions_have_separate_curve_and_paper_holdouts() -> None:
    source = (ROOT / "scripts/spe_raw_anchor_audit.py").read_text(encoding="utf-8")
    report = json.loads(
        (ROOT / "analysis/results/generality_20261014/raw_anchor/summary.json").read_text(
            encoding="utf-8"
        )
    )
    assert "doi_map[x] != held_doi" in source
    assert "scope == \"doi\"" in source
    assert "held.iloc[-1]" in source  # warmest actual source observation
    assert "raw" in report["method"].lower()
    assert report["raw_measurement_count"] == 7640
    a = report["curve"]["within_20_c"]
    b = report["doi"]["within_20_c"]
    assert (a["n_predictions"], a["n_curves"], a["n_families"]) == (979, 322, 14)
    assert (b["n_predictions"], b["n_curves"], b["n_families"]) == (767, 232, 5)
    assert abs(a["multiplicative_rmse"] - 1.658505360849546) < 1e-10
    assert abs(b["multiplicative_rmse"] - 1.704904458155343) < 1e-10
    assert report["curve"]["within_10_c"]["multiplicative_rmse"] < (
        report["curve"]["within_20_c"]["multiplicative_rmse"]
    )
    assert report["curve"]["within_20_c"]["multiplicative_rmse"] < (
        report["curve"]["within_30_c"]["multiplicative_rmse"]
    )
