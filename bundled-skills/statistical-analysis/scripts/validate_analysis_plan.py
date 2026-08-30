#!/usr/bin/env python3
"""Validate the minimum reproducible contract for a statistical analysis plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED = ("analysis_unit", "outcome", "estimand", "design", "primary_analysis", "assumptions", "missing_data_plan", "sensitivity_analyses", "multiplicity_plan", "reproducibility")


def validate(plan: Dict[str, Any]) -> Dict[str, Any]:
    missing = [key for key in REQUIRED if plan.get(key) in (None, "", [], {})]
    objective = str(plan.get("objective", "")).lower()
    objective_valid = objective in {"descriptive", "predictive", "causal", "associational"}
    primary = str(plan.get("primary_analysis", "")).lower()
    needs_separation = "logistic" in primary or "binomial" in primary
    separation_ok = not needs_separation or bool(plan.get("separation_screen"))
    observational = str(plan.get("design", "")).lower() in {"cohort", "case-control", "cross-sectional", "registry", "survey"}
    operationalization = bool(plan.get("variable_operationalization"))
    return {
        "artifact": "statistical-analysis-preflight-v1",
        "status": "READY_FOR_EXECUTION" if not missing and objective_valid and separation_ok else "BLOCKED",
        "checks": {
            "required_fields": {"passed": not missing, "missing": missing},
            "objective_classification": {"passed": objective_valid, "value": objective or None},
            "separation_screen": {"passed": separation_ok, "required": needs_separation},
            "variable_operationalization": {"passed": operationalization, "required": False, "detail": "recommended for observational designs" if observational else "not required by design"},
        },
        "plan": {key: plan.get(key) for key in REQUIRED},
        "limitations": ["Plan validation does not produce statistical estimates or scientific conclusions."],
        "next_action": "Run the plan on governed data with diagnostics and report any assumption failures." if not missing and objective_valid and separation_ok else "Supply the missing plan fields, objective classification, and any required separation screen before analysis.",
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a statistical analysis plan JSON object.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    payload = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        parser.error("input must be a JSON object")
    result = validate(payload)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] == "READY_FOR_EXECUTION" else 2


if __name__ == "__main__":
    raise SystemExit(main())
