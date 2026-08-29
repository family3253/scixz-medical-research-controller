#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from recover_schema_drift_v57 import (
    BLOCKING_AUDIT_CODES, COMPANION_FILES, MISSING, SPECS, clean, observed, read_tsv,
)


BLOCKING_AUDIT_RESOLUTIONS = set(BLOCKING_AUDIT_CODES)
COMPANION_COVERAGE_FIELDS = {
    "source_path", "source_row", "source_column", "entity_type", "report_id", "study_id",
    "entity_id", "field_name", "source_value", "result_status", "result_value", "visible_01",
}


def count_map(value: object, label: str, errors: list[str]) -> dict[str, int]:
    if not isinstance(value, dict):
        errors.append(f"manifest missing or invalid {label}")
        return {}
    result: dict[str, int] = {}
    for key, count in value.items():
        if not isinstance(key, str) or not isinstance(count, int) or isinstance(count, bool) or count < 0:
            errors.append(f"manifest {label} has invalid count for {key!r}: {count!r}")
            continue
        result[key] = count
    return result


def manifest_count(counts: dict, name: str, errors: list[str]) -> int | None:
    value = counts.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(f"manifest missing or invalid counts.{name}")
        return None
    return value


def truthy_01(value: object) -> bool:
    return clean(value).upper() in {"1", "TRUE", "YES", "Y"}


def row_identity(row: dict[str, str]) -> tuple[str, str, str]:
    return tuple(clean(row.get(k)) for k in ("report_id", "study_id", "entity_id"))


def validate(root: Path, mode: str = "migration") -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = root / "recovery_manifest.json"
    facts_path = root / "recovered_field_facts.tsv"
    audit_path = root / "recovery_audit.tsv"
    unresolved_path = root / "unresolved_fields.tsv"
    for path in (manifest_path, facts_path, audit_path, unresolved_path):
        if not path.is_file():
            errors.append(f"missing recovery artifact: {path.name}")
    if errors:
        return {"protocol": "v5.7", "mode": mode, "pass": False, "errors": errors, "warnings": warnings}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    _, facts = read_tsv(facts_path)
    _, audit = read_tsv(audit_path)
    _, unresolved = read_tsv(unresolved_path)
    keys: set[tuple[str, str, str, str, str]] = set()
    statuses: Counter[str] = Counter()
    recovered_entities: dict[str, set[tuple[str, str, str]]] = {}
    facts_by_key: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    for row in facts:
        key = tuple(clean(row.get(k)) for k in ("report_id", "study_id", "entity_type", "entity_id", "field_name"))
        if not all(key) or key in keys:
            errors.append(f"blank or duplicate recovered fact key: {key}")
        keys.add(key)
        facts_by_key[key] = row
        entity_type = key[2]
        recovered_entities.setdefault(entity_type, set()).add((key[0], key[1], key[3]))
        status = clean(row.get("value_status_code")).upper()
        statuses[status] += 1
        if status not in {"OBSERVED", "NOT_CAPTURED", "PENDING_REVIEW", "CONFLICT"}:
            errors.append(f"{key}: invalid recovery status {status or '<blank>'}")
        if status == "NR_SOURCE":
            errors.append(f"{key}: schema recovery cannot assert NR_SOURCE without a source-search contract")
        raw = clean(row.get("raw_value")); normalized = clean(row.get("normalized_value"))
        if status == "OBSERVED":
            if not raw and not normalized:
                errors.append(f"{key}: OBSERVED has no value")
            if raw.upper() in MISSING or normalized.upper() in MISSING:
                errors.append(f"{key}: legacy missing token marked OBSERVED")
        elif raw or normalized:
            errors.append(f"{key}: {status} hides a value in value columns")
        try:
            candidates = json.loads(row.get("candidate_values_json") or "[]")
            if not isinstance(candidates, list):
                raise ValueError
        except (json.JSONDecodeError, ValueError):
            errors.append(f"{key}: invalid candidate_values_json")
    audit_resolution_counts = Counter(clean(r.get("resolution")).upper() for r in audit)
    blocking_audit_counts = {
        code: audit_resolution_counts[code]
        for code in sorted(BLOCKING_AUDIT_RESOLUTIONS)
        if audit_resolution_counts[code]
    }
    for code, count in blocking_audit_counts.items():
        errors.append(f"blocking recovery audit resolution {code}: {count} row(s)")
    unmapped = [r for r in audit if clean(r.get("resolution")).upper() in {
        "UNMAPPED_NONMISSING_SOURCE_FIELD", "UNMAPPED_BRANCH_ENTITY_ID"
    }]
    if unmapped:
        errors.append(f"{len(unmapped)} nonmissing source fields lack semantic mappings")
    if manifest.get("guarantees", {}).get("a_b_conflict_silently_resolved") is not False:
        errors.append("manifest does not guarantee conflict preservation")
    if manifest.get("guarantees", {}).get("companion_tables_materialized") is not True:
        errors.append("manifest does not guarantee companion materialization")
    counts = manifest.get("counts")
    if not isinstance(counts, dict):
        errors.append("manifest missing or invalid counts")
        counts = {}
    canonical_claims = count_map(counts.get("canonical_entities"), "counts.canonical_entities", errors)
    entity_claims = count_map(counts.get("entities"), "counts.entities", errors)
    claimed_facts = manifest_count(counts, "facts", errors)
    claimed_statuses = count_map(counts.get("statuses"), "counts.statuses", errors)
    claimed_blockers = manifest_count(counts, "blocking_audit_issues", errors)
    claimed_unmapped = manifest_count(counts, "unmapped_or_unlinked_source_fields", errors)
    actual_blockers = sum(blocking_audit_counts.values())
    if claimed_blockers is not None and claimed_blockers != actual_blockers:
        errors.append(
            f"manifest blocking audit count {claimed_blockers} != recovery audit count {actual_blockers}"
        )
    if claimed_unmapped is not None and claimed_unmapped != len(unmapped):
        errors.append(
            f"manifest unmapped source count {claimed_unmapped} != recovery audit count {len(unmapped)}"
        )
    if claimed_facts is not None and claimed_facts != len(facts):
        errors.append(f"manifest facts {claimed_facts} != recovered fact count {len(facts)}")
    if claimed_statuses != dict(statuses):
        errors.append(f"manifest status counts {claimed_statuses} != recovered status counts {dict(statuses)}")

    view_rows: dict[str, list[dict[str, str]]] = {}
    view_by_identity: dict[str, dict[tuple[str, str, str], dict[str, str]]] = {}
    tables = set(canonical_claims) | set(entity_claims) | set(recovered_entities)
    for table in sorted(tables):
        if table not in SPECS:
            errors.append(f"manifest or facts contain unknown recovered entity table: {table}")
            continue
        view = root / "views" / f"{table}_recovered.tsv"
        canonical_expected = canonical_claims.get(table, 0)
        expected = entity_claims.get(table, 0)
        actual_entities = len(recovered_entities.get(table, set()))
        entity_keys = recovered_entities.get(table, set())
        expected_fact_keys = {
            (report_id, study_id, table, entity_id, field)
            for report_id, study_id, entity_id in entity_keys
            for field in SPECS[table]["fields"]
        }
        actual_fact_keys = {key for key in keys if key[2] == table}
        missing_fact_keys = expected_fact_keys - actual_fact_keys
        extra_fact_keys = actual_fact_keys - expected_fact_keys
        if missing_fact_keys:
            errors.append(f"{table}: {len(missing_fact_keys)} expected field facts are missing")
        if extra_fact_keys:
            errors.append(f"{table}: {len(extra_fact_keys)} undeclared field facts are present")
        if canonical_expected != expected:
            errors.append(f"{table}: canonical entity count {canonical_expected} != recovered manifest count {expected}")
        if actual_entities != expected:
            errors.append(f"{table}: recovered fact entity count {actual_entities} != manifest count {expected}")
        if expected and not view.is_file():
            errors.append(f"missing recovered view for {table}")
        elif view.is_file():
            view_headers, rows = read_tsv(view)
            view_rows[table] = rows
            expected_view_headers = {"report_id", "study_id", "entity_id"}
            for field in SPECS[table]["fields"]:
                expected_view_headers.update({field, field + "__status"})
            if set(view_headers) != expected_view_headers:
                errors.append(f"{table}: recovered view headers do not match the declared field inventory")
            if len(rows) != expected:
                errors.append(f"{table}: recovered view row count {len(rows)} != {expected}")
            identities = [row_identity(row) for row in rows]
            if any(not all(identity) for identity in identities):
                errors.append(f"{table}: recovered view has blank report/study/entity identity")
            if len(set(identities)) != len(identities):
                errors.append(f"{table}: recovered view has duplicate entity rows")
            view_by_identity[table] = {row_identity(row): row for row in rows}

    companions = manifest.get("companion_tables_consumed")
    if not isinstance(companions, list) or any(not isinstance(x, str) or not x for x in companions):
        errors.append("manifest companion_tables_consumed must be a list of filenames")
        companions = []
    claimed_companions = {Path(x).name for x in companions}
    if len(claimed_companions) != len(companions):
        errors.append("manifest companion_tables_consumed contains duplicate filenames")
    unknown_companions = sorted(claimed_companions - COMPANION_FILES)
    if unknown_companions:
        errors.append(f"manifest claims unknown companion tables: {', '.join(unknown_companions)}")
    companion_sources = manifest.get("companion_sources_consumed")
    claimed_source_paths: set[str] = set()
    if not isinstance(companion_sources, list):
        errors.append("manifest companion_sources_consumed must be a list")
        companion_sources = []
    for index, source in enumerate(companion_sources, 1):
        if not isinstance(source, dict):
            errors.append(f"companion source {index} is not an object")
            continue
        source_path = Path(clean(source.get("path")))
        source_name = clean(source.get("name"))
        source_hash = clean(source.get("sha256")).lower()
        if not source_path.is_absolute() or not source_path.is_file() or source_name != source_path.name:
            errors.append(f"companion source {index} has an invalid path/name")
            continue
        actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if source_hash != actual_hash:
            errors.append(f"companion source {index} hash mismatch")
        normalized_path = str(source_path.resolve())
        if normalized_path in claimed_source_paths:
            errors.append(f"duplicate companion source path: {source_path}")
        claimed_source_paths.add(normalized_path)
    if {Path(path).name for path in claimed_source_paths} != claimed_companions:
        errors.append("companion source paths and companion table names disagree")

    coverage_path = root / "companion_coverage.tsv"
    coverage_rows: list[dict[str, str]] = []
    if not coverage_path.is_file():
        errors.append("missing recovery artifact: companion_coverage.tsv")
    else:
        coverage_headers, coverage_rows = read_tsv(coverage_path)
        missing_headers = sorted(COMPANION_COVERAGE_FIELDS - set(coverage_headers))
        if missing_headers:
            errors.append(f"companion_coverage.tsv missing columns: {', '.join(missing_headers)}")

    claimed_coverage_rows = manifest_count(counts, "companion_coverage_rows", errors)
    claimed_visible = manifest_count(counts, "companion_coverage_visible", errors)
    claimed_failed = manifest_count(counts, "companion_coverage_failed", errors)
    actual_visible = sum(truthy_01(r.get("visible_01")) for r in coverage_rows)
    actual_failed = len(coverage_rows) - actual_visible
    for label, claimed, actual in (
        ("companion_coverage_rows", claimed_coverage_rows, len(coverage_rows)),
        ("companion_coverage_visible", claimed_visible, actual_visible),
        ("companion_coverage_failed", claimed_failed, actual_failed),
    ):
        if claimed is not None and claimed != actual:
            errors.append(f"manifest {label} {claimed} != actual {actual}")
    if claimed_visible is not None and claimed_failed is not None and claimed_coverage_rows is not None:
        if claimed_visible + claimed_failed != claimed_coverage_rows:
            errors.append("manifest companion coverage visible + failed does not equal rows")

    coverage_by_companion: Counter[str] = Counter()
    companion_source_cache: dict[Path, tuple[list[str], list[dict[str, str]]]] = {}
    for row_number, row in enumerate(coverage_rows, 2):
        declared_source = Path(clean(row.get("source_path")))
        source_name = declared_source.name
        coverage_by_companion[source_name] += 1
        if source_name not in claimed_companions:
            errors.append(f"companion coverage row {row_number} comes from unclaimed table {source_name or '<blank>'}")
        source_path = declared_source
        if not source_path.is_absolute():
            canonical_root = Path(clean(manifest.get("canonical_source")))
            canonical_candidate = canonical_root / source_name
            source_path = canonical_candidate if canonical_candidate.is_file() else root / declared_source
        if source_path.is_absolute() and str(source_path.resolve()) not in claimed_source_paths:
            errors.append(f"companion coverage row {row_number} source path is not declared in the manifest")
        if not source_path.is_file():
            errors.append(f"companion coverage row {row_number} source file is missing: {declared_source}")
        else:
            if source_path not in companion_source_cache:
                companion_source_cache[source_path] = read_tsv(source_path)
            source_headers, source_rows = companion_source_cache[source_path]
            source_column = clean(row.get("source_column"))
            try:
                source_row_number = int(clean(row.get("source_row")))
            except ValueError:
                source_row_number = 0
            if source_column not in source_headers or source_row_number < 2 or source_row_number > len(source_rows) + 1:
                errors.append(f"companion coverage row {row_number} has an invalid source coordinate")
            elif clean(source_rows[source_row_number - 2].get(source_column)) != clean(row.get("source_value")):
                errors.append(f"companion coverage row {row_number} disagrees with the source companion cell")
        entity_type = clean(row.get("entity_type"))
        fact_key = tuple(clean(row.get(k)) for k in (
            "report_id", "study_id", "entity_type", "entity_id", "field_name"
        ))
        source_value = clean(row.get("source_value"))
        normalized_source_value = clean(row.get("normalized_source_value")) or source_value
        result_value = clean(row.get("result_value"))
        result_status = clean(row.get("result_status")).upper()
        visible = truthy_01(row.get("visible_01"))
        if not all(fact_key) or not observed(source_value):
            errors.append(f"companion coverage row {row_number} has a blank identity or source value")
        if (result_status != "OBSERVED" or not observed(result_value) or
                result_value != normalized_source_value or not visible):
            errors.append(f"companion coverage row {row_number} is not visibly materialized")
        fact = facts_by_key.get(fact_key)
        if fact is None:
            errors.append(f"companion coverage row {row_number} has no recovered fact {fact_key}")
        else:
            fact_status = clean(fact.get("value_status_code")).upper()
            fact_value = clean(fact.get("normalized_value") or fact.get("raw_value"))
            if fact_status != "OBSERVED" or fact_value != result_value:
                errors.append(f"companion coverage row {row_number} disagrees with recovered fact")
        matching_view = view_by_identity.get(entity_type, {}).get((fact_key[0], fact_key[1], fact_key[3]))
        field = fact_key[4]
        if matching_view is None:
            errors.append(f"companion coverage row {row_number} has no unique recovered view row")
        elif (clean(matching_view.get(field)) != result_value or
              clean(matching_view.get(field + "__status")).upper() != "OBSERVED"):
            errors.append(f"companion coverage row {row_number} is not visible in the recovered view")
    for name in sorted(claimed_companions):
        if not coverage_by_companion[name]:
            errors.append(f"manifest claims companion {name} but no rows were consumed")
    if actual_failed:
        errors.append(f"{actual_failed} companion value row(s) are not export-visible")
    if mode == "freeze":
        blockers = {"NOT_CAPTURED", "PENDING_REVIEW", "CONFLICT"}
        present = sorted(code for code in blockers if statuses[code])
        if present:
            errors.append(f"freeze blocked by statuses: {', '.join(present)}")
        if unresolved:
            errors.append(f"freeze blocked by {len(unresolved)} unresolved fields")
    return {"protocol": "v5.7", "mode": mode, "pass": not errors,
            "counts": {"facts": len(facts), "statuses": dict(statuses), "unmapped": len(unmapped),
                       "unresolved": len(unresolved), "blocking_audit_issues": actual_blockers,
                       "canonical_entities": canonical_claims, "entities": entity_claims,
                       "companion_coverage_rows": len(coverage_rows),
                       "companion_coverage_visible": actual_visible,
                       "companion_coverage_failed": actual_failed},
            "errors": errors, "warnings": warnings}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate schema recovery, field overlays, and companion materialization")
    parser.add_argument("--recovery-root", type=Path, required=True)
    parser.add_argument("--mode", choices=("migration", "freeze"), default="migration")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = validate(args.recovery_root, args.mode)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
