#!/usr/bin/env python3
"""Validate the reproducible intake contract for multiomics integration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


REQUIRED = ("question", "modalities", "analysis_unit", "sample_matching", "provenance", "batch", "missingness_plan", "integration_objective", "validation_design", "claim_level", "leakage_control")


def validate(plan: Dict[str, Any]) -> Dict[str, Any]:
    missing = [key for key in REQUIRED if plan.get(key) in (None, "", [], {})]
    matched = bool(plan.get("sample_matching", {}).get("matched")) if isinstance(plan.get("sample_matching"), dict) else False
    provenance = bool(plan.get("provenance", {}).get("verified")) if isinstance(plan.get("provenance"), dict) else False
    claim_level = str(plan.get("claim_level", "")).lower()
    claim_valid = claim_level in {"associational", "predictive", "mechanistic"}
    status = "READY_FOR_EXECUTION" if not missing and matched and provenance and claim_valid else "BLOCKED"
    return {
        "artifact": "multiomics-analysis-preflight-v1",
        "status": status,
        "checks": {
            "required_fields": {"passed": not missing, "missing": missing},
            "matched_samples": {"passed": matched},
            "provenance_verified": {"passed": provenance},
            "claim_level": {"passed": claim_valid, "value": claim_level or None},
        },
        "plan": {key: plan.get(key) for key in REQUIRED},
        "limitations": ["Preflight does not generate molecular findings, pathway enrichment, or mechanistic claims."],
        "next_action": "Run documented preprocessing and integration with held-out or independent validation." if status == "READY_FOR_EXECUTION" else "Repair missing metadata, matching, or provenance before cross-omics integration.",
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a multiomics integration plan JSON object.")
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
