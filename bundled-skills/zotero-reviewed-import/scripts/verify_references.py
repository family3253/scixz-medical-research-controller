from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable

import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from docx import Document
from habanero import Crossref
import httpx
from thefuzz import fuzz


DOI_RE = re.compile(r"(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


@dataclass
class VerificationResult:
    raw_reference: str
    status: str
    confidence: float
    title: str = ""
    doi: str = ""
    year: str = ""
    container_title: str = ""
    authors: str = ""
    reason: str = ""
    suggested_citekey: str = ""


def read_input(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    raise ValueError(f"Unsupported input type: {suffix}")


def split_references(text: str) -> list[str]:
    lines = [line.rstrip() for line in text.splitlines()]
    chunks: list[str] = []
    current: list[str] = []

    def flush() -> None:
        if current:
            entry = " ".join(part.strip() for part in current if part.strip()).strip()
            entry = re.sub(r"^\[\d+\]\s*", "", entry)
            entry = re.sub(r"^\d+\.\s*", "", entry)
            if entry:
                chunks.append(entry)
            current.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush()
            continue
        if current and re.match(r"^(\[\d+\]|\d+\.)\s+", stripped):
            flush()
        current.append(stripped)
    flush()

    if len(chunks) <= 1:
        items = [
            re.sub(r"^\s*(\[\d+\]|\d+\.)\s*", "", part).strip()
            for part in re.split(r"\n(?=(?:\[\d+\]|\d+\.)\s+)", text)
            if part.strip()
        ]
        return items or chunks

    return chunks


def authors_to_string(message: dict) -> str:
    authors = message.get("author", [])
    names = []
    for author in authors:
        given = author.get("given", "").strip()
        family = author.get("family", "").strip()
        name = " ".join(part for part in [given, family] if part)
        if name:
            names.append(name)
    return "; ".join(names)


def pick_title(message: dict) -> str:
    titles = message.get("title", [])
    return titles[0].strip() if titles else ""


def pick_container(message: dict) -> str:
    containers = message.get("container-title", [])
    return containers[0].strip() if containers else ""


def pick_year(message: dict) -> str:
    for key in ("published-print", "published-online", "created", "issued"):
        parts = message.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def make_citekey(message: dict) -> str:
    authors = message.get("author", [])
    family = authors[0].get("family", "ref").lower() if authors else "ref"
    title = pick_title(message)
    words = [re.sub(r"[^a-z0-9]+", "", w.lower()) for w in title.split()]
    words = [w for w in words if w]
    short = "".join(words[:3])[:18] or "item"
    year = pick_year(message) or "nd"
    return f"{family}{short}{year}"


def score_candidate(reference: str, message: dict) -> tuple[float, str]:
    title = pick_title(message)
    title_ratio = fuzz.token_set_ratio(reference.lower(), title.lower()) / 100.0 if title else 0.0
    year_hint = YEAR_RE.search(reference)
    candidate_year = pick_year(message)
    year_bonus = 0.08 if year_hint and candidate_year and year_hint.group(0) == candidate_year else 0.0
    doi_bonus = 0.05 if message.get("DOI") else 0.0
    score = min(1.0, title_ratio + year_bonus + doi_bonus)
    reason = f"title_match={title_ratio:.2f}"
    if year_bonus:
        reason += ", year_match=1"
    if doi_bonus:
        reason += ", has_doi=1"
    return score, reason


def query_crossref(reference: str, cr: Crossref) -> VerificationResult:
    doi_match = DOI_RE.search(reference)
    if doi_match:
        doi = doi_match.group(1).rstrip(".,);]")
        try:
            message = cr.works(ids=doi)["message"]
            return build_result(reference, message, 0.99, "verified", "matched by DOI")
        except Exception as exc:
            datacite_result = query_datacite(reference, doi)
            if datacite_result is not None:
                return datacite_result
            return VerificationResult(
                raw_reference=reference,
                status="rejected",
                confidence=0.0,
                doi=doi,
                reason=f"DOI lookup failed: {exc}",
            )

    try:
        resp = cr.works(query_bibliographic=reference, limit=5)
    except Exception as exc:
        return VerificationResult(
            raw_reference=reference,
            status="uncertain",
            confidence=0.0,
            reason=f"Crossref search failed: {exc}",
        )

    items = resp.get("message", {}).get("items", [])
    if not items:
        return VerificationResult(
            raw_reference=reference,
            status="rejected",
            confidence=0.0,
            reason="No candidate returned by Crossref",
        )

    best_message = None
    best_score = -1.0
    best_reason = ""
    for item in items:
        score, reason = score_candidate(reference, item)
        if score > best_score:
            best_message = item
            best_score = score
            best_reason = reason

    assert best_message is not None

    if best_score >= 0.82:
        status = "verified"
    elif best_score >= 0.65:
        status = "uncertain"
    else:
        status = "rejected"

    return build_result(reference, best_message, best_score, status, best_reason)


def query_datacite(reference: str, doi: str) -> VerificationResult | None:
    url = f"https://api.datacite.org/dois/{doi}"
    try:
        response = httpx.get(url, timeout=15)
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return None

    attributes = payload.get("data", {}).get("attributes", {})
    titles = attributes.get("titles", [])
    creators = attributes.get("creators", [])
    title = titles[0].get("title", "").strip() if titles else ""
    authors = []
    for creator in creators:
        name = creator.get("name") or " ".join(
            part for part in [creator.get("givenName", "").strip(), creator.get("familyName", "").strip()] if part
        )
        if name:
            authors.append(name)

    return VerificationResult(
        raw_reference=reference,
        status="verified",
        confidence=0.95,
        title=title,
        doi=doi,
        year=str(attributes.get("publicationYear", "")),
        container_title=attributes.get("publisher", ""),
        authors="; ".join(authors),
        reason="matched by DOI via DataCite fallback",
        suggested_citekey=make_datacite_citekey(title, authors, attributes.get("publicationYear", "")),
    )


def make_datacite_citekey(title: str, authors: list[str], year: str | int | None) -> str:
    family = re.sub(r"[^a-z0-9]+", "", authors[0].split()[-1].lower()) if authors else "ref"
    words = [re.sub(r"[^a-z0-9]+", "", w.lower()) for w in title.split()]
    words = [w for w in words if w]
    short = "".join(words[:3])[:18] or "item"
    return f"{family}{short}{year or 'nd'}"


def build_result(reference: str, message: dict, confidence: float, status: str, reason: str) -> VerificationResult:
    return VerificationResult(
        raw_reference=reference,
        status=status,
        confidence=round(confidence, 3),
        title=pick_title(message),
        doi=message.get("DOI", ""),
        year=pick_year(message),
        container_title=pick_container(message),
        authors=authors_to_string(message),
        reason=reason,
        suggested_citekey=make_citekey(message),
    )


def to_bib_entry(result: VerificationResult) -> dict:
    author_value = " and ".join(part.strip() for part in result.authors.split(";") if part.strip())
    entry = {
        "ENTRYTYPE": "article",
        "ID": result.suggested_citekey or "ref",
        "title": result.title,
        "author": author_value,
        "year": result.year,
        "journal": result.container_title,
        "doi": result.doi,
    }
    return {k: v for k, v in entry.items() if v}


def write_outputs(results: Iterable[VerificationResult], output_dir: Path) -> None:
    results = list(results)

    (output_dir / "verification.json").write_text(
        json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    with (output_dir / "verification.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(asdict(results[0]).keys()) if results else [])
        if results:
            writer.writeheader()
            for item in results:
                writer.writerow(asdict(item))

    lines = ["# Verification Report", ""]
    for item in results:
        lines.extend(
            [
                f"## {item.status.upper()} | {item.confidence:.3f}",
                f"- Raw: {item.raw_reference}",
                f"- Title: {item.title or 'N/A'}",
                f"- DOI: {item.doi or 'N/A'}",
                f"- Year: {item.year or 'N/A'}",
                f"- Source: {item.container_title or 'N/A'}",
                f"- Authors: {item.authors or 'N/A'}",
                f"- Reason: {item.reason}",
                "",
            ]
        )
    (output_dir / "verification.md").write_text("\n".join(lines), encoding="utf-8")

    verified = [item for item in results if item.status == "verified"]
    bib_db = bibtexparser.bibdatabase.BibDatabase()
    bib_db.entries = [to_bib_entry(item) for item in verified]
    writer = BibTexWriter()
    writer.order_entries_by = None
    (output_dir / "verified.bib").write_text(writer.write(bib_db), encoding="utf-8")

    (output_dir / "verified_dois.txt").write_text(
        "\n".join(item.doi for item in verified if item.doi),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify bibliography entries against Crossref before Zotero import.")
    parser.add_argument("--input", required=True, help="Path to .txt, .md, or .docx bibliography file")
    parser.add_argument("--output-dir", help="Optional explicit output directory")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base_output = Path(args.output_dir).expanduser().resolve() if args.output_dir else input_path.parent.parent / "outputs" / stamp
    base_output.mkdir(parents=True, exist_ok=True)

    text = read_input(input_path)
    references = split_references(text)
    cr = Crossref()
    results = [query_crossref(ref, cr) for ref in references if ref.strip()]
    write_outputs(results, base_output)

    verified = sum(1 for item in results if item.status == "verified")
    uncertain = sum(1 for item in results if item.status == "uncertain")
    rejected = sum(1 for item in results if item.status == "rejected")
    print(f"Processed {len(results)} references")
    print(f"Verified: {verified}")
    print(f"Uncertain: {uncertain}")
    print(f"Rejected: {rejected}")
    print(f"Output: {base_output}")


if __name__ == "__main__":
    main()
