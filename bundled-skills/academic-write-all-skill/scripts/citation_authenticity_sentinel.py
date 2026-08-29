from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


DOI_PATTERN = re.compile(r"^10\.\d{4,}/[^\s]+$")
ARXIV_PATTERN = re.compile(r"(?:arXiv:)?\d{4}\.\d{4,5}(?:v\d+)?$")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def identity_status(value: str, source: str, title: str, year: str) -> str:
    value = (value or "").strip()
    if value.startswith("10.") and DOI_PATTERN.match(value):
        return "valid_doi_format"
    if (
        "arxiv" in (source or "").lower()
        or value.lower().startswith("arxiv:")
        or ARXIV_PATTERN.match(value)
    ):
        return (
            "valid_arxiv_style"
            if (
                value.lower().startswith("arxiv:")
                or ARXIV_PATTERN.match(value)
                or "arxiv.org" in value.lower()
            )
            else "arxiv_unconfirmed"
        )
    if title and year:
        return "bibliographic_identity_only"
    return "missing_or_invalid"


def source_status(source: str, doc_type: str) -> str:
    source_l = (source or "").lower()
    doc_l = (doc_type or "").lower()
    if "arxiv" in source_l or "preprint" in doc_l:
        return "preprint"
    if any(
        token in doc_l
        for token in ["article", "journal", "conference", "inproceedings"]
    ):
        return "formal_publication"
    return "unknown"


def claim_support_status(row: dict[str, str]) -> str:
    finding = (row.get("key_finding") or "").strip()
    role = (row.get("manuscript_role") or "").strip()
    trace = (row.get("trace_back_page_table_figure_section") or "").strip()
    if finding and role and trace:
        return "supported"
    if finding and role:
        return "weak_traceability"
    return "unsupported"


def manuscript_binding_status(
    citation_id: str, claim_mapping: str, draft_text: str
) -> str:
    in_claims = citation_id in claim_mapping
    in_draft = citation_id in draft_text
    if in_claims and in_draft:
        return "bound_to_claims_and_draft"
    if in_claims:
        return "bound_to_claims_only"
    if in_draft:
        return "bound_to_draft_only"
    return "unbound"


def decision(identity: str, source_s: str, support: str, binding: str) -> str:
    if identity == "missing_or_invalid" or support == "unsupported":
        return "PIVOT"
    if binding == "unbound" or support == "weak_traceability" or source_s == "unknown":
        return "REFINE"
    return "PROCEED"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a four-layer literature authenticity sentinel for an AWAS project."
    )
    parser.add_argument("project_dir")
    args = parser.parse_args()

    root = Path(args.project_dir).expanduser().resolve()
    candidate_rows = read_csv(
        root / "02_candidate_pool_and_screening" / "candidate_pool.csv"
    )
    evidence_rows = read_csv(
        root / "04_evidence_extraction" / "evidence_extraction.csv"
    )
    claim_mapping = read_text(
        root / "06_claim_mapping_and_outline" / "claim_mapping.md"
    )
    draft_text = read_text(root / "07_draft" / "draft_sections.md")

    candidate_index = {row.get("citation_id", ""): row for row in candidate_rows}
    report_rows = []
    counts = {"PROCEED": 0, "REFINE": 0, "PIVOT": 0}

    for row in evidence_rows:
        citation_id = row.get("citation_id", "").strip()
        source_row = candidate_index.get(citation_id, {})
        ident = identity_status(
            source_row.get("doi_or_link", ""),
            source_row.get("database_source", ""),
            row.get("title", ""),
            row.get("year", ""),
        )
        src = source_status(
            source_row.get("database_source", ""),
            source_row.get("document_type", "") or row.get("study_type", ""),
        )
        support = claim_support_status(row)
        binding = manuscript_binding_status(citation_id, claim_mapping, draft_text)
        dec = decision(ident, src, support, binding)
        counts[dec] += 1
        note_parts = []
        if src == "preprint":
            note_parts.append("preprint status should remain visible")
        if binding == "unbound":
            note_parts.append("not referenced in claim mapping or draft")
        report_rows.append(
            (citation_id, ident, src, support, binding, dec, "; ".join(note_parts))
        )

    out = root / "citation_authenticity_report.md"
    lines = [
        "# Citation Authenticity Report",
        "",
        "## Summary",
        "",
        f"- total_citations: {len(report_rows)}",
        f"- proceed_count: {counts['PROCEED']}",
        f"- refine_count: {counts['REFINE']}",
        f"- pivot_count: {counts['PIVOT']}",
        "",
        "## Four-Layer Verification Table",
        "",
        "| Citation ID | Identity | Source Status | Claim Support | Manuscript Binding | Decision | Notes |",
        "|---|---|---|---|---|---|---|",
    ]
    for item in report_rows:
        lines.append(
            f"| {item[0]} | {item[1]} | {item[2]} | {item[3]} | {item[4]} | {item[5]} | {item[6]} |"
        )
    lines.extend(
        [
            "",
            "## Blocking Risks",
            "",
        ]
    )
    pivot_ids = [row[0] for row in report_rows if row[5] == "PIVOT"]
    lines.extend(
        [f"- {cid} should not currently carry its intended claim" for cid in pivot_ids]
        or ["-"]
    )
    lines.extend(
        [
            "",
            "## Required Fixes",
            "",
        ]
    )
    refine_ids = [row[0] for row in report_rows if row[5] == "REFINE"]
    lines.extend(
        [f"- refine citation binding/support for {cid}" for cid in refine_ids] or ["-"]
    )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] wrote citation authenticity report: {out}")


if __name__ == "__main__":
    main()
