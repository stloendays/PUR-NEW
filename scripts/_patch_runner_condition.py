"""One-shot source patch: give scripts/run_agent_v5.py a --condition selector.

Default ``A_drift`` resolves to the original registry, catalog and BASE_WEIGHTS, so an
invocation without the flag behaves exactly as the frozen Condition-A series did.
"""

from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "scripts" / "run_agent_v5.py"
source = TARGET.read_text(encoding="utf-8")
before = len(source)


def sub(old: str, new: str, label: str) -> None:
    global source
    found = source.count(old)
    if found != 1:
        raise SystemExit(f"ANCHOR FAIL [{label}]: found {found} occurrences, expected 1")
    source = source.replace(old, new)
    print(f"ok  {label}")


sub(
    '    parser.add_argument("--inspection-status", default="frozen_pre_result")',
    '    parser.add_argument("--inspection-status", default="frozen_pre_result")\n'
    '    parser.add_argument(\n'
    '        "--condition",\n'
    '        default=None,\n'
    '        help=(\n'
    '            "named decision condition from configs/decision_conditions.json. It fixes the "\n'
    '            "hypothesis registry, the measurement catalog and the VOI weights. Both arms of a "\n'
    '            "comparison must run under the same condition. Defaults to the declared default."\n'
    '        ),\n'
    '    )',
    "condition argument",
)

sub(
    '    registry = load_hypothesis_registry()\n    catalog = load_measurement_catalog()',
    '    condition = load_condition(args.condition)\n'
    '    registry = condition["registry"]\n'
    '    catalog = condition["catalog"]\n'
    '    voi_weights = condition["weights"] or dict(BASE_WEIGHTS)',
    "condition load",
)

sub(
    '    cards = build_experiment_cards(candidate_set["candidates"], registry=registry, catalog=catalog)',
    '    cards = build_experiment_cards(\n'
    '        candidate_set["candidates"], registry=registry, catalog=catalog, weights=voi_weights\n'
    '    )',
    "card build weights",
)

sub(
    '    gate = audit_summary(audit, enforce=gate_enforced, top_k=args.top_k)',
    '    gate = audit_summary(audit, enforce=gate_enforced, top_k=args.top_k, weights=voi_weights)',
    "audit_summary weights",
)

sub(
    '    sweep = decision_stability(selectable)',
    '    sweep = decision_stability(selectable, base_weights=voi_weights)',
    "decision_stability weights",
)

sub(
    '    voi_for_model = build_voi_payload(audit, top_k=args.top_k, enforce=gate_enforced)',
    '    voi_for_model = build_voi_payload(\n'
    '        audit, top_k=args.top_k, enforce=gate_enforced, weights=voi_weights\n'
    '    )',
    "build_voi_payload weights",
)

sub(
    '        "hypothesis_registry_hash": canonical_hash(registry),\n'
    '        "measurement_catalog_hash": canonical_hash(catalog),',
    '        "hypothesis_registry_hash": canonical_hash(registry),\n'
    '        "measurement_catalog_hash": canonical_hash(catalog),\n'
    '        "decision_condition_hash": canonical_hash(condition["declared"]),',
    "condition hash",
)

sub(
    '            recommendation_digest=digest,\n            git_commit=current_git_commit(),',
    '            recommendation_digest=digest,\n'
    '            git_commit=current_git_commit(),\n'
    '            weights=voi_weights,',
    "freeze weights",
)

sub(
    '                "arm": args.arm,\n'
    '                "applicability_gate_enforced": gate_enforced,\n'
    '                "weights": BASE_WEIGHTS,',
    '                "arm": args.arm,\n'
    '                "applicability_gate_enforced": gate_enforced,\n'
    '                "decision_condition": condition["condition_id"],\n'
    '                "weights": voi_weights,',
    "experiment_cards weights",
)

sub(
    'from pur_new.voi import (  # noqa: E402\n    BASE_WEIGHTS,',
    'from pur_new.conditions import load_condition  # noqa: E402\nfrom pur_new.voi import (  # noqa: E402\n    BASE_WEIGHTS,',
    "condition import",
)

TARGET.write_text(source, encoding="utf-8")
print(f"run_agent_v5.py patched: {before} -> {len(source)} bytes")
