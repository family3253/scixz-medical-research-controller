#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from protocol_v54 import norm, read_tsv

# Compatibility super-header migration only. Use recover_schema_drift_v57.py for active
# field-level migration, adjudication overlay, and companion-table materialization.

ELIGIBILITY_LEGACY_23 = [
    "assessment_id","report_id","study_id","outcome_id","model_id","cohort_entry_time_raw",
    "model_application_t0_raw","target_state_onset_raw","reference_specimen_time_raw","reference_result_time_raw",
    "target_present_at_t0_01","organism_unknown_at_t0_01","organism_restricted_cohort_01","future_event_target_01",
    "diagnostic_vs_prognostic_final","eligibility_status","major_flag_code","evidence_id","reviewer_a_decision",
    "reviewer_b_decision","adjudicator_decision","adjudication_status","notes",
]
ELIGIBILITY_B03_EXTRA = [
    "current_hidden_state_01","diagnostic_current_state_eligible_01","synthesis_eligible_01",
    "exclusion_reason_code","reviewer_id","review_round","last_updated",
]
ELIGIBILITY_V54 = [
    "eligibility_scope_id","cohort_id","model_branch_id","parent_model_id","branch_label_raw",
    "model_specification_status","t0_code","current_organism_input_at_t0_01",
    "current_organism_input_level_code","organism_restriction_level_code","organism_restriction_basis_code",
    "prior_colonization_or_infection_history_only_01","diagnostic_prognostic_code","branch_eligibility_status",
    "eligibility_reason_code","inventory_status","source_evidence_id","protocol_version","protocol_hash",
    "branch_status","migration_source_schema","migration_status",
]
ELIGIBILITY_HEADER = ELIGIBILITY_LEGACY_23[:10] + ELIGIBILITY_B03_EXTRA[:1] + ELIGIBILITY_LEGACY_23[10:15] + \
    ELIGIBILITY_B03_EXTRA[1:4] + ELIGIBILITY_LEGACY_23[14:17] + ELIGIBILITY_B03_EXTRA[3:4] + \
    ELIGIBILITY_LEGACY_23[17:21] + ELIGIBILITY_B03_EXTRA[4:] + ELIGIBILITY_LEGACY_23[21:] + \
    [x for x in ELIGIBILITY_V54 if x not in ELIGIBILITY_LEGACY_23 and x not in ELIGIBILITY_B03_EXTRA]
ELIGIBILITY_HEADER = list(dict.fromkeys(ELIGIBILITY_HEADER))

UNIT_PILOT_32 = [
    "unit_id","report_id","study_id","cohort_id","independent_cohort_id","outcome_id","model_id","model_family_id",
    "dataset_id","dataset_role_code","external_validation_axis_code","investigator_relation_code","performance_context_code",
    "performance_ids","analysis_population_id","dependent_effect_cluster_id","clinical_task_bucket","outcome_bucket",
    "phenotype_bucket","setting_bucket","synthesis_group_id","primary_synthesis_eligible_01","selection_rationale","unit_status",
    "source_anchor","reviewer_id","agent_mode","protocol_version","review_round","branch_status","last_updated","notes",
]
UNIT_B03_23 = [
    "inventory_id","report_id","study_id","outcome_id","model_id","dataset_id","dataset_role_code","performance_id",
    "threshold_ids","calibration_ids","analysis_population_id","physical_cohort_id","independent_cohort_id",
    "dependent_effect_cluster_id","inventory_status","eligibility_status","source_evidence_id","reviewer_id","agent_mode",
    "protocol_version","review_round","branch_status","notes",
]
UNIT_HEADER = UNIT_PILOT_32 + [x for x in UNIT_B03_23 if x not in UNIT_PILOT_32] + [
    "eligibility_scope_id","migration_source_schema","migration_status",
]


def write_tsv(path: Path, header: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as h:
        w=csv.DictWriter(h,fieldnames=header,delimiter="\t",lineterminator="\n",extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def migrate_eligibility(path: Path, cohort_lookup: dict[tuple[str,str,str,str], str]) -> tuple[list[dict[str,str]], dict]:
    headers, source = read_tsv(path); schema=f"ELIGIBILITY_V53_{len(headers)}COL"
    out=[]
    for src in source:
        row={k:(src.get(k,"") if src.get(k,"")!="" else "NOT_CAPTURED") for k in ELIGIBILITY_HEADER}
        row.update(src)
        aid=src.get("assessment_id",""); row["eligibility_scope_id"]=aid
        cohort_value=cohort_lookup.get((src.get("report_id",""),src.get("study_id",""),src.get("outcome_id",""),src.get("model_id","")),"UNCLEAR")
        row["cohort_id"]=cohort_value
        row["model_branch_id"]=src.get("model_id","") or "UNCLEAR"; row["parent_model_id"]="NA_STRUCTURAL"; row["branch_label_raw"]="NOT_CAPTURED"
        final=norm(src.get("diagnostic_vs_prognostic_final")); status=norm(src.get("eligibility_status")); flag=norm(src.get("major_flag_code"))
        pending="PENDING" in status or "UNRESOLVED" in final
        row["model_specification_status"]="FINAL_FEATURE_SET_UNREPORTED" if pending else "UNCLEAR"
        row["t0_code"]="UNCLEAR"; row["diagnostic_prognostic_code"]=("PROGNOSTIC_FUTURE_EVENT" if "PROGNOSTIC" in final or "FUTURE" in final else "DIAGNOSTIC_CURRENT_STATE")
        if "KNOWN_ORGANISM" in final or "KNOWN_ORGANISM" in flag:
            row["current_organism_input_at_t0_01"]="1"; row["current_organism_input_level_code"]="UNCLEAR"
        elif norm(src.get("organism_unknown_at_t0_01"))=="1":
            row["current_organism_input_at_t0_01"]="0"; row["current_organism_input_level_code"]="NONE"
        else:
            row["current_organism_input_at_t0_01"]="UNCLEAR"; row["current_organism_input_level_code"]="UNCLEAR"
        if norm(src.get("organism_restricted_cohort_01"))=="0":
            row["organism_restriction_level_code"]="NONE"; row["organism_restriction_basis_code"]="NONE"
        else:
            row["organism_restriction_level_code"]="UNCLEAR"; row["organism_restriction_basis_code"]="UNCLEAR"
        row["prior_colonization_or_infection_history_only_01"]="1" if "HISTORY" in flag else "UNCLEAR"
        if "PROGNOSTIC" in row["diagnostic_prognostic_code"]: branch="EXCLUDE_PROGNOSTIC_FUTURE_EVENT"
        elif row["current_organism_input_at_t0_01"]=="1": branch="EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"
        elif norm(src.get("organism_restricted_cohort_01"))=="1": branch="EXCLUDE_ORGANISM_RESTRICTED_COHORT"
        elif pending: branch="PENDING_FINAL_MODEL_SPECIFICATION"
        elif status.startswith("INCLUDE"): branch="INCLUDE_DIAGNOSTIC_CURRENT_STATE"
        elif status.startswith("EXCLUDE"): branch="EXCLUDE_NO_PREDICTION_MODEL"
        else: branch="PENDING_PROTOCOL_ADJUDICATION"
        row["branch_eligibility_status"]=branch
        row["eligibility_reason_code"]=src.get("exclusion_reason_code","") or (branch if branch!="INCLUDE_DIAGNOSTIC_CURRENT_STATE" else "NA_STRUCTURAL")
        row["inventory_status"]="INVENTORY_ACTIVE"; row["source_evidence_id"]=src.get("evidence_id","") or "UNCLEAR"
        row["protocol_version"]="mdrgnb-meta v5.4-migrated"; row["protocol_hash"]="PENDING_CANDIDATE_MANIFEST"
        row["branch_status"]=src.get("adjudication_status","") or src.get("branch_status","") or "UNCLEAR"
        row["migration_source_schema"]=schema
        row["migration_status"]=("MIGRATED_REQUIRES_SCOPE_EXPANSION" if cohort_value.startswith("MULTIPLE_COHORTS_REQUIRES_SCOPE_SPLIT") else "MIGRATED_NO_SOURCE_REPLAY")
        out.append(row)
    preserved=all(all(o.get(k)==s.get(k) for k in headers) for s,o in zip(source,out))
    return out,{"source":str(path),"source_columns":len(headers),"rows":len(source),"all_source_cells_preserved":preserved}


def migrate_units(path: Path) -> tuple[list[dict[str,str]], dict, dict[tuple[str,str,str,str],str]]:
    headers, source=read_tsv(path); schema=f"UNIT_V53_{len(headers)}COL"; out=[]; cohort_sets={}
    for src in source:
        row={k:(src.get(k,"") if src.get(k,"")!="" else "NOT_CAPTURED") for k in UNIT_HEADER}; row.update(src)
        uid=src.get("unit_id","") or src.get("inventory_id",""); row["unit_id"]=src.get("unit_id","") or uid; row["inventory_id"]=src.get("inventory_id","") or uid
        cohort=src.get("cohort_id","") or src.get("physical_cohort_id","") or "UNCLEAR"; row["cohort_id"]=src.get("cohort_id","") or cohort; row["physical_cohort_id"]=src.get("physical_cohort_id","") or cohort
        perf=src.get("performance_id",""); row["performance_ids"]=src.get("performance_ids","") or perf or "NOT_CAPTURED"
        row["performance_id"]=perf or (row["performance_ids"] if all(x not in row["performance_ids"] for x in (";","|")) else "UNCLEAR")
        row["inventory_status"]=src.get("inventory_status","") or src.get("unit_status","") or "UNCLEAR"; row["unit_status"]=src.get("unit_status","") or row["inventory_status"]
        row["source_evidence_id"]=src.get("source_evidence_id","") or src.get("source_anchor","") or "UNCLEAR"; row["source_anchor"]=src.get("source_anchor","") or row["source_evidence_id"]
        row["eligibility_scope_id"]="UNCLEAR"; row["migration_source_schema"]=schema; row["migration_status"]="MIGRATED_NO_SOURCE_REPLAY"
        out.append(row)
        key=(src.get("report_id",""),src.get("study_id",""),src.get("outcome_id",""),src.get("model_id",""))
        cohort_sets.setdefault(key,set()).add(cohort)
    lookup={key:(next(iter(values)) if len(values)==1 else "MULTIPLE_COHORTS_REQUIRES_SCOPE_SPLIT:"+"|".join(sorted(values))) for key,values in cohort_sets.items()}
    preserved=all(all(o.get(k)==s.get(k) for k in headers) for s,o in zip(source,out))
    return out,{"source":str(path),"source_columns":len(headers),"rows":len(source),"all_source_cells_preserved":preserved},lookup


def migrate_batch(src_dir: Path, out_dir: Path) -> dict:
    units,uq,lookup=migrate_units(src_dir/"unit_inventory.tsv"); elig,eq=migrate_eligibility(src_dir/"eligibility_t0.tsv",lookup)
    write_tsv(out_dir/"unit_inventory.tsv",UNIT_HEADER,units); write_tsv(out_dir/"eligibility_t0.tsv",ELIGIBILITY_HEADER,elig)
    return {"batch":src_dir.name,"unit":uq,"eligibility":eq,"output":str(out_dir)}


def main()->int:
    p=argparse.ArgumentParser(); p.add_argument("--input",type=Path,action="append",required=True); p.add_argument("--output-root",type=Path,required=True); p.add_argument("--out",type=Path)
    a=p.parse_args();
    if a.output_root.exists() and any(a.output_root.iterdir()): raise SystemExit("refusing to overwrite non-empty output-root")
    a.output_root.mkdir(parents=True,exist_ok=True); results=[]
    for src in a.input: results.append(migrate_batch(src,a.output_root/src.name))
    source_preservation_pass=all(x["unit"]["all_source_cells_preserved"] and x["eligibility"]["all_source_cells_preserved"] for x in results)
    payload={"protocol":"SCHEMA_MIGRATION_V53_TO_V54_COMPATIBILITY_VIEW","compatibility_only":True,
             "active_recovery_command":"recover_schema_drift_v57.py",
             "source_preservation_pass":source_preservation_pass,
             "migration_release_pass":False,"requires_v57_recovery":True,
             "batches":results,"eligibility_header":ELIGIBILITY_HEADER,"unit_header":UNIT_HEADER}
    rendered=json.dumps(payload,ensure_ascii=False,indent=2)+"\n"; (a.out.write_text(rendered,encoding="utf-8") if a.out else None); print(rendered,end=""); return 0 if source_preservation_pass else 1


if __name__=="__main__": raise SystemExit(main())
