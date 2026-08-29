#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

MISSING = {"", "NR", "NA", "N/A", "NA_UNDEFINED", "UNKNOWN", "NOT REPORTED", "未报告", "不详"}
FINAL_ROLES = {"FINAL", "FINAL_ENTITY", "FINAL_VALUE"}
BRANCH_ROLES = {"A", "B", "THIRD", "FINAL"}
PROVENANCE_FIELDS = {
    "reviewer_id", "review_round", "adjudication_status", "last_updated", "branch_status",
    "protocol_version", "protocol_hash", "migration_source_schema", "migration_status",
    "source_package_id", "source_package_path", "source_file_name", "source_file_sha256",
    "source_row_number", "source_schema_generation", "extractor_id", "adjudicator_id",
    "extraction_timestamp", "confidence", "qa_status", "inventory_status",
}

CANONICAL_MAIN_FILES = {
    "study": ("study.tsv",), "outcome": ("outcome.tsv",), "model": ("model.tsv",),
    "dataset": ("dataset.tsv",), "performance": ("performance.tsv", "discrimination.tsv"),
    "threshold": ("threshold.tsv",), "calibration": ("calibration.tsv",),
    "predictor": ("predictor.tsv",), "tripod": ("tripod_ai_long.tsv", "TRIPOD.tsv"),
    "probast": ("probast_ai_long.tsv", "PROBAST_dev.tsv", "PROBAST_eval.tsv"),
    "source_evidence": ("source_evidence.tsv",),
}

COMPANION_FILES = {
    "dataset_values.tsv", "performance_values.tsv", "threshold_values.tsv",
    "threshold_2x2_values.tsv", "calibration_values.tsv", "predictor_values.tsv",
    "tripod_scoring_adjudication.tsv", "probast_record_type.tsv",
    "probast_scoring_adjudication.tsv",
}

COMPANION_FIELD_ALLOWLIST = {
    "tripod_scoring_adjudication.tsv": {
        "component_id", "item_code", "status", "adjudication_rationale",
    },
    "probast_record_type.tsv": {"record_type"},
    "probast_scoring_adjudication.tsv": {
        "assessment_type", "scope_id", "model_id", "outcome_id", "dataset_id",
        "item_code", "record_type", "response", "rationale",
    },
}

COMPANION_PROVENANCE_COLUMNS = {
    "tripod_scoring_adjudication.tsv": {
        "adjudication_id", "reviewer_a_response", "reviewer_a_evidence_id",
        "reviewer_b_response", "reviewer_b_evidence_id", "blind_third_response",
        "blind_third_evidence_id", "adjudicator_id",
    },
    "probast_record_type.tsv": {"response"},
    "probast_scoring_adjudication.tsv": {
        "adjudication_id", "reviewer_a_response", "reviewer_a_evidence_id",
        "reviewer_b_response", "reviewer_b_evidence_id", "blind_third_response",
        "blind_third_evidence_id", "adjudicator_id",
    },
}

BLOCKING_AUDIT_CODES = {
    "UNMAPPED_NONMISSING_SOURCE_FIELD", "UNMAPPED_BRANCH_ENTITY_ID",
    "AMBIGUOUS_BRANCH_ENTITY_MAPPING", "AMBIGUOUS_CANONICAL_ENTITY_ID",
    "ORPHAN_COMPANION_KEY", "DUPLICATE_COMPANION_KEY", "MISSING_COMPANION_TABLE",
    "CROSSWALK_SPLIT_REQUIRES_ADJUDICATION", "UNAPPROVED_FINAL_OVERRIDE",
    "AMBIGUOUS_ALIAS", "DUPLICATE_CANONICAL_ENTITY_KEY", "UNMATCHED_ROW_NO_ENTITY_ID",
    "FALSE_NR_COMPANION_VALUE_EXISTS",
    "UNSCOPED_FINAL_REQUIRES_ADJUDICATION",
}

UNMAPPED_SOURCE_AUDIT_CODES = {
    "UNMAPPED_NONMISSING_SOURCE_FIELD", "UNMAPPED_BRANCH_ENTITY_ID",
}


def spec(entity: str, ids: list[str], fields: dict[str, list[str]], files: list[str]) -> dict:
    return {"entity": entity, "ids": ids, "fields": fields, "files": files}


COMMON = {
    "report_id": ["report_id"],
    "study_id": ["study_id", "stu"],
    "semantic_key": ["semantic_key", "final_semantic_key"],
}

EVIDENCE_ALIASES = ["source_evidence_id", "final_evidence_id", "source_anchor", "evidence_id"]


SPECS = {
    "study": spec("study", ["entity_id", "study_id"], COMMON | {
        "first_author": ["first_author_raw", "first_author"],
        "publication_year": ["publication_year", "year"],
        "title": ["title_raw", "title"],
        "title_standard": ["title_standard_zh", "title_standard"],
        "journal": ["journal_raw", "journal"],
        "doi": ["doi"], "country": ["country_raw", "country"], "country_code": ["country_code"],
        "center_type": ["center_type_raw", "centers_raw"], "n_centers": ["n_centers", "centers_n"],
        "study_design": ["study_design_raw", "design_raw", "design"],
        "study_design_code": ["study_design_code", "design_code"],
        "recruitment": ["recruitment"], "recruitment_period_raw": ["recruitment_period_raw"],
        "recruitment_start": ["recruitment_start", "recruitment_period_start"],
        "recruitment_end": ["recruitment_end", "recruitment_period_end"],
        "patient_n_total": ["patient_n_total"], "episode_n_total": ["episode_n_total"],
        "population": ["population_raw", "population"],
        "prospective_status": ["prospective_status"],
        "source_integrity_status": ["source_integrity_status"],
        "clinical_setting": ["clinical_setting_raw", "setting_raw"],
        "clinical_setting_code": ["clinical_setting_code", "setting_code"],
        "department": ["department_raw"], "age_scope": ["age_scope_code", "age_scope"],
        "age_min_numeric": ["age_min_numeric"], "age_min_raw": ["age_min_raw"],
        "age_summary": ["age_summary_raw"],
        "data_source": ["data_source_raw"], "funding": ["funding_raw"],
        "funding_conflicts": ["funding_conflicts"], "setting": ["setting"],
        "index_condition_raw": ["index_condition_raw"],
        "conflict_of_interest": ["conflict_of_interest_raw"], "eligibility_status": ["eligibility_status"],
        "eligibility_reason_code": ["eligibility_reason_code"],
        "synthesis_eligibility_status": ["synthesis_eligibility_status"],
        "project": ["project", "project_signature_code"], "notes": ["notes"],
    }, ["study.tsv", "study_values.tsv"]),
    "outcome": spec("outcome", ["entity_id", "outcome_id"], COMMON | {
        "outcome_id": ["outcome_id", "entity_id"], "outcome": ["outcome_raw", "target", "target_raw"],
        "target_state_type": ["target_state_type_code", "target_type", "state_type"],
        "phenotype": ["phenotype_raw", "phenotype"], "species_scope": ["species_scope_raw", "species", "organism_scope"],
        "specimen": ["specimen_raw", "specimen"], "reference_standard": ["reference_standard_raw", "reference"],
        "t0": ["t0_raw", "t0", "index_time"], "case_control": ["case_control_definition_raw", "case_control"],
        "notes": ["notes"],
    }, ["outcome.tsv", "outcome_values.tsv"]),
    "model": spec("model", ["entity_id", "model_id"], COMMON | {
        "model_id": ["model_id", "entity_id"], "outcome_id": ["outcome_id", "outcome"],
        "model_name": ["model_name_raw", "model_name", "family"], "algorithm": ["algorithm_raw", "algorithm"],
        "predictor_set": ["predictor_set_raw", "predictors"], "version": ["version", "model_version"],
        "model_role": ["model_role_code", "model_role"], "formula": ["formula_raw", "formula"],
        "presentation": ["presentation_form_code", "presentation"], "feature_selection": ["feature_selection_raw"],
        "missing_data": ["missing_data_raw"], "class_imbalance": ["class_imbalance_raw"],
        "hyperparameter_tuning": ["hyperparameter_tuning_raw"], "notes": ["notes"],
    }, ["model.tsv", "model_values.tsv"]),
    "dataset": spec("dataset", ["entity_id", "dataset_id"], COMMON | {
        "dataset_id": ["dataset_id", "entity_id"],
        "cohort_id": ["cohort_id", "physical_cohort_id", "cohort"],
        "independent_cohort_id": ["independent_cohort_id"],
        "synthesis_cohort_id": ["synthesis_cohort_id"], "outcome_id": ["outcome_id"],
        "dataset_name_raw": ["dataset_name_raw", "dataset_label_raw"],
        "dataset_role": ["dataset_role_code", "role"], "dataset_role_raw": ["dataset_role_raw"],
        "analysis_population": ["analysis_population_id", "population"],
        "external_axis": ["external_validation_axis_code", "axis"],
        "investigator_relation": ["investigator_relation_code"],
        "sample_n": ["sample_n", "n", "n_total"], "n_total_raw": ["n_total_raw"],
        "event_n": ["event_n", "events", "n_events", "n_events_bsi_or_primary"],
        "event_n_raw": ["n_events_raw"],
        "nonevent_n": ["nonevent_n", "non_events", "n_non_events", "n_non_events_primary"],
        "nonevent_n_raw": ["n_non_events_raw"],
        "prevalence": ["prevalence", "prevalence_primary"],
        "split_method": ["split_method_raw", "split_strategy_raw"],
        "validation_raw": ["validation_raw"], "internal_validation_raw": ["internal_validation_raw"],
        "same_site_as_development_01": ["same_site_as_development_01"],
        "later_period_than_development_01": ["later_period_than_development_01"],
        "different_site_from_development_01": ["different_site_from_development_01"],
        "investigator_independent_01": ["investigator_independent_01"],
        "locked_model_before_test_01": ["locked_model_before_test_01"],
        "used_for_tuning_01": ["used_for_tuning_01"],
        "independent_dataset_01": ["independent_dataset_01"],
        "institution_raw": ["institution_raw"], "country_raw": ["country_raw"],
        "source_period_raw": ["source_period_raw"],
        "recruitment_start": ["recruitment_start"], "recruitment_end": ["recruitment_end"],
        "nested_with_dataset_id": ["nested_with_dataset_id"],
        "dependent_effect_cluster_id": ["dependent_effect_cluster_id", "dependency_cluster_id"],
        "overlap_group_id": ["overlap_group_id"],
        "unit_of_analysis": ["unit_of_analysis", "unit_of_analysis_raw"],
        "unit_of_analysis_code": ["unit_of_analysis_code"],
        "sampling_frame_code": ["sampling_frame_code"],
        "site_time_signature_code": ["site_time_signature_code"],
        "physical_source_code": ["physical_source_code"], "data_source_raw": ["data_source_raw"],
        "eligibility_status": ["eligibility_status"],
        "synthesis_eligibility_status": ["synthesis_eligibility_status"],
        "data_status": ["data_status"], "notes": ["notes"],
    }, ["dataset.tsv", "dataset_values.tsv"]),
    "performance": spec("performance", ["entity_id", "performance_id"], COMMON | {
        "performance_id": ["performance_id", "entity_id"], "model_id": ["model_id", "model"],
        "outcome_id": ["outcome_id", "outcome"], "dataset_id": ["dataset_id", "dataset"],
        "analysis_population": ["analysis_population_id", "population"],
        "metric": ["metric_code", "metric"], "metric_raw": ["metric_raw"],
        "estimate": ["estimate", "auc"], "estimate_raw": ["value_raw", "estimate_raw"], "ci": ["ci"],
        "ci_lower": ["auc_lcl", "ci_lower", "lcl"],
        "ci_upper": ["auc_ucl", "ci_upper", "ucl"], "sample_n": ["sample_n"], "event_n": ["event_n"],
        "nonevent_n": ["nonevent_n"], "prevalence": ["prevalence"],
        "dataset_role": ["dataset_role_code"], "performance_context": ["performance_context_code"],
        "subgroup": ["subgroup_id", "subgroup"], "subgroup_code": ["subgroup_code"],
        "timepoint": ["timepoint"], "timepoint_code": ["timepoint_code"],
        "effect_scale": ["effect_scale"], "variance_scale": ["variance_scale"],
        "auc_se_reported": ["auc_se_reported"], "auc_se_derived": ["auc_se_derived"],
        "auc_se_source": ["auc_se_source"], "logit_auc_derived": ["logit_auc_derived"],
        "logit_auc_se_derived": ["logit_auc_se_derived"],
        "reported_or_derived": ["reported_or_derived"], "derivation_method": ["derivation_method"],
        "internal_consistency_status": ["internal_consistency_status"],
        "uncertainty_method_raw": ["uncertainty_method_raw"], "ci_level": ["ci_level"],
        "eligibility_status": ["eligibility_status"],
        "synthesis_eligibility_status": ["synthesis_eligibility_status"], "notes": ["notes"],
    }, ["performance.tsv", "discrimination.tsv", "performance_values.tsv"]),
    "threshold": spec("threshold", ["entity_id", "threshold_id", "performance_id"], COMMON | {
        "threshold_id": ["threshold_id", "entity_id"], "performance_id": ["performance_id", "performance"],
        "threshold": ["threshold_raw", "threshold", "cutoff"],
        "threshold_numeric": ["threshold_numeric", "threshold_score"],
        "selection": ["selection_code", "selection", "threshold_selection_code"],
        "threshold_unit": ["threshold_unit"],
        "threshold_selection_method_raw": ["threshold_selection_method_raw", "threshold_selection_raw"],
        "threshold_normalized": ["threshold_normalized"],
        "sensitivity": ["sensitivity", "sens"], "sensitivity_reported_pct": ["sensitivity_reported_pct"],
        "specificity": ["specificity", "spec"], "specificity_reported_pct": ["specificity_reported_pct"],
        "ppv": ["ppv"], "ppv_reported_pct": ["ppv_reported_pct"],
        "npv": ["npv"], "npv_reported_pct": ["npv_reported_pct"],
        "sensitivity_raw": ["sensitivity_raw"], "specificity_raw": ["specificity_raw"],
        "ppv_raw": ["ppv_raw"], "npv_raw": ["npv_raw"],
        "accuracy": ["accuracy", "accuracy_derived"], "accuracy_raw": ["accuracy_raw"],
        "accuracy_reported_pct": ["accuracy_reported_pct"],
        "lr_plus": ["lr_plus_derived", "lr_positive_raw"],
        "lr_minus": ["lr_minus_derived", "lr_negative_raw"],
        "youden_raw": ["youden_raw"],
        "diagnostic_odds_ratio": ["dor_derived"], "f1": ["f1", "f1_score"],
        "tp": ["tp"], "fp": ["fp"], "fn": ["fn"], "tn": ["tn"],
        "model_id": ["model_id"], "outcome_id": ["outcome_id"], "dataset_id": ["dataset_id"],
        "analysis_population": ["analysis_population_id"], "n_total": ["n_total", "n_total_derived"],
        "event_n": ["n_events", "event_n_derived"],
        "nonevent_n": ["n_non_events", "nonevent_n_derived"],
        "threshold_2x2_id": ["threshold_2x2_id"],
        "arithmetic_status": ["arithmetic_status", "arithmetic_qa_status", "internal_consistency_status"],
        "conflict_detail": ["conflict_detail"],
        "derivation_status": ["derivation_status", "derivation_code"],
        "two_by_two_status": ["two_by_two_status"], "eligibility_status": ["eligibility_status"],
        "synthesis_eligibility_status": ["synthesis_eligibility_status"],
        "notes": ["notes"],
    }, ["threshold.tsv", "threshold_values.tsv", "threshold_2x2_values.tsv"]),
    "calibration": spec("calibration", ["entity_id", "calibration_id", "performance_id"], COMMON | {
        "calibration_id": ["calibration_id", "entity_id"], "performance_id": ["performance_id", "performance"],
        "outcome_id": ["outcome_id"], "model_id": ["model_id"], "dataset_id": ["dataset_id"],
        "metric": ["metric_code", "metric"], "metric_raw": ["metric_raw"],
        "estimate": ["estimate", "value", "value_raw"], "estimate_raw": ["estimate_raw"],
        "calibration_method_raw": ["calibration_method_raw", "method_raw"],
        "calibration_intercept": ["calibration_intercept", "intercept"],
        "calibration_slope": ["calibration_slope", "slope"], "oe_ratio": ["oe_ratio", "o_e"],
        "brier_score": ["brier_score", "brier"], "hl_p": ["hl_p", "hosmer_lemeshow_p"],
        "calibration_plot_01": ["calibration_plot_01", "plot_reported_01"],
        "dca_reported_01": ["dca_reported_01"],
        "dca": ["dca_raw", "decision_curve", "dca_threshold_range_raw"],
        "net_benefit": ["net_benefit", "net_benefit_raw"],
        "clinical_threshold_raw": ["clinical_threshold_raw"],
        "eligibility_status": ["eligibility_status"],
        "synthesis_eligibility_status": ["synthesis_eligibility_status"], "notes": ["notes"],
    }, ["calibration.tsv", "calibration_values.tsv"]),
    "predictor": spec("predictor", ["entity_id", "predictor_id"], COMMON | {
        "predictor_id": ["predictor_id", "entity_id"], "model_id": ["model_id", "model"],
        "outcome_id": ["outcome_id"], "predictor_role": ["predictor_role", "role"],
        "predictor": ["predictor_raw", "predictor_name_raw", "construct"],
        "predictor_standard_zh": ["predictor_standard_zh"],
        "predictor_standard_en": ["predictor_standard_en"],
        "predictor_code": ["predictor_code", "construct_code"],
        "predictor_domain": ["predictor_domain_code", "domain"],
        "drug_or_exposure_class": ["drug_or_exposure_class"],
        "window": ["lookback_window_raw", "measurement_window_raw", "window"],
        "window_code": ["measurement_window_code"],
        "window_days": ["lookback_window_days"], "measurement_time": ["measurement_time_raw"],
        "available_at_t0": ["availability_at_t0_01", "availability_at_t0"],
        "unit": ["unit_raw", "measurement_unit_raw", "unit"],
        "unit_code": ["measurement_unit_code"],
        "coding": ["coding_raw", "coding"], "coding_code": ["coding_code"],
        "effect_measure": ["effect_measure_raw"],
        "effect_estimate": ["effect_estimate", "coefficient", "coefficient_raw"],
        "effect_code": ["coefficient_code"], "points": ["points_raw"],
        "effect_lcl": ["effect_lcl"], "effect_ucl": ["effect_ucl"],
        "direction": ["direction_code"], "selection_method": ["selection_method_raw"],
        "mapping_status": ["mapping_status", "eligible_status"], "notes": ["notes"],
    }, ["predictor.tsv", "predictor_values.tsv"]),
    "tripod": spec("tripod", ["tripod_assessment_id", "assessment_id"], COMMON | {
        "assessment_id": ["tripod_assessment_id", "assessment_id"],
        "component_id": ["component_id", "tripod_component_id"], "outcome_id": ["outcome_id"],
        "model_ids": ["model_ids"], "framework_version": ["framework_version"], "item_code": ["item_code"],
        "item_text": ["item_text_zh", "topic"], "component_stage": ["component_stage", "component_type_code"],
        "section": ["section"],
        "status": ["status", "final_rating", "final_response"], "applicability_justification": ["applicability_justification", "not_applicable_reason"],
        "locator": ["locator"], "evidence_summary": ["evidence_summary"],
        "reviewer_a_rating": ["reviewer_a_rating"], "reviewer_b_rating": ["reviewer_b_rating"],
        "reviewer_a_evidence_id": ["reviewer_a_evidence_id"],
        "reviewer_b_evidence_id": ["reviewer_b_evidence_id"],
        "final_evidence_id": ["final_evidence_id"],
        "adjudication_status": ["adjudication_status"],
        "adjudication_rationale": ["adjudication_rationale"], "notes": ["notes"],
    }, ["tripod_ai_long.tsv", "TRIPOD.tsv", "tripod_scoring_adjudication.tsv"]),
    "probast": spec("probast", ["probast_assessment_id", "assessment_id"], COMMON | {
        "assessment_id": ["probast_assessment_id", "assessment_id"],
        "scope_id": ["scope_id", "assessment_scope_id", "final_scope_id"], "assessment_type": ["assessment_type"],
        "eligibility_scope_id": ["eligibility_scope_id"], "model_id": ["model_id"], "outcome_id": ["outcome_id"],
        "dataset_id": ["dataset_id"], "analysis_population": ["analysis_population_id"],
        "evaluation_unit_id": ["evaluation_unit_id"], "dataset_role": ["dataset_role_code"],
        "performance_ids": ["performance_ids"],
        "framework_version": ["framework_version"], "record_type": ["record_type", "record_type_guard"],
        "domain_code": ["domain_code"], "item_code": ["item_code"], "item_text": ["item_text_zh"],
        "performance_context": ["performance_context", "performance_context_code"],
        "response": ["response", "final_response"], "rationale": ["rationale", "final_rationale", "adjudication_rationale"],
        "reviewer_a_response": ["reviewer_a_response"], "reviewer_b_response": ["reviewer_b_response"],
        "reviewer_a_evidence_id": ["reviewer_a_evidence_id"],
        "reviewer_b_evidence_id": ["reviewer_b_evidence_id"],
        "final_evidence_id": ["final_evidence_id"],
        "not_applicable_reason": ["not_applicable_reason"],
        "scope_status": ["scope_status"], "adjudication_status": ["adjudication_status"],
        "notes": ["notes"],
    }, ["probast_ai_long.tsv", "PROBAST_dev.tsv", "PROBAST_eval.tsv",
        "probast_record_type.tsv", "probast_scoring_adjudication.tsv"]),
    "source_evidence": spec("source_evidence", ["evidence_id"], {
        "evidence_id": ["evidence_id"], "report_id": ["report_id"], "study_id": ["study_id"],
        "source_file": ["source_path", "source_file"], "source_sha256": ["source_sha256"],
        "source_type": ["source_type"], "locator": ["locator", "page_or_location"],
        "table_figure_section": ["table_figure_section", "table_figure_id"],
        "evidence_span": ["evidence_span", "evidence_snippet"], "target_table": ["target_table", "entity_type"],
        "target_entity_id": ["target_entity_id", "entity_id"], "extraction_method": ["extraction_method"],
        "reviewer_id": ["reviewer_id"], "review_round": ["review_round"],
        "confidence": ["confidence", "evidence_confidence"], "timestamp": ["extraction_timestamp", "last_updated"],
        "notes": ["notes"],
    }, ["source_evidence.tsv"]),
}


def clean(value: object) -> str:
    return "" if value is None else str(value).strip()


def observed(value: object) -> bool:
    return clean(value).upper() not in MISSING


def compare_key(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip()).casefold()


def normalize_candidate_value(table: str, field: str, source_column: str, value: str) -> str:
    """Normalize only deterministic scale variants; retain the exact source cell separately."""
    if table == "threshold" and field in {
        "sensitivity", "specificity", "ppv", "npv", "accuracy",
        "sensitivity_reported_pct", "specificity_reported_pct", "ppv_reported_pct",
        "npv_reported_pct", "accuracy_reported_pct",
    }:
        token = value.strip().replace(",", "")
        is_percent = token.endswith("%") or source_column.endswith("_reported_pct")
        if token.endswith("%"):
            token = token[:-1].strip()
        try:
            number = float(token)
        except ValueError:
            return value
        if is_percent or 1 < number <= 100:
            number /= 100.0
        if 0 <= number <= 1:
            return f"{number:.6f}".rstrip("0").rstrip(".")
    return value


def calibration_metric_projection(row: dict[str, str]) -> tuple[str, str, str] | None:
    metric = clean(row.get("metric_code") or row.get("metric")).upper()
    raw = clean(row.get("value_raw") or row.get("estimate") or row.get("value"))
    if not observed(raw):
        return None
    field_by_metric = {
        "CALIBRATION_INTERCEPT": "calibration_intercept",
        "CALIBRATION_SLOPE": "calibration_slope",
        "BRIER_SCORE": "brier_score",
        "O_E_RATIO": "oe_ratio", "OE_RATIO": "oe_ratio",
        "HOSMER_LEMESHOW_P": "hl_p", "H_L_P": "hl_p",
    }
    if metric in field_by_metric:
        match = re.match(r"^\s*([<>]=?|[≤≥])?\s*(-?\d+(?:\.\d+)?)", raw)
        normalized = ((match.group(1) or "") + match.group(2)) if match else raw
        return field_by_metric[metric], raw, normalized
    if metric in {"VISUAL_CALIBRATION_PLOT", "CALIBRATION_PLOT", "VISUALCALIBRATIONCURVE"}:
        return "calibration_plot_01", raw, "1"
    return None


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def probast_assessment_type(row: dict[str, str]) -> str:
    value, _ = first_value(row, ["assessment_type"])
    if value:
        return value.upper()
    item = clean(row.get("item_code")).upper()
    if item.startswith("DEV-"):
        return "DEVELOPMENT"
    if item.startswith("EVAL-"):
        return "EVALUATION"
    return ""


def scoring_parent_key(table: str, row: dict[str, str]) -> tuple[str, ...]:
    report = clean(row.get("report_id")); study = clean(row.get("study_id"))
    item = clean(row.get("item_code"))
    if table == "tripod":
        component, _ = first_value(row, ["component_id", "tripod_component_id"])
        return report, study, component, item
    if table == "probast":
        scope, _ = first_value(row, ["final_scope_id", "scope_id", "assessment_scope_id"])
        return report, study, probast_assessment_type(row), scope, item
    return ()


def build_scoring_parent_index(canonical: Path) -> dict[str, dict[tuple[str, ...], set[str]]]:
    result: dict[str, dict[tuple[str, ...], set[str]]] = {
        "tripod": defaultdict(set), "probast": defaultdict(set),
    }
    for table, filename in (("tripod", "tripod_ai_long.tsv"), ("probast", "probast_ai_long.tsv")):
        path = canonical / filename
        if not path.is_file():
            continue
        _, rows = read_tsv(path)
        definition = SPECS[table]
        for row in rows:
            eid = entity_id(row, definition["ids"])
            key = scoring_parent_key(table, row)
            if eid and key and all(key):
                result[table][key].add(eid)
    return result


def load_adjudication_scope(path: Path | None) -> dict[tuple[str, str, str, str, str], dict[str, str]]:
    if path is None:
        return {}
    _, rows = read_tsv(path)
    result: dict[tuple[str, str, str, str, str], dict[str, str]] = {}
    approved = {"APPROVED", "FINAL_ADJUDICATED", "FROZEN_FINAL_ADJUDICATED"}
    for row_number, row in enumerate(rows, 2):
        key = tuple(clean(row.get(k)) for k in (
            "report_id", "study_id", "entity_type", "entity_id", "field_name"
        ))
        status = clean(row.get("adjudication_status")).upper()
        evidence = clean(row.get("evidence_id") or row.get("final_evidence_id"))
        if not all(key) or status not in approved or not evidence:
            raise ValueError(f"invalid adjudication-scope row {row_number}: complete key, approved status, and evidence are required")
        if key in result:
            raise ValueError(f"duplicate adjudication-scope key at row {row_number}: {key}")
        result[key] = dict(row)
    return result


def entity_id(row: dict[str, str], aliases: list[str]) -> str:
    for name in aliases:
        if observed(row.get(name)):
            return clean(row.get(name))
    return ""


def first_value(row: dict[str, str], aliases: list[str]) -> tuple[str, str]:
    for name in aliases:
        if observed(row.get(name)):
            return clean(row.get(name)), name
    return "", ""


def table_for_file(name: str, selected: set[str] | None = None) -> str | None:
    for table, definition in SPECS.items():
        if selected and table not in selected:
            continue
        if name in definition["files"]:
            return table
    return None


def file_role(path: Path, canonical: Path, declared: str) -> str:
    if declared:
        return declared
    if path.parent == canonical:
        if path.name in COMPANION_FILES:
            return "FINAL_VALUE"
        return "FINAL_ENTITY"
    return ""


def load_entity_crosswalk(canonical: Path) -> dict[str, object]:
    path = canonical / "semantic_key_crosswalk.tsv"
    exact: dict[tuple[str, str, str, str, str], set[tuple[str, str, str]]] = defaultdict(set)
    loose: dict[tuple[str, str, str], set[tuple[str, str, str]]] = defaultdict(set)
    removed_exact: set[tuple[str, str, str, str, str]] = set()
    removed_loose: set[tuple[str, str, str]] = set()
    if not path.is_file():
        return {"exact": exact, "loose": loose, "removed_exact": removed_exact,
                "removed_loose": removed_loose}
    _, rows = read_tsv(path)
    role_columns = {"A": "a_entity_id", "B": "b_entity_id", "THIRD": "third_entity_id", "FINAL": "final_entity_id"}
    for row in rows:
        final_id = clean(row.get("final_entity_id"))
        report = clean(row.get("report_id")); study = clean(row.get("study_id")); entity = clean(row.get("entity_type")).lower()
        decision = clean(row.get("mapping_decision")).upper()
        for role, column in role_columns.items():
            source_id = clean(row.get(column))
            if observed(source_id):
                key = (report, study, entity, role, source_id)
                loose_key = (entity, role, source_id)
                if observed(final_id):
                    target = (report, study, final_id)
                    exact[key].add(target); loose[loose_key].add(target)
                elif decision in {"REMOVED_DUPLICATE", "REMOVED_INELIGIBLE_ENTITY"}:
                    removed_exact.add(key); removed_loose.add(loose_key)
    return {"exact": exact, "loose": loose, "removed_exact": removed_exact,
            "removed_loose": removed_loose}


def row_identity(row: dict[str, str], definition: dict,
                 study_reports: dict[str, set[str]]) -> tuple[str, str]:
    report_id, _ = first_value(row, definition["fields"].get("report_id", []))
    study_id, _ = first_value(row, definition["fields"].get("study_id", []))
    if study_id and not report_id and len(study_reports.get(study_id, set())) == 1:
        report_id = next(iter(study_reports[study_id]))
    return report_id, study_id


def seed_canonical_inventory(canonical: Path, selected_tables: set[str] | None,
                             audit: list[dict]) -> tuple[dict[str, set[tuple[str, str, str]]],
                                                        dict[str, dict[str, set[tuple[str, str, str]]]],
                                                        dict[str, set[str]], list[tuple[Path, str]]]:
    entities: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    by_id: dict[str, dict[str, set[tuple[str, str, str]]]] = defaultdict(lambda: defaultdict(set))
    study_reports: dict[str, set[str]] = defaultdict(set)
    main_files: list[tuple[Path, str]] = []
    study_path = canonical / "study.tsv"
    if selected_tables and "study" not in selected_tables and study_path.is_file():
        _, identity_rows = read_tsv(study_path)
        for row in identity_rows:
            study_id, _ = first_value(row, SPECS["study"]["fields"]["study_id"])
            report_id, _ = first_value(row, SPECS["study"]["fields"]["report_id"])
            if study_id and report_id:
                study_reports[study_id].add(report_id)
    tables = ["study"] + [x for x in SPECS if x != "study"]
    for table in tables:
        if selected_tables and table not in selected_tables:
            continue
        for name in CANONICAL_MAIN_FILES.get(table, ()):
            path = canonical / name
            if not path.is_file():
                continue
            main_files.append((path, table))
            _, rows = read_tsv(path)
            definition = SPECS[table]
            for row_number, row in enumerate(rows, 2):
                eid = entity_id(row, definition["ids"])
                if not eid:
                    audit.append({"table": table, "entity_id": "", "field_name": "",
                                  "resolution": "UNMATCHED_ROW_NO_ENTITY_ID", "source_role": "FINAL_ENTITY",
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "Canonical entity row has no stable entity identifier"})
                    continue
                report_id, study_id = row_identity(row, definition, study_reports)
                if table == "study" and not study_id:
                    study_id = eid
                if table == "study" and report_id and study_id:
                    study_reports[study_id].add(report_id)
                if study_id and not report_id and len(study_reports.get(study_id, set())) == 1:
                    report_id = next(iter(study_reports[study_id]))
                key = (report_id, study_id, eid)
                if key in entities[table]:
                    audit.append({"table": table, "entity_id": eid, "field_name": "",
                                  "resolution": "DUPLICATE_CANONICAL_ENTITY_KEY", "source_role": "FINAL_ENTITY",
                                  "source_path": str(path), "source_row": row_number,
                                  "details": f"Duplicate canonical compound key {key!r}"})
                entities[table].add(key); by_id[table][eid].add(key)
    return entities, by_id, study_reports, main_files


def crosswalk_lookup(id_map: dict[str, object], report_id: str, study_id: str, table: str,
                     role: str, source_eid: str) -> tuple[str, set[tuple[str, str, str]]]:
    exact_key = (report_id, study_id, table, role, source_eid)
    loose_key = (table, role, source_eid)
    exact = id_map["exact"].get(exact_key, set())
    if exact:
        return "TARGET", set(exact)
    if exact_key in id_map["removed_exact"]:
        return "REMOVED", set()
    loose = id_map["loose"].get(loose_key, set())
    if len(loose) == 1:
        return "TARGET", set(loose)
    if loose_key in id_map["removed_loose"] and not loose:
        return "REMOVED", set()
    if len(loose) > 1:
        return "AMBIGUOUS", set(loose)
    return "NONE", set()


def preserve_source_row(path: Path, row_number: int, row: dict[str, str], table: str, role: str,
                        source_eid: str, reason: str, source_values: list[dict]) -> None:
    for column, value in row.items():
        if observed(value):
            source_values.append({"entity_type": table, "source_entity_id": source_eid,
                                  "source_role": role, "source_path": str(path),
                                  "source_row": row_number, "source_column": column,
                                  "source_value": clean(value), "preservation_reason": reason})


def collect_file(path: Path, table: str, role: str, candidates: dict,
                 entities: dict[str, set[tuple[str, str, str]]],
                 canonical_entities: dict[str, set[tuple[str, str, str]]],
                 canonical_by_id: dict[str, dict[str, set[tuple[str, str, str]]]], audit: list[dict],
                 id_map: dict[str, object], study_reports: dict[str, set[str]],
                 source_values: list[dict], companion_claims: list[dict], companion_seen: dict[tuple, tuple[str, str]],
                 scoring_parent_index: dict[str, dict[tuple[str, ...], set[str]]],
                 adjudication_scope: dict[tuple[str, str, str, str, str], dict[str, str]]) -> None:
    definition = SPECS[table]
    headers, rows = read_tsv(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    mapped_columns = ({alias for aliases in definition["fields"].values() for alias in aliases} |
                      set(definition["ids"]) | set(EVIDENCE_ALIASES) |
                      COMPANION_PROVENANCE_COLUMNS.get(path.name, set()))
    is_companion = path.name in COMPANION_FILES
    allowed_companion_fields = COMPANION_FIELD_ALLOWLIST.get(path.name)
    for row_number, row in enumerate(rows, 2):
        source_eid = entity_id(row, definition["ids"])
        if not source_eid and path.name in {
            "tripod_scoring_adjudication.tsv", "probast_scoring_adjudication.tsv"
        }:
            parent_key = scoring_parent_key(table, row)
            parent_matches = scoring_parent_index.get(table, {}).get(parent_key, set())
            if len(parent_matches) == 1:
                source_eid = next(iter(parent_matches))
            elif len(parent_matches) > 1:
                audit.append({"table": table, "entity_id": "", "field_name": "",
                              "resolution": "AMBIGUOUS_CANONICAL_ENTITY_ID", "source_role": role,
                              "source_path": str(path), "source_row": row_number,
                              "details": f"Scoring companion natural key matches multiple parents: {parent_key!r}"})
                preserve_source_row(path, row_number, row, table, role, "", "AMBIGUOUS_CANONICAL_ENTITY_ID", source_values)
                continue
        if not source_eid:
            audit.append({"table": table, "entity_id": "", "field_name": "", "resolution": "UNMATCHED_ROW_NO_ENTITY_ID",
                          "source_role": role, "source_path": str(path), "source_row": row_number, "details": "No stable entity identifier"})
            continue
        report_id, study_id = row_identity(row, definition, study_reports)
        direct = (report_id, study_id, source_eid)
        target_keys: set[tuple[str, str, str]] = set()
        if role in FINAL_ROLES:
            if direct in canonical_entities[table]:
                target_keys = {direct}
            else:
                matches = set(canonical_by_id[table].get(source_eid, set()))
                if study_id:
                    matches = {x for x in matches if x[1] == study_id}
                if report_id:
                    matches = {x for x in matches if x[0] == report_id}
                if len(matches) == 1:
                    target_keys = matches
                elif len(matches) > 1:
                    audit.append({"table": table, "entity_id": source_eid, "field_name": "",
                                  "resolution": "AMBIGUOUS_CANONICAL_ENTITY_ID", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "Entity ID matches multiple report/study compound keys"})
                    preserve_source_row(path, row_number, row, table, role, source_eid,
                                        "AMBIGUOUS_CANONICAL_ENTITY_ID", source_values)
                    continue
                elif is_companion:
                    audit.append({"table": table, "entity_id": source_eid, "field_name": "",
                                  "resolution": "ORPHAN_COMPANION_KEY", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "Companion entity key has no canonical parent"})
                    preserve_source_row(path, row_number, row, table, role, source_eid,
                                        "ORPHAN_COMPANION_KEY", source_values)
                    continue
                else:
                    target_keys = {direct}
        else:
            state, mapped = crosswalk_lookup(id_map, report_id, study_id, table, role, source_eid)
            if state == "REMOVED":
                audit.append({"table": table, "entity_id": source_eid, "field_name": "",
                              "resolution": "REMOVED_BRANCH_ENTITY_SOURCE_PRESERVED", "source_role": role,
                              "source_path": str(path), "source_row": row_number,
                              "details": "SEMKEY adjudication removed this source entity; values retained only in audit"})
                preserve_source_row(path, row_number, row, table, role, source_eid,
                                    "REMOVED_BRANCH_ENTITY", source_values)
                continue
            if state == "AMBIGUOUS" or len(mapped) > 1:
                code = "CROSSWALK_SPLIT_REQUIRES_ADJUDICATION" if mapped else "AMBIGUOUS_BRANCH_ENTITY_MAPPING"
                audit.append({"table": table, "entity_id": source_eid, "field_name": "",
                              "resolution": code, "source_role": role, "source_path": str(path),
                              "source_row": row_number,
                              "details": "One source entity has multiple possible final destinations; field broadcasting is prohibited"})
                preserve_source_row(path, row_number, row, table, role, source_eid, code, source_values)
                continue
            if state == "TARGET":
                target_keys = mapped
            elif direct in canonical_entities[table]:
                target_keys = {direct}
            else:
                matches = set(canonical_by_id[table].get(source_eid, set()))
                if study_id:
                    matches = {x for x in matches if x[1] == study_id}
                if report_id:
                    matches = {x for x in matches if x[0] == report_id}
                if len(matches) == 1:
                    target_keys = matches
                elif not canonical_entities[table]:
                    target_keys = {direct}
                else:
                    audit.append({"table": table, "entity_id": source_eid, "field_name": "",
                                  "resolution": "UNMAPPED_BRANCH_ENTITY_ID", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "No unique A/B/third-to-final SEMKEY destination; source values retained only in audit"})
                    preserve_source_row(path, row_number, row, table, role, source_eid,
                                        "UNMAPPED_BRANCH_ENTITY_ID", source_values)
                    continue
        for report_key, study_key, eid in sorted(target_keys):
            entity_key = (report_key, study_key, eid)
            entities[table].add(entity_key)
            for field, aliases in definition["fields"].items():
                if allowed_companion_fields is not None and field not in allowed_companion_fields:
                    continue
                values_by_alias = [(clean(row.get(alias)), alias) for alias in aliases if observed(row.get(alias))]
                normalized_by_alias = [
                    (normalize_candidate_value(table, field, alias, value), value, alias)
                    for value, alias in values_by_alias
                ]
                unique = {compare_key(value) for value, _, _ in normalized_by_alias}
                if len(unique) > 1:
                    audit.append({"table": table, "entity_id": eid, "field_name": field,
                                  "resolution": "AMBIGUOUS_ALIAS", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": json.dumps(values_by_alias, ensure_ascii=False)})
                    continue
                normalized_value, value, source_column = (
                    normalized_by_alias[0] if normalized_by_alias else ("", "", ""))
                if not value:
                    continue
                evidence, _ = first_value(row, EVIDENCE_ALIASES)
                candidate_role = role
                scope_key = (report_key, study_key, table, eid, field)
                scope_record = adjudication_scope.get(scope_key)
                if role == "FINAL":
                    candidate_role = "FINAL_APPROVED" if scope_record else "FINAL_UNSCOPED"
                    if scope_record and not evidence:
                        evidence = clean(scope_record.get("evidence_id") or scope_record.get("final_evidence_id"))
                candidate = {"value": normalized_value, "raw_value": value, "role": candidate_role,
                             "source_entity_id": source_eid,
                             "source_path": str(path), "source_row": str(row_number),
                             "source_column": source_column, "source_sha256": digest, "evidence_id": evidence,
                             "report_id": report_key, "study_id": study_key}
                candidate_key = (table, report_key, study_key, eid, field)
                if is_companion:
                    duplicate_role = "FINAL" if role in FINAL_ROLES else role
                    duplicate_key = (duplicate_role, report_key, study_key, eid, field)
                    previous = companion_seen.get(duplicate_key)
                    compatible_record_type_guard = (
                        previous is not None and table == "probast" and field == "record_type" and
                        {previous[1], path.name} == {
                            "probast_record_type.tsv", "probast_scoring_adjudication.tsv"
                        } and compare_key(previous[0]) == compare_key(normalized_value)
                    )
                    identity_field = field in {"report_id", "study_id", "semantic_key"} or field.endswith("_id")
                    if previous is not None and not compatible_record_type_guard and not identity_field:
                        audit.append({"table": table, "entity_id": eid, "field_name": field,
                                      "resolution": "DUPLICATE_COMPANION_KEY", "source_role": role,
                                      "source_path": str(path), "source_row": row_number,
                                      "details": "Duplicate companion entity key and canonical target field"})
                    companion_seen[duplicate_key] = (normalized_value, path.name)
                candidates[candidate_key].append(candidate)
                if is_companion and role in FINAL_ROLES:
                    companion_claims.append({"source_path": str(path), "source_row": str(row_number),
                                             "source_column": source_column, "entity_type": table,
                                             "report_id": report_key, "study_id": study_key, "entity_id": eid,
                                             "field_name": field, "source_value": value,
                                             "normalized_source_value": normalized_value})
            projection = calibration_metric_projection(row) if table == "calibration" and is_companion else None
            if projection:
                field, raw_projection, normalized_projection = projection
                source_column = next((x for x in ("value_raw", "estimate", "value") if observed(row.get(x))), "")
                evidence, _ = first_value(row, EVIDENCE_ALIASES)
                candidate_role = role
                scope_key = (report_key, study_key, table, eid, field)
                scope_record = adjudication_scope.get(scope_key)
                if role == "FINAL":
                    candidate_role = "FINAL_APPROVED" if scope_record else "FINAL_UNSCOPED"
                    if scope_record and not evidence:
                        evidence = clean(scope_record.get("evidence_id") or scope_record.get("final_evidence_id"))
                candidate = {"value": normalized_projection, "raw_value": raw_projection, "role": candidate_role,
                             "source_entity_id": source_eid, "source_path": str(path),
                             "source_row": str(row_number), "source_column": source_column,
                             "source_sha256": digest, "evidence_id": evidence,
                             "report_id": report_key, "study_id": study_key,
                             "projection_rule": "CALIBRATION_METRIC_CODE_TO_TYPED_FIELD"}
                candidate_key = (table, report_key, study_key, eid, field)
                duplicate_role = "FINAL" if role in FINAL_ROLES else role
                duplicate_key = (duplicate_role, report_key, study_key, eid, field)
                if duplicate_key in companion_seen:
                    audit.append({"table": table, "entity_id": eid, "field_name": field,
                                  "resolution": "DUPLICATE_COMPANION_KEY", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "Duplicate projected calibration companion field"})
                companion_seen[duplicate_key] = (normalized_projection, path.name)
                candidates[candidate_key].append(candidate)
                if role in FINAL_ROLES:
                    companion_claims.append({"source_path": str(path), "source_row": str(row_number),
                                             "source_column": source_column, "entity_type": table,
                                             "report_id": report_key, "study_id": study_key, "entity_id": eid,
                                             "field_name": field, "source_value": raw_projection,
                                             "normalized_source_value": normalized_projection})
            for field, aliases in definition["fields"].items():
                if allowed_companion_fields is not None and field not in allowed_companion_fields:
                    continue
                if not aliases:
                    continue
                primary = aliases[0]
                if primary in headers and not observed(row.get(primary)):
                    value, alias = first_value(row, aliases[1:])
                    if value:
                        audit.append({"table": table, "entity_id": eid, "field_name": field, "resolution": "FAKE_NR_ALIAS_RECOVERABLE",
                                      "source_role": role, "source_path": str(path), "source_row": row_number,
                                      "details": f"{primary} missing while {alias} contains data"})
            for column in headers:
                if (column in mapped_columns or column in PROVENANCE_FIELDS or
                        column.lstrip("_") in PROVENANCE_FIELDS or column.startswith("_source_")):
                    continue
                if observed(row.get(column)):
                    audit.append({"table": table, "entity_id": eid, "field_name": column,
                                  "resolution": "UNMAPPED_NONMISSING_SOURCE_FIELD", "source_role": role,
                                  "source_path": str(path), "source_row": row_number,
                                  "details": "Nonmissing source field has no declared semantic mapping"})


def unique_values(items: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in items:
        grouped[compare_key(item["value"])].append(item)
    return grouped


def resolve(items: list[dict]) -> tuple[str, str, str, list[dict]]:
    authoritative = [x for x in items if x["role"] in {"FINAL_APPROVED", "FINAL_VALUE"}]
    if authoritative:
        grouped = unique_values(authoritative)
        if len(grouped) == 1:
            chosen = next(iter(grouped.values()))[0]
            return "OBSERVED", chosen["value"], "RECOVERED_FINAL_OR_COMPANION", authoritative
        return "CONFLICT", "", "CONFLICT_WITHIN_FINAL_OR_COMPANION", authoritative
    by_role = {role: [x for x in items if x["role"] == role] for role in BRANCH_ROLES}
    final_entity = [x for x in items if x["role"] == "FINAL_ENTITY"]
    unscoped_final = [x for x in items if x["role"] == "FINAL_UNSCOPED"]
    if by_role["A"] and by_role["B"]:
        a = unique_values(by_role["A"]); b = unique_values(by_role["B"])
        common = set(a) & set(b)
        if len(common) == 1 and len(a) == len(b) == 1:
            chosen = a[next(iter(common))][0]
            final_checks = final_entity + unscoped_final
            if final_checks:
                canonical = unique_values(final_checks)
                if len(canonical) != 1 or next(iter(canonical)) != next(iter(common)):
                    return "CONFLICT", "", "UNAPPROVED_FINAL_OVERRIDE", final_checks + by_role["A"] + by_role["B"]
            return "OBSERVED", chosen["value"], "RECOVERED_A_B_CONSENSUS", by_role["A"] + by_role["B"]
        return "CONFLICT", "", "A_B_FIELD_CONFLICT", by_role["A"] + by_role["B"]
    if final_entity:
        grouped = unique_values(final_entity)
        if len(grouped) == 1:
            chosen = next(iter(grouped.values()))[0]
            if unscoped_final:
                proposed = unique_values(unscoped_final)
                if len(proposed) != 1 or next(iter(proposed)) != next(iter(grouped)):
                    return "CONFLICT", "", "UNAPPROVED_FINAL_OVERRIDE", final_entity + unscoped_final
            return "OBSERVED", chosen["value"], "RECOVERED_CANONICAL_ENTITY", final_entity
        return "CONFLICT", "", "CONFLICT_WITHIN_CANONICAL_ENTITY", final_entity
    if unscoped_final:
        return "PENDING_REVIEW", "", "UNSCOPED_FINAL_REQUIRES_ADJUDICATION", unscoped_final
    observed_branches = [x for x in items if x["role"] in BRANCH_ROLES]
    if observed_branches:
        return "PENDING_REVIEW", "", "SINGLE_BRANCH_VALUE_REQUIRES_ADJUDICATION", observed_branches
    return "NOT_CAPTURED", "", "NO_MAPPED_VALUE", items


def fact_key(row: dict[str, str]) -> tuple[str, str, str, str, str]:
    return tuple(clean(row.get(k)) for k in ("report_id", "study_id", "entity_type", "entity_id", "field_name"))


def apply_field_overlay(base_rows: list[dict[str, str]], final_rows: list[dict[str, str]],
                        adjudication_scope: set[tuple[str, str, str, str, str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """Overlay adjudicated facts by field key; a narrow final table cannot erase rich base facts."""
    merged = {fact_key(row): dict(row) for row in base_rows}
    audit: list[dict[str, str]] = []
    if len(merged) != len(base_rows) or any(not all(key) for key in merged):
        raise ValueError("base facts require unique, complete field keys")
    seen: set[tuple[str, str, str, str, str]] = set()
    for final in final_rows:
        key = fact_key(final)
        if not all(key) or key in seen:
            raise ValueError("final facts require unique, complete field keys")
        seen.add(key)
        old = merged.get(key)
        new_status = clean(final.get("value_status_code")).upper()
        new_value = clean(final.get("normalized_value") or final.get("raw_value"))
        old_status = clean((old or {}).get("value_status_code")).upper()
        old_value = clean((old or {}).get("normalized_value") or (old or {}).get("raw_value"))
        if key not in adjudication_scope:
            if old is None or (new_status, new_value) != (old_status, old_value):
                raise ValueError(f"final fact outside adjudication scope changes {key}")
            continue
        if old and old_status == "OBSERVED" and (new_status in {"", "NOT_CAPTURED"} or not observed(new_value)):
            audit.append({"fact_key": "|".join(key), "action": "PRESERVE_BASE_OBSERVED",
                          "old_value": old_value, "new_value": new_value,
                          "reason": "Missing/narrow final field cannot erase an observed base fact"})
            continue
        merged[key] = dict(final)
        audit.append({"fact_key": "|".join(key), "action": "APPLY_ADJUDICATED_FIELD",
                      "old_value": old_value, "new_value": new_value, "reason": "Key is in adjudication scope"})
    return list(merged.values()), audit


def recover(canonical: Path, branches: list[tuple[str, Path]], output: Path,
            selected_tables: set[str] | None = None,
            required_companions: set[str] | None = None,
            adjudication_scope_path: Path | None = None) -> dict:
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"refusing to overwrite non-empty output: {output}")
    output.mkdir(parents=True, exist_ok=True)
    candidates: dict[tuple[str, str, str, str, str], list[dict]] = defaultdict(list)
    audit: list[dict] = []
    canonical_entities, canonical_by_id, study_reports, main_files = seed_canonical_inventory(
        canonical, selected_tables, audit)
    entities: dict[str, set[tuple[str, str, str]]] = defaultdict(set)
    for table, keys in canonical_entities.items():
        entities[table].update(keys)
    id_map = load_entity_crosswalk(canonical)
    scoring_parent_index = build_scoring_parent_index(canonical)
    adjudication_scope = load_adjudication_scope(adjudication_scope_path)
    source_values: list[dict] = []
    companion_claims: list[dict] = []
    companion_seen: dict[tuple, tuple[str, str]] = {}
    consumed_final_companion_paths: set[Path] = set()
    consumed_branch_companion_paths: set[Path] = set()
    main_path_set = {path for path, _ in main_files}

    for path, table in main_files:
        collect_file(path, table, "FINAL_ENTITY", candidates, entities, canonical_entities,
                     canonical_by_id, audit, id_map, study_reports, source_values,
                     companion_claims, companion_seen, scoring_parent_index, adjudication_scope)
    for path in sorted(canonical.glob("*.tsv")):
        if path in main_path_set:
            continue
        table = table_for_file(path.name, selected_tables)
        if table:
            if path.name in COMPANION_FILES:
                consumed_final_companion_paths.add(path)
            collect_file(path, table, file_role(path, canonical, ""), candidates, entities,
                         canonical_entities, canonical_by_id, audit, id_map, study_reports,
                         source_values, companion_claims, companion_seen,
                         scoring_parent_index, adjudication_scope)
    for role, root in branches:
        if role not in BRANCH_ROLES:
            raise ValueError(f"invalid branch role {role!r}")
        for table_name, definition in SPECS.items():
            if selected_tables and table_name not in selected_tables:
                continue
            for name in definition["files"]:
                if name in {"tripod_scoring_adjudication.tsv", "probast_scoring_adjudication.tsv"} and role != "FINAL":
                    continue
                path = root / name
                if path.is_file():
                    if path.name in COMPANION_FILES:
                        if role == "FINAL":
                            consumed_final_companion_paths.add(path)
                        else:
                            consumed_branch_companion_paths.add(path)
                    collect_file(path, definition["entity"], role, candidates, entities,
                                 canonical_entities, canonical_by_id, audit, id_map, study_reports,
                                 source_values, companion_claims, companion_seen,
                                 scoring_parent_index, adjudication_scope)

    declared_required = set(required_companions or set())
    manifest_path = canonical / "table_family_manifest.json"
    if manifest_path.is_file():
        declared = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        declared_required.update(declared.get("required_companions", []))
    available_names = {p.name for p in consumed_final_companion_paths}
    for name in sorted(declared_required):
        if name not in available_names:
            audit.append({"table": table_for_file(name, selected_tables) or "", "entity_id": "",
                          "field_name": "", "resolution": "MISSING_COMPANION_TABLE",
                          "source_role": "PACKAGE", "source_path": str(canonical / name),
                          "source_row": "", "details": "Companion declared required but not found"})

    facts: list[dict] = []
    unresolved: list[dict] = []
    views: dict[str, list[dict]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    fact_lookup: dict[tuple[str, str, str, str, str], tuple[str, str]] = {}
    for table, entity_keys in sorted(entities.items()):
        definition = SPECS[table]
        for report_id, study_id, eid in sorted(entity_keys):
            view: dict[str, str] = {"report_id": report_id, "study_id": study_id, "entity_id": eid}
            for field in definition["fields"]:
                key = (table, report_id, study_id, eid, field)
                items = candidates.get(key, [])
                status, value, resolution, used = resolve(items)
                status_counts[status] += 1
                evidence_ids = sorted({x["evidence_id"] for x in used if observed(x.get("evidence_id"))})
                raw_value = ""
                if status == "OBSERVED":
                    raw_value = next((x.get("raw_value", x["value"]) for x in used
                                      if compare_key(x["value"]) == compare_key(value)), value)
                fact_id = "REC-" + hashlib.sha1("|".join(key).encode()).hexdigest()[:16].upper()
                facts.append({
                    "fact_id": fact_id, "report_id": report_id, "study_id": study_id,
                    "entity_type": table, "entity_id": eid, "field_name": field,
                    "raw_value": raw_value, "normalized_value": value if status == "OBSERVED" else "",
                    "value_status_code": status, "status_rationale": "" if status == "OBSERVED" else resolution,
                    "evidence_id": "|".join(evidence_ids), "extractor_id": "SCHEMA_RECOVERY_V57",
                    "review_round": "LEGACY_RECOVERY", "branch_status": "OPEN" if status != "OBSERVED" else "FROZEN_FINAL",
                    "adjudication_status": "PENDING_ADJUDICATION" if status != "OBSERVED" else "FINAL_ADJUDICATED",
                    "status_rule_id": "", "context_json": json.dumps({"resolution": resolution}, ensure_ascii=False),
                    "writeback_table": table, "writeback_key": eid, "resolution_code": resolution,
                    "candidate_values_json": json.dumps(used, ensure_ascii=False),
                })
                fact_lookup[key] = (status, value)
                view[field] = value if status == "OBSERVED" else status
                view[field + "__status"] = status
                if resolution in {"UNAPPROVED_FINAL_OVERRIDE", "UNSCOPED_FINAL_REQUIRES_ADJUDICATION"}:
                    audit.append({"table": table, "entity_id": eid, "field_name": field,
                                  "resolution": resolution, "source_role": "FINAL_ENTITY",
                                  "source_path": str(canonical), "source_row": "",
                                  "details": "Final value lacks a matching field-level adjudication scope or conflicts with preserved evidence"})
                if status in {"CONFLICT", "PENDING_REVIEW"}:
                    unresolved.append({"report_id": report_id, "study_id": study_id,
                                       "entity_type": table, "entity_id": eid, "field_name": field,
                                       "status": status, "resolution_code": resolution,
                                       "candidate_values_json": json.dumps(used, ensure_ascii=False)})
            views[table].append(view)

    companion_coverage: list[dict] = []
    for claim in companion_claims:
        key = (claim["entity_type"], claim["report_id"], claim["study_id"],
               claim["entity_id"], claim["field_name"])
        result_status, result_value = fact_lookup.get(key, ("NOT_CAPTURED", ""))
        visible = (result_status == "OBSERVED" and
                   compare_key(result_value) == compare_key(claim["normalized_source_value"]))
        row = dict(claim)
        row.update({"result_status": result_status, "result_value": result_value,
                    "visible_01": "1" if visible else "0"})
        companion_coverage.append(row)
        if not visible:
            audit.append({"table": claim["entity_type"], "entity_id": claim["entity_id"],
                          "field_name": claim["field_name"],
                          "resolution": "FALSE_NR_COMPANION_VALUE_EXISTS", "source_role": "FINAL_VALUE",
                          "source_path": claim["source_path"], "source_row": claim["source_row"],
                          "details": f"Companion value {claim['source_value']!r} is not visible in recovered view"})

    fact_fields = ["fact_id", "report_id", "study_id", "entity_type", "entity_id", "field_name", "raw_value",
                   "normalized_value", "value_status_code", "status_rationale", "evidence_id", "extractor_id",
                   "review_round", "branch_status", "adjudication_status", "status_rule_id", "context_json",
                   "writeback_table", "writeback_key", "resolution_code", "candidate_values_json"]
    write_tsv(output / "recovered_field_facts.tsv", fact_fields, facts)
    write_tsv(output / "recovery_audit.tsv", ["table", "entity_id", "field_name", "resolution", "source_role", "source_path", "source_row", "details"], audit)
    write_tsv(output / "unresolved_fields.tsv", ["report_id", "study_id", "entity_type", "entity_id", "field_name", "status", "resolution_code", "candidate_values_json"], unresolved)
    write_tsv(output / "unlinked_source_values.tsv",
              ["entity_type", "source_entity_id", "source_role", "source_path", "source_row",
               "source_column", "source_value", "preservation_reason"], source_values)
    write_tsv(output / "companion_coverage.tsv",
              ["source_path", "source_row", "source_column", "entity_type", "report_id", "study_id",
               "entity_id", "field_name", "source_value", "normalized_source_value",
               "result_status", "result_value", "visible_01"],
              companion_coverage)
    for table, rows in views.items():
        fields = ["report_id", "study_id", "entity_id"]
        for field in SPECS[table]["fields"]:
            fields.extend([field, field + "__status"])
        write_tsv(output / "views" / f"{table}_recovered.tsv", fields, rows)
    companion_files = sorted({p.name for p in consumed_final_companion_paths})
    audit_resolution_counts = Counter(x["resolution"] for x in audit)
    blocking_by_code = {
        code: audit_resolution_counts[code]
        for code in sorted(BLOCKING_AUDIT_CODES)
        if audit_resolution_counts[code]
    }
    blocking = sum(blocking_by_code.values())
    unmapped_source_fields = sum(
        audit_resolution_counts[code] for code in UNMAPPED_SOURCE_AUDIT_CODES
    )
    failed_coverage = sum(x["visible_01"] != "1" for x in companion_coverage)
    manifest = {
        "protocol": "mdrgnb-meta-v5.7-schema-recovery",
        "status": "OPEN_RECOVERY" if unresolved or blocking else "RECOVERED_NO_FIELD_CONFLICT",
        "canonical_source": str(canonical), "branch_sources": [{"role": r, "path": str(p)} for r, p in branches],
        "selected_tables": sorted(selected_tables) if selected_tables else sorted(SPECS),
        "counts": {"canonical_entities": {k: len(v) for k, v in sorted(canonical_entities.items())},
                   "entities": {k: len(v) for k, v in sorted(entities.items())}, "facts": len(facts),
                   "statuses": dict(sorted(status_counts.items())), "unresolved": len(unresolved),
                   "fake_nr_aliases": sum(x["resolution"] == "FAKE_NR_ALIAS_RECOVERABLE" for x in audit),
                   "unmapped_source_fields": unmapped_source_fields,
                   "unmapped_or_unlinked_source_fields": unmapped_source_fields,
                   "blocking_audit_issues": blocking,
                   "blocking_audit_issues_by_code": blocking_by_code,
                   "companion_coverage_rows": len(companion_coverage),
                   "companion_coverage_visible": len(companion_coverage) - failed_coverage,
                   "companion_coverage_failed": failed_coverage},
        "companion_tables_consumed": sorted(companion_files),
        "companion_sources_consumed": [
            {"name": p.name, "path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
            for p in sorted(consumed_final_companion_paths)
        ],
        "branch_companion_tables_read": sorted({p.name for p in consumed_branch_companion_paths}),
        "required_companions": sorted(declared_required),
        "adjudication_scope_source": str(adjudication_scope_path) if adjudication_scope_path else "",
        "adjudication_scope_sha256": (
            hashlib.sha256(adjudication_scope_path.read_bytes()).hexdigest()
            if adjudication_scope_path else ""
        ),
        "guarantees": {"source_files_immutable": True, "literal_legacy_missing_written_as_observed": False,
                       "a_b_conflict_silently_resolved": False,
                       "companion_tables_materialized": failed_coverage == 0,
                       "canonical_entity_cardinality_preserved": all(
                           len(entities.get(k, set())) == len(v) for k, v in canonical_entities.items() if v)},
    }
    (output / "recovery_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def parse_branch(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("branch must be ROLE=PATH")
    role, path = value.split("=", 1)
    return role.strip().upper(), Path(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover MDR-GNB legacy values without treating schema gaps as source NR")
    parser.add_argument("--canonical", type=Path, required=True)
    parser.add_argument("--branch", action="append", type=parse_branch, default=[])
    parser.add_argument("--table", action="append", choices=sorted(SPECS), dest="tables")
    parser.add_argument("--require-companion", action="append", default=[], dest="required_companions")
    parser.add_argument("--adjudication-scope", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = recover(args.canonical, args.branch, args.output, set(args.tables) if args.tables else None,
                     set(args.required_companions), args.adjudication_scope)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
