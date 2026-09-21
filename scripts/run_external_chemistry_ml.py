#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pur_new.external_ml import (
    build_external_thermal_response_report,
    load_pugar_feature_workbook,
    load_pugar_viscosity_workbook,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--curve-workbook", type=Path, required=True)
    parser.add_argument("--feature-workbook", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    curves = load_pugar_viscosity_workbook(args.curve_workbook)
    features = load_pugar_feature_workbook(args.feature_workbook)
    report, merged, low_fit = build_external_thermal_response_report(curves, features)

    (args.output_dir / "external_thermal_response_report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    merged.to_csv(args.output_dir / "external_thermal_response_samples.csv", index=False)
    low_fit.to_csv(args.output_dir / "external_thermal_response_low_fit_curves.csv", index=False)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
