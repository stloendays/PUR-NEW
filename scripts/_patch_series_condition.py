"""One-shot source patch: give scripts/run_agent_v5_series.py a --condition selector.

The series contract records which condition it froze, hashes that condition's registry,
catalog and protocol alongside the shared inputs, and computes the arm-parity payload hash
under the condition's own weights.
"""

from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "scripts" / "run_agent_v5_series.py"
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
    'from pur_new.voi import build_experiment_cards  # noqa: E402',
    'from pur_new.conditions import load_condition  # noqa: E402\n'
    'from pur_new.voi import BASE_WEIGHTS, build_experiment_cards  # noqa: E402',
    "imports",
)

sub(
    '''SERIES_INPUT_FILES = (
    "configs/agent_v5.json",
    "configs/agent_v5_comparison_protocol.json",
    "configs/verified_shape_transfer.json",
    "configs/hypothesis_registry.json",
    "configs/measurement_catalog.json",
    "configs/evidence_access_profiles.json",''',
    '''#: Inputs every series hashes regardless of condition. The condition contributes its own
#: registry, catalog and protocol on top of these, so a Condition-B contract cannot be
#: satisfied by a Condition-A input set and vice versa.
SERIES_INPUT_FILES = (
    "configs/agent_v5.json",
    "configs/decision_conditions.json",
    "configs/verified_shape_transfer.json",
    "configs/evidence_access_profiles.json",''',
    "shared input files",
)

sub(
    'ARM_PARITY_FILES = tuple(name for name in SERIES_INPUT_FILES)',
    '''def series_input_files(condition: dict[str, Any]) -> tuple[str, ...]:
    """Shared inputs plus the files the chosen condition declares."""
    declared = condition["declared"]
    extra = [declared["hypothesis_registry"], declared["measurement_catalog"]]
    protocol = declared.get("protocol")
    if protocol:
        extra.append(protocol)
    return tuple(SERIES_INPUT_FILES) + tuple(sorted(set(extra)))''',
    "condition input files",
)

sub(
    '''    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument(
        "--resume",''',
    '''    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument(
        "--condition",
        default=None,
        help="named decision condition; both arms of a comparison must declare the same one",
    )
    parser.add_argument(
        "--resume",''',
    "condition argument",
)

sub(
    '''    candidates = json.loads(args.candidate_set.read_text(encoding="utf-8"))["candidates"]
    audit = audit_experiment_cards(
        build_experiment_cards(candidates), candidates=candidates, verified=load_verified_shape_transfer()
    )
    parity_hash = pre_enforcement_payload_hash(audit, top_k=args.top_k)''',
    '''    condition = load_condition(args.condition)
    voi_weights = condition["weights"] or dict(BASE_WEIGHTS)
    input_files = series_input_files(condition)
    candidates = json.loads(args.candidate_set.read_text(encoding="utf-8"))["candidates"]
    audit = audit_experiment_cards(
        build_experiment_cards(
            candidates,
            registry=condition["registry"],
            catalog=condition["catalog"],
            weights=voi_weights,
        ),
        candidates=candidates,
        verified=load_verified_shape_transfer(),
    )
    parity_hash = pre_enforcement_payload_hash(audit, top_k=args.top_k, weights=voi_weights)''',
    "condition-aware parity hash",
)

sub(
    '''        "arm": args.arm,
        "applicability_audit_visible_to_model": True,''',
    '''        "arm": args.arm,
        "decision_condition": condition["condition_id"],
        "decision_condition_protocol": condition["protocol"],
        "decision_question": condition["decision_question"],
        "voi_weights": voi_weights,
        "applicability_audit_visible_to_model": True,''',
    "manifest condition fields",
)

sub(
    '''        "series_input_hashes": {name: sha256_file(ROOT / name) for name in SERIES_INPUT_FILES},
        "arm_parity_files": list(ARM_PARITY_FILES),''',
    '''        "series_input_hashes": {name: sha256_file(ROOT / name) for name in input_files},
        "arm_parity_files": list(input_files),''',
    "manifest input hashes",
)

sub(
    '''        if existing["n_runs_declared"] != args.n_runs:''',
    '''        if existing.get("decision_condition") != condition["condition_id"]:
            raise SystemExit(
                f"resume refused: manifest declares condition {existing.get('decision_condition')!r}, "
                f"invoked with {condition['condition_id']!r}"
            )
        if existing["n_runs_declared"] != args.n_runs:''',
    "resume condition guard",
)

sub(
    '''            "--top-k",
            str(args.top_k),
            "--output-dir",
            str(run_dir),
        ]''',
    '''            "--top-k",
            str(args.top_k),
            "--condition",
            condition["condition_id"],
            "--output-dir",
            str(run_dir),
        ]''',
    "child condition argument",
)

TARGET.write_text(source, encoding="utf-8")
print(f"run_agent_v5_series.py patched: {before} -> {len(source)} bytes")
