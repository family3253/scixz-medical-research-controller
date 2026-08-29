from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from review_project_schema import CANDIDATE_HEADERS, SCHEMA_VERSION


SOURCE_ALIASES = {
    "title": ["title", "articletitle", "paper title", "标题"],
    "authors": ["authors", "authorstring", "author", "作者"],
    "year": ["year", "pubyear", "publication year", "年份"],
    "venue": ["journal", "journaltitle", "source", "venue", "期刊"],
    "doi": ["doi", "doi/link", "链接"],
    "pmid": ["pmid"],
    "pmcid": ["pmcid"],
    "type": ["publication_type", "category", "type", "文献类型"],
    "thesis_type": ["thesis_type", "论文类型", "学位论文类型", "degree_type"],
    "degree_level": ["degree_level", "degree", "学位", "学位级别"],
    "institution": [
        "institution",
        "granting_institution",
        "授予单位",
        "学位授予单位",
        "学校",
        "机构",
    ],
    "advisor": ["advisor", "supervisor", "导师"],
    "institution_filter": ["institution_filter", "unit_filter", "机构筛选", "学校筛选"],
    "source_provider": ["source_provider", "provider", "平台", "来源平台"],
    "access_mode": ["access_mode", "访问方式", "获取方式"],
    "design": ["study_type", "evidence_hint", "设计"],
    "topic_tag": ["topic_tag", "subtheme", "source_queries", "主题标签"],
    "full_text": [
        "full_text_available",
        "oa",
        "open_access",
        "isopenaccess",
        "hasfulltext",
        "是否全文",
    ],
}


def norm(value: str) -> str:
    result = (value or "").strip().lower().replace("\ufeff", "")
    for token in (" ", "\t", "\r", "\n", "_", "-", "/", "\\"):
        result = result.replace(token, "")
    return result


def truthy(value: str) -> bool:
    return norm(value) in {"1", "true", "yes", "y", "open", "oa", "available"}


def first_value(row: dict[str, str], aliases: list[str]) -> str:
    alias_set = {norm(a) for a in aliases}
    for key, value in row.items():
        if norm(key) in alias_set:
            return (value or "").strip()
    return ""


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [
            {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            for row in reader
        ]


def canonical_key(row: dict[str, str]) -> str:
    for field in ("doi", "pmid", "pmcid", "title"):
        value = first_value(row, SOURCE_ALIASES[field])
        if value:
            return norm(value)
    return ""


def choose_id(row: dict[str, str], seq: int) -> str:
    for field in ("pmid", "pmcid", "doi"):
        value = first_value(row, SOURCE_ALIASES[field])
        if value:
            return value
    return f"IMPORT-{seq:04d}"


def map_row(
    row: dict[str, str],
    *,
    seq: int,
    batch_name: str,
    database_name: str,
    retrieval_date: str,
    default_topic_tag: str,
    source_file: Path,
    duplicate_target: str | None,
) -> dict[str, str]:
    mapped = {header: "" for header in CANDIDATE_HEADERS}
    mapped["citation_id"] = choose_id(row, seq)
    mapped["search_batch"] = batch_name
    mapped["database_source"] = database_name
    mapped["source_provider"] = (
        first_value(row, SOURCE_ALIASES["source_provider"]) or database_name
    )
    mapped["access_mode"] = first_value(row, SOURCE_ALIASES["access_mode"])
    mapped["retrieval_date"] = retrieval_date
    mapped["title"] = first_value(row, SOURCE_ALIASES["title"])
    mapped["authors"] = first_value(row, SOURCE_ALIASES["authors"])
    mapped["year"] = first_value(row, SOURCE_ALIASES["year"])
    mapped["venue"] = first_value(row, SOURCE_ALIASES["venue"])
    mapped["doi_or_link"] = first_value(row, SOURCE_ALIASES["doi"])
    mapped["document_type"] = first_value(row, SOURCE_ALIASES["type"])
    mapped["thesis_type"] = first_value(row, SOURCE_ALIASES["thesis_type"])
    mapped["degree_level"] = first_value(row, SOURCE_ALIASES["degree_level"])
    mapped["granting_institution"] = first_value(row, SOURCE_ALIASES["institution"])
    mapped["advisor"] = first_value(row, SOURCE_ALIASES["advisor"])
    mapped["institution_filter"] = first_value(
        row, SOURCE_ALIASES["institution_filter"]
    )
    mapped["study_or_evidence_hint"] = first_value(row, SOURCE_ALIASES["design"])
    mapped["topic_tag"] = (
        first_value(row, SOURCE_ALIASES["topic_tag"]) or default_topic_tag
    )
    mapped["duplicate_status"] = (
        "unique" if duplicate_target is None else f"duplicate -> {duplicate_target}"
    )
    mapped["full_text_available"] = (
        "yes" if truthy(first_value(row, SOURCE_ALIASES["full_text"])) else ""
    )
    mapped["notes"] = f"schema={SCHEMA_VERSION}; source_file={source_file.name}"
    return mapped


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Normalize external export CSVs into AWAS candidate-pool schema."
    )
    parser.add_argument("input_files", nargs="+")
    parser.add_argument("--output", required=True)
    parser.add_argument("--database-name", default="")
    parser.add_argument("--batch-name", default="")
    parser.add_argument("--retrieval-date", default="")
    parser.add_argument("--default-topic-tag", default="")
    args = parser.parse_args()

    batch_name = args.batch_name or datetime.now().strftime("batch-%Y%m%d-%H%M%S")
    retrieval_date = args.retrieval_date or datetime.now().strftime("%Y-%m-%d")
    all_rows: list[dict[str, str]] = []
    seen: dict[str, str] = {}
    seq = 1

    for file_str in args.input_files:
        source_file = Path(file_str).expanduser().resolve()
        for row in load_rows(source_file):
            key = canonical_key(row)
            duplicate_target = seen.get(key) if key else None
            mapped = map_row(
                row,
                seq=seq,
                batch_name=batch_name,
                database_name=args.database_name or source_file.stem,
                retrieval_date=retrieval_date,
                default_topic_tag=args.default_topic_tag,
                source_file=source_file,
                duplicate_target=duplicate_target,
            )
            if key and duplicate_target is None:
                seen[key] = mapped["citation_id"]
            all_rows.append(mapped)
            seq += 1

    write_rows(Path(args.output).expanduser().resolve(), all_rows)
    duplicate_count = sum(
        1 for row in all_rows if row["duplicate_status"].startswith("duplicate")
    )
    print(f"[ok] wrote {len(all_rows)} rows; duplicates flagged: {duplicate_count}")


if __name__ == "__main__":
    main()
