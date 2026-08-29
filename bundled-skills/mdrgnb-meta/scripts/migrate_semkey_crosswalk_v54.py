#!/usr/bin/env python3
"""Add auditable v5.4 relation groups to a clean legacy crosswalk.

This is deliberately conservative. A legacy crosswalk that reuses any A/B/third
source entity is not auto-migrated, because reuse may be either a legitimate split
or a factual mapping error. Such packages require source-adjudicated repair.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from protocol_v54 import read_tsv, write_json
from qa_semantic_key_v1 import validate

RELATION_COLUMNS = [
    "relation_group_id", "a_source_cardinality", "b_source_cardinality",
    "third_source_cardinality", "final_cardinality", "relation_basis_code",
    "relation_evidence_id",
]


def source_duplicates(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    counts: Counter[tuple[str, str, str, str, str]] = Counter()
    for row in rows:
        for branch in ("a", "b", "third"):
            sid = row.get(f"{branch}_entity_id", "").strip()
            if sid not in {"", "NA"}:
                counts[(branch, row.get("report_id", ""), row.get("study_id", ""), row.get("entity_type", ""), sid)] += 1
    return [{"source_identity": list(key), "occurrences": n} for key, n in counts.items() if n > 1]


def migrate(alignment: Path, crosswalk: Path, output: Path) -> dict:
    headers, rows = read_tsv(crosswalk)
    duplicates = source_duplicates(rows)
    if duplicates:
        return {
            "protocol": "SEMKEY_CROSSWALK_MIGRATION_V54", "pass": False,
            "status": "REQUIRES_FACTUAL_CROSSWALK_REPAIR", "errors": [
                "legacy source entities are reused; automatic ONE_TO_ONE migration is forbidden"
            ], "duplicate_source_groups": duplicates, "rows": len(rows),
        }
    new_header = headers + [c for c in RELATION_COLUMNS if c not in headers]
    migrated = []
    for i, src in enumerate(rows, 1):
        row = dict(src)
        represented = {b: row.get(f"{b}_entity_id", "").strip() not in {"", "NA"} for b in ("a", "b", "third")}
        removed = row.get("mapping_decision", "") in {"REMOVED_DUPLICATE", "REMOVED_INELIGIBLE_ENTITY"}
        final_present = row.get("final_entity_id", "").strip() not in {"", "NA"} and not removed
        if removed:
            decision, basis, final_cardinality = row["mapping_decision"], "SOURCE_REMOVAL", 0
        elif any(represented.values()):
            decision, basis, final_cardinality = "ONE_TO_ONE", "IDENTITY", 1
        else:
            decision, basis, final_cardinality = "ADDED_BY_ADJUDICATION", "ADJUDICATOR_ADDITION", 1
        if not final_present and final_cardinality == 1:
            return {"protocol":"SEMKEY_CROSSWALK_MIGRATION_V54","pass":False,"status":"INVALID_LEGACY_ROW",
                    "errors":[f"row {i+1}: expected final entity"],"rows":len(rows)}
        row.update({
            "mapping_decision": decision, "relation_group_id": f"REL-MIG-{i:05d}",
            "a_source_cardinality": "1" if represented["a"] else "0",
            "b_source_cardinality": "1" if represented["b"] else "0",
            "third_source_cardinality": "1" if represented["third"] else "0",
            "final_cardinality": str(final_cardinality), "relation_basis_code": basis,
            "relation_evidence_id": row.get("final_evidence_id", "") or "UNCLEAR",
        })
        migrated.append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=new_header, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(migrated)
    result = validate(alignment, output, None, False)
    return {"protocol":"SEMKEY_CROSSWALK_MIGRATION_V54","pass":result["pass"],
            "status":"MIGRATED_STRICT" if result["pass"] else "MIGRATED_BUT_INVALID",
            "errors":result["errors"],"warnings":result["warnings"],"rows":len(rows),
            "output":str(output),"strict_validation":result}


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--alignment",type=Path,required=True)
    parser.add_argument("--crosswalk",type=Path,required=True); parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--out",type=Path); args=parser.parse_args()
    result=migrate(args.alignment,args.crosswalk,args.output); write_json(result,args.out)
    return 0 if result["pass"] else 1


if __name__=="__main__": raise SystemExit(main())
