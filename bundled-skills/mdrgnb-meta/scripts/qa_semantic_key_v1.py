#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path

from protocol_v54 import MAPPING_DECISIONS, RELATION_BASIS_CODES, SEMKEY_COMMON, SEMKEY_SUFFIX, parse_semkey, read_tsv, write_json

LEDGER_REQUIRED = {
    "alignment_id", "report_id", "study_id", "entity_type", "entity_id", "semantic_key",
    "split_link_code", "source_evidence_id", "reviewer_id", "review_round", "adjudication_status",
}
CROSSWALK_REQUIRED = {
    "crosswalk_id", "report_id", "study_id", "entity_type", "a_entity_id", "a_semantic_key",
    "b_entity_id", "b_semantic_key", "third_entity_id", "third_semantic_key", "final_entity_id",
    "final_semantic_key", "mapping_decision", "mapping_rationale", "final_evidence_id",
    "adjudicator_id", "adjudication_timestamp", "qa_status",
}
CROSSWALK_RELATION_REQUIRED = {
    "relation_group_id", "a_source_cardinality", "b_source_cardinality",
    "third_source_cardinality", "final_cardinality",
    "relation_basis_code", "relation_evidence_id",
}


def validate(alignment: Path, crosswalk: Path | None, expected_reports: int | None,
             compat_v53: bool = False) -> dict:
    errors: list[str] = []
    warnings: list[str] = []
    headers, rows = read_tsv(alignment)
    missing = sorted(LEDGER_REQUIRED - set(headers))
    if missing:
        errors.append(f"alignment missing columns: {missing}")
    seen_ids, seen_entities, seen_keys = set(), set(), {}
    finals, reports = {}, set()
    counts: Counter[str] = Counter()
    for n, row in enumerate(rows, 2):
        aid, report, study = row.get("alignment_id", ""), row.get("report_id", ""), row.get("study_id", "")
        etype, eid, key = row.get("entity_type", ""), row.get("entity_id", ""), row.get("semantic_key", "")
        if aid in seen_ids: errors.append(f"row {n}: duplicate alignment_id {aid}")
        seen_ids.add(aid)
        identity = (report, study, etype, eid)
        if identity in seen_entities: errors.append(f"row {n}: duplicate active entity {identity}")
        seen_entities.add(identity); finals[identity] = key; reports.add(report); counts[etype] += 1
        if etype not in SEMKEY_SUFFIX:
            errors.append(f"row {n}: invalid entity_type {etype!r}"); continue
        names, values, parse_errors = parse_semkey(key, compat_v53)
        errors.extend(f"row {n}: {e}" for e in parse_errors)
        expected = list(SEMKEY_COMMON + SEMKEY_SUFFIX[etype])
        if names != expected: errors.append(f"row {n}: field order {names} != {expected}")
        for field, wanted in (("v", "SEMKEY_V1"), ("entity", etype), ("report", report), ("study", study)):
            if values.get(field) != wanted: errors.append(f"row {n}: key {field} mismatch")
        if "PENDING_ADJUDICATION" in values.values(): errors.append(f"row {n}: pending code in final key")
        if key in seen_keys: errors.append(f"row {n}: duplicate semantic_key also used by {seen_keys[key]}")
        seen_keys[key] = aid
        for field in ("report_id", "study_id", "entity_id", "split_link_code", "source_evidence_id", "adjudication_status"):
            if not row.get(field, "").strip(): errors.append(f"row {n}: blank {field}")
    if expected_reports is not None and len(reports) != expected_reports:
        errors.append(f"expected {expected_reports} reports, observed {len(reports)}")

    source_dest: defaultdict[tuple[str, str, str, str, str], int] = defaultdict(int)
    source_groups: defaultdict[tuple[str, str, str, str, str], set[str]] = defaultdict(set)
    relation_groups: defaultdict[str, list[dict[str, str]]] = defaultdict(list)
    mapped_finals: set[tuple[str, str, str, str]] = set()
    xrows = []
    if crosswalk:
        xheaders, xrows = read_tsv(crosswalk)
        missing = sorted(CROSSWALK_REQUIRED - set(xheaders))
        if missing: errors.append(f"crosswalk missing columns: {missing}")
        missing_relation = sorted(CROSSWALK_RELATION_REQUIRED - set(xheaders))
        has_relation_schema = not missing_relation
        if missing_relation:
            if compat_v53:
                warnings.append(f"legacy crosswalk lacks v5.4 relation columns: {missing_relation}")
            else:
                errors.append(f"crosswalk missing relation columns: {missing_relation}")
        seen_xids = set()
        for n, row in enumerate(xrows, 2):
            xid = row.get("crosswalk_id", "")
            if xid in seen_xids: errors.append(f"crosswalk row {n}: duplicate crosswalk_id {xid}")
            seen_xids.add(xid)
            report, study, etype, final_id = (row.get(k, "") for k in ("report_id", "study_id", "entity_type", "final_entity_id"))
            final_identity = (report, study, etype, final_id)
            decision = row.get("mapping_decision", "")
            if decision not in MAPPING_DECISIONS:
                if compat_v53: warnings.append(f"crosswalk row {n}: legacy mapping_decision {decision!r}")
                else: errors.append(f"crosswalk row {n}: invalid mapping_decision {decision!r}")
            if decision not in {"REMOVED_DUPLICATE", "REMOVED_INELIGIBLE_ENTITY"}:
                if final_identity not in finals: errors.append(f"crosswalk row {n}: orphan final {final_identity}")
                elif finals[final_identity] != row.get("final_semantic_key", ""):
                    errors.append(f"crosswalk row {n}: final_semantic_key mismatch")
                mapped_finals.add(final_identity)
            relation_group = row.get("relation_group_id", "").strip()
            if has_relation_schema:
                if not relation_group:
                    errors.append(f"crosswalk row {n}: blank relation_group_id")
                else:
                    relation_groups[relation_group].append(row)
            for branch in ("a", "b", "third"):
                sid = row.get(f"{branch}_entity_id", "").strip()
                skey = row.get(f"{branch}_semantic_key", "").strip()
                if sid not in {"", "NA"}:
                    if not skey or skey == "NA": errors.append(f"crosswalk row {n}: {branch} entity lacks key")
                    source_dest[(branch, report, study, etype, sid)] += 1
                    if relation_group:
                        source_groups[(branch, report, study, etype, sid)].add(relation_group)
            for field in ("mapping_rationale", "final_evidence_id", "adjudicator_id", "adjudication_timestamp", "qa_status"):
                if not row.get(field, "").strip(): errors.append(f"crosswalk row {n}: blank {field}")
        if has_relation_schema:
            for source, groups in source_groups.items():
                if len(groups) != 1:
                    errors.append(f"source entity occurs in multiple relation groups {sorted(groups)}: {source}")
            for gid, grows in relation_groups.items():
                decisions = {r.get("mapping_decision", "") for r in grows}
                reports_g = {(r.get("report_id", ""), r.get("study_id", ""), r.get("entity_type", "")) for r in grows}
                bases = {r.get("relation_basis_code", "") for r in grows}
                evidences = {r.get("relation_evidence_id", "") for r in grows}
                if len(decisions) != 1: errors.append(f"relation group {gid}: mixed mapping decisions {sorted(decisions)}")
                if len(reports_g) != 1: errors.append(f"relation group {gid}: mixed report/study/entity types")
                if len(bases) != 1 or next(iter(bases), "") not in RELATION_BASIS_CODES:
                    errors.append(f"relation group {gid}: invalid/inconsistent relation_basis_code {sorted(bases)}")
                if len(evidences) != 1 or next(iter(evidences), "") in {"", "NA"}:
                    errors.append(f"relation group {gid}: blank/inconsistent relation_evidence_id")
                try:
                    declared_by_branch = {
                        branch: {int(r.get(f"{branch}_source_cardinality", "")) for r in grows}
                        for branch in ("a", "b", "third")
                    }
                    declared_final = {int(r.get("final_cardinality", "")) for r in grows}
                except ValueError:
                    errors.append(f"relation group {gid}: noninteger cardinality")
                    continue
                if any(len(values) != 1 for values in declared_by_branch.values()) or len(declared_final) != 1:
                    errors.append(f"relation group {gid}: inconsistent cardinality declarations")
                    continue
                source_set = set()
                source_occurrences: Counter[tuple[str, str, str, str, str]] = Counter()
                final_set = set()
                final_occurrences: Counter[tuple[str, str, str, str]] = Counter()
                for r in grows:
                    report, study, etype = r.get("report_id", ""), r.get("study_id", ""), r.get("entity_type", "")
                    for branch in ("a", "b", "third"):
                        sid = r.get(f"{branch}_entity_id", "").strip()
                        if sid not in {"", "NA"}:
                            identity = (branch, report, study, etype, sid)
                            source_set.add(identity); source_occurrences[identity] += 1
                    fid = r.get("final_entity_id", "").strip()
                    if fid not in {"", "NA"} and r.get("mapping_decision", "") not in {"REMOVED_DUPLICATE", "REMOVED_INELIGIBLE_ENTITY"}:
                        identity = (report, study, etype, fid)
                        final_set.add(identity); final_occurrences[identity] += 1
                declared_counts = {branch: next(iter(values)) for branch, values in declared_by_branch.items()}
                actual_counts = {
                    branch: len({identity for identity in source_set if identity[0] == branch})
                    for branch in ("a", "b", "third")
                }
                fc = next(iter(declared_final))
                for branch in ("a", "b", "third"):
                    if actual_counts[branch] != declared_counts[branch]:
                        errors.append(f"relation group {gid}: {branch} source cardinality {actual_counts[branch]} != {declared_counts[branch]}")
                if len(final_set) != fc: errors.append(f"relation group {gid}: final cardinality {len(final_set)} != {fc}")
                decision = next(iter(decisions), "")
                active_counts = [n for n in actual_counts.values() if n > 0]
                if decision == "ONE_TO_ONE" and not (active_counts and all(n == 1 for n in active_counts) and fc == 1 and len(grows) == 1):
                    errors.append(f"relation group {gid}: ONE_TO_ONE requires one source per represented branch, 1 final, 1 row")
                elif decision == "SPLIT_TO_FINAL":
                    if not (active_counts and fc >= 2 and len(grows) == fc):
                        errors.append(f"relation group {gid}: SPLIT_TO_FINAL requires represented source branch(es), >=2 unique finals and one row per final")
                    if not any(n > 1 for n in source_occurrences.values()):
                        errors.append(f"relation group {gid}: SPLIT_TO_FINAL has no repeated coarse source entity")
                elif decision == "MERGED_TO_FINAL":
                    if not (any(n >= 2 for n in active_counts) and fc == 1):
                        errors.append(f"relation group {gid}: MERGED_TO_FINAL requires >=2 sources in at least one branch and 1 final")
                elif decision in {"REMOVED_DUPLICATE", "REMOVED_INELIGIBLE_ENTITY"} and not (active_counts and fc == 0):
                    errors.append(f"relation group {gid}: removal requires represented source(s) and 0 finals")
                elif decision == "ADDED_BY_ADJUDICATION" and not (not active_counts and fc == 1):
                    errors.append(f"relation group {gid}: addition requires 0 sources and 1 final")
                if decision != "MERGED_TO_FINAL" and any(n > 1 for n in final_occurrences.values()):
                    errors.append(f"relation group {gid}: duplicate final target outside a merge")
                if decision != "SPLIT_TO_FINAL" and any(n > 1 for n in source_occurrences.values()):
                    errors.append(f"relation group {gid}: repeated source outside an explicit split")
        else:
            # v5.3 compatibility keeps the strict legacy invariant. Repeated source
            # IDs remain blocking until migrated into an explicit audited relation group.
            for source, count in source_dest.items():
                if count != 1: errors.append(f"source entity maps {count} times: {source}")
        for final_identity in set(finals) - mapped_finals:
            errors.append(f"final entity lacks crosswalk: {final_identity}")
    return {"protocol": "SEMKEY_V1/v5.4", "pass": not errors, "compat_v53": compat_v53,
            "errors": errors, "warnings": warnings,
            "counts": {"alignment_rows": len(rows), "crosswalk_rows": len(xrows),
                       "reports": len(reports), "entities_by_type": dict(counts)}}


def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("alignment", type=Path); p.add_argument("--crosswalk", type=Path)
    p.add_argument("--expected-reports", type=int); p.add_argument("--compat-v53", action="store_true"); p.add_argument("--out", type=Path)
    a = p.parse_args(); result = validate(a.alignment, a.crosswalk, a.expected_reports, a.compat_v53)
    write_json(result, a.out); return 0 if result["pass"] else 1


if __name__ == "__main__": raise SystemExit(main())
