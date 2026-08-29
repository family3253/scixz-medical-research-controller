#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from missingness_v56 import REVIEWABLE_STATUS_CODES, normalize_code, validate_fact

FACT_REQUIRED = {
    "fact_id", "report_id", "study_id", "entity_type", "entity_id", "field_name",
    "raw_value", "normalized_value", "value_status_code", "status_rationale", "evidence_id",
    "extractor_id", "review_round", "branch_status", "adjudication_status", "writeback_table",
    "status_rule_id", "context_json", "writeback_key",
}
EVIDENCE_REQUIRED = {
    "evidence_id", "report_id", "source_file_id", "source_sha256", "page_or_location",
    "table_figure_section", "evidence_span", "extraction_method", "search_scope",
    "reviewer_id", "timestamp",
}
QUESTION_REQUIRED = {
    "question_id", "priority", "report_id", "entity_type", "entity_id", "field_name", "issue_type",
    "evidence_a", "evidence_b", "source_locator", "recommended_answer", "recommendation_basis",
    "options_json", "user_answer", "adjudication_rationale", "status", "writeback_table",
    "writeback_key", "writeback_field", "expected_type", "allowed_values", "created_at", "resolved_at",
}
SOURCE_MANIFEST_REQUIRED = {
    "source_file_id", "report_id", "source_sha256", "source_role", "access_status",
    "text_layer_status", "ocr_status", "page_count", "included_in_complete_search_01",
}
STRUCTURAL_RULE_REQUIRED = {
    "rule_id", "entity_type", "field_name", "condition_field", "condition_operator",
    "condition_value", "rule_version", "rationale", "active_01",
}
BRANCH_STATUS_CODES = {"OPEN", "FROZEN_A", "FROZEN_B", "FROZEN_THIRD", "FROZEN_FINAL"}
ADJUDICATION_STATUS_CODES = {"NOT_ADJUDICATED", "PENDING_ADJUDICATION", "BRANCH", "FINAL_ADJUDICATED"}


def read_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        delimiter = "\t" if path.suffix.lower() == ".tsv" else csv.Sniffer().sniff(sample, delimiters=",\t;").delimiter
        reader = csv.DictReader(handle, delimiter=delimiter)
        return list(reader.fieldnames or []), list(reader)


def require_headers(name: str, headers: list[str], required: set[str], errors: list[str]) -> None:
    missing = sorted(required - set(headers))
    if missing:
        errors.append(f"{name}: missing required headers: {', '.join(missing)}")


def evaluate_structural_rule(rule: dict[str, str], context: dict) -> bool:
    field = (rule.get("condition_field") or "").strip()
    operator = normalize_code(rule.get("condition_operator"))
    expected = (rule.get("condition_value") or "").strip()
    present = field in context and context[field] is not None and context[field] != ""
    actual = context.get(field)
    if operator == "PRESENT":
        return present
    if operator == "ABSENT":
        return not present
    if operator in {"EQ", "NE", "IN", "NOT_IN"} and not present:
        return False
    if operator == "EQ":
        return normalize_code(str(actual)) == normalize_code(expected)
    if operator == "NE":
        return normalize_code(str(actual)) != normalize_code(expected)
    allowed = {normalize_code(x) for x in expected.split("|") if x.strip()}
    if operator == "IN":
        return normalize_code(str(actual)) in allowed
    if operator == "NOT_IN":
        return normalize_code(str(actual)) not in allowed
    raise ValueError(f"unsupported condition_operator {operator!r}")


def validate(
    facts_path: Path,
    evidence_path: Path,
    questions_path: Path | None,
    source_manifest_path: Path,
    structural_rules_path: Path,
    mode: str,
) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    fact_headers, facts = read_table(facts_path)
    evidence_headers, evidence = read_table(evidence_path)
    source_headers, sources = read_table(source_manifest_path)
    rule_headers, structural_rules = read_table(structural_rules_path)
    require_headers("facts", fact_headers, FACT_REQUIRED, errors)
    require_headers("evidence", evidence_headers, EVIDENCE_REQUIRED, errors)
    require_headers("source_manifest", source_headers, SOURCE_MANIFEST_REQUIRED, errors)
    require_headers("structural_rules", rule_headers, STRUCTURAL_RULE_REQUIRED, errors)
    if errors:
        return {"protocol": "v5.6", "mode": mode, "pass": False, "errors": errors, "warnings": warnings}

    source_by_id: dict[str, dict[str, str]] = {}
    complete_sources_by_report: dict[str, set[str]] = {}
    for row in sources:
        source_id = (row.get("source_file_id") or "").strip()
        report_id = (row.get("report_id") or "").strip()
        if not source_id or source_id in source_by_id:
            errors.append(f"source_manifest: blank or duplicate source_file_id {source_id!r}")
            continue
        for key in SOURCE_MANIFEST_REQUIRED:
            if not (row.get(key) or "").strip():
                errors.append(f"{source_id}: source manifest field {key} is required")
        source_by_id[source_id] = row
        if normalize_code(row.get("included_in_complete_search_01")) in {"1", "TRUE", "YES"} and normalize_code(row.get("access_status")) in {"ACCESSIBLE", "AVAILABLE", "FULLTEXT_AVAILABLE"}:
            complete_sources_by_report.setdefault(report_id, set()).add(source_id)

    structural_rule_by_id: dict[str, dict[str, str]] = {}
    for row in structural_rules:
        rule_id = (row.get("rule_id") or "").strip()
        if not rule_id or rule_id in structural_rule_by_id:
            errors.append(f"structural_rules: blank or duplicate rule_id {rule_id!r}")
            continue
        for key in STRUCTURAL_RULE_REQUIRED:
            if not (row.get(key) or "").strip():
                errors.append(f"{rule_id}: structural rule field {key} is required")
        structural_rule_by_id[rule_id] = row

    evidence_ids = {(r.get("evidence_id") or "").strip() for r in evidence if (r.get("evidence_id") or "").strip()}
    evidence_by_id = {(r.get("evidence_id") or "").strip(): r for r in evidence}
    if len(evidence_ids) != len(evidence):
        errors.append("evidence: blank or duplicate evidence_id")
    for row in evidence:
        eid = (row.get("evidence_id") or "<missing>").strip()
        for key in ("report_id", "source_file_id", "source_sha256", "page_or_location", "table_figure_section", "evidence_span",
                    "extraction_method", "search_scope", "reviewer_id", "timestamp"):
            if not (row.get(key) or "").strip():
                errors.append(f"{eid}: evidence field {key} is required")
        source_id = (row.get("source_file_id") or "").strip()
        source_row = source_by_id.get(source_id)
        if not source_row:
            errors.append(f"{eid}: source_file_id {source_id!r} is absent from source manifest")
        else:
            if (source_row.get("report_id") or "").strip() != (row.get("report_id") or "").strip():
                errors.append(f"{eid}: source manifest report mismatch")
            if (source_row.get("source_sha256") or "").strip() != (row.get("source_sha256") or "").strip():
                errors.append(f"{eid}: source SHA-256 mismatch")

    fact_ids: set[str] = set()
    final_keys: set[tuple[str, str, str, str]] = set()
    status_counts: Counter[str] = Counter()
    reviewable_keys: set[tuple[str, str, str, str]] = set()
    for row in facts:
        fid = (row.get("fact_id") or "").strip()
        if not fid or fid in fact_ids:
            errors.append(f"facts: blank or duplicate fact_id {fid!r}")
        fact_ids.add(fid)
        for key in ("report_id", "study_id", "entity_type", "entity_id", "field_name", "extractor_id",
                    "review_round", "branch_status", "adjudication_status", "context_json", "writeback_table", "writeback_key"):
            if not (row.get(key) or "").strip():
                errors.append(f"{fid or '<missing>'}: {key} is required")
        try:
            if not isinstance(json.loads(row.get("context_json") or ""), dict):
                errors.append(f"{fid}: context_json must be an object")
        except json.JSONDecodeError as exc:
            errors.append(f"{fid}: invalid context_json: {exc}")
        result = validate_fact(row, evidence_ids, mode)
        errors.extend(result.errors)
        warnings.extend(result.warnings)
        status = normalize_code(row.get("value_status_code"))
        status_counts[status] += 1
        if normalize_code(row.get("branch_status")) not in BRANCH_STATUS_CODES:
            errors.append(f"{fid}: invalid branch_status")
        if normalize_code(row.get("adjudication_status")) not in ADJUDICATION_STATUS_CODES:
            errors.append(f"{fid}: invalid adjudication_status")
        rule_id = (row.get("status_rule_id") or "").strip()
        if status == "NA_STRUCTURAL":
            rule = structural_rule_by_id.get(rule_id)
            if not rule:
                errors.append(f"{fid}: NA_STRUCTURAL requires a valid status_rule_id")
            else:
                if normalize_code(rule.get("active_01")) not in {"1", "TRUE", "YES"}:
                    errors.append(f"{fid}: structural rule {rule_id} is inactive")
                if (rule.get("entity_type") or "").strip() != (row.get("entity_type") or "").strip() or (rule.get("field_name") or "").strip() != (row.get("field_name") or "").strip():
                    errors.append(f"{fid}: structural rule {rule_id} does not match entity_type/field_name")
                try:
                    context = json.loads(row.get("context_json") or "{}")
                    if not isinstance(context, dict) or not evaluate_structural_rule(rule, context):
                        errors.append(f"{fid}: structural rule {rule_id} condition is not satisfied")
                except (json.JSONDecodeError, TypeError, ValueError) as exc:
                    errors.append(f"{fid}: invalid structural-rule context: {exc}")
        elif rule_id:
            errors.append(f"{fid}: status_rule_id is only valid for NA_STRUCTURAL")
        for linked_evidence_id in [x.strip() for x in (row.get("evidence_id") or "").split("|") if x.strip()]:
            evidence_row = evidence_by_id.get(linked_evidence_id)
            if evidence_row and (evidence_row.get("report_id") or "").strip() != (row.get("report_id") or "").strip():
                errors.append(f"{fid}: evidence {linked_evidence_id} belongs to a different report")
            if status == "NR_SOURCE" and evidence_row:
                try:
                    scope = json.loads(evidence_row.get("search_scope") or "{}")
                    searched = {str(x) for x in scope.get("source_file_ids", [])}
                    locations = scope.get("locations_searched", [])
                    required_sources = complete_sources_by_report.get((row.get("report_id") or "").strip(), set())
                    if scope.get("complete_source_package_01") is not True:
                        raise ValueError("complete_source_package_01 must be true")
                    if scope.get("field_name") != (row.get("field_name") or "").strip():
                        raise ValueError("field_name does not match fact")
                    if scope.get("study_id") != (row.get("study_id") or "").strip():
                        raise ValueError("study_id does not match fact")
                    if scope.get("entity_type") != (row.get("entity_type") or "").strip():
                        raise ValueError("entity_type does not match fact")
                    if scope.get("entity_id") != (row.get("entity_id") or "").strip():
                        raise ValueError("entity_id does not match fact")
                    if not required_sources or not required_sources.issubset(searched):
                        raise ValueError("search does not cover every accessible relevant source")
                    if not isinstance(locations, list) or not locations:
                        raise ValueError("locations_searched is empty")
                except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as exc:
                    errors.append(f"{fid}: invalid NR_SOURCE search_scope: {exc}")
        if mode == "freeze":
            if normalize_code(row.get("branch_status")) != "FROZEN_FINAL":
                errors.append(f"{fid}: freeze requires branch_status FROZEN_FINAL")
            if normalize_code(row.get("adjudication_status")) != "FINAL_ADJUDICATED":
                errors.append(f"{fid}: freeze requires adjudication_status FINAL_ADJUDICATED")
        key = ((row.get("report_id") or "").strip(), (row.get("entity_type") or "").strip(),
               (row.get("entity_id") or "").strip(), (row.get("field_name") or "").strip())
        if status in REVIEWABLE_STATUS_CODES:
            reviewable_keys.add(key)
        if normalize_code(row.get("adjudication_status")) in {"FINAL", "FINAL_ADJUDICATED"}:
            final_key = key
            if final_key in final_keys:
                errors.append(f"facts: duplicate final fact for {final_key}")
            final_keys.add(final_key)

    question_keys: set[tuple[str, str, str, str]] = set()
    if questions_path:
        q_headers, questions = read_table(questions_path)
        require_headers("questions", q_headers, QUESTION_REQUIRED, errors)
        qids: set[str] = set()
        for row in questions:
            qid = (row.get("question_id") or "").strip()
            if not qid or qid in qids:
                errors.append(f"questions: blank or duplicate question_id {qid!r}")
            qids.add(qid)
            for field in ("priority", "report_id", "entity_type", "entity_id", "field_name", "issue_type",
                          "source_locator", "recommendation_basis", "status", "writeback_table", "writeback_key",
                          "writeback_field", "expected_type", "allowed_values", "created_at"):
                if not (row.get(field) or "").strip():
                    errors.append(f"{qid or '<missing>'}: question field {field} is required")
            if not (row.get("evidence_a") or "").strip() and not (row.get("evidence_b") or "").strip():
                errors.append(f"{qid or '<missing>'}: at least one branch evidence value is required")
            if normalize_code(row.get("issue_type")) == "CONFLICT" and (not (row.get("evidence_a") or "").strip() or not (row.get("evidence_b") or "").strip()):
                errors.append(f"{qid or '<missing>'}: CONFLICT question requires evidence_a and evidence_b")
            key = ((row.get("report_id") or "").strip(), (row.get("entity_type") or "").strip(),
                   (row.get("entity_id") or "").strip(), (row.get("field_name") or "").strip())
            question_keys.add(key)
            try:
                options = json.loads(row.get("options_json") or "[]")
                if not isinstance(options, list) or not 2 <= len(options) <= 6 or len({str(x) for x in options}) != len(options):
                    raise ValueError("options must contain 2-6 unique values")
                recommendation = (row.get("recommended_answer") or "").strip()
                if not recommendation:
                    errors.append(f"{qid}: recommended_answer is required")
                elif recommendation not in {str(x) for x in options}:
                    errors.append(f"{qid}: recommended_answer is not in options_json")
            except (json.JSONDecodeError, ValueError) as exc:
                errors.append(f"{qid}: invalid options_json: {exc}")
    missing_questions = sorted(reviewable_keys - question_keys)
    if missing_questions:
        errors.append(f"questions: {len(missing_questions)} reviewable facts lack a question")
    extra_questions = sorted(question_keys - reviewable_keys)
    if extra_questions:
        warnings.append(f"questions: {len(extra_questions)} questions do not map to a reviewable fact")

    return {
        "protocol": "v5.6", "mode": mode, "pass": not errors,
        "counts": {"facts": len(facts), "evidence": len(evidence), "questions": len(question_keys),
                   "status": dict(sorted(status_counts.items()))},
        "errors": errors, "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate MDR-GNB v5.6 extraction fact/evidence package")
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--questions", type=Path)
    parser.add_argument("--source-manifest", type=Path, required=True)
    parser.add_argument("--structural-rules", type=Path, required=True)
    parser.add_argument("--mode", choices=("branch", "freeze"), default="branch")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate(args.facts, args.evidence, args.questions, args.source_manifest, args.structural_rules, args.mode)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
