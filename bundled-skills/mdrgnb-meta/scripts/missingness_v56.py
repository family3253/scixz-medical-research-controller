#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass

VALUE_STATUS_CODES = {
    "OBSERVED", "NR_SOURCE", "NA_STRUCTURAL", "NOT_CALCULABLE", "NOT_RUN",
    "NOT_CAPTURED", "UNCLEAR", "PENDING_REVIEW", "SOURCE_NOT_ACCESSIBLE", "CONFLICT",
}
LEGACY_MISSING_TOKENS = {"", "NR", "NA", "N/A", "UNKNOWN", "NOT REPORTED", "未报告", "不详"}
REVIEWABLE_STATUS_CODES = {"UNCLEAR", "PENDING_REVIEW", "CONFLICT"}
FREEZE_BLOCKING_STATUS_CODES = {"NOT_CAPTURED", "PENDING_REVIEW", "CONFLICT"}
EVIDENCE_REQUIRED_STATUS_CODES = {
    "OBSERVED", "NR_SOURCE", "UNCLEAR", "PENDING_REVIEW", "SOURCE_NOT_ACCESSIBLE", "CONFLICT",
}


def normalize_code(value: str | None) -> str:
    return (value or "").strip().upper()


def migrate_legacy_value(value: str | None) -> tuple[str, str]:
    """Return preserved legacy text and its conservative v5.6 status."""
    raw = "" if value is None else str(value).strip()
    if normalize_code(raw) in LEGACY_MISSING_TOKENS:
        return raw, "NOT_CAPTURED"
    return raw, "OBSERVED"


@dataclass(frozen=True)
class FactValidation:
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def validate_fact(row: dict[str, str], evidence_ids: set[str], mode: str = "branch") -> FactValidation:
    errors: list[str] = []
    warnings: list[str] = []
    fact_id = (row.get("fact_id") or "<missing fact_id>").strip()
    status = normalize_code(row.get("value_status_code"))
    raw = (row.get("raw_value") or "").strip()
    normalized = (row.get("normalized_value") or "").strip()
    evidence_id = (row.get("evidence_id") or "").strip()
    rationale = (row.get("status_rationale") or "").strip()

    if status not in VALUE_STATUS_CODES:
        errors.append(f"{fact_id}: invalid value_status_code {status!r}")
        return FactValidation(tuple(errors), tuple(warnings))

    if status == "OBSERVED":
        if not raw and not normalized:
            errors.append(f"{fact_id}: OBSERVED requires raw_value and/or normalized_value")
        if normalize_code(raw) in LEGACY_MISSING_TOKENS or normalize_code(normalized) in LEGACY_MISSING_TOKENS:
            errors.append(f"{fact_id}: literal legacy missing token cannot be OBSERVED")
    elif raw or normalized:
        errors.append(f"{fact_id}: {status} must not hide a value in raw/normalized columns")

    if status in EVIDENCE_REQUIRED_STATUS_CODES:
        if not evidence_id:
            errors.append(f"{fact_id}: {status} requires evidence_id")
        else:
            linked_ids = [x.strip() for x in evidence_id.split("|") if x.strip()]
            missing_ids = [x for x in linked_ids if x not in evidence_ids]
            if not linked_ids or missing_ids:
                errors.append(f"{fact_id}: missing linked evidence IDs {missing_ids or [evidence_id]}")
            if status == "CONFLICT" and len(linked_ids) < 2:
                errors.append(f"{fact_id}: CONFLICT requires at least two linked evidence IDs")

    if status != "OBSERVED" and not rationale:
        errors.append(f"{fact_id}: {status} requires status_rationale")

    if mode == "freeze" and status in FREEZE_BLOCKING_STATUS_CODES:
        errors.append(f"{fact_id}: {status} blocks freeze")
    elif status == "NOT_CAPTURED":
        warnings.append(f"{fact_id}: field requires extraction before closure")

    return FactValidation(tuple(errors), tuple(warnings))
