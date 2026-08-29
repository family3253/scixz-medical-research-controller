#!/usr/bin/env python3
"""Audit DOI resolution and compare cited metadata with Crossref records."""

from __future__ import annotations

import argparse
import csv
import difflib
import json
import re
import sys
import unicodedata
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Dict, List


DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
USER_AGENT = (
    "sci-manuscript-preflight "
    "(https://github.com/VivalavidaLu/sci-manuscript-preflight)"
)
OUTPUT_FIELDS = [
    "doi",
    "status",
    "duplicate",
    "compared_fields",
    "mismatch_fields",
    "cited_title",
    "crossref_title",
    "cited_first_author",
    "crossref_first_author",
    "cited_year",
    "crossref_year",
    "cited_journal",
    "crossref_journal",
    "type",
    "publisher",
    "error",
    "context",
]


def clean_doi(doi: str) -> str:
    return doi.strip().rstrip(".,;:)]}")


def extract_dois(text: str) -> List[str]:
    return [clean_doi(match.group(0)) for match in DOI_RE.finditer(text)]


def crossref_lookup(doi: str, timeout: int = 15) -> Dict[str, Any]:
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return {
                    "ok": False,
                    "status": response.status,
                    "error": f"HTTP {response.status}",
                }
            data = json.loads(response.read().decode("utf-8"))
        message = data.get("message", {})
        date_source = (
            message.get("published-print")
            or message.get("published-online")
            or message.get("issued")
            or {}
        )
        date_parts = date_source.get("date-parts") or [[""]]
        authors = message.get("author") or []
        first_author = authors[0].get("family", "") if authors else ""
        return {
            "ok": True,
            "status": 200,
            "title": " ".join(message.get("title", [])[:1]),
            "first_author": first_author,
            "container_title": " ".join(message.get("container-title", [])[:1]),
            "year": str(date_parts[0][0]),
            "type": message.get("type", ""),
            "publisher": message.get("publisher", ""),
        }
    except Exception as exc:
        return {"ok": False, "status": "", "error": str(exc)}


def chunk_reference_context(text: str, doi: str) -> str:
    index = text.lower().find(doi.lower())
    if index < 0:
        return ""
    start = max(0, index - 500)
    end = min(len(text), index + 500)
    return " ".join(text[start:end].split())


def reference_record(text: str, doi: str) -> str:
    for match in re.finditer(
        r"(?ms)^@\w+\s*[({].*?(?=^@\w+\s*[({]|\Z)", text
    ):
        if doi.lower() in match.group(0).lower():
            return match.group(0)

    for block in re.split(r"(?m)^ER\s{2}-.*$", text):
        if doi.lower() in block.lower():
            return block

    for line in text.splitlines():
        if doi.lower() in line.lower():
            return line

    return chunk_reference_context(text, doi)


def _field_from_bib(record: str, field: str) -> str:
    match = re.search(
        rf"(?ims)^\s*{re.escape(field)}\s*=\s*[{{\"](.+?)[}}\"]\s*,?\s*$",
        record,
    )
    return match.group(1).strip() if match else ""


def _field_from_tagged(record: str, tags: tuple[str, ...]) -> str:
    for tag in tags:
        match = re.search(rf"(?im)^{re.escape(tag)}\s*-\s*(.+)$", record)
        if match:
            return match.group(1).strip()
    return ""


def _first_surname(author_text: str) -> str:
    if not author_text:
        return ""
    first_author = re.split(r"\s+and\s+|;", author_text, maxsplit=1, flags=re.I)[0]
    first_author = re.sub(r"[{}]", "", first_author).strip()
    if "," in first_author:
        return first_author.split(",", 1)[0].strip()
    parts = first_author.split()
    return parts[-1] if parts else ""


def extract_cited_metadata(record: str) -> dict[str, str]:
    is_bib = bool(re.search(r"(?m)^@\w+\s*[({]", record))
    if is_bib:
        title = _field_from_bib(record, "title")
        author = _field_from_bib(record, "author")
        year = _field_from_bib(record, "year")
        journal = _field_from_bib(record, "journal")
    else:
        title = _field_from_tagged(record, ("TI ", "T1 "))
        author = _field_from_tagged(record, ("AU ", "A1 ", "FAU"))
        year = _field_from_tagged(record, ("PY ", "Y1 ", "DP "))
        journal = _field_from_tagged(record, ("JO ", "JF ", "T2 ", "JT "))

    year_match = re.search(r"\b(19|20)\d{2}\b", year)
    return {
        "title": title,
        "first_author": _first_surname(author),
        "year": year_match.group(0) if year_match else "",
        "journal": journal,
    }


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = value.encode("ascii", "ignore").decode("ascii")
    return " ".join(re.findall(r"[a-z0-9]+", value.lower()))


def similar(left: str, right: str, threshold: float) -> bool:
    left_normalized = normalize_text(left)
    right_normalized = normalize_text(right)
    if not left_normalized or not right_normalized:
        return False
    return (
        difflib.SequenceMatcher(None, left_normalized, right_normalized).ratio()
        >= threshold
    )


def compare_metadata(
    cited: dict[str, str], resolved: dict[str, Any]
) -> dict[str, list[str]]:
    compared: list[str] = []
    mismatches: list[str] = []

    if cited["title"] and resolved.get("title"):
        compared.append("title")
        if not similar(cited["title"], str(resolved["title"]), 0.85):
            mismatches.append("title")

    if cited["first_author"] and resolved.get("first_author"):
        compared.append("first_author")
        if normalize_text(cited["first_author"]) != normalize_text(
            str(resolved["first_author"])
        ):
            mismatches.append("first_author")

    if cited["year"] and resolved.get("year"):
        compared.append("year")
        if cited["year"] != str(resolved["year"]):
            mismatches.append("year")

    if cited["journal"] and resolved.get("container_title"):
        compared.append("journal")
        if not similar(cited["journal"], str(resolved["container_title"]), 0.75):
            mismatches.append("journal")

    return {"compared": compared, "mismatches": mismatches}


def metadata_status(
    result: dict[str, Any], comparison: dict[str, list[str]]
) -> str:
    if not result.get("ok"):
        return "unresolved"
    if comparison["mismatches"]:
        return "metadata_mismatch"
    if comparison["compared"]:
        return "metadata_match"
    return "doi_resolves"


def audit_text(
    text: str,
    lookup: Callable[[str], Dict[str, Any]] = crossref_lookup,
) -> list[dict[str, Any]]:
    dois = extract_dois(text)
    counts = Counter(doi.lower() for doi in dois)
    cache: dict[str, Dict[str, Any]] = {}
    seen: set[str] = set()
    rows: list[dict[str, Any]] = []

    for doi in dois:
        key = doi.lower()
        if key not in cache:
            cache[key] = lookup(doi)
        result = cache[key]
        cited = extract_cited_metadata(reference_record(text, doi))
        comparison = compare_metadata(cited, result) if result.get("ok") else {
            "compared": [],
            "mismatches": [],
        }
        rows.append({
            "doi": doi,
            "status": metadata_status(result, comparison),
            "duplicate": "yes" if counts[key] > 1 and key in seen else "no",
            "compared_fields": ",".join(comparison["compared"]),
            "mismatch_fields": ",".join(comparison["mismatches"]),
            "cited_title": cited["title"],
            "crossref_title": result.get("title", ""),
            "cited_first_author": cited["first_author"],
            "crossref_first_author": result.get("first_author", ""),
            "cited_year": cited["year"],
            "crossref_year": result.get("year", ""),
            "cited_journal": cited["journal"],
            "crossref_journal": result.get("container_title", ""),
            "type": result.get("type", ""),
            "publisher": result.get("publisher", ""),
            "error": result.get("error", ""),
            "context": chunk_reference_context(text, doi)[:500],
        })
        seen.add(key)

    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit DOI resolution and cited metadata via Crossref"
    )
    parser.add_argument("reference_file", help="Reference file, such as .bib, .ris, .txt")
    parser.add_argument("--out", default="reference_audit.tsv", help="Output TSV file")
    args = parser.parse_args()

    path = Path(args.reference_file)
    if not path.is_file():
        print(f"REFERENCE AUDIT ERROR: file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8", errors="replace")
    rows = audit_text(text)
    with open(args.out, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

    if not rows:
        print(f"No DOI records found; coverage=NOT_ASSESSED; wrote {args.out}")
        return 2

    unresolved = sum(row["status"] == "unresolved" for row in rows)
    mismatched = sum(row["status"] == "metadata_mismatch" for row in rows)
    duplicates = sum(row["duplicate"] == "yes" for row in rows)
    print(
        f"Audited {len(rows)} DOI records; unresolved={unresolved}; "
        f"metadata_mismatch={mismatched}; duplicates={duplicates}; wrote {args.out}"
    )
    return 1 if unresolved or mismatched or duplicates else 0


if __name__ == "__main__":
    raise SystemExit(main())
