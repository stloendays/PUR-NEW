"""Tests for the deterministic Agent V4 VOI tool.

The central test in this file is `test_voi_is_not_distance_to_the_held_out_formulation`:
it loads the held-out composition (which the Agent runtime never sees) purely to prove
that the score does not encode it.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from pur_new.voi import (
    BASE_WEIGHTS,
    POSITIVE_TERMS,
    RISK_TERMS,
    build_experiment_cards,
    hypothesis_discrimination,
    load_hypothesis_registry,
    load_measurement_catalog,
    predict_drift,
    reactive_mass_fraction,
    voi_robustness_sweep,
)

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_SET = ROOT / "derived" / "stage1_blind_candidate_space_v1.json"


@pytest.fixture(scope="module")
def candidates() -> list[dict]:
    return json.loads(CANDIDATE_SET.read_text(encoding="utf-8"))["candidates"]


@pytest.fixture(scope="module")
def cards(candidates) -> list[dict]:
    return build_experiment_cards(candidates)


@pytest.fixture(scope="module")
def held_out_modifier_coordinates() -> tuple[float, float]:
    """The held-out F1 composition, normalized to total weight percent.

    Used ONLY to assert that the VOI score is independent of it.
    """
    with (ROOT / "data" / "formulations.csv").open(newline="", encoding="utf-8") as handle:
        row = next(item for item in csv.DictReader(handle) if item["formulation_id"] == "F1")
    parts = {key: float(row[key]) for key in ("ppg2000", "pdp70", "ac1920", "tk100", "mdi")}
    total = sum(parts.values())
    return 100.0 * parts["ac1920"] / total, 100.0 * parts["tk100"] / total


def test_every_card_carries_the_required_experiment_fields(cards):
    required = (
        "candidate_id",
        "measurement_plan",
        "scientific_hypotheses_addressed",
        "acceptance_criterion",
        "falsification_criterion",
    )
    for card in cards:
        for field in required:
            assert card[field], f"{card['experiment_id']} missing {field}"
        assert card["measurement_plan"]["primary_observable"]


def test_components_are_normalized_to_the_unit_interval(cards):
    for card in cards:
        for name, value in card["voi_components"].items():
            assert 0.0 <= value <= 1.0, f"{card['experiment_id']}.{name} = {value}"


def test_weight_terms_cover_every_component_exactly_once(cards):
    assert set(POSITIVE_TERMS) | set(RISK_TERMS) == set(BASE_WEIGHTS)
    assert not set(POSITIVE_TERMS) & set(RISK_TERMS)
    assert set(cards[0]["voi_components"]) == set(BASE_WEIGHTS)


def test_voi_is_not_distance_to_the_held_out_formulation(cards, held_out_modifier_coordinates):
    """Two experiments at very different distances from the held-out point score identically.

    S1C41 is the lattice node nearest the held-out composition. S1C61 is far from it on the
    acrylic axis. If VOI encoded proximity to the answer, these could not tie.
    """
    target_acrylic, target_tackifier = held_out_modifier_coordinates
    by_id = {card["experiment_id"]: card for card in cards}
    near = by_id["S1C41::M-HOLD-120"]
    far = by_id["S1C61::M-HOLD-120"]

    def l1(card: dict) -> float:
        return abs(card["acrylic_like_pct"] - target_acrylic) + abs(
            card["minor_tackifier_like_pct"] - target_tackifier
        )

    assert l1(far) > l1(near) + 5.0
    assert near["voi_score"] == far["voi_score"]
    assert near["voi_components"] == far["voi_components"]


def test_no_held_out_coordinate_appears_in_the_voi_layer():
    forbidden = ("14.004", "4.1189", "4.1190", "1230", "1320", "1281", "1228")
    sources = [
        ROOT / "src" / "pur_new" / "voi.py",
        ROOT / "configs" / "hypothesis_registry.json",
        ROOT / "configs" / "measurement_catalog.json",
        ROOT / "configs" / "agent_v4.json",
    ]
    for path in sources:
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path.name} contains held-out token {token}"


def test_only_the_hold_measurement_discriminates_the_registered_hypotheses(candidates):
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    dual_axis = next(c for c in candidates if c["candidate_id"] == "S1C41")
    scores = {
        measurement["measurement_id"]: hypothesis_discrimination(dual_axis, measurement, registry)["score"]
        for measurement in catalog["measurements"]
    }
    assert scores["M-HOLD-120"] > 0.0
    assert all(value == 0.0 for key, value in scores.items() if key != "M-HOLD-120")


def test_reactive_core_only_composition_cannot_separate_any_hypothesis(candidates):
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    hold = next(m for m in catalog["measurements"] if m["measurement_id"] == "M-HOLD-120")
    core_only = next(
        c
        for c in candidates
        if float(c["formulation_state"].get("AC1920", 0.0) or 0.0) == 0.0
        and float(c["formulation_state"].get("TK100", 0.0) or 0.0) == 0.0
    )
    assert hypothesis_discrimination(core_only, hold, registry)["score"] == 0.0


def test_acrylic_only_and_dual_axis_leave_different_hypothesis_pairs_entangled(candidates):
    registry = load_hypothesis_registry()
    catalog = load_measurement_catalog()
    hold = next(m for m in catalog["measurements"] if m["measurement_id"] == "M-HOLD-120")
    by_id = {c["candidate_id"]: c for c in candidates}
    acrylic_only = next(
        c
        for c in candidates
        if float(c["formulation_state"]["AC1920"]) > 0 and float(c["formulation_state"]["TK100"]) == 0
    )
    dual = by_id["S1C41"]

    acrylic_pairs = {tuple(p) for p in hypothesis_discrimination(acrylic_only, hold, registry)["separated_pairs"]}
    dual_pairs = {tuple(p) for p in hypothesis_discrimination(dual, hold, registry)["separated_pairs"]}

    # An acrylic-only hold separates H-RESIN from H-DUAL, because only H-DUAL requires
    # the tackifier axis to reach the low-drift regime. A dual-axis hold cannot: both
    # predict suppression there. This is why one experiment cannot close all three.
    assert acrylic_pairs != dual_pairs
    assert ("H-RESIN", "H-DUAL") in acrylic_pairs
    assert ("H-RESIN", "H-DUAL") not in dual_pairs
    assert ("H-CORE", "H-DUAL") in dual_pairs
    assert ("H-CORE", "H-DUAL") not in acrylic_pairs


def test_prediction_rules_follow_the_registered_statements(candidates):
    registry = load_hypothesis_registry()
    reference = float(registry["reference_observations"]["E1_drift_15_60_pct"])
    by_id = {c["candidate_id"]: c for c in candidates}
    dual = by_id["S1C41"]
    phi_r = reactive_mass_fraction(dual)
    hypotheses = {h["hypothesis_id"]: h for h in registry["hypotheses"]}

    assert predict_drift(hypotheses["H-CORE"], dual, reference) == pytest.approx(reference * phi_r)
    assert predict_drift(hypotheses["H-RESIN"], dual, reference) == pytest.approx(0.5 * reference * phi_r)
    assert predict_drift(hypotheses["H-DUAL"], dual, reference) == pytest.approx(0.5 * reference * phi_r)


def test_reactive_mass_fraction_is_below_one_for_modified_compositions(candidates):
    by_id = {c["candidate_id"]: c for c in candidates}
    assert reactive_mass_fraction(by_id["S1C41"]) < 1.0
    core_only = next(
        c
        for c in candidates
        if float(c["formulation_state"].get("AC1920", 0.0) or 0.0) == 0.0
        and float(c["formulation_state"].get("TK100", 0.0) or 0.0) == 0.0
    )
    assert reactive_mass_fraction(core_only) == pytest.approx(1.0)


def test_ties_are_reported_rather_than_broken_silently(cards):
    best = max(card["voi_score"] for card in cards)
    tied = [card for card in cards if card["voi_score"] == best]
    assert len(tied) > 1
    assert len({json.dumps(card["voi_components"], sort_keys=True) for card in tied}) == 1


def test_decision_stability_is_set_based_and_not_called_confidence(candidates):
    sweep = voi_robustness_sweep(candidates)
    assert sweep["metric_name"] == "decision_stability"
    assert "confidence" in sweep["metric_is_not"]
    assert sweep["n_tied_at_base_top"] > 1
    assert set(sweep["stability"]) == {
        "top_experiment_set_stability",
        "top_experiment_set_mean_jaccard",
        "intervention_family_stability",
        "measurement_plan_stability",
    }
    for value in sweep["stability"].values():
        assert 0.0 <= value <= 1.0
    assert sweep["base_margin_to_first_strictly_lower"] > 0.0


def test_v3_artifacts_are_untouched_by_the_v4_layer():
    """V4 must be additive. These V3 inputs are read, never written, by V4."""
    for path in (
        ROOT / "configs" / "agent_v3.json",
        ROOT / "src" / "pur_new" / "agent_v3.py",
        ROOT / "prompts" / "agent_v3_judge.txt",
    ):
        assert path.exists()
    v4_sources = (ROOT / "src" / "pur_new" / "voi.py").read_text(encoding="utf-8")
    assert "write_text" not in v4_sources
    assert "open(" not in v4_sources
