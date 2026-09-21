from pur_new.chemistry_tools import assess_shared_shape_applicability


def test_unmodified_local_family_allows_state_anchor_interpolation():
    result = assess_shared_shape_applicability(
        {"formulation_state": {"PPG2000": 40, "PDP70": 40, "MDI": 20, "AC1920": 0, "TK100": 0}}
    )
    assert result["status"] == "local_family_interpolation"
    assert result["shared_shape_use"] == "allowed_with_state_anchor"
    assert result["recommended_measurement"] == "M-ANCHOR"


def test_resin_modified_candidate_requires_direct_shape_verification():
    result = assess_shared_shape_applicability(
        {"formulation_state": {"PPG2000": 34, "PDP70": 34, "MDI": 17, "AC1920": 15, "TK100": 0}}
    )
    assert result["status"] == "modified_chemistry_unvalidated"
    assert result["shared_shape_use"] == "verification_only"
    assert result["recommended_measurement"] == "M-SWEEP"
    assert result["modifier_fraction"] == 0.15
