#!/usr/bin/env python3
"""Structural audit for submission DOCX files.

This script intentionally does not replace visual rendering. It catches defects that
are cheap to detect in OOXML before the render/inspect gate.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PLACEHOLDER_RE = re.compile(
    r"AUTHOR_INPUT_NEEDED|\bTODO\b|\bFIXME\b|author notes|next revision", re.I
)
VERSION_RE = re.compile(r"(?<![A-Za-z0-9])V(?:0|[1-9]\d*)(?![A-Za-z0-9])")
LATEX_RE = re.compile(r"\\(?:eta|frac|approx|mathbf|mathrm|ln|beta|mu|delta|times|text)\b")


def xml_text(xml: bytes) -> str:
    root = ET.fromstring(xml)
    parts: list[str] = []
    for el in root.iter():
        if el.tag.endswith("}t") and el.text:
            parts.append(el.text)
    return " ".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--min-images", type=int, default=0)
    ap.add_argument("--min-math", type=int, default=0)
    ap.add_argument("--require-font")
    ap.add_argument("--allow-comments", action="store_true")
    ap.add_argument("--allow-tracked-changes", action="store_true")
    ap.add_argument("--allow-version-labels", action="store_true")
    args = ap.parse_args()

    blockers: list[str] = []
    warnings: list[str] = []

    if not args.docx.exists():
        print("BLOCKER: file does not exist:", args.docx)
        return 1

    with zipfile.ZipFile(args.docx) as z:
        names = set(z.namelist())
        if "word/document.xml" not in names:
            print("BLOCKER: not a valid WordprocessingML DOCX")
            return 1

        document = z.read("word/document.xml")
        text = xml_text(document)
        media = [n for n in names if n.startswith("word/media/")]
        omml = document.count(b"<m:oMath")
        tables = document.count(b"<w:tbl>")
        comments = False
        if "word/comments.xml" in names:
            comments_xml = z.read("word/comments.xml")
            comments = bool(re.search(rb"<w:comment(?:\s|>)", comments_xml))
        tracked = bool(re.search(rb"<w:(?:ins|del)(?:\s|>)", document))

        if len(media) < args.min_images:
            blockers.append(f"embedded media {len(media)} < required {args.min_images}")
        if omml < args.min_math:
            blockers.append(f"OMML equation elements {omml} < required {args.min_math}")
        if comments and not args.allow_comments:
            blockers.append("comments.xml present in clean submission copy")
        if tracked and not args.allow_tracked_changes:
            blockers.append("tracked changes present in clean submission copy")
        if PLACEHOLDER_RE.search(text):
            blockers.append("visible drafting placeholder remains")
        if not args.allow_version_labels:
            versions = sorted(set(VERSION_RE.findall(text)))
            if versions:
                blockers.append(f"visible development version label(s): {versions}")
        latex = sorted(set(LATEX_RE.findall(text)))
        if latex:
            blockers.append("literal LaTeX command(s) visible in DOCX: " + ", ".join(latex))

        relname = "word/_rels/document.xml.rels"
        if relname in names:
            relroot = ET.fromstring(z.read(relname))
            for rel in relroot:
                target_mode = rel.attrib.get("TargetMode")
                target = rel.attrib.get("Target", "")
                rel_type = rel.attrib.get("Type", "")
                if target_mode == "External" and "image" in rel_type.lower():
                    blockers.append(f"externally linked image relationship: {target}")

        styles = z.read("word/styles.xml") if "word/styles.xml" in names else b""
        if args.require_font and args.require_font.encode("utf-8") not in styles:
            blockers.append(f"required font not found in styles.xml: {args.require_font}")

        if b'w:val="Compact"' in document and b'w:styleId="Compact"' not in styles:
            warnings.append("unresolved paragraph style 'Compact' may destabilize table layout in LibreOffice")

    print("File:", args.docx)
    print("Embedded media:", len(media))
    print("OMML equation elements:", omml)
    print("Tables:", tables)
    print(f"Blockers: {len(blockers)}")
    for x in blockers:
        print("  BLOCKER:", x)
    print(f"Warnings: {len(warnings)}")
    for x in warnings:
        print("  WARNING:", x)
    return 1 if blockers else 0


if __name__ == "__main__":
    sys.exit(main())
