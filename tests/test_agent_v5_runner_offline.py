"""End-to-end offline exercise of the Agent V5 runner.

The five model calls are replaced by canned stage outputs, so the whole runtime -- forced
tool execution, chemistry gate, VOI over the admissible set, freeze, schema validation and
the output contract -- is exercised without an API key and without spending a single token.

This is the test that catches a broken runner before a paid series is launched.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v5 import (  # noqa: E402
    admissible_cards,
    audit_experiment_cards,
    load_verified_shape_transfer,
)
from pur_new.voi import build_experiment_cards  # noqa: E402

REQUIRED_OUTPUTS = (
    "deliberation.json",
    "recommendation.json",
    "admissibility_audit.json",
    "experiment_cards.json",
    "decision_stability.json",
)


@pytest.fixture(scope="module")
def runner():
    spec = importlib.util.spec_from_file_location("run_agent_v5", ROOT / "scripts" / "run_agent_v5.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def gate_sets() -> dict[str, list[str]]:
    candidates = json.loads(
        (ROOT / "derived" / "stage1_blind_candidate_space_v1.json").read_text(encoding="utf-8")
    )["candidates"]
    cards = build_experiment_cards(candidates)
    audit = audit_experiment_cards(
        cards, candidates=candidates, enforce=True, verified=load_verified_shape_transfer()
    )
    return {
        "admissible_top": admissible_cards(audit)[0]["experiment_id"],
        "blocked": audit["deterministically_inadmissible_experiment_ids"][0],
    }


def make_call_json(selected_experiment_id: str):
    candidate_id, measurement_id = selected_experiment_id.split("::")
    meta = {
        "model": "offline-test-model",
        "latency_s": 0.0,
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
    }

    def call_json(client, *, model, system_prompt, payload):
        if system_prompt.startswith("You are the Planner"):
            return (
                {
                    "failure_mode": "thermal-hold viscosity drift at 120 C",
                    "scientific_question": "does resin modification suppress drift beyond dilution",
                    "least_resolved_coordinate": "isothermal time trajectory",
                    "action_requests": [
                        {"name": "get_candidate_hypothesis", "args": {}, "reason": "registry context"}
                    ],
                },
                dict(meta),
            )
        if system_prompt.startswith("You are the Proposer"):
            return (
                {
                    "proposed_experiment_id": selected_experiment_id,
                    "candidate_id": candidate_id,
                    "measurement_id": measurement_id,
                },
                dict(meta),
            )
        if system_prompt.startswith("You are the Skeptic"):
            return ({"objections": [], "strongest_objection": None}, dict(meta))
        if system_prompt.startswith("You are the Robustness Adjudicator"):
            return (
                {
                    "proposal_in_deterministic_top_set": True,
                    "preferred_experiment_id": selected_experiment_id,
                    "skeptic_objection_effect": "no_effect",
                },
                dict(meta),
            )
        if system_prompt.startswith("You are the Judge"):
            return (
                {
                    "decision_mode": "committed_experiment",
                    "selected_experiment_id": selected_experiment_id,
                    "selected_candidate_id": candidate_id,
                    "selected_measurement_id": measurement_id,
                    "primary_observable": "matched-window 15-60 min drift",
                    "hypotheses_addressed": ["H-CORE", "H-RESIN"],
                    "hypotheses_left_entangled": ["H-DUAL"],
                    "acceptance_criterion": "drift below 3.00 percent across two repeats",
                    "falsification_criterion": "drift at or above 6.00 percent falsifies H-RESIN",
                    "uncertainty_decomposition": {"measurement_uncertainty": "declared resolution"},
                    "rationale": "offline test decision",
                },
                dict(meta),
            )
        raise AssertionError(f"unexpected stage prompt: {system_prompt[:40]!r}")

    return call_json


def run_offline(runner, monkeypatch, tmp_path, *, arm: str, selected: str) -> None:
    monkeypatch.setattr(runner, "OpenAI", lambda **kwargs: object())
    monkeypatch.setattr(runner, "call_json", make_call_json(selected))
    monkeypatch.setenv("OPENAI_API_KEY", "offline-test")
    monkeypatch.setenv("OPENAI_MODEL", "offline-test-model")
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.setattr(
        sys, "argv", ["run_agent_v5.py", "--arm", arm, "--output-dir", str(tmp_path), "--top-k", "5"]
    )
    runner.main()


@pytest.mark.parametrize("arm", ["V5_NO_GATE", "V5_FULL"])
def test_runner_produces_the_full_output_contract(runner, gate_sets, monkeypatch, tmp_path, arm):
    run_offline(runner, monkeypatch, tmp_path, arm=arm, selected=gate_sets["admissible_top"])

    run_dirs = [path for path in tmp_path.iterdir() if path.name.startswith("EXP_V5_")]
    assert len(run_dirs) == 1
    run_dir = run_dirs[0]
    for name in REQUIRED_OUTPUTS:
        assert (run_dir / name).exists(), name

    recommendation = json.loads((run_dir / "recommendation.json").read_text(encoding="utf-8"))
    assert recommendation["arm"] == arm
    assert recommendation["gate_enforced"] is (arm == "V5_FULL")
    assert recommendation["selected_experiment_id"] == gate_sets["admissible_top"]
    assert recommendation["chemistry_gate"]["selection"]["chemistry_domain_violation"] is False
    for key in ("prompt_hash", "input_hash", "candidate_set_hash", "verified_shape_transfer_hash"):
        assert recommendation[key]

    deliberation = json.loads((run_dir / "deliberation.json").read_text(encoding="utf-8"))
    assert deliberation["mandatory_local_science_tool_executed"] is True
    assert deliberation["llm_usage_total"]["llm_calls"] == 5
    assert deliberation["llm_usage_total"]["total_tokens"] == 75

    voi_sent = deliberation["voi_sent_to_model"]
    audit = json.loads((run_dir / "admissibility_audit.json").read_text(encoding="utf-8"))
    cards = json.loads((run_dir / "experiment_cards.json").read_text(encoding="utf-8"))
    assert audit["n_cards_total"] == len(cards["cards"]) == 292
    assert audit["n_cards_deterministically_inadmissible"] > 0

    if arm == "V5_FULL":
        assert "chemistry_domain_gate" in voi_sent
        assert audit["n_cards_removed_from_ranked_set"] == audit["n_cards_deterministically_inadmissible"]
        assert len(cards["ranked_admissible_experiment_ids"]) == 292 - audit["n_cards_removed_from_ranked_set"]
        assert gate_sets["blocked"] not in cards["ranked_admissible_experiment_ids"]
    else:
        assert "chemistry_domain_gate" not in voi_sent
        assert audit["n_cards_removed_from_ranked_set"] == 0
        assert len(cards["ranked_admissible_experiment_ids"]) == 292
        # the control arm is never told the rule exists
        assert "shared_shape_use" not in json.dumps(voi_sent)


def test_gated_arm_rejects_a_blocked_selection_as_an_invalid_run(runner, gate_sets, monkeypatch, tmp_path):
    with pytest.raises(SystemExit) as excinfo:
        run_offline(runner, monkeypatch, tmp_path, arm="V5_FULL", selected=gate_sets["blocked"])
    assert excinfo.value.code == runner.EXIT_INVALID_MODEL_OUTPUT

    assert not [path for path in tmp_path.iterdir() if path.name.startswith("EXP_V5_")]
    rejected = json.loads(
        (tmp_path / "REJECTED" / "rejected_deliberation.json").read_text(encoding="utf-8")
    )
    assert rejected["rejection_class"] == "inadmissible_selection"
    assert gate_sets["blocked"] in rejected["rejection_reason"]
    assert rejected["judge_normalized"]["selected_experiment_id"] == gate_sets["blocked"]


def test_control_arm_accepts_the_same_selection_the_gate_would_block(runner, gate_sets, monkeypatch, tmp_path):
    """The two arms differ in enforcement, and the audit still records the violation."""
    run_offline(runner, monkeypatch, tmp_path, arm="V5_NO_GATE", selected=gate_sets["blocked"])

    run_dir = next(path for path in tmp_path.iterdir() if path.name.startswith("EXP_V5_"))
    recommendation = json.loads((run_dir / "recommendation.json").read_text(encoding="utf-8"))
    selection = recommendation["chemistry_gate"]["selection"]
    assert recommendation["selected_experiment_id"] == gate_sets["blocked"]
    assert selection["chemistry_domain_violation"] is True
    assert selection["unsupported_shortcut"] is True
    assert selection["admissibility_rule_id"] == "inadmissible_before_shape_verification"
