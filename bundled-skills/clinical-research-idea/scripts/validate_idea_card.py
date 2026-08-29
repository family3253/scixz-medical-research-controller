#!/usr/bin/env python3
"""Validate the structure and gating logic of a clinical research Idea Card JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"provisional", "shortlisted", "recommended", "deferred", "reject"}
REQUIRED_TEXT = (
    "title",
    "clinical_decision",
    "research_question",
    "study_type",
    "framework",
    "population",
    "intervention_exposure_test_or_predictors",
    "comparator",
    "outcomes",
    "time_horizon",
    "data_source",
    "evidence_gap",
    "analysis_outline",
    "reporting_guideline",
    "risk_of_bias_tool",
)
REQUIRED_SCORES = {
    "clinical_impact": 0.25,
    "novelty_evidence": 0.15,
    "feasibility": 0.20,
    "methodological_validity": 0.20,
    "ethics_equity": 0.10,
    "reproducibility": 0.10,
}
REQUIRED_GATES = (
    "current_evidence_searched",
    "registry_searched",
    "identifiers_verified",
    "design_reporting_separated",
    "no_fabricated_results",
    "privacy_checked",
)


def is_nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate(card: Any) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(card, dict):
        return {"valid": False, "errors": ["Top-level JSON must be an object."], "warnings": []}

    status = card.get("status")
    if status not in ALLOWED_STATUSES:
        errors.append(f"status must be one of {sorted(ALLOWED_STATUSES)}.")

    for field in REQUIRED_TEXT:
        if not is_nonempty_text(card.get(field)):
            errors.append(f"{field} must be non-empty text.")

    for field in ("bias_risks", "hard_blockers", "assumptions", "next_steps"):
        if not isinstance(card.get(field), list):
            errors.append(f"{field} must be a list.")

    sources = card.get("key_sources")
    if not isinstance(sources, list) or not sources:
        errors.append("key_sources must be a non-empty list.")
        sources = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"key_sources[{index}] must be an object.")
            continue
        for field in ("citation", "identifier", "source_type", "verification_scope", "supports"):
            if not is_nonempty_text(source.get(field)):
                errors.append(f"key_sources[{index}].{field} must be non-empty text.")
        if not isinstance(source.get("verified"), bool):
            errors.append(f"key_sources[{index}].verified must be boolean.")

    feasibility = card.get("feasibility")
    if not isinstance(feasibility, dict):
        errors.append("feasibility must be an object.")
    else:
        for field in ("data_access", "sample_size_or_events", "timeline", "resources"):
            if not is_nonempty_text(feasibility.get(field)):
                errors.append(f"feasibility.{field} must be non-empty text.")

    ethics = card.get("ethics_registration")
    if not isinstance(ethics, dict):
        errors.append("ethics_registration must be an object.")
    else:
        for field in ("irb", "consent", "registration", "privacy"):
            if not is_nonempty_text(ethics.get(field)):
                errors.append(f"ethics_registration.{field} must be non-empty text.")

    scores = card.get("scores")
    weighted_score: float | None = None
    if not isinstance(scores, dict):
        errors.append("scores must be an object.")
    else:
        weighted_score = 0.0
        for field, weight in REQUIRED_SCORES.items():
            value = scores.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                errors.append(f"scores.{field} must be numeric.")
                continue
            if not 0 <= value <= 5:
                errors.append(f"scores.{field} must be between 0 and 5.")
                continue
            weighted_score += float(value) * weight
        weighted_score = round(weighted_score, 2)

    gates = card.get("quality_gates")
    if not isinstance(gates, dict):
        errors.append("quality_gates must be an object.")
        gates = {}
    for field in REQUIRED_GATES:
        if not isinstance(gates.get(field), bool):
            errors.append(f"quality_gates.{field} must be boolean.")

    blockers = card.get("hard_blockers") if isinstance(card.get("hard_blockers"), list) else []
    if status == "recommended":
        failed_gates = [field for field in REQUIRED_GATES if gates.get(field) is not True]
        if failed_gates:
            errors.append("recommended status requires all quality gates to pass: " + ", ".join(failed_gates))
        if blockers:
            errors.append("recommended status is not allowed while hard_blockers is non-empty.")
        if any(source.get("verified") is not True for source in sources if isinstance(source, dict)):
            errors.append("recommended status requires every key source identifier to be verified.")

    if status in {"provisional", "shortlisted"} and not card.get("next_steps"):
        warnings.append(f"{status} status should state next_steps needed for progression.")
    if not blockers and status in {"deferred", "reject"}:
        warnings.append(f"{status} status should usually explain at least one hard blocker or decisive reason.")
    if weighted_score is not None and weighted_score >= 4 and status != "recommended":
        warnings.append("A high weighted score does not itself justify recommended status; confirm gates, blockers, and human decisions.")

    return {
        "valid": not errors,
        "status": status,
        "weighted_score_0_to_5": weighted_score,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="Path to an Idea Card JSON file")
    args = parser.parse_args()

    try:
        card = json.loads(args.path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        print(json.dumps({"valid": False, "errors": [f"File not found: {args.path}"]}, ensure_ascii=False))
        return 2
    except json.JSONDecodeError as exc:
        print(json.dumps({"valid": False, "errors": [f"Invalid JSON: {exc}"]}, ensure_ascii=False))
        return 2

    result = validate(card)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
