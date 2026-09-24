#!/usr/bin/env python3
"""Generic source-level submission audit for scientific Markdown manuscripts.

Standard-library only. Designed for main manuscript + SI + BibTeX workflows.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(
    r"AUTHOR_INPUT_NEEDED|\bTODO\b|\bFIXME\b|author notes|next revision|"
    r"placeholder affiliation|placeholder email",
    re.I,
)
VERSION_RE = re.compile(r"(?<![A-Za-z0-9])V(?:0|[1-9]\d*)(?![A-Za-z0-9])")
SINGLE_DOLLAR_RE = re.compile(r"^\s*\$\s*$", re.M)
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
CITE_BLOCK_RE = re.compile(r"\[@([^\]]+)\]")
CITE_BARE_RE = re.compile(r"(?<!\[)@([A-Za-z0-9_:.+\-/]+)")
BIB_KEY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)")
CAPTION_RE = re.compile(r"^\*\*(?:Supplementary )?(Figure|Table)\s+(S?\d+)\.", re.I)
LATEX_CMD_RE = re.compile(r"\\(?:frac|eta|approx|mathbf|mathrm|ln|beta|mu|delta|times|text)\b")
MATH_UNIT_RE = re.compile(
    r"\$[^$]*(?:\\mathrm\{(?:kJ|J|Pa|mPa|h)|mol\^\{|K\^\{|s\^\{)[^$]*\$"
)


def read(path: Path | None) -> str:
    return path.read_text(encoding="utf-8") if path else ""


def citations(text: str) -> set[str]:
    out: set[str] = set()
    for m in CITE_BLOCK_RE.finditer(text):
        for part in m.group(1).split(";"):
            key = part.strip().lstrip("@").split()[0].split(",")[0]
            if key:
                out.add(key)
    for m in CITE_BARE_RE.finditer(text):
        out.add(m.group(1))
    return out


def title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
        if line.startswith("## "):
            return line[3:].strip()
    return ""


def check_markdown(
    label: str,
    path: Path,
    text: str,
    repo_root: Path,
    block_versions: bool,
    blockers: list[str],
    warnings: list[str],
) -> None:
    if PLACEHOLDER_RE.search(text):
        blockers.append(f"{label}: unresolved drafting placeholder")
    if SINGLE_DOLLAR_RE.search(text):
        blockers.append(f"{label}: lone '$' display delimiter; use $$ blocks or inline math")
    if block_versions:
        versions = sorted(set(VERSION_RE.findall(text)))
        if versions:
            blockers.append(f"{label}: reader-facing development version label(s): {versions}")

    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = IMAGE_RE.search(line)
        if m:
            alt, target = m.group(1).strip(), m.group(2).strip()
            if not re.match(r"^[a-z]+://", target, re.I):
                img = (path.parent / target).resolve()
                if not img.exists():
                    blockers.append(f"{label}: missing image at line {i+1}: {target}")
            if alt:
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j < len(lines) and CAPTION_RE.match(lines[j].strip()):
                    warnings.append(
                        f"{label}: image alt text at line {i+1} may duplicate the authored caption in Pandoc export"
                    )

        stripped = re.sub(r"\$\$.*?\$\$", "", line)
        stripped = re.sub(r"\$[^$]*\$", "", stripped)
        if LATEX_CMD_RE.search(stripped):
            warnings.append(f"{label}: possible literal LaTeX outside math at line {i+1}")

    if MATH_UNIT_RE.search(text):
        warnings.append(
            f"{label}: unit text appears inside math mode; verify Word typography or move human-readable units to text"
        )

    groups: dict[str, list[int]] = {"Figure": [], "Table": [], "SFigure": [], "STable": []}
    for line in lines:
        m = CAPTION_RE.match(line.strip())
        if not m:
            continue
        kind, n = m.groups()
        is_s = n.startswith("S")
        num = int(n.lstrip("S"))
        key = ("S" if is_s else "") + kind.capitalize()
        groups[key].append(num)
    for key, nums in groups.items():
        if not nums:
            continue
        if len(nums) != len(set(nums)):
            blockers.append(f"{label}: duplicate {key} caption number(s): {nums}")
        uniq = sorted(set(nums))
        if uniq != list(range(uniq[0], uniq[-1] + 1)):
            warnings.append(f"{label}: non-contiguous {key} caption sequence: {uniq}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", type=Path, required=True)
    ap.add_argument("--si", type=Path)
    ap.add_argument("--bib", type=Path)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument(
        "--allow-version-labels",
        action="store_true",
        help="Do not block reader-facing V<number> labels.",
    )
    args = ap.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []

    main_text = read(args.main)
    si_text = read(args.si)
    bib_text = read(args.bib)

    check_markdown(
        "main",
        args.main,
        main_text,
        args.repo_root,
        not args.allow_version_labels,
        blockers,
        warnings,
    )
    if args.si:
        check_markdown(
            "SI",
            args.si,
            si_text,
            args.repo_root,
            not args.allow_version_labels,
            blockers,
            warnings,
        )

    if args.si:
        mt, st = title(main_text), title(si_text)
        if mt and st and mt != st and "supplementary" not in st.lower():
            warnings.append(f"title mismatch: main={mt!r}, SI={st!r}")

    if args.bib:
        keys = BIB_KEY_RE.findall(bib_text)
        dup = sorted({k for k in keys if keys.count(k) > 1})
        if dup:
            blockers.append("duplicate BibTeX key(s): " + ", ".join(dup))
        cited = citations(main_text) | citations(si_text)
        missing = sorted(cited - set(keys))
        if missing:
            blockers.append("citation key(s) missing from bibliography: " + ", ".join(missing))
        unused = sorted(set(keys) - cited)
        if unused:
            warnings.append(f"unused bibliography entries: {len(unused)}")

    print(f"Blockers: {len(blockers)}")
    for x in blockers:
        print("  BLOCKER:", x)
    print(f"Warnings: {len(warnings)}")
    for x in warnings:
        print("  WARNING:", x)
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
