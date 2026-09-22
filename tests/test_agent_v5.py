"""Agent V5 chemistry-domain gate: admissibility, information parity, blindness, V4 invariance.

These tests are the acceptance contract of the V5 implementation under comparison protocol
v1.1. They run without any API key: every property they check is deterministic.
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
    ARM_ENFORCES_GATE,
    ARMS,
    AUDIT_CARD_FIELDS,
    MANDATORY_LOCAL_SCIENCE_TOOL,
    SHAPE_DEPENDENT_MEASUREMENTS,
    InadmissibleSelectionError,
    assess_candidate,
    audit_experiment_cards,
    audit_summary,
    build_pre_enforcement_payload,
    build_voi_payload,
    canonical_bytes,
    chemistry_family,
    ensure_mandatory_tools,
    execute_planned_actions,
    freeze_experiment,
    load_verified_shape_transfer,
    mandatory_tool_executed,
    measurement_admissibility,
    pre_enforcement_payload_hash,
    ranked_cards,
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
TOP_K = 12


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
def audit(cards, candidates, verified) -> dict:
    """One audit. Protocol v1.1: the audit cannot depend on the arm, so there is only one."""
    return audit_experiment_cards(cards, candidates=candidates, verified=verified)


def local_family_candidate(candidates: list[dict]) -> dict:
    return next(c for c in candidates if chemistry_family(c) == "unmodified_ppg2000_pdp70_mdi")


def resin_modified_candidate(candidates: list[dict]) -> dict:
    return next(c for c in candidates if chemistry_family(c).startswith("resin_modified"))


def freeze_kwargs(audit: dict, *, arm: str) -> dict:
    selectable = ranked_cards(audit, enforce=ARM_ENFORCES_GATE[arm])
    return dict(
        arm=arm,
        cards_by_id={card["experiment_id"]: card for card in audit["cards"]},
        selectable_by_id={card["experiment_id"]: card for card in selectable},
        tied=tied_top_set(selectable),
        audit_summary=audit_summary(audit, enforce=ARM_ENFORCES_GATE[arm], top_k=TOP_K),
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
        architecture_version="5.1.0",
        inspection_status="test",
        claim_boundary="test",
        frozen_utc="2026-01-01T00:00:00Z",
        recommendation_digest="deadbeef01",
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
            {"chemistry_family": family, "verified_by_measurement": "M-SWEEP", "record": "test fixture"}
        ],
    }
    rule = measurement_admissibility("M-ANCHOR", assess_candidate(candidate, verified=verified))

    assert rule["measurement_admissible"] is True
    assert rule["admissibility_rule_id"] == "admissible_prior_verified_shape_transfer"


# 4. blocked cards never enter the VOI ranked set of the enforced arm
def test_blocked_cards_never_enter_the_enforced_ranked_set(audit):
    blocked = set(audit["inadmissible_experiment_ids"])
    selectable = ranked_cards(audit, enforce=True)
    selectable_ids = {card["experiment_id"] for card in selectable}

    assert blocked, "the audit must block something in this candidate lattice"
    assert not (blocked & selectable_ids)
    assert len(selectable) == audit["n_cards_total"] - audit["n_cards_inadmissible"]
    assert all(
        card["measurement_id"] in SHAPE_DEPENDENT_MEASUREMENTS
        for card in audit["cards"]
        if card["experiment_id"] in blocked
    )

    payload = build_voi_payload(audit, top_k=TOP_K, enforce=True)
    payload_ids = {card["experiment_id"] for card in payload["voi"]["top_cards"]}
    assert not (blocked & payload_ids)
    assert payload["voi"]["n_experiment_cards"] == len(selectable)
    applicability = payload["chemistry_applicability_audit"]
    assert applicability["enforcement"] == "binding"
    assert applicability["n_cards_removed_from_selectable_set"] == len(blocked)


def test_advice_only_arm_keeps_every_card_selectable(audit, cards):
    selectable = ranked_cards(audit, enforce=False)
    assert len(selectable) == len(cards)

    payload = build_voi_payload(audit, top_k=TOP_K, enforce=False)
    applicability = payload["chemistry_applicability_audit"]
    assert applicability["enforcement"] == "advisory"
    assert applicability["n_cards_removed_from_selectable_set"] == 0
    assert payload["voi"]["n_experiment_cards"] == len(cards)
    # the control arm sees the SAME audit facts, it is simply not bound by them
    assert applicability["inadmissible_experiment_ids"] == audit["inadmissible_experiment_ids"]
    assert applicability["candidate_assessments"] == audit["candidate_assessments"]


# protocol v1.1 required parity test
def test_pre_enforcement_model_payload_is_byte_identical_across_arms(audit):
    """Serialize the model-visible pre-enforcement scientific payload and prove equality.

    The payload builder takes no arm argument, so the two arms cannot diverge before the
    enforcement step. This test freezes that property against future edits.
    """
    payloads = {}
    for arm in ARMS:
        full = build_voi_payload(audit, top_k=TOP_K, enforce=ARM_ENFORCES_GATE[arm])
        applicability = dict(full["chemistry_applicability_audit"])
        # remove only the explicit arm / enforcement identifiers
        for key in (
            "enforcement",
            "enforcement_note",
            "applicability_gate_enforced",
            "n_cards_removed_from_selectable_set",
        ):
            applicability.pop(key, None)
        payloads[arm] = canonical_bytes(
            {"chemistry_applicability_audit": applicability, "voi_pre_enforcement": build_pre_enforcement_payload(audit, top_k=TOP_K)["voi"]}
        )

    assert payloads["V5_NO_GATE"] == payloads["V5_FULL"]
    assert (
        pre_enforcement_payload_hash(audit, top_k=TOP_K)
        == audit_summary(audit, enforce=False, top_k=TOP_K)["pre_enforcement_payload_sha256"]
        == audit_summary(audit, enforce=True, top_k=TOP_K)["pre_enforcement_payload_sha256"]
    )
    # the applicability facts themselves are visible in both arms
    for arm in ARMS:
        applicability = build_voi_payload(audit, top_k=TOP_K, enforce=ARM_ENFORCES_GATE[arm])[
            "chemistry_applicability_audit"
        ]
        assert applicability["applicability_audit_visible_to_model"] is True
        assert len(applicability["candidate_assessments"]) == 73
        assert applicability["n_cards_inadmissible"] == audit["n_cards_inadmissible"]


def test_no_arm_identifier_leaks_into_the_audit(audit):
    serialized = json.dumps(audit, sort_keys=True)
    assert "V5_FULL" not in serialized
    assert "V5_NO_GATE" not in serialized
    assert audit["audit_is_arm_independent"] is True


# 5. a model output naming a blocked experiment is rejected at freeze in the enforced arm
def test_freeze_rejects_a_blocked_selection_under_enforcement(audit):
    blocked_id = audit["inadmissible_experiment_ids"][0]
    candidate_id, measurement_id = blocked_id.split("::")
    judge = {
        "decision_mode": "committed_experiment",
        "selected_experiment_id": blocked_id,
        "selected_candidate_id": candidate_id,
        "selected_measurement_id": measurement_id,
        "acceptance_criterion": "x",
        "falsification_criterion": "y",
    }
    with pytest.raises(InadmissibleSelectionError):
        freeze_experiment(judge, **freeze_kwargs(audit, arm="V5_FULL"))

    allowed = ranked_cards(audit, enforce=True)[0]
    allowed_candidate, allowed_measurement = allowed["experiment_id"].split("::")
    ok = freeze_experiment(
        {
            **judge,
            "selected_experiment_id": allowed["experiment_id"],
            "selected_candidate_id": allowed_candidate,
            "selected_measurement_id": allowed_measurement,
        },
        **freeze_kwargs(audit, arm="V5_FULL"),
    )
    assert ok["selected_experiment_id"] == allowed["experiment_id"]
    assert ok["chemistry_gate"]["selection"]["chemistry_domain_violation"] is False
    assert ok["chemistry_gate"]["applicability_gate_enforced"] is True


def test_advice_only_arm_commits_the_same_selection_and_records_the_violation(audit):
    """The control arm may commit a violating selection; the audit must still name it."""
    blocked_id = audit["inadmissible_experiment_ids"][0]
    candidate_id, measurement_id = blocked_id.split("::")
    frozen = freeze_experiment(
        {
            "decision_mode": "committed_experiment",
            "selected_experiment_id": blocked_id,
            "selected_candidate_id": candidate_id,
            "selected_measurement_id": measurement_id,
            "acceptance_criterion": "x",
            "falsification_criterion": "y",
        },
        **freeze_kwargs(audit, arm="V5_NO_GATE"),
    )
    selection = frozen["chemistry_gate"]["selection"]
    assert selection["chemistry_domain_violation"] is True
    assert selection["unsupported_shortcut"] is True
    assert frozen["chemistry_gate"]["applicability_gate_enforced"] is False


# 6. the two arms use byte-identical candidate, hypothesis and measurement inputs
def test_primary_arms_share_byte_identical_scientific_inputs(audit, cards):
    def canonical(value) -> str:
        return hashlib.sha256(canonical_bytes(value)).hexdigest()

    stripped = [
        {key: value for key, value in card.items() if key not in set(AUDIT_CARD_FIELDS)}
        for card in audit["cards"]
    ]
    assert canonical(stripped) == canonical(cards)

    # the selectable sets differ only by the enforced removal
    no_gate = {c["experiment_id"] for c in ranked_cards(audit, enforce=False)}
    full = {c["experiment_id"] for c in ranked_cards(audit, enforce=True)}
    assert no_gate - full == set(audit["inadmissible_experiment_ids"])
    assert full - no_gate == set()


# 7. held-out identity and outcome cannot enter the planner or any downstream payload
def test_held_out_identity_and_outcome_never_enter_a_model_payload(audit, registry, catalog):
    profiles = read_json(ROOT / "configs" / "evidence_access_profiles.json")["profiles"]
    evidence = filter_evidence_state(
        read_json(ROOT / "derived" / "evidence_state.json"),
        policy=profiles["blind_pre_result"],
        blinded_formulation_ids=BLINDED_IDS,
    )
    assert_blind_payload_clean(evidence, blinded_formulation_ids=BLINDED_IDS)

    for arm in ARMS:
        voi = build_voi_payload(audit, top_k=TOP_K, enforce=ARM_ENFORCES_GATE[arm])
        payload = {
            "filtered_evidence_state": evidence,
            "hypothesis_registry": registry,
            "measurement_catalog": catalog,
            **voi,
        }
        assert find_blind_payload_violations(payload, blinded_formulation_ids=BLINDED_IDS) == []
        # The evidence layer legitimately declares WHICH formulation is blinded; the
        # experiment and VOI layer must not mention it at all.
        decision_layer = json.dumps(
            {key: value for key, value in payload.items() if key != "filtered_evidence_state"},
            sort_keys=True,
        )
        assert "F1" not in decision_layer
        assert "follow_up" not in decision_layer
        assert all(
            row.get("stage") != "follow_up"
            for row in evidence.get("thermal_hold", {}).get("runs", [])
        )

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
    """Every V4-defining input and frozen V4 result still hashes to the V5-start baseline.

    Protocol v1.1: this baseline proves only that the V5 work caused no further drift. It is
    not a reconstruction of the original V4 source tree, and the pre-existing drift stays
    recorded in the baseline file rather than repaired.
    """
    baseline = read_json(ROOT / "configs" / "v4_invariance_baseline.json")
    assert baseline["v4_input_files"], "baseline must list the V4 input files"
    assert len(baseline["frozen_v4_result_files"]) > 100
    assert baseline["preexisting_series_manifest_drift"]["drifted_inputs_by_manifest"]

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


def test_gate_output_is_machine_readable_for_every_card(audit):
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
    for card in audit["cards"]:
        for field in required:
            assert field in card, field
        if not card["measurement_admissible"]:
            assert card["required_precondition"]
    assert audit["inadmissible_by_rule_id"] == {
        "inadmissible_before_shape_verification": audit["n_cards_inadmissible"]
    }
    assert len(audit["candidate_assessments"]) == len({c["candidate_id"] for c in audit["cards"]})


def test_gate_does_not_mutate_the_input_cards(cards, candidates, verified):
    before = copy.deepcopy(cards)
    audit_experiment_cards(cards, candidates=candidates, verified=verified)
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
        "applicability_audit_visible_to_model": True,
        "applicability_gate_enforced": ARM_ENFORCES_GATE[arm],
        "series_label": f"series_{arm.lower()}",
        "model": "test-model",
        "api_base_host": "example.test",
        "candidate_set_sha256": "abc",
        "evidence_state_sha256": "def",
        "n_runs_declared": 10,
        "top_k": TOP_K,
        "pre_enforcement_payload_sha256": "parity-hash",
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


def test_comparison_parity_check_catches_unequal_pre_enforcement_payloads():
    module = _load_comparison_module()
    drifted = _manifest("V5_FULL", pre_enforcement_payload_sha256="different-hash")
    parity = module.check_parity({"V5_NO_GATE": _manifest("V5_NO_GATE"), "V5_FULL": drifted})
    assert parity["parity_ok"] is False
    assert any("pre_enforcement_payload" in item for item in parity["differences"])


def test_comparison_reports_both_denominators():
    module = _load_comparison_module()
    manifest = _manifest("V5_FULL")
    blank = {column: None for column in module.CSV_COLUMNS}
    rows = [
        blank | {"run_index": 1, "status": "ok", "decision_mode": "committed_experiment", "chemistry_domain_violation": True, "unsupported_shortcut": True, "selected_experiment_id": "S1C41::M-ANCHOR"},
        blank | {"run_index": 2, "status": "ok", "decision_mode": "abstain"},
        blank | {"run_index": 3, "status": "invalid"},
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
    assert summary["primary_metrics"]["unsupported_shortcut_rate_over_declared"]["denominator"] == 10
