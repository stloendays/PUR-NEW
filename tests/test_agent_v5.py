"""Agent V5 chemistry-domain gate: admissibility, parity, blindness and V4 invariance.

These tests are the acceptance contract of the V5 implementation. They run without any API
key: every property they check is deterministic.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pur_new.agent_v5 import (
    ARMS,
    GATE_CARD_FIELDS,
    MANDATORY_LOCAL_SCIENCE_TOOL,
    SHAPE_DEPENDENT_MEASUREMENTS,
    InadmissibleSelectionError,
    admissible_cards,
    assess_candidate,
    audit_experiment_cards,
    audit_summary,
    build_voi_payload,
    card_for_model,
    chemistry_family,
    ensure_mandatory_tools,
    execute_planned_actions,
    freeze_experiment,
    load_verified_shape_transfer,
    mandatory_tool_executed,
    measurement_admissibility,
    tied_top_set,
)
from pur_new.evidence_firewall import (
    assert_blind_payload_clean,
    filter_evidence_state,
    find_blind_payload_violations,
)
from pur_new.voi import build_experiment_cards, load_hypothesis_registry, load_measurement_catalog

CANDIDATE_SET = ROOT / "derived" / "stage1_blind_candidate_space_v1.json"
BLINDED_IDS = {"F1"}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def candidates() -> list[dict]:
    return read_json(CANDIDATE_SET)["candidates"]


@pytest.fixture(scope="module")
def registry() -> dict:
    return load_hypothesis_registry()


@pytest.fixture(scope="module")
def catalog() -> dict:
    return load_measurement_catalog()


@pytest.fixture(scope="module")
def cards(candidates, registry, catalog) -> list[dict]:
    return build_experiment_cards(candidates, registry=registry, catalog=catalog)


@pytest.fixture(scope="module")
def verified() -> dict:
    return load_verified_shape_transfer()


@pytest.fixture(scope="module")
def audits(cards, candidates, verified) -> dict[str, dict]:
    return {
        arm: audit_experiment_cards(
            cards, candidates=candidates, enforce=(arm == "V5_FULL"), verified=verified
        )
        for arm in ARMS
    }


def local_family_candidate(candidates: list[dict]) -> dict:
    return next(
        candidate
        for candidate in candidates
        if chemistry_family(candidate) == "unmodified_ppg2000_pdp70_mdi"
    )


def resin_modified_candidate(candidates: list[dict]) -> dict:
    return next(
        candidate
        for candidate in candidates
        if chemistry_family(candidate).startswith("resin_modified")
    )


# 1. resin-modified + M-ANCHOR is blocked without a verified sweep
def test_resin_modified_anchor_is_blocked_without_verified_sweep(candidates, verified):
    candidate = resin_modified_candidate(candidates)
    assessment = assess_candidate(candidate, verified=verified)
    rule = measurement_admissibility("M-ANCHOR", assessment)

    assert assessment["has_prior_verified_shape_transfer"] is False
    assert rule["measurement_admissible"] is False
    assert rule["admissibility_rule_id"] == "inadmissible_before_shape_verification"
    assert "M-SWEEP" in rule["required_precondition"]


# 2. unmodified local-family + M-ANCHOR remains allowed
def test_local_family_anchor_remains_allowed(candidates, verified):
    candidate = local_family_candidate(candidates)
    assessment = assess_candidate(candidate, verified=verified)
    rule = measurement_admissibility("M-ANCHOR", assessment)

    assert assessment["shared_shape_use"] == "allowed_with_state_anchor"
    assert rule["measurement_admissible"] is True
    assert rule["admissibility_rule_id"] == "admissible_shared_shape_supported"


# 3. resin-modified + M-SWEEP remains allowed, as do the other direct measurements
def test_resin_modified_direct_measurements_remain_allowed(candidates, verified):
    candidate = resin_modified_candidate(candidates)
    assessment = assess_candidate(candidate, verified=verified)

    for measurement_id in ("M-SWEEP", "M-HOLD-120", "M-REPEAT"):
        rule = measurement_admissibility(measurement_id, assessment)
        assert rule["measurement_admissible"] is True, measurement_id
        assert rule["required_precondition"] is None


def test_versioned_prior_sweep_unblocks_the_anchor(candidates):
    """The exemption path exists, is versioned, and is the only way past the rule."""
    candidate = resin_modified_candidate(candidates)
    family = chemistry_family(candidate)
    verified = {
        "version": "test",
        "verified_chemistry_families": [
            {
                "chemistry_family": family,
                "verified_by_measurement": "M-SWEEP",
                "record": "test-only fixture",
            }
        ],
    }
    rule = measurement_admissibility("M-ANCHOR", assess_candidate(candidate, verified=verified))

    assert rule["measurement_admissible"] is True
    assert rule["admissibility_rule_id"] == "admissible_prior_verified_shape_transfer"


# 4. blocked cards never enter the VOI ranked set
def test_blocked_cards_never_enter_the_voi_ranked_set(audits):
    audit = audits["V5_FULL"]
    blocked = set(audit["deterministically_inadmissible_experiment_ids"])
    ranked = admissible_cards(audit)
    ranked_ids = {card["experiment_id"] for card in ranked}

    assert blocked, "the gate must block something in this candidate lattice"
    assert not (blocked & ranked_ids)
    assert len(ranked) == audit["n_cards_total"] - audit["n_cards_deterministically_inadmissible"]
    assert all(card["measurement_id"] in SHAPE_DEPENDENT_MEASUREMENTS for card in audit["cards"] if card["experiment_id"] in blocked)

    payload = build_voi_payload(ranked, top_k=12, enforced=True, audit=audit)
    payload_ids = {card["experiment_id"] for card in payload["top_cards"]}
    assert not (blocked & payload_ids)
    assert payload["chemistry_domain_gate"]["n_cards_removed"] == len(blocked)
    # the ranked set the model sees is the post-gate set, not a re-ranked full set
    assert payload["n_experiment_cards"] == len(ranked)


def test_control_arm_ranks_every_card_and_sees_no_applicability_field(audits, cards):
    audit = audits["V5_NO_GATE"]
    ranked = admissible_cards(audit)
    assert len(ranked) == len(cards)

    payload = build_voi_payload(ranked, top_k=12, enforced=False, audit=audit)
    assert "chemistry_domain_gate" not in payload
    serialized = json.dumps(payload, sort_keys=True)
    for field in GATE_CARD_FIELDS:
        assert field not in serialized
    assert "shared_shape" not in serialized
    assert "admissib" not in serialized

    # With the gate disabled the projection is byte-identical to the pre-gate VOI card.
    by_id = {card["experiment_id"]: card for card in cards}
    for card in payload["top_cards"]:
        assert card == by_id[card["experiment_id"]]


# 5. a model output naming a blocked experiment is rejected at freeze
def test_freeze_rejects_a_selection_the_gate_removed(audits):
    audit = audits["V5_FULL"]
    ranked = admissible_cards(audit)
    blocked_id = audit["deterministically_inadmissible_experiment_ids"][0]
    candidate_id, measurement_id = blocked_id.split("::")
    judge = {
        "decision_mode": "committed_experiment",
        "selected_experiment_id": blocked_id,
        "selected_candidate_id": candidate_id,
        "selected_measurement_id": measurement_id,
        "acceptance_criterion": "x",
        "falsification_criterion": "y",
    }
    kwargs = dict(
        arm="V5_FULL",
        gate_enforced=True,
        cards_by_id={card["experiment_id"]: card for card in audit["cards"]},
        admissible_by_id={card["experiment_id"]: card for card in ranked},
        tied=tied_top_set(ranked),
        audit_summary=audit_summary(audit),
        hashes={
            "prompt_hash": "p",
            "input_hash": "i",
            "candidate_set_hash": "c",
            "hypothesis_registry_hash": "h",
            "measurement_catalog_hash": "m",
            "verified_shape_transfer_hash": "v",
        },
        model="test-model",
        workflow_version="test",
        architecture_version="5.0.0",
        inspection_status="test",
        claim_boundary="test",
        frozen_utc="2026-01-01T00:00:00Z",
        recommendation_digest="deadbeef01",
    )

    with pytest.raises(InadmissibleSelectionError):
        freeze_experiment(judge, **kwargs)

    # the same judge output is a valid decision when the card was never removed
    allowed_id = ranked[0]["experiment_id"]
    allowed_candidate, allowed_measurement = allowed_id.split("::")
    ok = freeze_experiment(
        {
            **judge,
            "selected_experiment_id": allowed_id,
            "selected_candidate_id": allowed_candidate,
            "selected_measurement_id": allowed_measurement,
        },
        **kwargs,
    )
    assert ok["selected_experiment_id"] == allowed_id
    assert ok["chemistry_gate"]["selection"]["chemistry_domain_violation"] is False


def test_freeze_records_a_control_arm_domain_violation_without_blocking_it(audits):
    """The control arm may commit a violating selection; the audit must still name it."""
    audit = audits["V5_NO_GATE"]
    ranked = admissible_cards(audit)
    violating = next(card for card in ranked if not card["deterministic_measurement_admissible"])
    candidate_id, measurement_id = violating["experiment_id"].split("::")
    frozen = freeze_experiment(
        {
            "decision_mode": "committed_experiment",
            "selected_experiment_id": violating["experiment_id"],
            "selected_candidate_id": candidate_id,
            "selected_measurement_id": measurement_id,
            "acceptance_criterion": "x",
            "falsification_criterion": "y",
        },
        arm="V5_NO_GATE",
        gate_enforced=False,
        cards_by_id={card["experiment_id"]: card for card in audit["cards"]},
        admissible_by_id={card["experiment_id"]: card for card in ranked},
        tied=tied_top_set(ranked),
        audit_summary=audit_summary(audit),
        hashes={
            "prompt_hash": "p",
            "input_hash": "i",
            "candidate_set_hash": "c",
            "hypothesis_registry_hash": "h",
            "measurement_catalog_hash": "m",
            "verified_shape_transfer_hash": "v",
        },
        model="test-model",
        workflow_version="test",
        architecture_version="5.0.0",
        inspection_status="test",
        claim_boundary="test",
        frozen_utc="2026-01-01T00:00:00Z",
        recommendation_digest="deadbeef02",
    )
    selection = frozen["chemistry_gate"]["selection"]
    assert selection["chemistry_domain_violation"] is True
    assert selection["unsupported_shortcut"] is True


# 6. the two arms use byte-identical candidate, hypothesis and measurement inputs
def test_primary_arms_share_byte_identical_scientific_inputs(audits, cards):
    def canonical(value) -> str:
        return hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()

    pre_gate = canonical(cards)
    for arm in ARMS:
        audit = audits[arm]
        stripped = [
            {
                key: value
                for key, value in card.items()
                if key
                not in set(GATE_CARD_FIELDS)
                | {
                    "deterministic_measurement_admissible",
                    "deterministic_admissibility_reason",
                    "deterministic_admissibility_rule_id",
                    "deterministic_required_precondition",
                    "gate_enforced",
                }
            }
            for card in audit["cards"]
        ]
        assert canonical(stripped) == pre_gate, arm

    assert canonical(read_json(CANDIDATE_SET)) == canonical(read_json(CANDIDATE_SET))
    assert canonical(load_hypothesis_registry()) == canonical(load_hypothesis_registry())
    assert canonical(load_measurement_catalog()) == canonical(load_measurement_catalog())

    # The deterministic verdict itself is arm-independent: only enforcement differs.
    verdicts = {
        arm: {
            card["experiment_id"]: card["deterministic_measurement_admissible"]
            for card in audits[arm]["cards"]
        }
        for arm in ARMS
    }
    assert verdicts["V5_NO_GATE"] == verdicts["V5_FULL"]
    assert audits["V5_NO_GATE"]["n_cards_removed_from_ranked_set"] == 0
    assert audits["V5_FULL"]["n_cards_removed_from_ranked_set"] > 0


# 7. held-out identity and outcome cannot enter the planner or any downstream payload
def test_held_out_identity_and_outcome_never_enter_a_model_payload(audits, registry, catalog):
    profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    evidence = filter_evidence_state(
        read_json(ROOT / "derived" / "evidence_state.json"),
        policy=profiles["blind_pre_result"],
        blinded_formulation_ids=BLINDED_IDS,
    )
    assert_blind_payload_clean(evidence, blinded_formulation_ids=BLINDED_IDS)

    for arm in ARMS:
        audit = audits[arm]
        ranked = admissible_cards(audit)
        payload = {
            "filtered_evidence_state": evidence,
            "hypothesis_registry": registry,
            "measurement_catalog": catalog,
            "voi": build_voi_payload(
                ranked, top_k=12, enforced=(arm == "V5_FULL"), audit=audit
            ),
        }
        assert find_blind_payload_violations(payload, blinded_formulation_ids=BLINDED_IDS) == []
        # The evidence layer legitimately declares WHICH formulation is blinded; the experiment
        # and VOI layer must not mention it at all.
        decision_layer = json.dumps(
            {key: value for key, value in payload.items() if key != "filtered_evidence_state"},
            sort_keys=True,
        )
        assert "F1" not in decision_layer
        assert "follow_up" not in decision_layer
        # The access-profile declaration names the follow-up switches; no DATA row may carry
        # the follow-up stage, which is what the structural check above enforces.
        assert all(
            row.get("stage") != "follow_up"
            for row in payload["filtered_evidence_state"].get("thermal_hold", {}).get("runs", [])
        )

    # every model payload in the runner passes through the blind-payload guard
    source = (ROOT / "scripts" / "run_agent_v5.py").read_text(encoding="utf-8")
    for name in ("planner_payload", "proposer_payload", "skeptic_payload", "robustness_payload", "judge_payload"):
        assert f"guard({name})" in source, name


# 8. the mandatory chemistry-audited summary is always executed
def test_mandatory_chemistry_audited_summary_is_always_executed():
    for requests in ([], None, [{"name": "get_candidate_hypothesis", "args": {}}]):
        forced = ensure_mandatory_tools(requests)
        assert forced[0]["name"] == MANDATORY_LOCAL_SCIENCE_TOOL
        assert forced[0]["forced_by_architecture"] is True

    already = [{"name": MANDATORY_LOCAL_SCIENCE_TOOL, "args": {}, "reason": "planner asked"}]
    assert ensure_mandatory_tools(already) == already

    trace = execute_planned_actions(
        ensure_mandatory_tools([{"name": "not_an_action", "args": {}}]),
        include_follow_up=False,
        blind_target_formulation_ids=BLINDED_IDS,
    )
    assert mandatory_tool_executed(trace) is True
    # one malformed request degrades that request only
    assert [item["status"] for item in trace] == ["ok", "invalid_arguments"]
    summary = next(item for item in trace if item["name"] == MANDATORY_LOCAL_SCIENCE_TOOL)
    assert summary["result"]["validation_formulation_visible"] is False


def test_predecessor_rheology_tool_is_not_a_v5_planner_action():
    trace = execute_planned_actions(
        [{"name": "get_state_aware_rheology_summary", "args": {}}],
        include_follow_up=False,
        blind_target_formulation_ids=BLINDED_IDS,
    )
    assert trace[0]["status"] == "invalid_arguments"


# 9. V4 files and frozen result directories remain unchanged
def test_v4_inputs_and_frozen_results_are_unchanged_by_v5():
    """Every V4-defining input and every frozen V4 result file still hashes to the baseline.

    The baseline was captured at the commit V5 was implemented from, so this test fails the
    moment the V5 work edits a V4 input, a V4 prompt or a frozen V4 record.
    """
    baseline = read_json(ROOT / "configs" / "v4_invariance_baseline.json")
    assert baseline["v4_input_files"], "baseline must list the V4 input files"
    assert len(baseline["frozen_v4_result_files"]) > 100

    changed = [
        name
        for group in ("v4_input_files", "frozen_v4_result_files")
        for name, digest in baseline[group].items()
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != digest
    ]
    assert changed == [], f"V5 changed frozen V4 material: {changed}"


def test_v5_never_writes_into_a_frozen_v4_directory():
    for name in ("scripts/run_agent_v5.py", "scripts/run_agent_v5_series.py", "src/pur_new/agent_v5.py"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "agent_v4_voi" not in text
        assert "EXP_V4_" not in text


def test_v5_run_directories_are_named_apart_from_v4():
    assert "EXP_V5_" in (ROOT / "src" / "pur_new" / "agent_v5.py").read_text(encoding="utf-8")
    source = (ROOT / "scripts" / "run_agent_v5.py").read_text(encoding="utf-8")
    assert "Refusing to overwrite a frozen V5 run" in source
    assert "EXP_V5_" in (ROOT / "scripts" / "run_agent_v5_series.py").read_text(encoding="utf-8")


def test_gate_output_is_machine_readable_for_every_card(audits):
    required = (
        "candidate_id",
        "measurement_id",
        "experiment_id",
        "chemistry_applicability_status",
        "shared_shape_use",
        "measurement_admissible",
        "admissibility_reason",
        "chemistry_family",
        "voi_components",
        "voi_score",
    )
    audit = audits["V5_FULL"]
    for card in audit["cards"]:
        for field in required:
            assert field in card, field
        if not card["deterministic_measurement_admissible"]:
            assert card["deterministic_required_precondition"]
    assert audit["inadmissible_by_rule_id"] == {
        "inadmissible_before_shape_verification": audit["n_cards_deterministically_inadmissible"]
    }
    assert len(audit["candidate_assessments"]) == len(
        {card["candidate_id"] for card in audit["cards"]}
    )


def test_gate_does_not_depend_on_mutating_the_input_cards(cards, candidates, verified):
    before = copy.deepcopy(cards)
    audit_experiment_cards(cards, candidates=candidates, enforce=True, verified=verified)
    assert cards == before


def _load_comparison_module():
    spec = importlib.util.spec_from_file_location(
        "run_agent_v5_comparison", ROOT / "scripts" / "run_agent_v5_comparison.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / "scripts"))
    spec.loader.exec_module(module)
    return module


def _manifest(arm: str, **overrides) -> dict:
    manifest = {
        "arm": arm,
        "gate_enforced": arm == "V5_FULL",
        "series_label": f"series_{arm.lower()}",
        "model": "test-model",
        "api_base_host": "example.test",
        "candidate_set_sha256": "abc",
        "evidence_state_sha256": "def",
        "n_runs_declared": 10,
        "top_k": 12,
        "series_input_hashes": {name: "same" for name in _load_comparison_module().ARM_PARITY_FILES},
        "runs": [],
    }
    manifest.update(overrides)
    return manifest


def test_comparison_parity_check_passes_for_a_correctly_declared_pair():
    module = _load_comparison_module()
    parity = module.check_parity({"V5_NO_GATE": _manifest("V5_NO_GATE"), "V5_FULL": _manifest("V5_FULL")})
    assert parity["parity_ok"] is True
    assert parity["differences"] == []


def test_comparison_parity_check_catches_a_drifted_arm():
    module = _load_comparison_module()
    drifted = _manifest("V5_FULL", model="other-model")
    drifted["series_input_hashes"]["prompts/agent_v5_judge.txt"] = "changed"
    parity = module.check_parity({"V5_NO_GATE": _manifest("V5_NO_GATE"), "V5_FULL": drifted})
    assert parity["parity_ok"] is False
    assert any("agent_v5_judge.txt" in item for item in parity["differences"])
    assert any("model" in item for item in parity["differences"])


def test_comparison_reports_both_denominators(tmp_path):
    module = _load_comparison_module()
    manifest = _manifest("V5_FULL")
    rows = [
        {column: None for column in module.CSV_COLUMNS} | {"run_index": 1, "status": "ok", "decision_mode": "committed_experiment", "chemistry_domain_violation": True, "unsupported_shortcut": True, "selected_experiment_id": "S1C41::M-ANCHOR"},
        {column: None for column in module.CSV_COLUMNS} | {"run_index": 2, "status": "ok", "decision_mode": "abstain"},
        {column: None for column in module.CSV_COLUMNS} | {"run_index": 3, "status": "invalid"},
    ]
    summary = module.summarize_arm("V5_FULL", manifest, rows)
    assert summary["counts"] == {
        "declared": 10,
        "attempted": 3,
        "completed": 2,
        "committed": 1,
        "abstained": 1,
        "invalid": 1,
        "failed": 0,
    }
    shortcut = summary["primary_metrics"]["unsupported_shortcut_rate_over_committed"]
    assert shortcut["numerator"] == 1 and shortcut["denominator"] == 1
    declared = summary["primary_metrics"]["unsupported_shortcut_rate_over_declared"]
    assert declared["denominator"] == 10
