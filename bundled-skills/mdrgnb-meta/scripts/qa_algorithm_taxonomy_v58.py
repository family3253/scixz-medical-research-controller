#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

FAMILY_MAP = {
    "LOGISTIC_REGRESSION_UNPENALISED": ("TRADITIONAL_STATISTICAL", "TRADITIONAL"),
    "LOGISTIC_REGRESSION_PENALISED": ("TRADITIONAL_STATISTICAL", "TRADITIONAL"),
    "OTHER_CONVENTIONAL_REGRESSION": ("TRADITIONAL_STATISTICAL", "TRADITIONAL"),
    "DISCRIMINANT_OR_BAYES_CLASSIFIER": ("TRADITIONAL_STATISTICAL", "TRADITIONAL"),
    "EXPERT_OR_HEURISTIC_RULE": ("EXPERT_OR_HEURISTIC_RULE", "NOT_CLASSIFIABLE"),
    "DECISION_TREE_SINGLE": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "RANDOM_FOREST_OR_EXTRA_TREES": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "GRADIENT_BOOSTING_TREE": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "SUPPORT_VECTOR_MACHINE": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "K_NEAREST_NEIGHBOURS": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "NEURAL_NETWORK_OR_DEEP_LEARNING": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "STACKED_VOTING_OR_OTHER_ENSEMBLE": ("MACHINE_LEARNING", "MACHINE_LEARNING"),
    "OTHER_ALGORITHM": ("OTHER_UNCLEAR", "NOT_CLASSIFIABLE"),
    "ALGORITHM_UNCLEAR": ("OTHER_UNCLEAR", "NOT_CLASSIFIABLE"),
}

REQUIRED = {
    "algorithm_name_raw",
    "algorithm_name_normalized",
    "algorithm_family_v58",
    "algorithm_superclass_v58",
    "traditional_vs_ml_code",
    "regularization_code",
    "ensemble_status",
    "score_derivation_code",
    "author_designated_final_01",
    "model_role_code",
    "dependent_effect_cluster_id",
}


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate(path: Path, mode: str = "freeze") -> dict:
    rows = read_rows(path)
    if not rows:
        return {"pass": False, "errors": ["facts file is empty"], "warnings": [], "models": 0}
    field_col = "field_code" if "field_code" in rows[0] else "field_name"
    value_col = "normalized_value" if "normalized_value" in rows[0] else "value"
    status_col = "value_status" if "value_status" in rows[0] else None
    grouped: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    for row in rows:
        if (row.get("entity_type") or "").strip() != "MODEL":
            continue
        if status_col and (row.get(status_col) or "").strip() not in {"OBSERVED", "NA_STRUCTURAL"}:
            continue
        key = (
            (row.get("report_id") or "").strip(),
            (row.get("study_id") or "").strip(),
            (row.get("entity_id") or "").strip(),
        )
        field = (row.get(field_col) or "").strip()
        value = (row.get(value_col) or row.get("raw_value") or "").strip()
        if field and value:
            grouped[key][field] = value

    errors: list[str] = []
    warnings: list[str] = []
    for key, facts in sorted(grouped.items()):
        missing = sorted(REQUIRED - facts.keys())
        if missing:
            target = errors if mode == "freeze" else warnings
            target.append(f"{key}: missing algorithm fields: {', '.join(missing)}")
        family = facts.get("algorithm_family_v58")
        if family:
            if family not in FAMILY_MAP:
                errors.append(f"{key}: unknown algorithm_family_v58={family}")
            else:
                expected_super, expected_binary = FAMILY_MAP[family]
                if facts.get("algorithm_superclass_v58") and facts["algorithm_superclass_v58"] != expected_super:
                    errors.append(
                        f"{key}: {family} requires algorithm_superclass_v58={expected_super}"
                    )
                if facts.get("traditional_vs_ml_code") and facts["traditional_vs_ml_code"] != expected_binary:
                    errors.append(
                        f"{key}: {family} requires traditional_vs_ml_code={expected_binary}"
                    )
        score_code = facts.get("score_derivation_code")
        if score_code and score_code not in {"NOT_SCORE", "EXPERT_RULE"} and not facts.get("mother_model_id"):
            target = errors if mode == "freeze" else warnings
            target.append(f"{key}: derived score/nomogram requires mother_model_id")

    payload = {
        "protocol": "v5.8",
        "mode": mode,
        "pass": not errors,
        "models": len(grouped),
        "errors": errors,
        "warnings": warnings,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--mode", choices=["migration", "freeze"], default="freeze")
    args = parser.parse_args()
    payload = validate(args.facts, args.mode)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
