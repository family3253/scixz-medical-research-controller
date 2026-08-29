from __future__ import annotations

import csv
import json
import importlib
from pathlib import Path
from string import Template
from typing import Final, cast

JSONValue = str | int | float | bool | None | list["JSONValue"] | dict[str, "JSONValue"]

CANDIDATE_HEADERS: Final[list[str]] = cast(
    list[str],
    importlib.import_module(
        ".review_project_schema" if __package__ else "review_project_schema",
        package=__package__,
    ).CANDIDATE_HEADERS,
)


def load_json(path: Path) -> dict[str, JSONValue]:
    return cast(dict[str, JSONValue], json.loads(path.read_text(encoding="utf-8")))


def render_templates(value: JSONValue, variables: dict[str, str]) -> JSONValue:
    if isinstance(value, str):
        rendered = value
        for key, replacement in variables.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", replacement)
        return Template(rendered).safe_substitute(**variables)
    if isinstance(value, list):
        return [render_templates(item, variables) for item in value]
    if isinstance(value, dict):
        return {key: render_templates(val, variables) for key, val in value.items()}
    return value


def truthy(value: JSONValue) -> bool:
    return str(value or "").strip().lower() in {
        "1",
        "true",
        "yes",
        "y",
        "open",
        "oa",
        "available",
    }


def normalize_candidate_row(
    raw: dict[str, JSONValue], defaults: dict[str, str]
) -> dict[str, str]:
    row = {header: "" for header in CANDIDATE_HEADERS}
    row.update(defaults)
    for header in CANDIDATE_HEADERS:
        if header in raw and raw[header] is not None:
            row[header] = str(raw[header]).strip()

    if not row["full_text_available"] and truthy(
        raw.get("hasFulltext") or raw.get("full_text_available")
    ):
        row["full_text_available"] = "yes"
    if not row["title"]:
        row["title"] = str(raw.get("paper_title") or raw.get("name") or "").strip()
    if not row["authors"]:
        authors = raw.get("authors") or raw.get("creators") or []
        if isinstance(authors, list):
            row["authors"] = "; ".join(
                str(item).strip() for item in authors if str(item).strip()
            )
    if not row["granting_institution"]:
        units = raw.get("unitNames") or raw.get("institutions") or []
        if isinstance(units, list):
            row["granting_institution"] = "; ".join(
                str(item).strip() for item in units if str(item).strip()
            )
    if not row["venue"]:
        row["venue"] = str(raw.get("periodicalTitle") or raw.get("venue") or "").strip()
    if not row["year"]:
        row["year"] = str(raw.get("publishYear") or raw.get("year") or "").strip()
    if not row["citation_id"]:
        row["citation_id"] = str(
            raw.get("id")
            or raw.get("citation_id")
            or raw.get("doi")
            or raw.get("title")
            or ""
        ).strip()
    if not row["doi_or_link"]:
        row["doi_or_link"] = str(
            raw.get("doi") or raw.get("url") or raw.get("link") or ""
        ).strip()
    if not row["document_type"]:
        row["document_type"] = str(
            raw.get("type") or raw.get("document_type") or ""
        ).strip()
    if not row["source_provider"]:
        row["source_provider"] = defaults.get("source_provider", "")
    if not row["duplicate_status"]:
        row["duplicate_status"] = "unique"
    return row


def write_candidate_rows(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CANDIDATE_HEADERS)
        writer.writeheader()
        writer.writerows(rows)
