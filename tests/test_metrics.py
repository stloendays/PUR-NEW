from math import isclose

from pur_new.metrics import (
    coefficient_of_variation,
    hold_stability_index,
    max_min_ratio,
    mean_profile_si,
    stability_gain,
)


def test_hold_stability_indices_match_current_data():
    e1 = hold_stability_index(708.7, 776.1)
    e5 = hold_stability_index(2210.0, 3349.0)
    f1_r1 = hold_stability_index(1230.0, 1228.0)
    f1_r2 = hold_stability_index(1281.0, 1320.0)
    f1_mean = mean_profile_si([1230.0, 1281.0], [1228.0, 1320.0])

    assert isclose(e1, 0.09510371102017776, rel_tol=0, abs_tol=1e-12)
    assert isclose(e5, 0.5153846153846153, rel_tol=0, abs_tol=1e-12)
    assert isclose(f1_r1, -0.0016260162601626016, rel_tol=0, abs_tol=1e-12)
    assert isclose(f1_r2, 0.03044496487119438, rel_tol=0, abs_tol=1e-12)
    assert isclose(f1_mean, 0.014735165272799682, rel_tol=0, abs_tol=1e-12)


def test_descriptive_stability_gain_on_matched_window():
    e1 = hold_stability_index(708.7, 776.1)
    e5 = hold_stability_index(2210.0, 3349.0)
    f1_mean = mean_profile_si([1230.0, 1281.0], [1228.0, 1320.0])

    assert isclose(stability_gain(e1, f1_mean), 6.454200496531523, rel_tol=0, abs_tol=1e-9)
    assert isclose(stability_gain(e5, f1_mean), 34.97650727650727, rel_tol=0, abs_tol=1e-9)


def test_e2_repeat_spread_at_120_c():
    values = [1955.0, 4017.0, 6977.0]
    assert isclose(max_min_ratio(values), 6977.0 / 1955.0, rel_tol=0, abs_tol=1e-12)
    assert isclose(coefficient_of_variation(values), 0.5848356762251301, rel_tol=0, abs_tol=1e-12)
