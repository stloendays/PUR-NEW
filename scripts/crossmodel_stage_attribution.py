#!/usr/bin/env python3
"""Stage-level attribution of the gpt-5.6-sol vs gpt-5.6-luna decision differences.

Reads the frozen run-level table of the cross-model replication
(results/multimodel/gpt-5_6-sol/v4_benchmark, committed on agent-v5-implementation at
dc1f861) and asks at which deliberation stage the two base models diverge: does the
Proposer already depart from the deterministic geometry, or does a later stage
(Skeptic -> Robustness Adjudicator -> Judge) change a proposal that agreed with it?

For every run where the final experiment differs from the proposal, the Robustness
Adjudicator's preferred experiment is classified into the scientific move it represents.

Outputs go to analysis/results/upgrades_20261003/crossmodel_sol/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOL = Path(r"D:\Research\PUR-NEW\results\multimodel\gpt-5_6-sol\v4_benchmark")
OUT = ROOT / "analysis" / "results" / "upgrades_20261003" / "crossmodel_sol"

ARM_ORDER = [
    "rges_full_v4",
    "rges_voi_withheld",
    "rges_rule_order_minimality_first",
    "cbes_A_drift_V5_NO_GATE",
    "cbes_A_drift_V5_FULL",
    "cbes_B_processing_window_V5_NO_GATE",
    "cbes_B_processing_window_V5_FULL",
]


def truthy(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.lower().isin(["true", "1"])


def classify_change(row: pd.Series) -> str:
    final = str(row["selected_experiment_id"])
    if row["failure_category"] == "selection_outside_admissible_card_set":
        return "requested card outside the declared inventory (rejected at freeze)"
    if final.endswith("M-REPEAT"):
        return "replicated-preparation check before the direct measurement"
    if row["intervention_family"] == "acrylic_only":
        return "acrylic-only hold (separates H-RESIN from H-DUAL)"
    if final.split("::")[0] != str(row["proposer_experiment_id"]).split("::")[0]:
        return "different candidate, same measurement"
    return "different measurement"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sol-dir", type=Path, default=DEFAULT_SOL)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    src = args.sol_dir / "run_level_rows.csv"
    rows = pd.read_csv(src)
    rows = rows[rows["condition_key"].isin(ARM_ORDER)].copy()
    rows["attempted"] = 1
    rows["technical"] = truthy(rows["technical_failure"])
    valid = rows[~rows["technical"]].copy()
    for col in ("proposer_in_tied_top_set", "selected_in_tied_top_set", "final_differs_from_proposer",
                "final_decision_correct", "committed"):
        valid[col] = truthy(valid[col])
    valid["proposer_measurement"] = valid["proposer_experiment_id"].astype(str).str.split("::").str[-1]
    valid["invalid"] = valid["status"].eq("invalid")

    table = (
        valid.groupby(["condition_key", "model"])
        .agg(
            n_scientific=("run_id", "size"),
            n_invalid=("invalid", "sum"),
            proposer_in_tied_top_set=("proposer_in_tied_top_set", "sum"),
            final_in_tied_top_set=("selected_in_tied_top_set", "sum"),
            final_differs_from_proposer=("final_differs_from_proposer", "sum"),
            final_decision_correct=("final_decision_correct", "sum"),
        )
        .reset_index()
    )
    tech = rows.groupby(["condition_key", "model"])["technical"].sum().rename("n_technical_failure")
    table = table.merge(tech.reset_index(), on=["condition_key", "model"])
    table["condition_key"] = pd.Categorical(table["condition_key"], ARM_ORDER, ordered=True)
    table = table.sort_values(["condition_key", "model"])
    table.to_csv(OUT / "stage_attribution_by_arm.csv", index=False)

    proposer_measure = (
        valid.groupby(["condition_key", "model", "proposer_measurement"]).size().rename("n").reset_index()
    )
    proposer_measure.to_csv(OUT / "proposer_measurement_counts.csv", index=False)

    changed = valid[(valid["model"] == "gpt-5.6-sol") & (valid["final_differs_from_proposer"] | valid["invalid"])].copy()
    changed["robustness_move"] = changed.apply(classify_change, axis=1)
    moves = changed.groupby(["condition_key", "robustness_move"]).size().rename("n").reset_index()
    moves.to_csv(OUT / "sol_robustness_moves.csv", index=False)
    changed[["condition_key", "run_id", "proposer_experiment_id", "robustness_preferred_experiment_id",
             "selected_experiment_id", "status", "failure_category", "final_decision_correct",
             "robustness_move"]].to_csv(OUT / "sol_changed_runs.csv", index=False)

    summary = {
        "source": str(src),
        "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
        "source_commit": "dc1f861 (agent-v5-implementation)",
        "denominator_rule": "scientific denominator = attempted minus technical failures; invalid model outputs stay in",
        "by_arm": table.astype({"condition_key": str}).to_dict(orient="records"),
        "sol_robustness_moves": moves.to_dict(orient="records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=int) + "\n", encoding="utf-8")
    print(table.to_string(index=False))
    print(moves.to_string(index=False))
    print(proposer_measure[proposer_measure.condition_key.str.startswith(("cbes_B", "rges_full"))].to_string(index=False))


if __name__ == "__main__":
    main()
