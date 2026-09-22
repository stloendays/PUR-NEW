"""One-shot source patch: give the interleaved driver a --condition selector."""

from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "scripts" / "drive_v5_primary_comparison.py"
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
    '    parser.add_argument("--log", type=Path, default=None)\n    args = parser.parse_args()',
    '    parser.add_argument("--log", type=Path, default=None)\n'
    '    parser.add_argument(\n'
    '        "--condition",\n'
    '        default=None,\n'
    '        help=(\n'
    '            "named decision condition from configs/decision_conditions.json. Both arms are "\n'
    '            "driven under this one condition, so the arm contrast stays the enforcement flag."\n'
    '        ),\n'
    '    )\n'
    '    parser.add_argument(\n'
    '        "--label",\n'
    '        default=None,\n'
    '        help="suffix for the series and comparison directory names; defaults to the run count",\n'
    '    )\n'
    '    args = parser.parse_args()',
    "driver arguments",
)

sub(
    '''    arms = {
        "V5_NO_GATE": args.output_root / f"series_no_gate_n{args.n_runs}",
        "V5_FULL": args.output_root / f"series_full_n{args.n_runs}",
    }
    comparison_dir = args.output_root / f"comparison_n{args.n_runs}"''',
    '''    label = args.label or f"n{args.n_runs}"
    arms = {
        "V5_NO_GATE": args.output_root / f"series_no_gate_{label}",
        "V5_FULL": args.output_root / f"series_full_{label}",
    }
    comparison_dir = args.output_root / f"comparison_{label}"''',
    "series directory naming",
)

sub(
    '    log(f"driver started: N={args.n_runs} per arm, interleaved")',
    '    log(\n'
    '        f"driver started: N={args.n_runs} per arm, interleaved, "\n'
    '        f"condition={args.condition or \'<default>\'}"\n'
    '    )',
    "driver start log",
)

sub(
    '''                "--output-dir",
                str(out_dir),
                "--max-new-runs",
                "1",
            ]''',
    '''                "--output-dir",
                str(out_dir),
                "--max-new-runs",
                "1",
            ]
            if args.condition:
                cmd += ["--condition", args.condition]''',
    "child condition argument",
)

TARGET.write_text(source, encoding="utf-8")
print(f"drive_v5_primary_comparison.py patched: {before} -> {len(source)} bytes")
