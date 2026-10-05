from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path

from docx import Document

from common import iter_docx_xml, require_file


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
ORCID_RE = re.compile(r"\b\d{4}-\d{4}-\d{4}-\d{3}[\dX]\b", re.I)
URL_RE = re.compile(r"https?://[^\s<>'\"]+", re.I)
AUTHOR_ATTR_RE = re.compile(r"(?:w:author|author)=\"([^\"]+)\"")


def add(findings, kind, value, source):
    item = {"kind": kind, "value": value, "source": source}
    if item not in findings:
        findings.append(item)


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan DOCX visible and package-level identity surfaces")
    parser.add_argument("docx", type=Path)
    parser.add_argument("--term", action="append", default=[])
    parser.add_argument("--fail-on-high", action="store_true")
    args = parser.parse_args()
    path = require_file(args.docx, "DOCX")
    doc = Document(path)
    findings = []
    combined_parts = []
    for name, raw in iter_docx_xml(path):
        text = raw.decode("utf-8", errors="ignore")
        combined_parts.append(text)
        if name.endswith("comments.xml") or name.endswith("people.xml") or "w:ins" in text or "w:del" in text:
            for author in AUTHOR_ATTR_RE.findall(text):
                add(findings, "revision_or_comment_author", author, name)
    combined = "\n".join(combined_parts)

    for match in EMAIL_RE.finditer(combined):
        add(findings, "email", match.group(0), "document/package")
    for match in ORCID_RE.finditer(combined):
        add(findings, "orcid", match.group(0), "document/package")
    for match in URL_RE.finditer(combined):
        add(findings, "url", match.group(0), "document/package")
    for term in args.term:
        if term and term.casefold() in combined.casefold():
            add(findings, "user_term", term, "document/package")

    props = doc.core_properties
    if props.author:
        add(findings, "metadata_author", props.author, "core_properties")
    if props.last_modified_by:
        add(findings, "metadata_last_modified_by", props.last_modified_by, "core_properties")
    with zipfile.ZipFile(path) as archive:
        if "docProps/custom.xml" in archive.namelist():
            add(findings, "custom_properties_present", "docProps/custom.xml", "package")
        if "word/comments.xml" in archive.namelist():
            add(findings, "comments_present", "word/comments.xml", "package")

    high_kinds = {"email", "orcid", "user_term", "metadata_author", "metadata_last_modified_by", "revision_or_comment_author"}
    risk = "high" if any(item["kind"] in high_kinds for item in findings) else ("medium" if findings else "low")
    result = {"file": str(path), "risk": risk, "finding_count": len(findings), "findings": findings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if args.fail_on_high and risk == "high" else 0


if __name__ == "__main__":
    raise SystemExit(main())
