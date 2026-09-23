from __future__ import annotations

import json

from pur_new.agent_v3 import execute_planned_actions


def test_v3_planner_action_uses_enriched_scientific_tool():
    trace = execute_planned_actions(
        [
            {
                "name": "get_state_aware_rheology_summary",
                "args": {},
                "reason": "Use the upstream physical/model findings before candidate ranking.",
            }
        ],
        include_follow_up=False,
        blind_target_formulation_ids={"F1"},
    )
    assert len(trace) == 1
    assert trace[0]["status"] == "ok"
    result = trace[0]["result"]
    assert result["validation_formulation_visible"] is False
    assert result["tool_version"] == "3.6-state-anchor-bridge"
    assert result["provenance_audit"]["excluded_from_primary_state_model"] == ["E1__+P__day1_0"]

    patterns = result["discovered_patterns"]
    state = patterns["state_shift_master_curve"]
    assert state["formulation_only_r2"] < state["state_aware_shared_shape_r2"]
    assert state["model_free_check"]["pc1_explained_between_realization_variance_fraction"] > 0.99
    assert state["model_free_check"]["pc1_constant_vertical_shift_cosine_similarity"] > 0.99

    lo, hi = patterns["one_point_state_calibration"]["pooled_multiplicative_error_factor_range"]
    assert 1.0 < lo <= hi < 1.2

    bridge = patterns["same_formulation_anchor_information_gain"]
    assert bridge["n_held_realizations"] == 4
    assert bridge["anchor_temperature_c"] == 110.0
    assert bridge["target_temperatures_c"] == [120.0, 130.0]
    assert bridge["formulation_only_multiplicative_error"] > 1.8
    assert bridge["one_anchor_multiplicative_error"] < 1.1
    assert bridge["log_rmse_reduction_fraction"] > 0.85

    assert "temporal_stability_coordinate" in patterns

    perturb = patterns["chemical_perturbation_check"]
    assert perturb["condition"]["additive"] == "H3PO4"
    assert perturb["condition"]["amount_mmol"] == 0.025
    assert perturb["condition"]["standard_solution_concentration_mol_L"] == 0.1
    assert perturb["condition"]["addition_stage"] == "dehydration_stage"
    assert perturb["shared_shape_intercept_only_multiplicative_error"] < 1.1
    assert perturb["anchor_120c_predict_remaining_temperatures_multiplicative_error"] < 1.1

    assert state["n_points"] == 36
    assert state["n_realizations"] == 6
    assert "F1" not in json.dumps(result, sort_keys=True)
