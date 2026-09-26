#!/usr/bin/env python3
"""Run the preregistered Realization-Aware Evidence Integration diagnostic.

This is a separate diagnostic development line. It does not modify or reinterpret
frozen CRB/RGES/CBES records. Both evidence arms use the same chemistry-audited E2
measurements, the same decision question, the same measurement inventory and the same
five model stages. The only intended difference is whether realization structure and
its validated one-anchor consequence are visible to the Agent.

No held-out validation formulation or follow-up wet-lab outcome is loaded.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.scientific_tools import get_state_aware_rheology_summary_v3  # noqa: E402

PROTOCOL_PATH = ROOT / "configs" / "realization_evidence_ablation_v1.json"
TEMP_PATH = ROOT / "data" / "temperature_sweeps.csv"
META_PATH = ROOT / "data" / "realization_metadata.csv"
BRIDGE_PATH = ROOT / "derived" / "state_anchor_bridge" / "state_anchor_bridge_summary.json"

ARMS = ("NOMINAL_ONLY", "REALIZATION_AWARE")
PRIMARY_ROLES = {"primary", "primary_with_caveat"}


class ModelOutputError(ValueError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_hash(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def coefficient_of_variation(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    mean = statistics.fmean(values)
    if mean == 0:
        return None
    return statistics.stdev(values) / mean


def audited_e2_rows() -> list[dict[str, Any]]:
    meta = {row["realization_id"]: row for row in read_csv(META_PATH)}
    out: list[dict[str, Any]] = []
    for row in read_csv(TEMP_PATH):
        if row["formulation_id"] != "E2":
            continue
        retest = str(row["retest_after_1d"]).lower() == "true"
        rid = f"E2__{row['run_label']}__day1_{int(retest)}"
        m = meta.get(rid)
        if not m or m.get("analysis_role") not in PRIMARY_ROLES:
            continue
        out.append(
            {
                "realization_id": rid,
                "temperature_c": float(row["temperature_c"]),
                "viscosity_reported": float(row["viscosity_reported"]),
                "analysis_role": m["analysis_role"],
            }
        )
    if not out:
        raise RuntimeError("No chemistry-audited E2 rows were found")
    return out


def nominal_only_evidence(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_temp: dict[float, list[float]] = {}
    for row in rows:
        by_temp.setdefault(float(row["temperature_c"]), []).append(float(row["viscosity_reported"]))
    summaries = []
    for temp in sorted(by_temp):
        values = by_temp[temp]
        summaries.append(
            {
                "temperature_c": temp,
                "n_observations": len(values),
                "mean_viscosity": statistics.fmean(values),
                "min_viscosity": min(values),
                "max_viscosity": max(values),
                "sample_cv": coefficient_of_variation(values),
            }
        )
    return {
        "representation": "nominal formulation x temperature aggregation",
        "nominal_formulation": "E2",
        "chemistry_family": "unmodified_ppg2000_pdp70_mdi",
        "n_underlying_observations": len(rows),
        "n_realizations_in_source": len({row["realization_id"] for row in rows}),
        "temperature_summaries": summaries,
        "realization_identity_visible": False,
        "cross_temperature_pairing_visible": False,
        "state_conditioned_fit_visible": False,
        "one_anchor_validation_visible": False,
        "interpretation_boundary": (
            "These summaries establish substantial nominal-formulation spread at matched "
            "temperature but do not preserve which temperatures came from the same realization."
        ),
    }


def realization_aware_evidence(
    rows: list[dict[str, Any]], nominal: dict[str, Any]
) -> dict[str, Any]:
    by_realization: dict[str, list[dict[str, float]]] = {}
    for row in rows:
        by_realization.setdefault(row["realization_id"], []).append(
            {
                "temperature_c": float(row["temperature_c"]),
                "viscosity_reported": float(row["viscosity_reported"]),
            }
        )
    curves = [
        {
            "realization_id": rid,
            "points": sorted(points, key=lambda x: x["temperature_c"]),
        }
        for rid, points in sorted(by_realization.items())
    ]

    audited = get_state_aware_rheology_summary_v3()
    patterns = audited["discovered_patterns"]
    bridge = read_json(BRIDGE_PATH)

    return {
        "representation": "realization-aware state representation",
        "same_nominal_summary": nominal,
        "realization_identity_visible": True,
        "cross_temperature_pairing_visible": True,
        "e2_realization_curves": curves,
        "chemistry_audited_state_model": {
            "state_shift_master_curve": patterns["state_shift_master_curve"],
            "one_point_state_calibration_across_local_formulations": patterns[
                "one_point_state_calibration"
            ],
            "thermal_coordinate": patterns["thermal_coordinate"],
        },
        "same_formulation_e2_anchor_validation": {
            "analysis_population": bridge["analysis_population"],
            "anchor_temperature_c": bridge["anchor_temperature_c"],
            "target_temperatures_c": bridge["target_temperatures_c"],
            "n_held_realizations": bridge["n_held_realizations"],
            "n_predictions": bridge["n_predictions"],
            "formulation_only_multiplicative_rmse": bridge["formulation_only"][
                "multiplicative_rmse"
            ],
            "one_anchor_multiplicative_rmse": bridge["one_anchor_state_calibration"][
                "multiplicative_rmse"
            ],
            "log_rmse_reduction_fraction": bridge["log_rmse_reduction_fraction"],
            "cluster_bootstrap": bridge["cluster_bootstrap"],
            "interpretation": bridge["interpretation"],
            "agent_link": bridge["agent_link"],
        },
        "claim_boundary": [
            "The state/anchor evidence is local to the audited chemistry family.",
            "The task is explicitly inside that same unmodified E2 chemistry family.",
            "This evidence does not authorize one-point transfer after a chemistry shift.",
        ],
    }


def measurement_options(protocol: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "measurement_id": item["measurement_id"],
            "effort_points": item["effort_points"],
            "decision_quantity": item["decision_quantity"],
            "scientific_dependency": item["scientific_dependency"],
        }
        for item in protocol["measurement_inventory"]
    ]


def task_payload(protocol: dict[str, Any], arm: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "study": protocol["reader_facing_name"],
        "scientific_question": protocol["scientific_question"],
        "target_scenario": protocol["target_scenario"],
        "evidence_arm": arm,
        "scientific_evidence": evidence,
        "measurement_options": measurement_options(protocol),
        "selection_contract": [
            "Choose the lowest-burden measurement only after establishing that its scientific dependency is supported by the evidence supplied in this arm.",
            "Do not assume a cross-temperature transfer relation that is absent from the supplied evidence.",
            "A direct measurement may be preferable to a cheaper inferred measurement when the inference has not been validated.",
            "Do not use or speculate about any held-out validation formulation or future wet-lab outcome.",
        ],
    }


STAGE_PROMPTS = {
    "planner": """You are the Planner in a scientific experiment-selection Agent for reactive PUR.
You are choosing the next MEASUREMENT for a future realization of a fixed nominal formulation.
Do not select a measurement yet. Identify the target quantity, the dominant uncertainty, and the
specific evidence prerequisite that must be satisfied before a one-point anchor may replace a direct
temperature sweep. Use only the supplied evidence. Return JSON only:
{
  "target_quantity": "...",
  "dominant_uncertainty": "...",
  "anchor_prerequisite": "...",
  "evidence_for_anchor_prerequisite": "...",
  "decision_criteria": ["..."]
}""",
    "proposer": """You are the Proposer in a scientific experiment-selection Agent for reactive PUR.
Select exactly one listed measurement plan, or abstain if none is scientifically justified.
Minimize experimental burden only AFTER scientific sufficiency is established. A one-point anchor
is an inferred measurement and requires supplied evidence for cross-realization thermal-shape
transfer in the same chemistry. Return JSON only:
{
  "decision_mode": "commit|abstain",
  "selected_measurement_id": "M-ANCHOR|M-SWEEP|M-HOLD-120|M-REPEAT|null",
  "scientific_sufficiency": "supported|unsupported|uncertain",
  "evidence_used": ["..."],
  "reason": "...",
  "lower_burden_alternative_rejected_because": "..."
}""",
    "skeptic": """You are the Skeptic in a scientific experiment-selection Agent for reactive PUR.
Attack the proposed measurement, especially any inferred one-point shortcut. Check whether the
supplied evidence actually establishes its prerequisite, whether the target quantity is observed or
inferred, and whether a more direct plan is needed. Do not invent missing evidence. Return JSON only:
{
  "strongest_objection": "...",
  "severity": "low|moderate|high",
  "anchor_support": "established|not_established|uncertain",
  "target_quantity_resolved": true,
  "recommended_measurement_id": "M-ANCHOR|M-SWEEP|M-HOLD-120|M-REPEAT|abstain",
  "reason": "..."
}""",
    "robustness_adjudicator": """You are the Robustness Adjudicator in a scientific experiment-selection
Agent for reactive PUR. Decide whether the Proposer survives the Skeptic's strongest objection.
Scientific sufficiency has priority over cost; among sufficiently supported plans, prefer lower
experimental burden. Return JSON only:
{
  "proposal_survives": true,
  "recommended_measurement_id": "M-ANCHOR|M-SWEEP|M-HOLD-120|M-REPEAT|abstain",
  "change_required": true,
  "scientific_basis": "...",
  "remaining_uncertainty": "..."
}""",
    "judge": """You are the Judge in a scientific experiment-selection Agent for reactive PUR.
Commit to one listed measurement plan, or abstain. Resolve disagreements using the supplied
scientific evidence. The decision must answer the 120-130 C processing-window LEVEL question for a
future in-domain E2 realization; do not reward a cheap plan whose inference prerequisite is not
established. Return JSON only:
{
  "decision_mode": "commit|abstain",
  "selected_measurement_id": "M-ANCHOR|M-SWEEP|M-HOLD-120|M-REPEAT|null",
  "scientific_basis": "...",
  "why_not_the_main_alternative": "...",
  "claim_boundary": "..."
}""",
}


def extract_json_object(text: str) -> dict[str, Any]:
    stripped = text.strip()
    if stripped.startswith("~~~"):
        lines = stripped.splitlines()[1:]
        if lines and lines[-1].strip().startswith("~~~"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    try:
        value = json.loads(stripped)
    except json.JSONDecodeError:
        start, end = stripped.find("{"), stripped.rfind("}")
        if start < 0 or end <= start:
            raise ModelOutputError("model output did not contain a JSON object")
        try:
            value = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError as exc:
            raise ModelOutputError(f"model output JSON parse failed: {exc}") from exc
    if not isinstance(value, dict):
        raise ModelOutputError("model output must be a JSON object")
    return value


def call_stage(
    client: OpenAI,
    *,
    model: str,
    stage: str,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    started = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": STAGE_PROMPTS[stage]},
            {
                "role": "user",
                "content": json.dumps(payload, ensure_ascii=False, sort_keys=True),
            },
        ],
    )
    if not response.choices:
        raise RuntimeError(f"{stage}: API returned no choices")
    content = response.choices[0].message.content or ""
    parsed = extract_json_object(content)
    usage = getattr(response, "usage", None)
    usage_record = {
        "prompt_tokens": getattr(usage, "prompt_tokens", None),
        "completion_tokens": getattr(usage, "completion_tokens", None),
        "total_tokens": getattr(usage, "total_tokens", None),
        "latency_s": round(time.perf_counter() - started, 4),
    }
    return parsed, usage_record


def validate_measurement_id(value: Any, allowed: set[str], *, allow_abstain: bool = False) -> str | None:
    if value is None and allow_abstain:
        return None
    if value == "abstain" and allow_abstain:
        return None
    if not isinstance(value, str) or value not in allowed:
        raise ModelOutputError(f"invalid selected measurement: {value!r}")
    return value


def run_one(
    client: OpenAI,
    *,
    model: str,
    protocol: dict[str, Any],
    arm: str,
    evidence: dict[str, Any],
) -> dict[str, Any]:
    base = task_payload(protocol, arm, evidence)
    allowed = {item["measurement_id"] for item in protocol["measurement_inventory"]}
    usage: dict[str, dict[str, Any]] = {}

    planner, usage["planner"] = call_stage(
        client, model=model, stage="planner", payload=base
    )
    proposer, usage["proposer"] = call_stage(
        client,
        model=model,
        stage="proposer",
        payload={**base, "planner": planner},
    )
    validate_measurement_id(
        proposer.get("selected_measurement_id"),
        allowed,
        allow_abstain=proposer.get("decision_mode") == "abstain",
    )

    skeptic, usage["skeptic"] = call_stage(
        client,
        model=model,
        stage="skeptic",
        payload={**base, "planner": planner, "proposer": proposer},
    )
    validate_measurement_id(
        skeptic.get("recommended_measurement_id"), allowed, allow_abstain=True
    )

    robustness, usage["robustness_adjudicator"] = call_stage(
        client,
        model=model,
        stage="robustness_adjudicator",
        payload={
            **base,
            "planner": planner,
            "proposer": proposer,
            "skeptic": skeptic,
        },
    )
    validate_measurement_id(
        robustness.get("recommended_measurement_id"), allowed, allow_abstain=True
    )

    judge, usage["judge"] = call_stage(
        client,
        model=model,
        stage="judge",
        payload={
            **base,
            "planner": planner,
            "proposer": proposer,
            "skeptic": skeptic,
            "robustness_adjudication": robustness,
        },
    )
    mode = judge.get("decision_mode")
    if mode not in {"commit", "abstain"}:
        raise ModelOutputError(f"judge decision_mode must be commit|abstain, got {mode!r}")
    selected = validate_measurement_id(
        judge.get("selected_measurement_id"), allowed, allow_abstain=mode == "abstain"
    )
    if mode == "commit" and selected is None:
        raise ModelOutputError("commit requires a selected measurement")
    if mode == "abstain" and judge.get("selected_measurement_id") not in (None, "abstain"):
        raise ModelOutputError("abstain requires null selected_measurement_id")

    effort = None
    if selected is not None:
        effort = next(
            item["effort_points"]
            for item in protocol["measurement_inventory"]
            if item["measurement_id"] == selected
        )

    return {
        "status": "ok",
        "arm": arm,
        "model": model,
        "input_payload_sha256": canonical_hash(base),
        "planner": planner,
        "proposer": proposer,
        "skeptic": skeptic,
        "robustness_adjudication": robustness,
        "judge": judge,
        "decision_mode": mode,
        "selected_measurement_id": selected,
        "effort_points": effort,
        "proposer_measurement_id": proposer.get("selected_measurement_id"),
        "proposer_to_judge_reversal": (
            mode == "commit"
            and proposer.get("selected_measurement_id") != selected
        ),
        "llm_usage_by_stage": usage,
    }


def current_git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the RAEI diagnostic series")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-per-arm", type=int, default=5)
    parser.add_argument("--model", default=None)
    args = parser.parse_args()

    protocol = read_json(PROTOCOL_PATH)
    declared_n = int(protocol["run_design"]["diagnostic_runs_per_arm"])
    if args.n_per_arm != declared_n:
        raise SystemExit(
            f"Protocol declares N={declared_n} per arm; refusing invocation with N={args.n_per_arm}"
        )
    if args.output_dir.exists() and any(args.output_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {args.output_dir}")
    args.output_dir.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("OPENAI_API_KEY")
    model = args.model or os.environ.get("OPENAI_MODEL")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key or not model:
        raise SystemExit("OPENAI_API_KEY and OPENAI_MODEL are required")
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)

    rows = audited_e2_rows()
    nominal = nominal_only_evidence(rows)
    evidence_by_arm = {
        "NOMINAL_ONLY": nominal,
        "REALIZATION_AWARE": realization_aware_evidence(rows, nominal),
    }

    manifest = {
        "protocol_id": protocol["protocol_id"],
        "reader_facing_name": protocol["reader_facing_name"],
        "series_status": "declared_before_first_model_call",
        "declared_utc": utc_now(),
        "git_commit": current_git_commit(),
        "model": model,
        "n_per_arm": declared_n,
        "n_total_declared": declared_n * len(ARMS),
        "arms": list(ARMS),
        "run_order_rule": (
            "Interleaved by index; odd indices run NOMINAL_ONLY then REALIZATION_AWARE, "
            "even indices reverse the order."
        ),
        "input_hashes": {
            "protocol": sha256_file(PROTOCOL_PATH),
            "temperature_sweeps": sha256_file(TEMP_PATH),
            "realization_metadata": sha256_file(META_PATH),
            "state_anchor_bridge": sha256_file(BRIDGE_PATH),
            "runner": sha256_file(Path(__file__)),
        },
        "evidence_payload_hashes": {
            arm: canonical_hash(evidence_by_arm[arm]) for arm in ARMS
        },
        "reporting_rule": (
            "Every declared attempt is retained. Invalid model output and API/infrastructure "
            "failure are counted and are not silently replaced."
        ),
        "runs": [],
    }
    manifest_path = args.output_dir / "series_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    for index in range(1, declared_n + 1):
        order = ARMS if index % 2 else tuple(reversed(ARMS))
        for arm in order:
            started = utc_now()
            record: dict[str, Any] = {
                "run_index": index,
                "arm": arm,
                "started_utc": started,
            }
            try:
                result = run_one(
                    client,
                    model=model,
                    protocol=protocol,
                    arm=arm,
                    evidence=evidence_by_arm[arm],
                )
                record.update(result)
            except ModelOutputError as exc:
                record.update(
                    {
                        "status": "invalid",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            except Exception as exc:
                record.update(
                    {
                        "status": "failed",
                        "error_type": type(exc).__name__,
                        "error": str(exc),
                    }
                )
            record["finished_utc"] = utc_now()
            path = args.output_dir / f"run_{index:03d}_{arm.lower()}.json"
            path.write_text(
                json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            manifest["runs"].append(
                {
                    "run_index": index,
                    "arm": arm,
                    "status": record["status"],
                    "file": path.name,
                    "selected_measurement_id": record.get("selected_measurement_id"),
                    "decision_mode": record.get("decision_mode"),
                    "effort_points": record.get("effort_points"),
                }
            )
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            print(
                f"run {index}/{declared_n} {arm}: {record['status']} "
                f"{record.get('selected_measurement_id')}",
                flush=True,
            )

    manifest["finished_utc"] = utc_now()
    manifest["series_status"] = "complete"
    manifest["counts"] = {
        arm: {
            status: sum(
                1
                for row in manifest["runs"]
                if row["arm"] == arm and row["status"] == status
            )
            for status in ("ok", "invalid", "failed")
        }
        for arm in ARMS
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["counts"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
