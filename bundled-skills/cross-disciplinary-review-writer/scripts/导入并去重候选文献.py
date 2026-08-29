#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from review_project_schema import CANDIDATE_HEADERS, SCHEMA_VERSION


YES_TOKENS = {"1", "true", "yes", "y", "是", "可获取", "open", "oa"}

SOURCE_ALIASES = {
    "title": ["题名", "title", "ArticleTitle"],
    "authors": ["作者", "authors", "authorString", "Authors"],
    "year": ["年份", "year", "pubYear", "Year"],
    "venue": ["来源期刊/会议/出版社", "journal", "journalTitle", "source", "Source"],
    "doi": ["DOI/链接", "doi", "DOI"],
    "pmid": ["pmid", "PMID"],
    "pmcid": ["pmcid", "PMCID"],
    "type": ["文献类型", "title_type", "publication_type", "category"],
    "design": ["研究设计/方法类型", "evidence_hint", "study_type"],
    "subtheme": ["子主题标签", "subtheme", "source_queries"],
    "oa": ["是否可获取全文", "oa", "isOpenAccess", "open_access"],
}


def normalize_text(value: str) -> str:
    normalized = value.strip().lower().replace("\ufeff", "")
    for token in (" ", "\t", "\r", "\n", "_", "-", "/", "\\"):
        normalized = normalized.replace(token, "")
    return normalized


def is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


def truthy(value: str | None) -> bool:
    if is_blank(value):
        return False
    normalized = normalize_text(value)
    return normalized in {normalize_text(token) for token in YES_TOKENS}


def first_value(row: dict[str, str], aliases: list[str]) -> str:
    alias_set = {normalize_text(alias) for alias in aliases}
    for key, value in row.items():
        if normalize_text(key) in alias_set:
            return (value or "").strip()
    return ""


def detect_source_type(headers: list[str]) -> str:
    normalized = {normalize_text(header) for header in headers}
    if {"pmid", "pmcid", "sourcequeries"} & normalized:
        return "europepmc"
    if {"articletitle", "authors", "pmid"} <= normalized:
        return "pubmed"
    return "generic"


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [{(key or "").strip(): (value or "").strip() for key, value in row.items()} for row in reader]


def canonical_key(row: dict[str, str]) -> str:
    for alias_name in ("doi", "pmid", "pmcid", "title"):
        value = first_value(row, SOURCE_ALIASES[alias_name])
        if not is_blank(value):
            return normalize_text(value)
    return ""


def choose_identifier(row: dict[str, str], sequence: int) -> str:
    for alias_name in ("pmid", "pmcid", "doi"):
        value = first_value(row, SOURCE_ALIASES[alias_name])
        if not is_blank(value):
            return value
    return f"IMPORT-{sequence:04d}"


def map_row(
    row: dict[str, str],
    *,
    sequence: int,
    batch_name: str,
    database_name: str,
    retrieval_date: str,
    default_subtheme: str,
    source_file: Path,
    duplicate_target: str | None,
) -> dict[str, str]:
    identifier = choose_identifier(row, sequence)
    title = first_value(row, SOURCE_ALIASES["title"])
    authors = first_value(row, SOURCE_ALIASES["authors"])
    year = first_value(row, SOURCE_ALIASES["year"])
    venue = first_value(row, SOURCE_ALIASES["venue"])
    doi = first_value(row, SOURCE_ALIASES["doi"])
    document_type = first_value(row, SOURCE_ALIASES["type"])
    design = first_value(row, SOURCE_ALIASES["design"])
    subtheme = first_value(row, SOURCE_ALIASES["subtheme"]) or default_subtheme
    fulltext = "是" if truthy(first_value(row, SOURCE_ALIASES["oa"])) else ""

    mapped = {header: "" for header in CANDIDATE_HEADERS}
    mapped["文献编号"] = identifier
    mapped["检索批次"] = batch_name
    mapped["数据库/来源"] = database_name
    mapped["检索日期"] = retrieval_date
    mapped["题名"] = title
    mapped["作者"] = authors
    mapped["年份"] = year
    mapped["来源期刊/会议/出版社"] = venue
    mapped["DOI/链接"] = doi
    mapped["文献类型"] = document_type
    mapped["研究设计/方法类型"] = design
    mapped["子主题标签"] = subtheme
    mapped["去重状态"] = "保留" if duplicate_target is None else f"重复 -> {duplicate_target}"
    mapped["是否可获取全文"] = fulltext
    mapped["备注"] = f"schema={SCHEMA_VERSION}; source_file={source_file.name}"
    return mapped


def write_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="导入外部题录 CSV，并生成候选文献表模板格式")
    parser.add_argument("输入文件", nargs="+", help="一个或多个来源 CSV")
    parser.add_argument("--output", required=True, help="输出候选文献表 CSV 路径")
    parser.add_argument("--database-name", default="", help="写入 数据库/来源 列")
    parser.add_argument("--batch-name", default="", help="写入 检索批次 列，默认使用当前时间")
    parser.add_argument("--retrieval-date", default=datetime.now().strftime("%Y-%m-%d"), help="写入 检索日期 列")
    parser.add_argument("--default-subtheme", default="", help="当来源文件没有子主题信息时写入默认子主题")
    args = parser.parse_args()

    input_paths = [Path(item).expanduser().resolve() for item in args.输入文件]
    output_path = Path(args.output).expanduser().resolve()
    batch_name = args.batch_name or datetime.now().strftime("import-%Y%m%d-%H%M%S")

    rows_out: list[dict[str, str]] = []
    seen_keys: dict[str, str] = {}
    duplicate_count = 0
    imported_count = 0

    for path in input_paths:
        rows = load_rows(path)
        source_type = detect_source_type(list(rows[0].keys())) if rows else "generic"
        database_name = args.database_name or source_type
        for index, row in enumerate(rows, start=1):
            imported_count += 1
            key = canonical_key(row)
            duplicate_target = seen_keys.get(key) if key else None
            mapped = map_row(
                row,
                sequence=imported_count,
                batch_name=batch_name,
                database_name=database_name,
                retrieval_date=args.retrieval_date,
                default_subtheme=args.default_subtheme,
                source_file=path,
                duplicate_target=duplicate_target,
            )
            rows_out.append(mapped)
            if key and duplicate_target is None:
                seen_keys[key] = mapped["文献编号"]
            elif duplicate_target is not None:
                duplicate_count += 1

    write_rows(output_path, rows_out)
    print(f"[OK] 已写出候选文献表: {output_path}")
    print(f"[OK] schema={SCHEMA_VERSION}; imported={imported_count}; duplicates={duplicate_count}; retained={imported_count - duplicate_count}")


if __name__ == "__main__":
    main()
