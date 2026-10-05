from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
import re

from docx import Document
from docx.shared import Inches, Pt

from common import content_digest, has_dynamic_fields, require_file


REFERENCE_RE = re.compile(r"^\s*(\d+)[.)]\s+(.*)$")


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservatively rewrite plain-text numeric bibliography entries")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--style", choices=["vancouver", "nature", "apa"], required=True)
    parser.add_argument("--allow-dynamic-fields", action="store_true")
    args = parser.parse_args()
    source = require_file(args.input, "Input DOCX")
    if has_dynamic_fields(source) and not args.allow_dynamic_fields:
        print("BLOCKED: dynamic citation fields detected; refusing to flatten or rewrite the document.")
        return 2
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    lookup = {int(item["id"]): item["formatted"] for item in metadata if item.get("formatted")}
    doc = Document(source)
    in_refs = False
    rewritten = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip().casefold() in {"references", "bibliography", "reference list"}:
            in_refs = True
            continue
        if not in_refs:
            continue
        match = REFERENCE_RE.match(paragraph.text)
        if not match:
            continue
        ref_id = int(match.group(1))
        if ref_id not in lookup:
            continue
        paragraph.text = f"{ref_id}. {lookup[ref_id]}"
        paragraph.paragraph_format.left_indent = Inches(0.25)
        paragraph.paragraph_format.first_line_indent = Inches(-0.25)
        for run in paragraph.runs:
            run.font.size = Pt(10)
        rewritten.append(ref_id)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, args.output)
    doc.save(args.output)
    result = {
        "input": str(source),
        "output": str(args.output),
        "style": args.style,
        "rewritten_reference_ids": rewritten,
        "content_digest_before": content_digest(source),
        "content_digest_after": content_digest(args.output),
        "status": "applied" if rewritten else "manual_action_required",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
