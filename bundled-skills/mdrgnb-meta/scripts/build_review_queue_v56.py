#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

from missingness_v56 import REVIEWABLE_STATUS_CODES, normalize_code


def read_table(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t" if path.suffix.lower() == ".tsv" else ","))


def build(candidates: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    now = datetime.now(timezone.utc).isoformat()
    for index, row in enumerate(candidates, 1):
        status = normalize_code(row.get("value_status_code"))
        if status not in REVIEWABLE_STATUS_CODES:
            continue
        options = json.loads(row.get("options_json") or "[]")
        if not isinstance(options, list) or not 2 <= len(options) <= 6 or len({str(x) for x in options}) != len(options):
            raise ValueError(f"candidate {row.get('fact_id', index)} needs 2-6 unique options")
        recommended = (row.get("recommended_answer") or "").strip()
        if not recommended:
            raise ValueError(f"candidate {row.get('fact_id', index)} needs a recommended answer")
        if recommended not in {str(x) for x in options}:
            raise ValueError(f"candidate {row.get('fact_id', index)} recommendation is not an option")
        required = ("report_id", "entity_type", "entity_id", "field_name", "source_locator",
                    "recommendation_basis", "writeback_table", "writeback_key")
        missing = [key for key in required if not (row.get(key) or "").strip()]
        if missing:
            raise ValueError(f"candidate {row.get('fact_id', index)} missing {missing}")
        if not (row.get("evidence_a") or "").strip() and not (row.get("evidence_b") or "").strip():
            raise ValueError(f"candidate {row.get('fact_id', index)} needs branch evidence")
        if status == "CONFLICT" and (not (row.get("evidence_a") or "").strip() or not (row.get("evidence_b") or "").strip()):
            raise ValueError(f"candidate {row.get('fact_id', index)} conflict needs A and B evidence")
        output.append({
            "question_id": f"Q-{index:05d}", "priority": row.get("priority", "MEDIUM"),
            "report_id": row.get("report_id", ""), "entity_type": row.get("entity_type", ""),
            "entity_id": row.get("entity_id", ""), "field_name": row.get("field_name", ""),
            "issue_type": status, "evidence_a": row.get("evidence_a", ""),
            "evidence_b": row.get("evidence_b", ""), "source_locator": row.get("source_locator", ""),
            "recommended_answer": recommended, "recommendation_basis": row.get("recommendation_basis", ""),
            "options_json": json.dumps(options, ensure_ascii=False), "user_answer": "",
            "adjudication_rationale": "", "status": "OPEN",
            "writeback_table": row.get("writeback_table", ""), "writeback_key": row.get("writeback_key", ""),
            "writeback_field": row.get("field_name", ""), "expected_type": row.get("expected_type", "CATEGORY"),
            "allowed_values": row.get("allowed_values") or json.dumps(options, ensure_ascii=False),
            "created_at": now, "resolved_at": "",
        })
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a focused v5.6 human review queue")
    parser.add_argument("--candidates", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = build(read_table(args.candidates))
    if not rows:
        raise SystemExit("No reviewable candidates")
    with args.out.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t")
        writer.writeheader(); writer.writerows(rows)
    print(json.dumps({"protocol": "v5.6", "questions": len(rows), "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
