#!/usr/bin/env python3
"""Freeze what the deterministic layer does under a condition, BEFORE any model call.

The Condition-B protocol claims a specific property of the deterministic layer: without
enforcement the top-ranked card is a gated M-ANCHOR, and with enforcement it becomes the
same candidate's M-SWEEP. That claim is checkable without an API key, so it is recorded
first. Writing it afterwards would make it unfalsifiable.

The record contains no model output and no held-out outcome. It is a statement about the
scoring tool and the gate, both of which are deterministic.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v5 import (  # noqa: E402
    audit_experiment_cards,
    canonical_hash,
    load_verified_shape_transfer,
    pre_enforcement_payload_hash,
    ranked_cards,
    tied_top_set,
)
from pur_new.conditions import load_condition  # noqa: E402
from pur_new.voi import BASE_WEIGHTS, build_experiment_cards  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def arm_view(audit: dict, *, enforce: bool, top_k: int) -> dict:
    selectable = ranked_cards(audit, enforce=enforce)
    tied = tied_top_set(selectable)
    top = selectable[0]
    strictly_lower = [c for c in selectable if c["voi_score"] < top["voi_score"] - 1e-9]
    best_per_measurement: dict[str, float] = {}
    for card in selectable:
        best_per_measurement.setdefault(card["measurement_id"], card["voi_score"])
    return {
        "applicability_gate_enforced": enforce,
        "n_selectable_cards": len(selectable),
        "top_experiment_id": top["experiment_id"],
        "top_candidate_id": top["candidate_id"],
        "top_measurement_id": top["measurement_id"],
        "top_voi_score": top["voi_score"],
        "top_voi_components": top["voi_components"],
        "top_card_is_admissible": top["measurement_admissible"],
        "top_card_admissibility_rule_id": top["admissibility_rule_id"],
        "tied_top_experiment_ids": tied,
        "n_tied_at_top": len(tied),
        "tied_top_measurement_ids": sorted({eid.split("::")[1] for eid in tied}),
        "margin_to_first_strictly_lower": (
            round(top["voi_score"] - strictly_lower[0]["voi_score"], 6) if strictly_lower else None
        ),
        "best_voi_per_measurement_plan": best_per_measurement,
        "top_k_experiment_ids": [card["experiment_id"] for card in selectable[:top_k]],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Pre-register the deterministic layer of a condition")
    parser.add_argument("--condition", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument(
        "--candidate-set", type=Path, default=ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
    )
    args = parser.parse_args()

    if args.output.exists():
        raise SystemExit(
            f"refusing to overwrite an existing pre-registration: {args.output}. A pre-registration "
            "is written once; a changed one is a new versioned file."
        )

    condition = load_condition(args.condition)
    weights = condition["weights"] or dict(BASE_WEIGHTS)
    candidates = json.loads(args.candidate_set.read_text(encoding="utf-8"))["candidates"]
    cards = build_experiment_cards(
        candidates, registry=condition["registry"], catalog=condition["catalog"], weights=weights
    )
    audit = audit_experiment_cards(
        cards, candidates=candidates, verified=load_verified_shape_transfer()
    )

    ungated = arm_view(audit, enforce=False, top_k=args.top_k)
    gated = arm_view(audit, enforce=True, top_k=args.top_k)

    record = {
        "record_id": f"PUR_NEW_CONDITION_{args.condition}_DETERMINISTIC_PREREGISTRATION",
        "written_utc": utc_now(),
        "written_before_any_model_call_for_this_condition": True,
        "git_commit": git_commit(),
        "condition_id": condition["condition_id"],
        "decision_question": condition["decision_question"],
        "protocol": condition["protocol"],
        "hypothesis_registry": condition["hypothesis_registry_path"],
        "measurement_catalog": condition["measurement_catalog_path"],
        "voi_weights": weights,
        "candidate_set": str(args.candidate_set),
        "candidate_set_sha256": canonical_hash(json.loads(args.candidate_set.read_text(encoding="utf-8"))),
        "pre_enforcement_payload_sha256": pre_enforcement_payload_hash(
            audit, top_k=args.top_k, weights=weights
        ),
        "n_cards_total": audit["n_cards_total"],
        "n_cards_inadmissible": audit["n_cards_inadmissible"],
        "inadmissible_by_rule_id": audit["inadmissible_by_rule_id"],
        "arms": {"V5_NO_GATE": ungated, "V5_FULL": gated},
        "gate_changes_the_deterministic_top_card": (
            ungated["top_experiment_id"] != gated["top_experiment_id"]
        ),
        "deterministic_contrast": {
            "ungated_top_measurement": ungated["top_measurement_id"],
            "gated_top_measurement": gated["top_measurement_id"],
            "ungated_top_is_gated_card": not ungated["top_card_is_admissible"],
        },
        "interpretation": (
            "This records only what the deterministic scoring tool and the gate do. It is not a "
            "prediction about the model and must not be reported as a result. The empirical "
            "question is whether the un-gated model follows this ranking to the inadmissible card."
        ),
        "no_model_output_in_this_record": True,
        "no_held_out_outcome_in_this_record": True,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"pre-registration written: {args.output}")
    print(
        f"  un-gated top: {ungated['top_experiment_id']} "
        f"(voi {ungated['top_voi_score']}, admissible={ungated['top_card_is_admissible']})"
    )
    print(
        f"  gated    top: {gated['top_experiment_id']} "
        f"(voi {gated['top_voi_score']}, admissible={gated['top_card_is_admissible']})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
