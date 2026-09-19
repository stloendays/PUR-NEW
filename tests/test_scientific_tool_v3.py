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
    assert result["tool_version"] == "3.4-same-order-model-comparison"
    assert result["provenance_audit"]["excluded_from_primary_state_model"] == ["E1__+P__day1_0"]

    patterns = result["discovered_patterns"]
    state = patterns["state_shift_master_curve"]
    assert state["formulation_only_r2"] < state["state_aware_shared_shape_r2"]
    assert state["model_free_check"]["pc1_explained_between_realization_variance_fraction"] > 0.99
    assert state["model_free_check"]["pc1_constant_vertical_shift_cosine_similarity"] > 0.99

    lo, hi = patterns["one_point_state_calibration"]["pooled_multiplicative_error_factor_range"]
    assert 1.0 < lo <= hi < 1.2
    assert "temporal_stability_coordinate" in patterns
    assert "F1" not in json.dumps(result, sort_keys=True)
