#!/usr/bin/env python3
"""Release QA for the v6.0 completion overlay and generated-view contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


LEGACY_TOKENS = {
    "NR", "NA", "N/A", "UNKNOWN", "NR_SOURCE", "NOT_CAPTURED",
    "SOURCE_NOT_ACCESSIBLE",
}
NON_OBSERVED = {
    "NR_SOURCE", "NA_STRUCTURAL", "NOT_CALCULABLE", "NOT_RUN",
    "NOT_CAPTURED", "UNCLEAR", "PENDING_REVIEW", "SOURCE_NOT_ACCESSIBLE",
    "CONFLICT",
}
ALLOWED_STATUSES = {"OBSERVED"} | NON_OBSERVED
RELEASE_BLOCKING_STATUSES = {
    "NOT_CAPTURED", "UNCLEAR", "PENDING_REVIEW", "SOURCE_NOT_ACCESSIBLE", "CONFLICT",
}
MANDATORY_SOURCE_ROLES = {
    "MAIN", "MAIN_ARTICLE", "PRIMARY_REPORT", "FULL_TEXT",
    "SUPPLEMENT", "SUPPLEMENTARY_MATERIAL", "APPENDIX", "ATTACHMENT",
    "CORRECTION", "REGISTRATION",
}
ALLOWED_SOURCE_ROLES = MANDATORY_SOURCE_ROLES | {
    "OTHER", "METHODS_APPENDIX", "DATA_DICTIONARY", "SEARCH_LOG", "ACCESS_LOG",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def value(row: dict[str, str]) -> str:
    return (row.get("normalized_value") or row.get("raw_value") or "").strip()


def normalize_fact(row: dict[str, str]) -> dict[str, str]:
    """Accept compact v6 and canonical v5.6 fact names without silent bypass."""
    normalized = dict(row)
    normalized["field_code"] = row.get("field_code") or row.get("field_name") or ""
    normalized["value_status"] = row.get("value_status") or row.get("value_status_code") or ""
    normalized["derivation_rule"] = row.get("derivation_rule") or row.get("status_rationale") or ""
    normalized["reviewer"] = row.get("reviewer") or row.get("extractor_id") or ""
    normalized["_canonical_v56"] = "1" if (
        "field_name" in row or "value_status_code" in row or "status_rationale" in row
    ) else "0"
    return normalized


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def truthy(value: str) -> bool:
    return (value or "").strip().upper() in {"1", "TRUE", "YES"}


def evaluate_structural_rule(rule: dict[str, str], context: dict) -> bool:
    field = (rule.get("condition_field") or "").strip()
    operator = (rule.get("condition_operator") or "").strip().upper()
    expected = (rule.get("condition_value") or "").strip()
    present = field in context and context[field] not in {None, ""}
    actual = context.get(field)
    if operator == "PRESENT":
        return present
    if operator == "ABSENT":
        return not present
    if operator in {"EQ", "NE", "IN", "NOT_IN"} and not present:
        return False
    actual_code = str(actual).strip().upper()
    expected_code = expected.upper()
    if operator == "EQ":
        return actual_code == expected_code
    if operator == "NE":
        return actual_code != expected_code
    allowed = {x.strip().upper() for x in expected.split("|") if x.strip()}
    if operator == "IN":
        return actual_code in allowed
    if operator == "NOT_IN":
        return actual_code not in allowed
    raise ValueError(f"unsupported condition_operator {operator!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--facts", type=Path, required=True)
    parser.add_argument("--entities", type=Path, required=True)
    parser.add_argument(
        "--evidence",
        type=Path,
        help="Evidence TSV required whenever any effective fact is NR_SOURCE.",
    )
    parser.add_argument(
        "--source-manifest",
        type=Path,
        help="Source manifest required for NR_SOURCE coverage of main text, supplements, and accessible attachments.",
    )
    parser.add_argument(
        "--structural-rules",
        type=Path,
        help="Must be the frozen v6.0 structural-rule table bundled with this skill.",
    )
    parser.add_argument("--mode", choices=("release", "audit"), default="release")
    args = parser.parse_args()

    raw_facts = read_tsv(args.facts)
    fact_headers = set(raw_facts[0]) if raw_facts else set()
    schema_errors: list[dict[str, str]] = []
    required_fact_headers = {
        "report_id", "study_id", "entity_type", "entity_id", "raw_value",
        "normalized_value", "evidence_id", "review_round",
    }
    for missing_header in sorted(required_fact_headers - fact_headers):
        schema_errors.append({
            "code": "FACT_SCHEMA_HEADER_MISSING",
            "field": missing_header,
        })
    if not ({"field_code", "field_name"} & fact_headers):
        schema_errors.append({
            "code": "FACT_SCHEMA_HEADER_MISSING",
            "field": "field_code|field_name",
        })
    if not ({"value_status", "value_status_code"} & fact_headers):
        schema_errors.append({
            "code": "FACT_SCHEMA_HEADER_MISSING",
            "field": "value_status|value_status_code",
        })
    if not ({"derivation_rule", "status_rationale"} & fact_headers):
        schema_errors.append({
            "code": "FACT_SCHEMA_HEADER_MISSING",
            "field": "derivation_rule|status_rationale",
        })
    facts = [normalize_fact(row) for row in raw_facts]
    entities = read_tsv(args.entities)
    evidence = read_tsv(args.evidence) if args.evidence else []
    source_manifest = read_tsv(args.source_manifest) if args.source_manifest else []
    canonical_rule_path = Path(__file__).resolve().parents[1] / "references" / "structural-rules-v60.tsv"
    structural_rule_path = args.structural_rules or canonical_rule_path
    structural_rules = read_tsv(structural_rule_path)
    structural_rule_by_id = {
        (row.get("rule_id") or "").strip(): row
        for row in structural_rules
        if (row.get("rule_id") or "").strip()
    }
    sources_by_id: dict[str, dict[str, str]] = {}
    complete_sources_by_report: dict[str, set[str]] = defaultdict(set)
    source_roles_by_report: dict[str, set[str]] = defaultdict(set)
    source_rows_by_report: dict[str, list[dict[str, str]]] = defaultdict(list)
    source_id_counts: dict[str, int] = defaultdict(int)
    for source in source_manifest:
        report_id = (source.get("report_id") or "").strip()
        source_id = (source.get("source_file_id") or "").strip()
        source_id_counts[source_id] += 1
        if source_id:
            sources_by_id[source_id] = source
        source_rows_by_report[report_id].append(source)
        accessible = (source.get("access_status") or "").strip().upper() in {
            "ACCESSIBLE", "AVAILABLE", "FULLTEXT_AVAILABLE",
        }
        included = (source.get("included_in_complete_search_01") or "").strip().upper() in {
            "1", "TRUE", "YES",
        }
        if report_id and source_id and accessible and included:
            complete_sources_by_report[report_id].add(source_id)
            source_roles_by_report[report_id].add((source.get("source_role") or "").strip().upper())
    entity_keys = {
        (r.get("report_id", ""), r.get("study_id", ""), r.get("entity_type", ""), r.get("entity_id", ""))
        for r in entities
    }
    parent = {
        (r.get("report_id", ""), r.get("study_id", ""), r.get("entity_type", ""), r.get("entity_id", "")): r.get("parent_entity_id", "")
        for r in entities
    }
    facts_by_key: dict[tuple[str, str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in facts:
        key = (
            row.get("report_id", ""),
            row.get("study_id", ""),
            row.get("entity_type", ""),
            row.get("entity_id", ""),
            row.get("field_code", ""),
        )
        facts_by_key[key].append(row)
    duplicate_fact_errors: list[dict[str, str]] = []
    effective: list[dict[str, str]] = []
    for key, rows in facts_by_key.items():
        if len(rows) == 1:
            effective.append(rows[0])
            continue
        current = [row for row in rows if truthy(row.get("is_current_01") or "")]
        if len(current) != 1:
            duplicate_fact_errors.append({
                "code": "DUPLICATE_FACT_NO_UNIQUE_CURRENT",
                "fact_key": "/".join(key),
                "rows": str(len(rows)),
                "current_rows": str(len(current)),
                "message": "row order is not a precedence rule",
            })
            continue
        effective.append(current[0])

    fields = defaultdict(dict)
    for row in effective:
        key = (row.get("report_id", ""), row.get("study_id", ""), row.get("entity_type", ""), row.get("entity_id", ""))
        fields[key][row.get("field_code", "")] = row

    errors: list[dict[str, str]] = [*schema_errors, *duplicate_fact_errors]
    if structural_rule_path.resolve() != canonical_rule_path.resolve():
        errors.append({
            "code": "STRUCTURAL_RULE_TABLE_NOT_CANONICAL",
            "expected": str(canonical_rule_path),
            "observed": str(structural_rule_path),
        })
    for source_id, count in source_id_counts.items():
        if not source_id:
            errors.append({"code": "SOURCE_FILE_ID_MISSING"})
        elif count > 1:
            errors.append({
                "code": "SOURCE_FILE_ID_DUPLICATE",
                "source_file_id": source_id,
                "count": str(count),
            })
    # A manifest is not self-proving. Audit the declared source-package root
    # against the real directory tree so an omitted supplement/attachment is
    # visible, and recompute every registered file hash.
    for report_id, rows in source_rows_by_report.items():
        roots = {
            (row.get("source_package_root") or "").strip()
            for row in rows
            if (row.get("source_package_root") or "").strip()
        }
        if len(roots) != 1:
            errors.append({
                "code": "SOURCE_PACKAGE_ROOT_INVALID",
                "report_id": report_id,
                "message": "exactly one source_package_root is required",
            })
            continue
        if not all(truthy(row.get("inventory_complete_01") or "") for row in rows):
            errors.append({
                "code": "SOURCE_INVENTORY_NOT_DECLARED_COMPLETE",
                "report_id": report_id,
            })
        if not all(re.search(r"V6(?:\.0|0)", row.get("inventory_review_round") or "", flags=re.I) for row in rows):
            errors.append({
                "code": "SOURCE_INVENTORY_REVIEW_ROUND_INVALID",
                "report_id": report_id,
            })
        if not all((row.get("inventory_reviewer") or "").strip() for row in rows):
            errors.append({
                "code": "SOURCE_INVENTORY_REVIEWER_MISSING",
                "report_id": report_id,
            })
        root = Path(next(iter(roots)))
        if not root.is_dir():
            errors.append({
                "code": "SOURCE_PACKAGE_ROOT_NOT_FOUND",
                "report_id": report_id,
                "source_package_root": str(root),
            })
            continue
        registered_paths: set[Path] = set()
        seen_hashes: set[str] = set()
        for source in rows:
            source_id = (source.get("source_file_id") or "").strip()
            source_path_raw = (
                source.get("source_path")
                or source.get("resolved_path")
                or source.get("file_path")
                or ""
            ).strip()
            if not source_path_raw:
                errors.append({
                    "code": "SOURCE_MANIFEST_PATH_MISSING",
                    "report_id": report_id,
                    "source_file_id": source_id,
                })
                continue
            source_path = Path(source_path_raw).resolve()
            try:
                source_path.relative_to(root.resolve())
            except ValueError:
                errors.append({
                    "code": "SOURCE_MANIFEST_PATH_OUTSIDE_PACKAGE",
                    "report_id": report_id,
                    "source_file_id": source_id,
                })
                continue
            registered_paths.add(source_path)
            if sum(1 for row in rows if Path(
                row.get("source_path") or row.get("resolved_path") or row.get("file_path") or "."
            ).resolve() == source_path) > 1:
                errors.append({
                    "code": "SOURCE_MANIFEST_PATH_DUPLICATE",
                    "report_id": report_id,
                    "source_path": str(source_path),
                })
            if not source_path.is_file():
                errors.append({
                    "code": "SOURCE_MANIFEST_FILE_NOT_FOUND",
                    "report_id": report_id,
                    "source_file_id": source_id,
                })
                continue
            declared_hash = (source.get("source_sha256") or "").strip().lower()
            if declared_hash in seen_hashes:
                errors.append({
                    "code": "SOURCE_MANIFEST_HASH_DUPLICATE",
                    "report_id": report_id,
                    "source_sha256": declared_hash,
                })
            seen_hashes.add(declared_hash)
            if sha256_file(source_path).lower() != declared_hash:
                errors.append({
                    "code": "SOURCE_MANIFEST_REAL_HASH_MISMATCH",
                    "report_id": report_id,
                    "source_file_id": source_id,
                })
            accessible = (source.get("access_status") or "").strip().upper() in {
                "ACCESSIBLE", "AVAILABLE", "FULLTEXT_AVAILABLE",
            }
            included = truthy(source.get("included_in_complete_search_01") or "")
            role = (source.get("source_role") or "").strip().upper()
            if role not in ALLOWED_SOURCE_ROLES:
                errors.append({
                    "code": "SOURCE_ROLE_INVALID",
                    "report_id": report_id,
                    "source_file_id": source_id,
                    "source_role": role,
                })
            filename = source_path.name.lower()
            if re.search(r"supp|supplement|mmc|appendix|附录|补充", filename) and role not in {
                "SUPPLEMENT", "SUPPLEMENTARY_MATERIAL", "APPENDIX", "METHODS_APPENDIX",
            }:
                errors.append({
                    "code": "SOURCE_ROLE_FILENAME_MISMATCH",
                    "report_id": report_id,
                    "source_file_id": source_id,
                    "source_role": role,
                    "filename": source_path.name,
                })
            if accessible and not included:
                errors.append({
                    "code": "ACCESSIBLE_SOURCE_EXCLUDED",
                    "report_id": report_id,
                    "source_file_id": source_id,
                    "source_role": role,
                })
        actual_paths = {path.resolve() for path in root.rglob("*") if path.is_file()}
        for unregistered in sorted(actual_paths - registered_paths):
            errors.append({
                "code": "SOURCE_PACKAGE_FILE_UNREGISTERED",
                "report_id": report_id,
                "source_path": str(unregistered),
                "message": "register the file and explicitly include or exclude it from complete search",
            })
    observed_legacy = []
    nr_source_rows = []
    for row in effective:
        raw = (row.get("raw_value") or "").strip().upper()
        normalized = (row.get("normalized_value") or "").strip().upper()
        status = row.get("value_status", "")
        if status not in ALLOWED_STATUSES:
            errors.append({
                "code": "INVALID_VALUE_STATUS",
                "fact": f"{row.get('study_id','')}/{row.get('entity_id','')}/{row.get('field_code','')}",
                "value_status": status,
            })
        elif args.mode == "release" and status in RELEASE_BLOCKING_STATUSES:
            errors.append({
                "code": "RELEASE_BLOCKING_VALUE_STATUS",
                "fact": f"{row.get('study_id','')}/{row.get('entity_id','')}/{row.get('field_code','')}",
                "value_status": status,
            })
        # NA is a valid appraisal answer; all other entity types are checked.
        if row.get("entity_type") not in {"APPRAISAL_ITEM"} and status == "OBSERVED":
            if raw in LEGACY_TOKENS or normalized in LEGACY_TOKENS:
                observed_legacy.append(row)
        if row.get("entity_type") != "APPRAISAL_ITEM" and status == "NR_SOURCE":
            nr_source_rows.append(row)

    if observed_legacy:
        errors.append({
            "code": "OBSERVED_LEGACY_TOKEN",
            "count": str(len(observed_legacy)),
            "examples": "; ".join(
                f"{r.get('study_id')}/{r.get('entity_id')}/{r.get('field_code')}"
                for r in observed_legacy[:10]
            ),
        })

    # NR_SOURCE is a conclusion of a renewed field-level review, never a
    # migration default. The compact overlay does not duplicate the source
    # manifest, so the linked evidence row must carry a machine-readable
    # complete-source search scope and the v6.0 review round.
    evidence_by_id = {
        (row.get("evidence_id") or "").strip(): row
        for row in evidence
        if (row.get("evidence_id") or "").strip()
    }
    for row in nr_source_rows:
        study = row.get("study_id", "")
        eid = row.get("entity_id", "")
        field = row.get("field_code", "")
        fid = f"{study}/{eid}/{field}"
        if (row.get("raw_value") or "").strip() or (row.get("normalized_value") or "").strip():
            errors.append({
                "code": "NR_SOURCE_HAS_VALUE",
                "fact": fid,
                "message": "NR_SOURCE must have an empty typed value",
            })
        rationale = (row.get("derivation_rule") or "").strip()
        if row.get("_canonical_v56") == "1" and not (row.get("status_rationale") or "").strip():
            errors.append({
                "code": "NR_SOURCE_CANONICAL_STATUS_RATIONALE_MISSING",
                "fact": fid,
                "message": "canonical v5.6 facts must populate status_rationale itself",
            })
        if not rationale:
            errors.append({
                "code": "NR_SOURCE_RATIONALE_MISSING",
                "fact": fid,
            })
        elif not re.search(r"renew|re-?review|targeted", rationale, flags=re.I):
            errors.append({
                "code": "NR_SOURCE_RATIONALE_NOT_RENEWED",
                "fact": fid,
            })
        if not (row.get("reviewer") or "").strip():
            errors.append({
                "code": "NR_SOURCE_REVIEWER_MISSING",
                "fact": fid,
            })
        if not re.search(r"V6(?:\.0|0)", row.get("review_round") or "", flags=re.I):
            errors.append({
                "code": "NR_SOURCE_FACT_REVIEW_ROUND_INVALID",
                "fact": fid,
            })
        linked = [
            x.strip()
            for x in (row.get("evidence_id") or "").split("|")
            if x.strip()
        ]
        if not linked:
            errors.append({
                "code": "NR_SOURCE_EVIDENCE_MISSING",
                "fact": fid,
                "message": "renewed source evidence_id is required",
            })
            continue
        if not args.evidence:
            errors.append({
                "code": "NR_SOURCE_EVIDENCE_TABLE_REQUIRED",
                "fact": fid,
                "message": "--evidence is required to release NR_SOURCE",
            })
            continue
        if not args.source_manifest:
            errors.append({
                "code": "NR_SOURCE_MANIFEST_REQUIRED",
                "fact": fid,
                "message": "--source-manifest is required to prove main text/supplement/attachment coverage",
            })
            continue
        report_id = (row.get("report_id") or "").strip()
        required_sources = complete_sources_by_report.get(report_id, set())
        required_roles = source_roles_by_report.get(report_id, set())
        if not required_sources:
            errors.append({
                "code": "NR_SOURCE_MANIFEST_EMPTY",
                "fact": fid,
                "message": "no accessible source is marked for complete search",
            })
        if not any(role in {"MAIN", "MAIN_ARTICLE", "PRIMARY_REPORT", "FULL_TEXT"} for role in required_roles):
            errors.append({
                "code": "NR_SOURCE_MAIN_TEXT_NOT_IN_MANIFEST",
                "fact": fid,
            })
        valid_scope = False
        linked_evidence_sources: set[str] = set()
        for evidence_id in linked:
            ev = evidence_by_id.get(evidence_id)
            if not ev:
                errors.append({
                    "code": "NR_SOURCE_EVIDENCE_UNKNOWN",
                    "fact": fid,
                    "evidence_id": evidence_id,
                })
                continue
            if (ev.get("report_id") or "").strip() != report_id:
                errors.append({
                    "code": "NR_SOURCE_EVIDENCE_REPORT_MISMATCH",
                    "fact": fid,
                    "evidence_id": evidence_id,
                })
            required_evidence = {
                "report_id": ev.get("report_id"),
                "source_file_id": ev.get("source_file_id"),
                "source_sha256": ev.get("source_sha256"),
                "locator": ev.get("locator") or ev.get("page_or_location"),
                "table_figure_section": ev.get("table_figure_section"),
                "evidence_span": ev.get("evidence_span"),
                "extraction_method": ev.get("extraction_method"),
                "search_scope": ev.get("search_scope"),
                "reviewer": ev.get("reviewer") or ev.get("reviewer_id"),
            }
            for key, required_value in required_evidence.items():
                if not (required_value or "").strip():
                    errors.append({
                        "code": "NR_SOURCE_EVIDENCE_FIELD_MISSING",
                        "fact": fid,
                        "evidence_id": evidence_id,
                        "field": key,
                    })
            if not re.fullmatch(r"[0-9a-fA-F]{64}", (ev.get("source_sha256") or "").strip()):
                errors.append({
                    "code": "NR_SOURCE_HASH_INVALID",
                    "fact": fid,
                    "evidence_id": evidence_id,
                })
            source_row = sources_by_id.get((ev.get("source_file_id") or "").strip())
            if not source_row:
                errors.append({
                    "code": "NR_SOURCE_EVIDENCE_SOURCE_UNKNOWN",
                    "fact": fid,
                    "evidence_id": evidence_id,
                })
            else:
                source_id = (ev.get("source_file_id") or "").strip()
                linked_evidence_sources.add(source_id)
                if (source_row.get("report_id") or "").strip() != report_id:
                    errors.append({
                        "code": "NR_SOURCE_SOURCE_REPORT_MISMATCH",
                        "fact": fid,
                        "evidence_id": evidence_id,
                    })
                manifest_hash = (source_row.get("source_sha256") or "").strip().lower()
                evidence_hash = (ev.get("source_sha256") or "").strip().lower()
                if manifest_hash != evidence_hash:
                    errors.append({
                        "code": "NR_SOURCE_EVIDENCE_HASH_MISMATCH",
                        "fact": fid,
                        "evidence_id": evidence_id,
                    })
                source_path_raw = (
                    source_row.get("source_path")
                    or source_row.get("resolved_path")
                    or source_row.get("file_path")
                    or ""
                ).strip()
                if not source_path_raw:
                    errors.append({
                        "code": "NR_SOURCE_SOURCE_PATH_MISSING",
                        "fact": fid,
                        "source_file_id": source_id,
                    })
                else:
                    source_path = Path(source_path_raw)
                    if not source_path.is_file():
                        errors.append({
                            "code": "NR_SOURCE_SOURCE_FILE_NOT_FOUND",
                            "fact": fid,
                            "source_file_id": source_id,
                            "source_path": source_path_raw,
                        })
                    elif sha256_file(source_path).lower() != manifest_hash:
                        errors.append({
                            "code": "NR_SOURCE_SOURCE_FILE_HASH_MISMATCH",
                            "fact": fid,
                            "source_file_id": source_id,
                        })
            try:
                scope = json.loads(ev.get("search_scope") or "")
                if scope.get("complete_source_package_01") is not True:
                    raise ValueError("complete_source_package_01 must be true")
                if scope.get("study_id") != study:
                    raise ValueError("study_id does not match fact")
                if scope.get("entity_type") != row.get("entity_type", ""):
                    raise ValueError("entity_type does not match fact")
                if scope.get("entity_id") != eid:
                    raise ValueError("entity_id does not match fact")
                if scope.get("field_code", scope.get("field_name")) != field:
                    raise ValueError("field_code does not match fact")
                searched = scope.get("searched_source_files", scope.get("source_file_ids"))
                if not isinstance(searched, list) or not searched or not all(str(x).strip() for x in searched):
                    raise ValueError("searched_source_files is empty")
                searched_set = {str(x).strip() for x in searched}
                if not required_sources.issubset(searched_set):
                    missing_sources = sorted(required_sources - searched_set)
                    raise ValueError(
                        "search omits accessible main/supplement/attachment files: "
                        + ",".join(missing_sources)
                    )
                locations = scope.get("locations_searched")
                if not isinstance(locations, list) or not locations or not all(str(x).strip() for x in locations):
                    raise ValueError("locations_searched is empty")
                review_round = str(scope.get("review_round") or ev.get("review_round") or "")
                if not re.search(r"V6(?:\.0|0)", review_round, flags=re.I):
                    raise ValueError("review_round is not a v6.0 renewed review")
                rationale = str(scope.get("rationale") or scope.get("source_review_rationale") or "")
                if not re.search(r"renew|re-?review|targeted", rationale, flags=re.I):
                    raise ValueError("rationale does not document renewed targeted review")
                method = (ev.get("extraction_method") or "").lower()
                if "target" not in method or "review" not in method:
                    raise ValueError("extraction_method is not targeted source review")
                valid_scope = True
            except (json.JSONDecodeError, AttributeError, TypeError, ValueError) as exc:
                errors.append({
                    "code": "NR_SOURCE_SCOPE_INVALID",
                    "fact": fid,
                    "evidence_id": evidence_id,
                    "message": str(exc),
                })
        derivation = (row.get("derivation_rule") or "").lower()
        if re.search(r"legacy|migration|old cell|historical", derivation):
            errors.append({
                "code": "NR_SOURCE_LEGACY_INHERITED",
                "fact": fid,
                "message": "legacy evidence or migration text cannot justify NR_SOURCE",
            })
        if not valid_scope and linked:
            errors.append({
                "code": "NR_SOURCE_RENEWED_REVIEW_NOT_PROVEN",
                "fact": fid,
            })
        missing_per_file_evidence = required_sources - linked_evidence_sources
        if missing_per_file_evidence:
            errors.append({
                "code": "NR_SOURCE_PER_FILE_EVIDENCE_MISSING",
                "fact": fid,
                "source_file_ids": ",".join(sorted(missing_per_file_evidence)),
                "message": "each accessible main/supplement/attachment requires its own linked evidence and locator",
            })

    for row in effective:
        if row.get("entity_type") == "APPRAISAL_ITEM":
            continue
        if row.get("value_status") != "NA_STRUCTURAL":
            continue
        fact_label = f"{row.get('study_id','')}/{row.get('entity_id','')}/{row.get('field_code','')}"
        rule_id = (row.get("status_rule_id") or "").strip()
        if not rule_id:
            errors.append({
                "code": "NA_STRUCTURAL_RULE_MISSING",
                "fact": fact_label,
                "message": "NA_STRUCTURAL requires a deterministic status_rule_id",
            })
            continue
        rule = structural_rule_by_id.get(rule_id)
        if not rule:
            errors.append({
                "code": "NA_STRUCTURAL_RULE_UNKNOWN",
                "fact": fact_label,
                "status_rule_id": rule_id,
            })
            continue
        rule_field = (rule.get("field_code") or rule.get("field_name") or "").strip()
        if (rule.get("entity_type") or "").strip() != row.get("entity_type", "") or rule_field != row.get("field_code", ""):
            errors.append({
                "code": "NA_STRUCTURAL_RULE_SCOPE_MISMATCH",
                "fact": fact_label,
                "status_rule_id": rule_id,
            })
            continue
        if not truthy(rule.get("active_01") or ""):
            errors.append({
                "code": "NA_STRUCTURAL_RULE_INACTIVE",
                "fact": fact_label,
                "status_rule_id": rule_id,
            })
            continue
        for required_rule_field in ("rule_version", "rationale", "approver", "approval_round"):
            if not (rule.get(required_rule_field) or "").strip():
                errors.append({
                    "code": "NA_STRUCTURAL_RULE_METADATA_MISSING",
                    "fact": fact_label,
                    "status_rule_id": rule_id,
                    "field": required_rule_field,
                })
        if not truthy(rule.get("approved_01") or ""):
            errors.append({
                "code": "NA_STRUCTURAL_RULE_NOT_APPROVED",
                "fact": fact_label,
                "status_rule_id": rule_id,
            })
        try:
            context = json.loads(row.get("context_json") or "")
            if not isinstance(context, dict):
                raise ValueError("context_json must be an object")
            if not evaluate_structural_rule(rule, context):
                raise ValueError("structural rule condition is not satisfied")
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            errors.append({
                "code": "NA_STRUCTURAL_RULE_CONDITION_FAILED",
                "fact": fact_label,
                "status_rule_id": rule_id,
                "message": str(exc),
            })

    # Every observed performance/threshold/calibration entity must resolve to
    # a context whose model, dataset, outcome, and analysis population are linked.
    companion_types = {"PERFORMANCE", "THRESHOLD", "CALIBRATION_UTILITY"}
    entity_types = {
        (r.get("report_id", ""), r.get("study_id", ""), r.get("entity_id", "")): r.get("entity_type", "")
        for r in entities
    }
    complete_contexts_by_model: dict[tuple[str, str, str], list[str]] = defaultdict(list)
    required = ("model_id", "dataset_id", "outcome_id", "analysis_population_id")
    for (report, study, et, eid), context_fields in fields.items():
        if et != "EVALUATION_CONTEXT":
            continue
        if all(value(context_fields.get(f, {})) for f in required):
            complete_contexts_by_model[(report, study, value(context_fields["model_id"]))].append(eid)

    checked_companions = 0
    warnings: list[dict[str, str]] = []
    companion_entities = {
        (r.get("report_id", ""), r.get("study_id", ""), r.get("entity_type", ""), r.get("entity_id", ""))
        for r in effective
        if r.get("entity_type") in companion_types
        and r.get("value_status") == "OBSERVED"
        and value(r)
    }
    for report, study, et, eid in sorted(companion_entities):
        if et not in companion_types:
            continue
        checked_companions += 1
        parent_id = parent.get((report, study, et, eid), "")
        parent_type = entity_types.get((report, study, parent_id), "")
        if parent_type == "EVALUATION_CONTEXT":
            ctx = fields.get((report, study, "EVALUATION_CONTEXT", parent_id), {})
            missing = [f for f in required if not value(ctx.get(f, {}))]
            if missing:
                errors.append({
                    "code": "COMPANION_CONTEXT_GAP",
                    "study_id": study,
                    "entity_id": eid,
                    "missing": ",".join(missing),
                })
            continue
        if parent_type == "MODEL":
            candidates = complete_contexts_by_model.get((report, study, parent_id), [])
            if candidates:
                warnings.append({
                    "code": "MODEL_PARENT_CONTEXT_MAPPING_REQUIRED",
                    "study_id": study,
                    "entity_id": eid,
                    "model_id": parent_id,
                    "candidate_contexts": ",".join(candidates),
                })
                continue
            errors.append({
                "code": "COMPANION_CONTEXT_GAP",
                "study_id": study,
                "entity_id": eid,
                "missing": "complete evaluation context for parent model",
            })
            continue
        errors.append({
            "code": "COMPANION_CONTEXT_GAP",
            "study_id": study,
            "entity_id": eid,
            "missing": "context or model parent",
        })

    # Every predictor must resolve to a model entity within the same study.
    checked_predictors = 0
    for row in effective:
        if row.get("entity_type") != "PREDICTOR" or row.get("field_code") != "predictor_raw":
            continue
        checked_predictors += 1
        study = row.get("study_id", "")
        report = row.get("report_id", "")
        model_id = parent.get((report, study, "PREDICTOR", row.get("entity_id", "")), "")
        if not model_id or (report, study, "MODEL", model_id) not in entity_keys:
            errors.append({
                "code": "PREDICTOR_MODEL_GAP",
                "study_id": study,
                "entity_id": row.get("entity_id", ""),
                "model_id": model_id,
            })

    # Future-event branches must not be represented as eligible diagnostic branches.
    future_hits = []
    for row in effective:
        if row.get("entity_type") == "OUTCOME" and any(
            token in (value(row) or "").lower()
            for token in ("future", "subsequent", "later infection", "mortality", "death", "recurrence")
        ):
            future_hits.append(row)

    payload = {
        "protocol": "mdrgnb-meta-v6.0",
        "pass": not errors,
        "facts": len(facts),
        "effective_field_facts": len(effective),
        "entities": len(entities),
        "checked_observed_companion_facts": checked_companions,
        "checked_predictor_facts": checked_predictors,
        "legacy_token_errors": len(observed_legacy),
        "nr_source_rows": len(nr_source_rows),
        "evidence_rows": len(evidence),
        "source_manifest_rows": len(source_manifest),
        "errors": errors,
        "warnings": warnings,
        "future_event_outcome_rows_audited": len(future_hits),
        "non_observed_statuses": sorted(NON_OBSERVED),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
