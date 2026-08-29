#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from protocol_v54 import TRUE, norm, read_tsv, write_json
from qa_source_identity_v1 import read_index

AUDIT_REQUIRED = {"audit_membership_id", "report_id", "study_id", "audit_set_40_01", "pool_version", "protocol_version"}
SYNTH_REQUIRED = {"synthesis_membership_id", "pool_version", "parent_audit_membership_id", "report_id", "study_id",
                  "eligibility_scope_id", "outcome_id", "model_id", "dataset_id", "analysis_population_id", "performance_id",
                  "synthesis_group_id", "synthesis_eligible_01", "exclusion_or_pending_code", "primary_secondary_code",
                  "selection_rationale", "independent_cohort_id", "dependent_effect_cluster_id", "adjudication_status", "final_evidence_id"}


def validate(audit: Path, synthesis: Path, eligibility: Path, source_index: Path,
             sheet: str, expected_reports: int) -> dict:
    errors: list[str] = []; warnings: list[str] = []
    ah, ar = read_tsv(audit); sh, sr = read_tsv(synthesis); eh, er = read_tsv(eligibility); ih, ir = read_index(source_index, sheet)
    for label, missing in (("audit", AUDIT_REQUIRED-set(ah)), ("synthesis", SYNTH_REQUIRED-set(sh))):
        if missing: errors.append(f"{label} missing columns: {sorted(missing)}")
    report_study = {r.get("report_id", ""): r.get("study_id", "") for r in ir}
    audit_ids=set(); audit_reports=set(); membership_to_report={}
    for n,r in enumerate(ar,2):
        mid=r.get("audit_membership_id",""); report=r.get("report_id",""); study=r.get("study_id","")
        if not mid or mid in audit_ids: errors.append(f"audit row {n}: blank/duplicate membership")
        audit_ids.add(mid); audit_reports.add(report); membership_to_report[mid]=(report,study)
        if norm(r.get("audit_set_40_01")) not in TRUE: errors.append(f"audit row {n}: audit_set_40_01 not 1")
        if report_study.get(report) != study: errors.append(f"audit row {n}: source-index mapping mismatch")
    if len(audit_reports)!=expected_reports or len(ar)!=expected_reports:
        errors.append(f"audit pool must have exactly {expected_reports} unique rows/reports; rows={len(ar)} reports={len(audit_reports)}")
    elig = {r.get("eligibility_scope_id",""): r for r in er}
    seen=set()
    for n,r in enumerate(sr,2):
        mid=r.get("synthesis_membership_id","")
        if not mid or mid in seen: errors.append(f"synthesis row {n}: blank/duplicate membership")
        seen.add(mid)
        parent=r.get("parent_audit_membership_id","")
        if parent not in membership_to_report: errors.append(f"synthesis row {n}: orphan audit membership")
        elif membership_to_report[parent]!=(r.get("report_id",""),r.get("study_id","")): errors.append(f"synthesis row {n}: parent identity mismatch")
        scope=r.get("eligibility_scope_id",""); e=elig.get(scope)
        if not e: errors.append(f"synthesis row {n}: missing eligibility scope {scope}"); continue
        if norm(r.get("synthesis_eligible_01")) not in TRUE: errors.append(f"synthesis row {n}: active row not eligible=1")
        if norm(e.get("branch_eligibility_status"))!="INCLUDE_DIAGNOSTIC_CURRENT_STATE": errors.append(f"synthesis row {n}: branch not diagnostic eligible")
        if norm(e.get("model_specification_status"))!="FIXED": errors.append(f"synthesis row {n}: model not fixed")
        if norm(e.get("synthesis_eligible_01")) not in TRUE: errors.append(f"synthesis row {n}: eligibility scope synthesis flag not 1")
        if norm(e.get("adjudication_status")) not in {"FINAL_ADJUDICATED","FROZEN_FINAL_ADJUDICATED"}: errors.append(f"synthesis row {n}: scope not final")
        if norm(r.get("exclusion_or_pending_code")) not in {"NA","NONE"}: errors.append(f"synthesis row {n}: pending/exclusion code present")
        for field in ("performance_id","synthesis_group_id","selection_rationale","independent_cohort_id","dependent_effect_cluster_id","final_evidence_id"):
            if not r.get(field,"").strip(): errors.append(f"synthesis row {n}: blank {field}")
    return {"protocol":"POOL_CONSISTENCY_V1/v5.4","pass":not errors,"errors":errors,"warnings":warnings,
            "counts":{"audit_rows":len(ar),"audit_reports":len(audit_reports),"synthesis_memberships":len(sr),"eligibility_scopes":len(er)}}


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--audit",type=Path,required=True); p.add_argument("--synthesis",type=Path,required=True)
    p.add_argument("--eligibility",type=Path,required=True); p.add_argument("--source-index",type=Path,required=True); p.add_argument("--sheet",default="01_Source_Report_Index")
    p.add_argument("--expected-reports",type=int,default=40); p.add_argument("--out",type=Path)
    a=p.parse_args(); result=validate(a.audit,a.synthesis,a.eligibility,a.source_index,a.sheet,a.expected_reports); write_json(result,a.out); return 0 if result["pass"] else 1


if __name__=="__main__": raise SystemExit(main())
