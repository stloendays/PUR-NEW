#!/usr/bin/env python3
"""Audit a canonical Markdown manuscript for common pre-export blockers."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BLOCKER_PATTERNS = [
    (re.compile(r"^##+\s+Author notes", re.I | re.M), "Author-notes section remains"),
    (re.compile(r"\bTODO\b|\bFIXME\b", re.I), "TODO/FIXME remains"),
    (
        re.compile(r"should be associated with (?:a )?(?:frozen )?release|archived commit at submission", re.I),
        "Data-availability placeholder remains",
    ),
]

WARNING_PATTERNS = [
    (re.compile(r"^\s*\$\s*$", re.M), "Single-dollar display delimiter line found; use $ for display math"),
    (re.compile(r"evidence-grounded", re.I), "Consider whether 'evidence-grounded' is necessary or AI-generic"),
    (re.compile(r"AI-guided", re.I), "Consider whether 'AI-guided' is scientifically specific enough"),
    (
        re.compile(
            r"(?:was\s+not\s+part\s+of|not\s+part\s+of).{0,80}(?:frozen\s+)?(?:Agent\s+)?evidence\s+contract"
            r"|(?:frozen\s+)?(?:Agent\s+)?evidence\s+contract.{0,80}(?:was\s+not|not\s+part)"
            r"|\bevidence\s+version\s+(?:v?\d|one|two|three)\b"
            r"|\btool[_ -]?version\b"
            r"|\b(?:git\s+)?commit\s+(?:sha|hash)\b"
            r"|\bbranch\s+(?:name|sha|hash)\b",
            re.I | re.S,
        ),
        (
            "Development/provenance wording detected. In main text, keep it only if it changes "
            "scientific interpretation or prevents false causal attribution; otherwise move exact "
            "evidence-version/tool/hash chronology to SI or repository provenance and lead with the scientific result."
        ),
    ),
]

IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FIGURE_CAPTION_RE = re.compile(r"\*\*Figure\s+(\d+)\.", re.I)


def audit(path: Path, repo_root: Path | None) -> tuple[list[str], list[str]]:
    text = path.read_text(encoding="utf-8")
    blockers: list[str] = []
    warnings: list[str] = []

    for pattern, message in BLOCKER_PATTERNS:
        if pattern.search(text):
            blockers.append(message)

    for pattern, message in WARNING_PATTERNS:
        if pattern.search(text):
            warnings.append(message)

    if text.count("$$") % 2 != 0:
        blockers.append("Unbalanced $$ display-math delimiters")

    captions = [int(x) for x in FIGURE_CAPTION_RE.findall(text)]
    if captions:
        unique = sorted(set(captions))
        expected = list(range(min(unique), max(unique) + 1))
        if unique != expected:
            warnings.append(f"Non-continuous figure captions: found {unique}, expected {expected}")

    for rel in IMAGE_RE.findall(text):
        if re.match(r"^[a-z]+://", rel, re.I):
            continue
        base = path.parent
        target = (base / rel).resolve()
        if repo_root is not None and not target.exists():
            alt = (repo_root / rel).resolve()
            if alt.exists():
                target = alt
        if not target.exists():
            blockers.append(f"Missing image file: {rel}")

    # Catch common literal LaTeX leakage in ordinary prose lines. This is heuristic.
    in_display = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if line.strip() == "$$":
            in_display = not in_display
            continue
        if in_display:
            continue
        stripped = re.sub(r"\$[^$]*\$", "", line)
        if re.search(r"\\(?:eta|alpha|beta|mu|delta|approx|frac|mathbf|mathrm)\b", stripped):
            warnings.append(f"Possible literal LaTeX outside math at line {line_no}")

    return blockers, warnings


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("manuscript", type=Path)
    p.add_argument("--repo-root", type=Path, default=None)
    args = p.parse_args()

    manuscript = args.manuscript.resolve()
    if not manuscript.exists():
        print(f"ERROR: manuscript not found: {manuscript}")
        return 2

    root = args.repo_root.resolve() if args.repo_root else None
    blockers, warnings = audit(manuscript, root)

    print(f"Manuscript: {manuscript}")
    print(f"Blockers: {len(blockers)}")
    for item in blockers:
        print(f"  BLOCKER: {item}")
    print(f"Warnings: {len(warnings)}")
    for item in warnings:
        print(f"  WARNING: {item}")

    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
