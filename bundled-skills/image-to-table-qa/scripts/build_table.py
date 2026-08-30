#!/usr/bin/env python3
"""Normalize auditable OCR extraction records into CSV-ready rows."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List


META_KEYS = ("unit", "flag", "confidence", "status", "raw")


def _cell(value: Any) -> Dict[str, Any]:
    if isinstance(value, dict):
        return {key: value.get(key) for key in ("value", *META_KEYS) if key in value}
    return {"value": value}


def build_table(payload: Dict[str, Any], confidence_threshold: float = 0.8) -> Dict[str, Any]:
    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list):
        raise ValueError("payload.records must be a list")

    seen_sources = set()
    field_order: List[str] = []
    field_meta: Dict[str, List[str]] = {}
    normalized = []

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each record must be an object")
        source = str(record.get("source", "")).strip()
        if not source:
            raise ValueError("record source is required")
        if source in seen_sources:
            raise ValueError(f"duplicate source: {source}")
        seen_sources.add(source)
        fields = record.get("fields")
        if not isinstance(fields, dict):
            raise ValueError(f"record fields must be an object: {source}")
        item = {"source": source, "fields": {}}
        for name, raw_value in fields.items():
            field = str(name).strip()
            if not field:
                continue
            if field not in field_order:
                field_order.append(field)
                field_meta[field] = []
            cell = _cell(raw_value)
            item["fields"][field] = cell
            for key in META_KEYS:
                if key in cell and key not in field_meta[field]:
                    field_meta[field].append(key)
        normalized.append(item)

    columns = ["_source_file", "_review_status"]
    for field in field_order:
        columns.append(field)
        columns.extend(f"{field}__{key}" for key in field_meta[field])

    rows = []
    low_confidence = 0
    unreadable = 0
    review_rows = 0
    for item in normalized:
        row = {column: "" for column in columns}
        row["_source_file"] = item["source"]
        needs_review = False
        for field in field_order:
            cell = item["fields"].get(field, {})
            status = str(cell.get("status", "")).strip().lower()
            if status in {"unreadable", "uncertain", "needs-review", "needs_review"}:
                unreadable += 1
                needs_review = True
            value = cell.get("value", "")
            row[field] = "" if value is None or status == "unreadable" else str(value)
            for key in field_meta[field]:
                meta_value = cell.get(key, "")
                row[f"{field}__{key}"] = "" if meta_value is None else str(meta_value)
            if "confidence" in cell:
                try:
                    if float(cell["confidence"]) < confidence_threshold:
                        low_confidence += 1
                        needs_review = True
                except (TypeError, ValueError):
                    needs_review = True
        row["_review_status"] = "needs-review" if needs_review else "ready"
        if needs_review:
            review_rows += 1
        rows.append(row)

    return {
        "columns": columns,
        "rows": rows,
        "qa": {
            "source_records": len(records),
            "output_rows": len(rows),
            "fields": len(field_order),
            "review_rows": review_rows,
            "low_confidence_cells": low_confidence,
            "unreadable_cells": unreadable,
            "confidence_threshold": confidence_threshold,
        },
    }


def write_outputs(result: Dict[str, Any], csv_path: Path | str, qa_path: Path | str) -> None:
    csv_target = Path(csv_path)
    qa_target = Path(qa_path)
    csv_target.parent.mkdir(parents=True, exist_ok=True)
    qa_target.parent.mkdir(parents=True, exist_ok=True)
    with csv_target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=result["columns"], extrasaction="raise")
        writer.writeheader()
        writer.writerows(result["rows"])
    qa_target.write_text(json.dumps(result["qa"], ensure_ascii=False, indent=2), encoding="utf-8")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize image/OCR extraction records into an auditable table.")
    parser.add_argument("input_json")
    parser.add_argument("--csv", required=True)
    parser.add_argument("--qa", required=True)
    parser.add_argument("--confidence-threshold", type=float, default=0.8)
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input_json).read_text(encoding="utf-8-sig"))
    result = build_table(payload, confidence_threshold=args.confidence_threshold)
    write_outputs(result, args.csv, args.qa)
    print(json.dumps(result["qa"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

