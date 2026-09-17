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
    patterns = result["discovered_patterns"]
    assert patterns["state_shift_master_curve"]["formulation_only_r2"] < patterns["state_shift_master_curve"]["state_aware_shared_shape_r2"]
    lo, hi = patterns["one_point_state_calibration"]["multiplicative_error_factor_range"]
    assert 1.0 < lo <= hi < 1.2
    assert "temporal_stability_coordinate" in patterns
    assert "F1" not in json.dumps(result, sort_keys=True)
