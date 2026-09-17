#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R_GAS = 8.31446261815324


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def linear_fit(x: list[float], y: list[float]) -> tuple[float, float, float]:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("matched x/y sequences with n>=2 are required")
    x_bar = statistics.fmean(x)
    y_bar = statistics.fmean(y)
    sxx = sum((xi - x_bar) ** 2 for xi in x)
    if sxx == 0:
        raise ValueError("x values must vary")
    slope = sum((xi - x_bar) * (yi - y_bar) for xi, yi in zip(x, y, strict=True)) / sxx
    intercept = y_bar - slope * x_bar
    fitted = [intercept + slope * xi for xi in x]
    ss_res = sum((yi - fi) ** 2 for yi, fi in zip(y, fitted, strict=True))
    ss_tot = sum((yi - y_bar) ** 2 for yi in y)
    r2 = 1.0 - ss_res / ss_tot if ss_tot else 1.0
    return slope, intercept, r2


def state_key(row: dict[str, str]) -> str:
    return f"{row['formulation_id']}|{row['run_label']}|retest={row['retest_after_1d'].lower()}"


def fit_temperature_group(rows: list[dict[str, str]]) -> dict[str, float]:
    x = [1.0 / (float(r["temperature_c"]) + 273.15) for r in rows]
    y = [math.log(float(r["viscosity_reported"])) for r in rows]
    slope, intercept, r2 = linear_fit(x, y)
    return {
        "slope_K": slope,
        "intercept": intercept,
        "r2": r2,
        "apparent_flow_activation_parameter_kJ_mol": slope * R_GAS / 1000.0,
    }


def temperature_realization_summary(rows: list[dict[str, str]]) -> dict:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[state_key(row)].append(row)

    fits = []
    for key, group in sorted(groups.items()):
        fit = fit_temperature_group(group)
        fits.append(
            {
                "state_id": key,
                "formulation_id": group[0]["formulation_id"],
                "run_label": group[0]["run_label"],
                "retest_after_1d": group[0]["retest_after_1d"].lower() == "true",
                "n_points": len(group),
                **fit,
            }
        )

    params = [x["apparent_flow_activation_parameter_kJ_mol"] for x in fits]
    r2s = [x["r2"] for x in fits]
    return {
        "n_realizations": len(fits),
        "per_realization": fits,
        "apparent_flow_parameter_summary_kJ_mol": {
            "mean": statistics.fmean(params),
            "sample_sd": statistics.stdev(params),
            "cv": statistics.stdev(params) / statistics.fmean(params),
            "min": min(params),
            "max": max(params),
        },
        "fit_r2_range": [min(r2s), max(r2s)],
        "interpretation_boundary": (
            "This is a descriptive Arrhenius/Andrade-like flow parameter from ln(viscosity) vs 1/T. "
            "It is not interpreted as a molecular reaction activation energy."
        ),
    }


def e2_nominal_spread(rows: list[dict[str, str]]) -> list[dict]:
    by_temp: dict[float, list[float]] = defaultdict(list)
    for row in rows:
        if row["formulation_id"] != "E2" or row["retest_after_1d"].lower() == "true":
            continue
        by_temp[float(row["temperature_c"])].append(float(row["viscosity_reported"]))

    output = []
    for temp, values in sorted(by_temp.items()):
        if len(values) < 2:
            continue
        mean = statistics.fmean(values)
        output.append(
            {
                "temperature_c": temp,
                "n_runs": len(values),
                "mean": mean,
                "sample_cv": statistics.stdev(values) / mean,
                "max_min_ratio": max(values) / min(values),
            }
        )
    return output


def _fit_predict(group: list[dict[str, str]], temperature_c: float) -> float:
    fit = fit_temperature_group(group)
    inv_t = 1.0 / (temperature_c + 273.15)
    return math.exp(fit["intercept"] + fit["slope_K"] * inv_t)


def leave_one_temperature_out(rows: list[dict[str, str]], *, e2_only: bool = False) -> dict:
    work = [
        r
        for r in rows
        if (
            not e2_only
            or (r["formulation_id"] == "E2" and r["retest_after_1d"].lower() == "false")
        )
    ]
    temperatures = sorted({float(r["temperature_c"]) for r in work})

    results = {}
    for mode in ("formulation_only", "realization_aware"):
        predictions = []
        for held_out_t in temperatures:
            train = [r for r in work if float(r["temperature_c"]) != held_out_t]
            test = [r for r in work if float(r["temperature_c"]) == held_out_t]
            for row in test:
                if mode == "formulation_only":
                    group = [r for r in train if r["formulation_id"] == row["formulation_id"]]
                else:
                    key = state_key(row)
                    group = [r for r in train if state_key(r) == key]
                pred = _fit_predict(group, held_out_t)
                obs = float(row["viscosity_reported"])
                predictions.append((obs, pred))

        ape = [abs(pred - obs) / obs for obs, pred in predictions]
        log_sq = [(math.log(pred) - math.log(obs)) ** 2 for obs, pred in predictions]
        results[mode] = {
            "n_predictions": len(predictions),
            "mape": statistics.fmean(ape),
            "log_rmse": math.sqrt(statistics.fmean(log_sq)),
        }

    results["interpretation_boundary"] = (
        "The realization-aware model conditions on run identity as a latent state proxy. "
        "This is an explanatory diagnostic, not a deployable predictor for unseen future batches."
    )
    return results


def hold_rate_summary(rows: list[dict[str, str]]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(row["formulation_id"], row["run_label"])].append(row)

    out = []
    for (formulation_id, run_label), group in sorted(groups.items()):
        x = [float(r["time_min"]) / 60.0 for r in group]
        y = [math.log(float(r["viscosity_reported"])) for r in group]
        slope, intercept, r2 = linear_fit(x, y)
        out.append(
            {
                "formulation_id": formulation_id,
                "run_label": run_label,
                "n_points": len(group),
                "log_linear_hold_rate_h-1": slope,
                "intercept": intercept,
                "r2": r2,
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Quantify temperature-shape conservation and realization sensitivity"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "derived" / "state_sensitivity_analysis.json",
    )
    args = parser.parse_args()

    temp_rows = read_csv(ROOT / "data" / "temperature_sweeps.csv")
    hold_rows = read_csv(ROOT / "data" / "thermal_hold.csv")

    result = {
        "analysis_id": "PUR_NEW_STATE_SENSITIVITY_V1",
        "source_files": ["data/temperature_sweeps.csv", "data/thermal_hold.csv"],
        "temperature_realizations": temperature_realization_summary(temp_rows),
        "e2_nominal_repeat_spread": e2_nominal_spread(temp_rows),
        "leave_one_temperature_out": {
            "all_recorded_realizations": leave_one_temperature_out(temp_rows),
            "e2_nominal_runs_only": leave_one_temperature_out(temp_rows, e2_only=True),
        },
        "thermal_hold_log_rate": hold_rate_summary(hold_rows),
        "claim_boundary": {
            "run_identity_is_latent_state_proxy_not_causal_variable": True,
            "apparent_flow_parameter_is_not_reaction_activation_energy": True,
            "flat_follow_up_should_be_compared_by_matched_window_SI_not_forced_kinetic_fit": True,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    temp_summary = result["temperature_realizations"][
        "apparent_flow_parameter_summary_kJ_mol"
    ]
    cv = result["leave_one_temperature_out"]["all_recorded_realizations"]
    print(
        f"apparent flow parameter: {temp_summary['mean']:.2f} +/- "
        f"{temp_summary['sample_sd']:.2f} kJ/mol; "
        f"formulation-only MAPE={cv['formulation_only']['mape']:.3f}; "
        f"realization-aware MAPE={cv['realization_aware']['mape']:.3f}"
    )
    print(args.output)


if __name__ == "__main__":
    main()
