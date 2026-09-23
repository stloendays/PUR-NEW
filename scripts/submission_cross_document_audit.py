#!/usr/bin/env python3
"""Cross-document submission audit for the canonical PUR manuscript and SI."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "manuscript" / "MAIN_TEXT_V5.md"
SI = ROOT / "manuscript" / "SUPPLEMENTARY_INFORMATION_V5.md"
BIB = ROOT / "manuscript" / "references.bib"

PLACEHOLDER_RE = re.compile(
    r"AUTHOR_INPUT_NEEDED|\bTODO\b|\bFIXME\b|^##+\s+Author notes|next revision",
    re.I | re.M,
)
VERSION_RE = re.compile(r"(?<![A-Za-z0-9])V[1-9](?![A-Za-z0-9])")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
CITE_BLOCK_RE = re.compile(r"\[@([^\]]+)\]")
CITE_BARE_RE = re.compile(r"(?<!\[)@([A-Za-z0-9_:.+-]+)")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)")
MAIN_FIG_RE = re.compile(r"\*\*Figure\s+(\d+)\.", re.I)
MAIN_TABLE_RE = re.compile(r"\*\*Table\s+(\d+)\.", re.I)
SI_FIG_RE = re.compile(r"\*\*Supplementary Figure S(\d+)\.", re.I)
SI_TABLE_RE = re.compile(r"^##\s+Supplementary Table S(\d+)\s*\|", re.I | re.M)


def citation_keys(text: str) -> set[str]:
    out: set[str] = set()
    for match in CITE_BLOCK_RE.finditer(text):
        for part in match.group(1).split(";"):
            key = part.strip().lstrip("@").split()[0].split(",")[0]
            if key:
                out.add(key)
    out.update(CITE_BARE_RE.findall(text))
    return out


def continuous(values: list[int], expected: list[int]) -> bool:
    return sorted(set(values)) == expected


def check_image_paths(md_path: Path, text: str, errors: list[str]) -> None:
    for rel in IMAGE_RE.findall(text):
        if re.match(r"^[a-z]+://", rel, re.I):
            continue
        target = (md_path.parent / rel).resolve()
        if not target.exists():
            errors.append(f"Missing image referenced by {md_path.name}: {rel}")


def require_all(text: str, tokens: list[str], scope: str, errors: list[str]) -> None:
    for token in tokens:
        if token not in text:
            errors.append(f"{scope} missing expected submission value: {token}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    for p in (MAIN, SI, BIB):
        if not p.exists():
            errors.append(f"Missing canonical file: {p.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print("BLOCKER:", e)
        return 1

    main = MAIN.read_text(encoding="utf-8")
    si = SI.read_text(encoding="utf-8")
    bib = BIB.read_text(encoding="utf-8")

    # Reader-facing hygiene.
    for name, text in (("main", main), ("SI", si)):
        if PLACEHOLDER_RE.search(text):
            errors.append(f"{name}: unresolved drafting placeholder remains")
        versions = sorted(set(VERSION_RE.findall(text)))
        if versions:
            errors.append(f"{name}: internal numbered development label(s) remain: {versions}")

    # Canonical title parity.
    main_title = next((x[2:].strip() for x in main.splitlines() if x.startswith("# ")), "")
    si_title = next((x[3:].strip() for x in si.splitlines() if x.startswith("## ")), "")
    if not main_title or main_title != si_title:
        errors.append(f"Title mismatch between main and SI: {main_title!r} vs {si_title!r}")

    # Citation parity.
    cited = citation_keys(main) | citation_keys(si)
    ref_keys = set(BIB_KEY_RE.findall(bib))
    missing = sorted(cited - ref_keys)
    unused = sorted(ref_keys - cited)
    if missing:
        errors.append("Citation key(s) missing from references.bib: " + ", ".join(missing))
    if unused:
        warnings.append("Unused bibliography entries: " + ", ".join(unused))

    # Figures/tables and paths.
    check_image_paths(MAIN, main, errors)
    check_image_paths(SI, si, errors)
    if not continuous([int(x) for x in MAIN_FIG_RE.findall(main)], list(range(1, 6))):
        errors.append("Main figure captions must be continuous Figure 1-5")
    if not continuous([int(x) for x in MAIN_TABLE_RE.findall(main)], [1, 2]):
        errors.append("Main table captions must be continuous Table 1-2")
    if not continuous([int(x) for x in SI_FIG_RE.findall(si)], [1, 2]):
        errors.append("SI figure captions must be Supplementary Figure S1-S2")
    if not continuous([int(x) for x in SI_TABLE_RE.findall(si)], list(range(1, 15))):
        errors.append("SI table headings must be continuous Supplementary Table S1-S14")

    # Headline values that must stay synchronized across documents.
    require_all(
        main,
        [
            "85.53%", "99.77%", "1.423×", "1.058×", "99.63%", "0.9998",
            "1.824×", "1.086×", "86.2%", "1.088×", "42.05", "5.77%",
            "4.29", "0.910", "-1.456", "0.851", "0.033", "9/10", "0/5",
            "10/10", "0.7392", "0.6875", "1.60%", "7.79%",
        ],
        "main",
        errors,
    )
    require_all(
        si,
        [
            "0.8553", "0.9977", "1.423×", "1.058×", "99.63%", "0.9998",
            "1.824×", "1.086×", "86.2%", "1.088", "42.05", "5.77%",
            "4.29", "0.910", "-1.456", "0.851", "0.033", "9/10", "0/5",
            "10/10", "0.7392", "0.6875", "1.60%", "7.79%",
        ],
        "SI",
        errors,
    )

    # Statistical-unit language required in the final Methods.
    required_stats = [
        "experimental realization was treated as the independent material-level unit",
        "10,000 bootstrap resamples with seed 20260918",
        "10,000 resamples with seed 20260923",
        "No multiplicity correction was applied",
        "two-sided 95% Wilson intervals",
    ]
    require_all(main, required_stats, "main statistical analysis", errors)

    print(f"Main: {MAIN.relative_to(ROOT)}")
    print(f"SI: {SI.relative_to(ROOT)}")
    print(f"References: {len(ref_keys)} entries; {len(cited)} cited keys")
    print(f"Blockers: {len(errors)}")
    for e in errors:
        print("  BLOCKER:", e)
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print("  WARNING:", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
