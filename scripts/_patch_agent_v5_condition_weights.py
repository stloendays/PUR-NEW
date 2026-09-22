"""One-shot source patch: thread condition VOI weights through the V5 payload builders.

Every signature gains a keyword-only ``weights`` defaulting to None, which resolves to
BASE_WEIGHTS. Condition A therefore produces a byte-identical payload, including the
pre-enforcement payload hash that the arm-parity test compares.
"""

from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "src" / "pur_new" / "agent_v5.py"
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
    'def _voi_view(cards: list[dict[str, Any]], *, top_k: int) -> dict[str, Any]:',
    'def _voi_view(\n'
    '    cards: list[dict[str, Any]], *, top_k: int, weights: dict[str, float] | None = None\n'
    ') -> dict[str, Any]:',
    "_voi_view signature",
)

sub(
    '        "formula": VOI_FORMULA,\n        "weights": BASE_WEIGHTS,',
    '        "formula": VOI_FORMULA,\n        "weights": weights or BASE_WEIGHTS,',
    "_voi_view weights",
)

sub(
    'def build_pre_enforcement_payload(audit: dict[str, Any], *, top_k: int) -> dict[str, Any]:',
    'def build_pre_enforcement_payload(\n'
    '    audit: dict[str, Any], *, top_k: int, weights: dict[str, float] | None = None\n'
    ') -> dict[str, Any]:',
    "pre_enforcement signature",
)

sub(
    '        "voi": _voi_view(_sorted_cards(audit["cards"]), top_k=top_k),',
    '        "voi": _voi_view(_sorted_cards(audit["cards"]), top_k=top_k, weights=weights),',
    "pre_enforcement voi",
)

sub(
    'def pre_enforcement_payload_hash(audit: dict[str, Any], *, top_k: int) -> str:\n'
    '    return canonical_hash(build_pre_enforcement_payload(audit, top_k=top_k))',
    'def pre_enforcement_payload_hash(\n'
    '    audit: dict[str, Any], *, top_k: int, weights: dict[str, float] | None = None\n'
    ') -> str:\n'
    '    return canonical_hash(build_pre_enforcement_payload(audit, top_k=top_k, weights=weights))',
    "pre_enforcement hash",
)

sub(
    'def build_voi_payload(audit: dict[str, Any], *, top_k: int, enforce: bool) -> dict[str, Any]:',
    'def build_voi_payload(\n'
    '    audit: dict[str, Any],\n'
    '    *,\n'
    '    top_k: int,\n'
    '    enforce: bool,\n'
    '    weights: dict[str, float] | None = None,\n'
    ') -> dict[str, Any]:',
    "build_voi_payload signature",
)

sub(
    '    payload = build_pre_enforcement_payload(audit, top_k=top_k)',
    '    payload = build_pre_enforcement_payload(audit, top_k=top_k, weights=weights)',
    "build_voi_payload pre",
)

sub(
    '        payload["voi"] = _voi_view(selectable, top_k=top_k)',
    '        payload["voi"] = _voi_view(selectable, top_k=top_k, weights=weights)',
    "build_voi_payload enforced",
)

TARGET.write_text(source, encoding="utf-8")
print(f"agent_v5.py patched: {before} -> {len(source)} bytes")
