from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path

from common import package_sha256, require_file


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
ORCID_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", re.I)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a blinded DOCX copy without changing scientific text unless terms are supplied")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--term", action="append", default=[])
    parser.add_argument("--replacement", default="[BLINDED]")
    parser.add_argument("--keep-custom-properties", action="store_true")
    args = parser.parse_args()
    source = require_file(args.input, "Input DOCX")
    if args.output.resolve() == source.resolve():
        raise SystemExit("Refusing to overwrite the source DOCX")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    replacements = []
    with zipfile.ZipFile(source) as archive:
        files = {name: archive.read(name) for name in archive.namelist()}
    for name, raw in list(files.items()):
        if name == "docProps/custom.xml" and not args.keep_custom_properties:
            del files[name]
            continue
        if not (name.endswith(".xml") or name.endswith(".rels")):
            continue
        text = raw.decode("utf-8", errors="ignore")
        if name == "docProps/core.xml":
            for tag in ("dc:creator", "cp:lastModifiedBy"):
                start = f"<{tag}>"
                end = f"</{tag}>"
                if start in text and end in text:
                    left, rest = text.split(start, 1)
                    _, right = rest.split(end, 1)
                    text = left + start + end + right
        for term in args.term:
            if term and term in text:
                text = text.replace(term, args.replacement)
                replacements.append(term)
        text, email_count = EMAIL_RE.subn(args.replacement, text)
        text, orcid_count = ORCID_RE.subn(args.replacement, text)
        if email_count:
            replacements.append(f"<emails:{email_count}>")
        if orcid_count:
            replacements.append(f"<orcids:{orcid_count}>")
        files[name] = text.encode("utf-8")
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, raw in files.items():
            archive.writestr(name, raw)
    result = {
        "input": str(source),
        "output": str(args.output),
        "replaced_terms": sorted(set(replacements)),
        "input_sha256": package_sha256(source),
        "output_sha256": package_sha256(args.output),
        "status": "created",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
