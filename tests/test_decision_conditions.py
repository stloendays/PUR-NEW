"""Condition-B scoring seams, and the guarantee that Condition A is unchanged by them.

Two separate obligations are tested here:

1. **Regression.** Adding the Condition-B seams must not move a single Condition-A number.
   The check is against the frozen Condition-A run artifacts on disk, not against a
   recomputation of the same code, so a shared bug cannot hide the drift.
2. **Bite.** Under Condition B the gated measurement must actually be the top-ranked card
   without enforcement, and must actually disappear with enforcement. If that fails, the
   comparison is again incapable of measuring the gate and must not be run.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pur_new.agent_v5 import audit_experiment_cards, ranked_cards, tied_top_set
from pur_new.conditions import load_condition
from pur_new.voi import BASE_WEIGHTS, build_experiment_cards, predict_level_change

ROOT = Path(__file__).resolve().parents[1]
FROZEN_CONDITION_A_RUNS = sorted(
    (ROOT / "results" / "agent_v5" / "series_full_n10").glob("run_*/EXP_V5_*/experiment_cards.json")
)


def _candidates() -> list[dict]:
    space = json.loads(
        (ROOT / "derived" / "stage1_blind_candidate_space_v1.json").read_text(encoding="utf-8")
    )
    return space["candidates"]


def _condition_cards(condition_id: str) -> list[dict]:
    condition = load_condition(condition_id)
    weights = condition["weights"] or dict(BASE_WEIGHTS)
    return build_experiment_cards(
        _candidates(),
        registry=condition["registry"],
        catalog=condition["catalog"],
        weights=weights,
    )


# --------------------------------------------------------------------------- regression


@pytest.mark.skipif(
    not FROZEN_CONDITION_A_RUNS,
    reason="frozen Condition-A run artifacts are not present in this checkout",
)
def test_condition_a_scores_match_the_frozen_run_exactly() -> None:
    """Every Condition-A card still scores exactly what the frozen series recorded."""
    frozen = json.loads(FROZEN_CONDITION_A_RUNS[0].read_text(encoding="utf-8"))
    frozen_cards = frozen["cards"] if isinstance(frozen, dict) else frozen
    frozen_by_id = {card["experiment_id"]: card for card in frozen_cards}

    recomputed = {card["experiment_id"]: card for card in _condition_cards("A_drift")}

    assert set(recomputed) == set(frozen_by_id)
    for experiment_id, card in recomputed.items():
        reference = frozen_by_id[experiment_id]
        assert card["voi_score"] == reference["voi_score"], experiment_id
        for term, value in reference["voi_components"].items():
            assert card["voi_components"][term] == value, f"{experiment_id}:{term}"


def test_condition_a_declares_no_budget_component() -> None:
    """The drift catalog declares no effort, so the budget term must not exist at all."""
    for card in _condition_cards("A_drift"):
        assert "budget_efficiency" not in card["voi_components"]
        assert "budget_efficiency_detail" not in card


@pytest.mark.skipif(
    not FROZEN_CONDITION_A_RUNS,
    reason="frozen Condition-A run artifacts are not present in this checkout",
)
def test_condition_a_cards_are_structurally_identical_to_the_frozen_run() -> None:
    """Not just the scores: no key appears, disappears or changes value.

    The frozen artifact stores the audited cards, so the comparison runs the same
    deterministic audit the series ran before diffing.
    """
    frozen = json.loads(FROZEN_CONDITION_A_RUNS[0].read_text(encoding="utf-8"))
    frozen_cards = frozen["cards"] if isinstance(frozen, dict) else frozen
    frozen_by_id = {card["experiment_id"]: card for card in frozen_cards}

    audit = audit_experiment_cards(_condition_cards("A_drift"), candidates=_candidates())
    for card in audit["cards"]:
        assert card == frozen_by_id[card["experiment_id"]], card["experiment_id"]


# -------------------------------------------------------------------------------- bite


def test_condition_b_top_card_without_enforcement_is_the_gated_anchor() -> None:
    cards = _condition_cards("B_processing_window")
    audit = audit_experiment_cards(cards, candidates=_candidates())
    top = ranked_cards(audit, enforce=False)[0]

    assert top["measurement_id"] == "M-ANCHOR"
    assert top["resin_modified"] is True
    assert top["measurement_admissible"] is False
    assert top["admissibility_rule_id"] == "inadmissible_before_shape_verification"


def test_condition_b_enforcement_replaces_the_anchor_with_the_direct_sweep() -> None:
    cards = _condition_cards("B_processing_window")
    audit = audit_experiment_cards(cards, candidates=_candidates())
    ungated_top = ranked_cards(audit, enforce=False)[0]
    gated_top = ranked_cards(audit, enforce=True)[0]

    assert gated_top["measurement_id"] == "M-SWEEP"
    assert gated_top["candidate_id"] == ungated_top["candidate_id"]
    assert gated_top["measurement_admissible"] is True


def test_condition_b_measurement_choice_is_a_strict_preference() -> None:
    """The contrast is only interpretable if the top set agrees on ONE measurement plan.

    Ties across equivalent *candidates* are deliberate in this project and are left to the
    Agent. A tie across *measurement plans* would not be: the gate acts on the measurement,
    so a measurement-level tie would make the enforced and un-enforced tops indistinguishable.
    """
    cards = _condition_cards("B_processing_window")
    audit = audit_experiment_cards(cards, candidates=_candidates())

    expected = {False: "M-ANCHOR", True: "M-SWEEP"}
    for enforce, measurement_id in expected.items():
        selectable = ranked_cards(audit, enforce=enforce)
        tied = set(tied_top_set(selectable))
        assert {eid.split("::")[1] for eid in tied} == {measurement_id}

    ungated = ranked_cards(audit, enforce=False)
    best_anchor = max(c["voi_score"] for c in ungated if c["measurement_id"] == "M-ANCHOR")
    best_sweep = max(c["voi_score"] for c in ungated if c["measurement_id"] == "M-SWEEP")
    assert best_anchor > best_sweep


def test_condition_b_leaves_the_anchor_admissible_inside_the_measured_family() -> None:
    """The gate must block the shortcut outside the measured chemistry, not everywhere."""
    cards = _condition_cards("B_processing_window")
    audit = audit_experiment_cards(cards, candidates=_candidates())
    unmodified_anchors = [
        card
        for card in audit["cards"]
        if card["measurement_id"] == "M-ANCHOR" and not card["resin_modified"]
    ]
    assert unmodified_anchors
    assert all(card["measurement_admissible"] for card in unmodified_anchors)


# ------------------------------------------------------------------------- predictions


def test_unmodified_candidate_separates_no_level_hypothesis() -> None:
    """With no modifier every level hypothesis collapses to the same prediction."""
    condition = load_condition("B_processing_window")
    unmodified = next(
        candidate
        for candidate in _candidates()
        if not (
            float(candidate["formulation_state"].get("AC1920", 0.0) or 0.0)
            + float(candidate["formulation_state"].get("TK100", 0.0) or 0.0)
        )
    )
    predictions = {
        h["hypothesis_id"]: predict_level_change(h, unmodified, condition["registry"])
        for h in condition["registry"]["hypotheses"]
    }
    assert len(set(round(value, 9) for value in predictions.values())) == 1


def test_level_predictions_are_clipped_at_the_declared_floor() -> None:
    condition = load_condition("B_processing_window")
    registry = condition["registry"]
    floor = float(registry["prediction_floor_pct"])
    extreme = {
        "candidate_id": "SYNTHETIC-EXTREME",
        "formulation_state": {"PPG2000": 1.0, "PDP70": 1.0, "MDI": 1.0, "AC1920": 90.0, "TK100": 7.0},
    }
    values = [
        predict_level_change(h, extreme, registry) for h in registry["hypotheses"]
    ]
    assert min(values) >= floor
