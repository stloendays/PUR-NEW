#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def bib_keys(text: str) -> set[str]:
    return set(re.findall(r"@[A-Za-z]+\s*\{\s*([^,\s]+)", text))


def citation_keys(text: str) -> set[str]:
    # Matches Pandoc-style citations such as [@Key] and [@Key1; @Key2].
    return set(re.findall(r"@([A-Za-z0-9_:\-.]+)", text))


def main() -> None:
    parser = argparse.ArgumentParser(description="Check manuscript citation keys against BibTeX entries")
    parser.add_argument(
        "--manuscript",
        type=Path,
        default=ROOT / "manuscript" / "MAIN_TEXT_DRAFT.md",
    )
    parser.add_argument(
        "--bibliography",
        type=Path,
        default=ROOT / "manuscript" / "references.bib",
    )
    args = parser.parse_args()

    manuscript = args.manuscript.read_text(encoding="utf-8")
    bibliography = args.bibliography.read_text(encoding="utf-8")

    cited = citation_keys(manuscript)
    available = bib_keys(bibliography)
    missing = sorted(cited - available)
    unused = sorted(available - cited)

    print(f"cited keys: {len(cited)}")
    print(f"bibliography entries: {len(available)}")
    if unused:
        print("unused bibliography entries:")
        for key in unused:
            print(f"  - {key}")

    if missing:
        print("missing bibliography entries:")
        for key in missing:
            print(f"  - {key}")
        raise SystemExit(1)

    print("citation integrity: OK")


if __name__ == "__main__":
    main()
