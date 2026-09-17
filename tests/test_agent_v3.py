from __future__ import annotations

import pytest

from pur_new.actions import get_state_aware_rheology_summary
from pur_new.agent_v3 import pareto_front, selection_entropy
from pur_new.evidence_firewall import (
    assert_blind_payload_clean,
    filter_evidence_state,
    find_blind_payload_violations,
)


def test_blind_firewall_removes_follow_up_rows_and_identity():
    state = {
        "temperature_response": {"runs": [{"formulation_id": "E1"}], "nominal_repeat_spread": []},
        "thermal_hold": {
            "runs": [
                {"formulation_id": "E1", "stage": "original", "si": {"15_to_60": 0.1}},
                {"formulation_id": "F1", "stage": "follow_up", "si": {"15_to_60": 0.01}},
            ],
            "follow_up_mean_profiles": [
                {"formulation_id": "F1", "si_15_to_60_mean_profile": 0.015}
            ],
        },
    }
    policy = {
        "description": "blind test",
        "allow_original_temperature_sweeps": True,
        "allow_original_hold_data": True,
        "allow_follow_up_formulation_identity": False,
        "allow_follow_up_hold_results": False,
    }
    filtered = filter_evidence_state(state, policy=policy, blinded_formulation_ids={"F1"})
    assert filtered["thermal_hold"]["runs"] == [
        {"formulation_id": "E1", "stage": "original", "si": {"15_to_60": 0.1}}
    ]
    assert filtered["thermal_hold"]["follow_up_mean_profiles"] == []
    assert find_blind_payload_violations(filtered, blinded_formulation_ids={"F1"}) == []
    assert_blind_payload_clean(filtered, blinded_formulation_ids={"F1"})


def test_blind_firewall_detects_leakage():
    bad = {"thermal_hold": {"runs": [{"formulation_id": "F1", "stage": "follow_up"}]}}
    findings = find_blind_payload_violations(bad, blinded_formulation_ids={"F1"})
    assert len(findings) == 2
    with pytest.raises(ValueError, match="blind payload leakage detected"):
        assert_blind_payload_clean(bad, blinded_formulation_ids={"F1"})


def test_state_aware_rheology_action_reproduces_frozen_local_descriptors():
    summary = get_state_aware_rheology_summary()
    state = summary["state_shift_evidence"]
    thermal = summary["temperature_sensitivity"]

    assert summary["source_scope"] == "original pre-validation local data only"
    assert state["n_complete_realizations"] == 7
    assert state["non_anchor_cv_range"][0] == pytest.approx(0.0338594, rel=1e-4)
    assert state["non_anchor_cv_range"][1] == pytest.approx(0.103424, rel=1e-4)
    assert thermal["mean_apparent_E_eta_kJ_mol"] == pytest.approx(41.8680, rel=1e-4)
    assert thermal["sd_apparent_E_eta_kJ_mol"] == pytest.approx(2.26705, rel=1e-4)
    assert thermal["median_ln_eta_inverse_T_r2"] == pytest.approx(0.994776, rel=1e-4)


def test_pareto_front_is_weight_free():
    cards = [
        {
            "candidate_id": "A",
            "support_value": 3,
            "resin_modified": True,
            "process_risk_value": 0,
            "missing_process_field_count": 1,
            "active_axis_distance_pct_points": 0.0,
        },
        {
            "candidate_id": "B",
            "support_value": 2,
            "resin_modified": True,
            "process_risk_value": 1,
            "missing_process_field_count": 2,
            "active_axis_distance_pct_points": 2.0,
        },
        {
            "candidate_id": "C",
            "support_value": 3,
            "resin_modified": False,
            "process_risk_value": 0,
            "missing_process_field_count": 1,
            "active_axis_distance_pct_points": 0.0,
        },
    ]
    assert pareto_front(cards) == ["A"]


def test_selection_entropy_tracks_instability():
    assert selection_entropy(["A", "A", "A"]) == pytest.approx(0.0)
    assert selection_entropy(["A", "B"]) == pytest.approx(1.0)
    assert selection_entropy(["A", None]) == pytest.approx(1.0)
