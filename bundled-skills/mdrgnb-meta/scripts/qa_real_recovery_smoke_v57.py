#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from recover_schema_drift_v57 import clean, read_tsv


EXPECTED_ENTITY_COUNTS = {
    "study": 40, "dataset": 144, "performance": 338,
    "threshold": 500, "calibration": 90, "predictor": 745,
}


def validate(root: Path) -> dict:
    errors: list[str] = []
    manifest_path = root / "recovery_manifest.json"
    facts_path = root / "recovered_field_facts.tsv"
    coverage_path = root / "companion_coverage.tsv"
    if not all(path.is_file() for path in (manifest_path, facts_path, coverage_path)):
        return {"protocol": "v5.7-real-smoke", "pass": False,
                "errors": ["missing manifest, recovered facts, or companion coverage"]}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _, facts = read_tsv(facts_path)
    _, coverage = read_tsv(coverage_path)
    entity_counts = manifest.get("counts", {}).get("entities", {})
    for table, expected in EXPECTED_ENTITY_COUNTS.items():
        if entity_counts.get(table) != expected:
            errors.append(f"{table}: expected {expected} entities, found {entity_counts.get(table)!r}")
    if any(clean(row.get("visible_01")) != "1" for row in coverage):
        errors.append("at least one final companion value is not export-visible")

    observed = {
        (row["study_id"], row["entity_type"], row["entity_id"], row["field_name"]): row["normalized_value"]
        for row in facts if clean(row.get("value_status_code")).upper() == "OBSERVED"
    }
    expected_values = {
        ("STU-018", "performance", "PERF018-AUC-APP", "estimate"): "0.792",
        ("STU-018", "performance", "PERF018-AUC-APP", "ci"): "0.615-0.869",
        ("STU-018", "threshold", "THR018-P48", "sensitivity"): "0.85",
        ("STU-018", "threshold", "THR018-P48", "specificity"): "0.831",
        ("STU-018", "calibration", "CAL018-HL", "hl_p"): "0.723",
        ("STU-018", "dataset", "DS018-DEV", "sample_n"): "119",
        ("STU-018", "dataset", "DS018-DEV", "event_n"): "60",
        ("STU-031", "performance", "P-031-M031_CIM-D031_CV-AUC", "estimate"): "0.945",
        ("STU-031", "performance", "P-031-M031_CLINICAL-D031_CV-AUC", "estimate"): "0.843",
        ("STU-039", "calibration", "CAL039_1", "calibration_intercept"): "-3.60",
        ("STU-039", "calibration", "CAL039_2", "calibration_slope"): "5.76",
        ("STU-039", "calibration", "CAL039_3", "brier_score"): "0.029",
        ("STU-039", "calibration", "CAL039_4", "calibration_plot_01"): "1",
    }
    for key, expected in expected_values.items():
        if observed.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, found {observed.get(key)!r}")

    aucs_039 = Counter(
        value for (study, entity_type, entity_id, field), value in observed.items()
        if study == "STU-039" and entity_type == "performance" and field == "estimate" and entity_id.endswith("-AUC")
    )
    if aucs_039 != Counter({"0.82": 2, "0.81": 1, "0.61": 1}):
        errors.append(f"STU-039 AUC multiset mismatch: {dict(aucs_039)}")
    return {"protocol": "v5.7-real-smoke", "pass": not errors,
            "counts": {"facts": len(facts), "coverage": len(coverage), "stu039_aucs": dict(aucs_039)},
            "errors": errors}


def main() -> int:
    parser = argparse.ArgumentParser(description="Project-level smoke test for repaired MDR-GNB facts")
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate(args.recovery_root)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
