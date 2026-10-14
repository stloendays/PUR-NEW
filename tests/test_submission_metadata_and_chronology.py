"""Protect scientific chronology, measurement metadata and manuscript source parity.

These assertions are read-only: historical protocols and measured values remain
untouched, while future editorial changes that would conflate evidence classes
or silently drop verified methods are blocked by CI.
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_instrument_csv_is_parseable_and_all_perturbation_fields_survive() -> None:
    source = read_text("data/experimental_methods_metadata.csv")
    assert r"\nE1_plusP_perturbation" not in source
    with (ROOT / "data/experimental_methods_metadata.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        assert reader.fieldnames == [
            "scope", "parameter", "value", "unit_or_basis", "source_note"
        ]
    assert len(rows) == 20
    assert all(row["scope"] and row["parameter"] and row["value"] for row in rows)
    keys = {(row["scope"], row["parameter"]): row["value"] for row in rows}
    assert len(keys) == len(rows)
    assert keys[("viscosity_measurement", "instrument_model")] == "RV-SSR-H"
    assert keys[("viscosity_measurement", "heater_model")] == "NKY-25"
    assert keys[("viscosity_measurement", "output_unit")] == "mPa·s"
    perturbation = {p: v for (g, p), v in keys.items() if g == "E1_plusP_perturbation"}
    assert len(perturbation) == 6
    assert perturbation["additive"] == "H3PO4"
    assert perturbation["h3po4_amount"] == "0.025"
    assert perturbation["standard_solution_concentration"] == "0.1"
    assert perturbation["calculated_solution_volume"] == "0.25"
    assert perturbation["calculated_h3po4_mass"] == "2.45"
    assert perturbation["addition_stage"] == "dehydration_stage"


def test_chronology_keeps_historical_selection_distinct_from_replay() -> None:
    main = read_text("manuscript/MAIN_TEXT_V5.md")
    si = read_text("manuscript/SUPPLEMENTARY_INFORMATION_V5.md")
    frozen = read_text("docs/EXPERIMENTAL_CHRONOLOGY.md")
    assert "not itself a contemporaneous pre-experiment timestamp" in frozen
    assert "outcome-blind replays" in main
    assert "original contemporaneously timestamped" in si
    assert "has **not** yet been recovered" in si
    assert "two separate five-run blocks" in si
    assert "after results from the first block were inspected" in si
    assert "0/5 zero-discrimination" in si
    assert "0/10" in si and "3/10" in si
    assert "three primary E2" in main.lower()
    assert "next-day retest" in main


def test_reader_evidence_and_current_scripts_stay_in_sync() -> None:
    main = read_text("manuscript/MAIN_TEXT_V5.md")
    evidence = read_text("docs/EXPERIMENTAL_EVIDENCE.md")
    bib = read_text("manuscript/references.bib")
    for string in ("RV-SSR-H", "NKY-25", "No. 27", "mPa·s"):
        assert string in main and string in evidence
    assert "NCO:OH equivalent ratio for this F1 resin-modified formulation is **1.82**" in evidence
    assert "mean absolute drift across the two F1 repeats (1.60%)" in evidence
    assert "original rheometer readings" in main
    assert "scripts/external_pur_raw_anchor.py" in main
    assert "scripts/spe_raw_anchor_audit.py" in main
    assert "Cisse2026ReasoningClosedLoop" in main
    assert "10.1039/D5DD00520E" in bib
