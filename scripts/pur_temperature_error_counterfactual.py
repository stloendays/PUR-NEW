#!/usr/bin/env python3
"""Temperature-miscalibration counterfactual for repeated nominal E2 PUR sweeps.

This tests a *mathematical alternative* to a realization-dependent viscosity
level: what effective temperature error would be needed to create the
measured high-vs-low E2 viscosity ratio at a given nominal temperature?
The shared descriptive apparent flow parameter E_eta is not a reaction
barrier and the equivalent delta-T is NOT a measured thermometer bias.

Assumed local Andrade null: eta(T) = C exp(E_eta / (R T)).
A constant measurement-temperature discrepancy is NOT fitted or claimed.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R_GAS_J_MOL_K = 8.314462618
OUT = ROOT / "analysis/results/local_temperature_error_counterfactual_20261014"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def equivalent_colder_offset(t_c: float, ratio: float, e_kj_mol: float) -> float:
    """Solve eta(T - dt)/eta(T) = ratio for dt under the local Andrade null."""
    if ratio <= 1 or e_kj_mol <= 0:
        raise ValueError("Expected positive E and a viscosity ratio above unity")
    tk = t_c + 273.15
    tk_effective = 1.0 / (
        1.0 / tk + R_GAS_J_MOL_K / (e_kj_mol * 1000.0) * math.log(ratio)
    )
    return tk - tk_effective


def colder_ratio(t_c: float, delta_c: float, e_kj_mol: float) -> float:
    tk = t_c + 273.15
    if tk <= delta_c:
        raise ValueError("Invalid shift")
    return math.exp(
        (e_kj_mol * 1000.0 / R_GAS_J_MOL_K)
        * (1.0 / (tk - delta_c) - 1.0 / tk)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    fits = read_rows(ROOT / "analysis/results/local_thermal_curve_fits.csv")
    metadata = read_rows(ROOT / "data/realization_metadata.csv")
    primary = {
        row["realization_id"]
        for row in metadata
        if row["analysis_role"] in ("primary", "primary_with_caveat")
    }
    audited = [
        float(row["apparent_E_kJ_mol"])
        for row in fits
        if row["realization_id"] in primary
    ]
    if len(audited) != 6:
        raise ValueError("The primary chemistry population must be six curves")
    e_mean = statistics.mean(audited)
    e_sd = statistics.stdev(audited)

    sweep = read_rows(ROOT / "data/temperature_sweeps.csv")
    def get(label: str) -> dict[float, float]:
        d = {
            float(row["temperature_c"]): float(row["viscosity_reported"])
            for row in sweep
            if row["formulation_id"] == "E2"
            and row["run_label"] == label
            and row["retest_after_1d"].lower() == "false"
        }
        if len(d) != 6:
            raise ValueError(f"Missing 80–130 °C E2 curve for {label}")
        return d

    low, high = get("R01"), get("R03")
    if set(low) != set(high):
        raise ValueError("High/low source temperatures differ")
    rows: list[dict] = []
    for temp in sorted(low):
        ratio = high[temp] / low[temp]
        rows.append(
            {
                "temperature_c": temp,
                "eta_E2_R01_mPa_s": low[temp],
                "eta_E2_R03_mPa_s": high[temp],
                "viscosity_ratio_R03_over_R01": ratio,
                "equivalent_colder_offset_c": equivalent_colder_offset(temp, ratio, e_mean),
                "equivalent_colder_offset_EminusSD_c": equivalent_colder_offset(temp, ratio, e_mean - e_sd),
                "equivalent_colder_offset_EplusSD_c": equivalent_colder_offset(temp, ratio, e_mean + e_sd),
                "ratio_from_1c_bias": colder_ratio(temp, 1.0, e_mean),
                "ratio_from_2c_bias": colder_ratio(temp, 2.0, e_mean),
            }
        )
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    with (out / "per_temperature.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    offsets = [r["equivalent_colder_offset_c"] for r in rows]
    ratios = [r["viscosity_ratio_R03_over_R01"] for r in rows]
    max_2c = max(r["ratio_from_2c_bias"] for r in rows)
    report = {
        "status": "Counterfactual analytic transformation of existing measurements; no additional wet-lab data",
        "source_sweeps": "data/temperature_sweeps.csv",
        "source_apparent_E": "analysis/results/local_thermal_curve_fits.csv",
        "chemistry_audited_realizations": 6,
        "apparent_E_mean_kJ_mol": e_mean,
        "apparent_E_sample_sd_kJ_mol": e_sd,
        "viscosity_ratio_range": [min(ratios), max(ratios)],
        "equivalent_colder_offset_c_range": [min(offsets), max(offsets)],
        "max_viscosity_ratio_from_2c_bias": max_2c,
        "source_pairs": "Nominal E2 R03 / E2 R01, no one-day retests",
        "interpretation": (
            "Under a constant apparent E_eta Andrade null, the observed same-temperature "
            "E2 contrast corresponds to a temperature displacement much larger than a "
            "hypothetical 1–2 C bias. These displacements are not observed thermometer "
            "offsets and do not identify the molecular cause of the state variation."
        ),
    }
    (out / "summary.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.check:
        assert len(rows) == 6
        assert abs(e_mean - 42.05) < 0.015
        assert 24.0 < min(offsets) < 25.0
        assert 35.0 < max(offsets) < 36.0
        assert max_2c < 1.10
        assert min(ratios) > 2.75 and max(ratios) > 3.5
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
