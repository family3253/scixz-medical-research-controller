#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from protocol_v54 import FALSE, TRUE, norm, read_tsv, write_json

BRANCH_REQUIRED = {
    "eligibility_scope_id", "report_id", "study_id", "cohort_id", "outcome_id", "model_id",
    "model_branch_id", "model_specification_status", "target_present_at_t0_01",
    "future_event_target_01", "organism_unknown_at_t0_01", "current_organism_input_at_t0_01",
    "current_organism_input_level_code", "organism_restricted_cohort_01",
    "organism_restriction_level_code", "organism_restriction_basis_code",
    "prior_colonization_or_infection_history_only_01", "diagnostic_prognostic_code",
    "branch_eligibility_status", "eligibility_reason_code", "inventory_status",
    "synthesis_eligible_01", "source_evidence_id", "adjudication_status",
}
LEGACY_FINAL_REQUIRED = {
    "assessment_id", "report_id", "study_id", "model_id", "target_present_at_t0_01",
    "organism_unknown_at_t0_01", "organism_restricted_cohort_01", "future_event_target_01",
    "diagnostic_vs_prognostic_final", "eligibility_status", "major_flag_code",
    "adjudicator_decision", "adjudication_status",
}


def bool_code(value: str, rid: str, field: str, errors: list[str], allow_missing: bool = False) -> str:
    v = norm(value)
    if v in TRUE: return "1"
    if v in FALSE: return "0"
    if allow_missing and v in {"UNCLEAR", "NR", "NA"}: return v
    errors.append(f"{rid}: invalid {field}={value!r}"); return v


def validate_branch(rows: list[dict[str, str]]) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []; warnings: list[str] = []; seen = set(); by_report = defaultdict(list)
    for row in rows:
        rid = row.get("eligibility_scope_id", "")
        if not rid or rid in seen: errors.append(f"blank/duplicate eligibility_scope_id {rid!r}")
        seen.add(rid); by_report[row.get("report_id", "")].append(row)
        target = bool_code(row.get("target_present_at_t0_01", ""), rid, "target_present_at_t0_01", errors, True)
        future = bool_code(row.get("future_event_target_01", ""), rid, "future_event_target_01", errors, True)
        unknown = bool_code(row.get("organism_unknown_at_t0_01", ""), rid, "organism_unknown_at_t0_01", errors, True)
        input_known = bool_code(row.get("current_organism_input_at_t0_01", ""), rid, "current_organism_input_at_t0_01", errors, True)
        restricted = bool_code(row.get("organism_restricted_cohort_01", ""), rid, "organism_restricted_cohort_01", errors, True)
        eligible = norm(row.get("branch_eligibility_status")) == "INCLUDE_DIAGNOSTIC_CURRENT_STATE"
        synth = norm(row.get("synthesis_eligible_01")) in TRUE
        status, reason = norm(row.get("branch_eligibility_status")), norm(row.get("eligibility_reason_code"))
        fixed = norm(row.get("model_specification_status")) == "FIXED"
        if eligible:
            for condition, msg in ((target != "1", "target not present at T0"), (future != "0", "future target"),
                                   (unknown != "1", "current organism not established unknown"),
                                   (input_known != "0", "known current organism input"),
                                   (restricted != "0", "organism-restricted cohort")):
                if condition: errors.append(f"{rid}: included branch {msg}")
        if synth and (not eligible or not fixed or norm(row.get("adjudication_status")) not in {"FINAL_ADJUDICATED", "FROZEN_FINAL_ADJUDICATED"}):
            errors.append(f"{rid}: synthesis member is not fixed/final/eligible")
        expected_reason = None
        if future == "1" or target == "0": expected_reason = "EXCLUDE_PROGNOSTIC_FUTURE_EVENT"
        elif input_known == "1": expected_reason = "EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"
        elif restricted == "1": expected_reason = "EXCLUDE_ORGANISM_RESTRICTED_COHORT"
        elif norm(row.get("model_specification_status")) == "FINAL_FEATURE_SET_UNREPORTED": expected_reason = "PENDING_FINAL_MODEL_SPECIFICATION"
        if expected_reason and status != expected_reason:
            errors.append(f"{rid}: fields imply {expected_reason}, observed {status}")
        if status.startswith(("EXCLUDE_", "PENDING_", "INVENTORY_")) and reason in {"", "NA"}:
            errors.append(f"{rid}: nonincluded branch lacks eligibility_reason_code")
        level = norm(row.get("current_organism_input_level_code"))
        if input_known == "0" and level not in {"NONE", "NA"}: errors.append(f"{rid}: input level present when input flag=0")
        if input_known == "1" and level in {"", "NONE", "NA"}: errors.append(f"{rid}: known input lacks level")
        rlevel = norm(row.get("organism_restriction_level_code")); rbasis = norm(row.get("organism_restriction_basis_code"))
        if restricted == "0" and (rlevel not in {"NONE", "NA"} or rbasis not in {"NONE", "NA", "OUTCOME_REFERENCE_ONLY"}):
            errors.append(f"{rid}: restriction level/basis conflicts with flag=0")
        if restricted == "1" and (rlevel in {"", "NONE", "NA"} or rbasis in {"", "NONE", "NA", "OUTCOME_REFERENCE_ONLY"}):
            errors.append(f"{rid}: restricted cohort lacks level/basis")
    report_status = {}
    for report, branches in by_report.items():
        statuses = [norm(x.get("branch_eligibility_status")) for x in branches]
        included = sum(x == "INCLUDE_DIAGNOSTIC_CURRENT_STATE" for x in statuses)
        pending = sum(x.startswith("PENDING_") for x in statuses)
        excluded = len(statuses) - included - pending
        if included and (pending or excluded): derived = "INCLUDE_DIAGNOSTIC_BRANCH_ONLY"
        elif included: derived = "INCLUDE_DIAGNOSTIC_MODEL"
        elif pending: derived = "PENDING_PROTOCOL_ADJUDICATION"
        else: derived = "EXCLUDE_ALL_BRANCHES"
        report_status[report] = derived
    return errors, warnings, {"derived_report_status": report_status,
                              "branch_status": dict(Counter(norm(r.get("branch_eligibility_status")) for r in rows))}


def validate_legacy(rows: list[dict[str, str]]) -> tuple[list[str], list[str], dict]:
    errors: list[str] = []; warnings: list[str] = []; seen = set()
    for row in rows:
        rid = norm(row.get("assessment_id"))
        if not rid or rid in seen: errors.append(f"blank/duplicate assessment_id {rid!r}")
        seen.add(rid)
        status = norm(row.get("eligibility_status")); final = norm(row.get("diagnostic_vs_prognostic_final"))
        included = status in {"INCLUDE", "INCLUDE_WITH_FLAG", "INCLUDE_DIAGNOSTIC_MODEL", "INCLUDE_DIAGNOSTIC_BRANCH_ONLY"}
        if included:
            if "DIAGNOSTIC" not in final or "PROGNOSTIC" in final: errors.append(f"{rid}: included row not diagnostic")
            if norm(row.get("target_present_at_t0_01")) not in TRUE: errors.append(f"{rid}: included target not present")
            if norm(row.get("future_event_target_01")) not in FALSE: errors.append(f"{rid}: included future flag not 0")
            if norm(row.get("organism_unknown_at_t0_01")) not in TRUE: errors.append(f"{rid}: included organism not unknown")
            if norm(row.get("organism_restricted_cohort_01")) not in FALSE: errors.append(f"{rid}: included restriction not 0")
        if "PROGNOSTIC" in final or "FUTURE_ACQUISITION" in final:
            if not status.startswith("EXCLUDE"): errors.append(f"{rid}: future row not excluded")
    return errors, warnings, {"eligibility_status": dict(Counter(norm(r.get("eligibility_status")) for r in rows))}


def validate(path: Path, mode: str = "auto") -> dict:
    headers, rows = read_tsv(path); h = set(headers)
    if mode == "auto": mode = "branch" if BRANCH_REQUIRED.issubset(h) else "final"
    required = BRANCH_REQUIRED if mode == "branch" else LEGACY_FINAL_REQUIRED
    missing = sorted(required - h)
    if missing: return {"protocol": "ELIGIBILITY_CONSISTENCY_V1/v5.4", "mode": mode, "pass": False,
                        "errors": [f"missing columns: {missing}"], "warnings": [], "counts": {"rows": len(rows)}}
    errors, warnings, extra = validate_branch(rows) if mode == "branch" else validate_legacy(rows)
    return {"protocol": "ELIGIBILITY_CONSISTENCY_V1/v5.4", "mode": mode, "pass": not errors,
            "errors": errors, "warnings": warnings,
            "counts": {"rows": len(rows), "reports": len({r.get('report_id','') for r in rows}), **extra}}


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("eligibility", type=Path); p.add_argument("--mode", choices=("auto", "branch", "final"), default="auto"); p.add_argument("--out", type=Path)
    a = p.parse_args(); result = validate(a.eligibility, a.mode); write_json(result, a.out); return 0 if result["pass"] else 1


if __name__ == "__main__": raise SystemExit(main())
