#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from qa_eligibility_consistency_v1 import validate as validate_eligibility
from qa_pool_consistency_v1 import validate as validate_pool
from qa_semantic_key_v1 import validate as validate_semkey
from qa_algorithm_taxonomy_v58 import validate as validate_algorithm

ROOT=Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Case:
    name:str; current:bool=True; known_input:bool=False; restricted:bool=False; model:bool=True
    performance:bool=True; age16:bool=False; pediatric:bool=False; mixed:bool=False; leakage:bool=False
    formula:bool=True; training_no_perf:bool=False; external_only:bool=False; tuning:bool=False
    expected:str="INCLUDE"; flags:tuple[str,...]=()


def decide(c:Case):
    flags=[]
    if c.pediatric:return "EXCLUDE_PEDIATRIC_ONLY_OR_INSEPARABLE",()
    if c.age16:flags.append("ADULT_ACCEPTED_16PLUS")
    if not c.current:return "EXCLUDE_PROGNOSTIC_FUTURE_EVENT",tuple(flags)
    if c.known_input:return "EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0",tuple(flags)
    if c.restricted:return "EXCLUDE_ORGANISM_RESTRICTED_COHORT",tuple(flags)
    if not c.model or not c.performance:return "EXCLUDE_NO_PREDICTION_MODEL",tuple(flags)
    if c.mixed:flags.append("TARGET_MIXED_CURRENT_INFECTION_COLONIZATION")
    if c.leakage:flags.append("INFORMATION_LEAKAGE_FLAG")
    if not c.formula:flags.append("FORMULA_NOT_REPORTED")
    if c.external_only:flags.append("PROBAST_EVALUATION_ONLY")
    if c.tuning:flags.append("NOT_UNBIASED_EVALUATION")
    if c.training_no_perf:return "INVENTORY_ONLY",("NO_PERFORMANCE_EFFECT",)
    return "INCLUDE",tuple(flags)


CASES=[
 Case("broad_uti_esbl"),Case("admission_cre"),Case("active_sepsis"),Case("febrile_neutropenia"),
 Case("mixed",mixed=True,flags=("TARGET_MIXED_CURRENT_INFECTION_COLONIZATION",)),
 Case("known_gnb",known_input=True,expected="EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"),
 Case("known_enterobacterales",known_input=True,expected="EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"),
 Case("known_genus",known_input=True,expected="EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"),
 Case("known_species",known_input=True,expected="EXCLUDE_KNOWN_CURRENT_ORGANISM_INPUT_AT_T0"),
 Case("restricted_ent",restricted=True,expected="EXCLUDE_ORGANISM_RESTRICTED_COHORT"),Case("restricted_species",restricted=True,expected="EXCLUDE_ORGANISM_RESTRICTED_COHORT"),
 Case("future_acquisition",current=False,expected="EXCLUDE_PROGNOSTIC_FUTURE_EVENT"),Case("future_death",current=False,expected="EXCLUDE_PROGNOSTIC_FUTURE_EVENT"),
 Case("pediatric",pediatric=True,expected="EXCLUDE_PEDIATRIC_ONLY_OR_INSEPARABLE"),Case("association_only",model=False,expected="EXCLUDE_NO_PREDICTION_MODEL"),
 Case("no_performance",performance=False,expected="EXCLUDE_NO_PREDICTION_MODEL"),Case("factors_title"),
 Case("formula_absent",formula=False,flags=("FORMULA_NOT_REPORTED",)),Case("leakage",leakage=True,flags=("INFORMATION_LEAKAGE_FLAG",)),
 Case("adult16",age16=True,flags=("ADULT_ACCEPTED_16PLUS",)),Case("training_no_perf",training_no_perf=True,expected="INVENTORY_ONLY",flags=("NO_PERFORMANCE_EFFECT",)),
 Case("external_only",external_only=True,flags=("PROBAST_EVALUATION_ONLY",)),Case("tuning",tuning=True,flags=("NOT_UNBIASED_EVALUATION",)),Case("prior_history_not_current_known"),
]


def granularity_cases():
    return [
      {"case":"same_training_cohort_two_roles","pass":len({"DEV","APP"})==2},
      {"case":"one_auc_multiple_thresholds","pass":len({"AUC"})==1 and len({.2,.4,.6})==3},
      {"case":"multiple_algorithms_dependent","pass":len({"LR","RF","XGB"})==3},
      {"case":"different_analysis_population","pass":len({"CC","IMPUTED"})==2},
      {"case":"pooled_sites_dependent","pass":len({"DEP-WU"})==1},
      {"case":"duplicate_semantic_key_removed","pass":len(set(["K","K"]))==1},
    ]


def main()->int:
    case_results=[]
    for c in CASES:
        observed,flags=decide(c); case_results.append({"case":c.name,"pass":observed==c.expected and set(flags)==set(c.flags),"expected":c.expected,"observed":observed,"flags":list(flags)})
    grain=granularity_cases()
    required=[ROOT/"references/semantic-key-v1.md",ROOT/"references/pool-governance-v5.md",ROOT/"references/schema-migration-v54.md",ROOT/"references/schema-recovery-v57.md",ROOT/"references/analysis-set-and-taxonomy-v55.md",ROOT/"references/extraction-data-contract-v56.md",
              ROOT/"references/algorithm-taxonomy-v58.md",ROOT/"references/supplementary-material-schema-v59.md",
              ROOT/"references/supplementary-material-schema-v60.md",ROOT/"references/release-v60-completion-overlay.md",ROOT/"references/structural-rules-v60.tsv",
              ROOT/"scripts/qa_semantic_key_v1.py",ROOT/"scripts/qa_eligibility_consistency_v1.py",ROOT/"scripts/qa_pool_consistency_v1.py",ROOT/"scripts/qa_full40_coverage_v1.py",ROOT/"scripts/migrate_semkey_crosswalk_v54.py",ROOT/"scripts/qa_extraction_package_v56.py",ROOT/"scripts/qa_algorithm_taxonomy_v58.py",ROOT/"scripts/qa_completion_release_v60.py",ROOT/"scripts/build_review_queue_v56.py",ROOT/"scripts/recover_schema_drift_v57.py",ROOT/"scripts/qa_schema_recovery_v57.py",ROOT/"scripts/qa_real_recovery_smoke_v57.py",ROOT/"scripts/export_recovered_workbook_v57.py"]
    analysis_protocol=(ROOT/"references/analysis-set-and-taxonomy-v55.md").read_text(encoding="utf-8")
    extraction_contract=(ROOT/"references/extraction-data-contract-v56.md").read_text(encoding="utf-8")
    recovery_protocol=(ROOT/"references/schema-recovery-v57.md").read_text(encoding="utf-8")
    algorithm_protocol=(ROOT/"references/algorithm-taxonomy-v58.md").read_text(encoding="utf-8")
    supplementary_protocol=(ROOT/"references/supplementary-material-schema-v60.md").read_text(encoding="utf-8")
    overlay_protocol=(ROOT/"references/release-v60-completion-overlay.md").read_text(encoding="utf-8")
    completion_qa=(ROOT/"scripts/qa_completion_release_v60.py").read_text(encoding="utf-8")
    structural={"required_files":all(p.exists() for p in required),"skill_v60":"v6.0" in (ROOT/"SKILL.md").read_text(encoding="utf-8"),
                "known_input_dual_track":"current_organism_input_at_t0_01" in (ROOT/"references/eligibility-protocol-v5.md").read_text(encoding="utf-8"),
                "audit_dynamic_pools":"AUDIT_POOL_40" in (ROOT/"references/pool-governance-v5.md").read_text(encoding="utf-8"),
                "analysis_sets_v55":all(x in analysis_protocol for x in ("PRIMARY_DIAGNOSTIC_39","STRICT_ADULT_38","STU-005","STU-016")),
                "liu_reference_only":"external methodological comparator only" in analysis_protocol,
                "missingness_v56":all(x in extraction_contract for x in ("NR_SOURCE", "NA_STRUCTURAL", "NOT_CAPTURED", "PENDING_REVIEW")),
                "no_silent_fallback":"Never fall back silently" in extraction_contract,
                "field_overlay_v57":"narrow final" in recovery_protocol.lower() and "field-level" in recovery_protocol.lower(),
                "companion_gate_v57":all(x in recovery_protocol for x in ("performance_values.tsv", "threshold_values.tsv", "calibration_values.tsv", "dataset_values.tsv")),
                "scoring_companion_gate_v57":all(x in recovery_protocol for x in ("tripod_scoring_adjudication.tsv", "probast_record_type.tsv", "probast_scoring_adjudication.tsv")),
                "adjudication_scope_gate_v57":"--adjudication-scope" in recovery_protocol,
                "compound_entity_gate_v57":"report_id × study_id × entity_id" in recovery_protocol,
                "companion_coverage_v57":"companion_coverage.tsv" in recovery_protocol,
                "workbook_roundtrip_gate_v57":"export_recovered_workbook_v57.py" in recovery_protocol,
                "algorithm_taxonomy_v58":all(x in algorithm_protocol for x in ("traditional_vs_ml_code", "mother_model_id", "LASSO", "dependent_effect_cluster_id")),
                "supplementary_schema_v60":all(x in supplementary_protocol for x in ("03_模型", "03_预测因子", "04_性能", "Do not create one worksheet")),
                "completion_overlay_v60":all(x in overlay_protocol for x in ("latest v6.0 adjudicated completion overlay", "same-entity frozen canonical fact", "STU-005", "NR_SOURCE")),
                "renewed_source_review_v60":all(x in overlay_protocol for x in ("renewed v6.0 field-level review", "main article", "accessible relevant supplement/attachment", "status_rule_id")),
                "source_package_integrity_v60":all(x in completion_qa for x in ("sha256_file", "SOURCE_PACKAGE_FILE_UNREGISTERED", "NR_SOURCE_PER_FILE_EVIDENCE_MISSING", "NR_SOURCE_EVIDENCE_REPORT_MISMATCH")),
                "dual_fact_schema_v60":all(x in completion_qa for x in ("field_code", "field_name", "value_status", "value_status_code", "NR_SOURCE_CANONICAL_STATUS_RATIONALE_MISSING")),
                "structural_rule_execution_v60":all(x in completion_qa for x in ("evaluate_structural_rule", "NA_STRUCTURAL_RULE_CONDITION_FAILED", "context_json")),
                "source_uniqueness_and_inclusion_v60":all(x in completion_qa for x in ("SOURCE_FILE_ID_DUPLICATE", "SOURCE_MANIFEST_PATH_DUPLICATE", "ACCESSIBLE_SOURCE_EXCLUDED", "SOURCE_ROLE_FILENAME_MISMATCH")),
                "canonical_structural_rules_v60":all(x in completion_qa for x in ("structural-rules-v60.tsv", "STRUCTURAL_RULE_TABLE_NOT_CANONICAL", "NA_STRUCTURAL_RULE_NOT_APPROVED")),
                "release_status_gate_v60":all(x in completion_qa for x in ("ALLOWED_STATUSES", "RELEASE_BLOCKING_STATUSES", "INVALID_VALUE_STATUS", "RELEASE_BLOCKING_VALUE_STATUS")),
                "full_fact_identity_v60":all(x in completion_qa for x in ("report_id", "is_current_01", "DUPLICATE_FACT_NO_UNIQUE_CURRENT", "row order is not a precedence rule")),
                "export_lineage_hotfix":all(x in (ROOT/"SKILL.md").read_text(encoding="utf-8") for x in ("exact context key", "LASSO/ridge/elastic-net", "mother-model rule")),
                "dataset_analysis_population_gate":all(x in supplementary_protocol for x in ("dataset × analysis population", "analysis population")),
                "model_method_view_gate":all(x in supplementary_protocol for x in ("missing data", "continuous-variable handling", "class imbalance", "impact evaluation")),
                "threshold_calibration_context_gate":all(x in supplementary_protocol for x in ("05_阈值四格", "06_校准临床价值", "complete context links"))}
    fixtures=ROOT/"tests"/"fixtures"
    branch_v54=validate_eligibility(fixtures/"eligibility"/"branch_v54_cases.tsv","branch")
    semkey_split=validate_semkey(fixtures/"semkey"/"alignment_split_pass.tsv",fixtures/"semkey"/"crosswalk_split_pass.tsv",1)
    pool_v54=validate_pool(fixtures/"pools"/"audit_40_pass.tsv",fixtures/"pools"/"synthesis_pass.tsv",fixtures/"eligibility"/"branch_pass.tsv",fixtures/"pools"/"source_index_40_pass.tsv","unused",40)
    algorithm_v58=validate_algorithm(fixtures/"algorithm"/"algorithm_pass.tsv","freeze")
    env=dict(os.environ); env["PYTHONIOENCODING"]="utf-8"
    cp=subprocess.run([sys.executable,"-m","unittest","discover","-s",str(ROOT/"tests"),"-p","test_*.py"],capture_output=True,text=True,encoding="utf-8",env=env)
    tests={"pass":cp.returncode==0,"stdout":cp.stdout,"stderr":cp.stderr}
    ok=all(x["pass"] for x in case_results) and all(x["pass"] for x in grain) and all(structural.values()) and branch_v54["pass"] and semkey_split["pass"] and pool_v54["pass"] and algorithm_v58["pass"] and tests["pass"]
    payload={"protocol":"v6.0","pass":ok,"legacy_eligibility_cases":case_results,"granularity_cases":grain,"new_branch_cases":{"pass":branch_v54["pass"],"counts":branch_v54["counts"],"errors":branch_v54["errors"]},"semkey_explicit_split":{"pass":semkey_split["pass"],"errors":semkey_split["errors"]},"pool_fixture":{"pass":pool_v54["pass"],"errors":pool_v54["errors"]},"algorithm_fixture":{"pass":algorithm_v58["pass"],"errors":algorithm_v58["errors"]},"structural_assertions":structural,"unittests":tests}
    print(json.dumps(payload,ensure_ascii=False,indent=2)); return 0 if ok else 1


if __name__=="__main__": raise SystemExit(main())
