from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_review_queue_v56 import build
from missingness_v56 import migrate_legacy_value
from qa_extraction_package_v56 import evaluate_structural_rule, validate


FACT_HEADERS = [
    "fact_id", "report_id", "study_id", "entity_type", "entity_id", "field_name", "raw_value",
    "normalized_value", "value_status_code", "status_rationale", "evidence_id", "extractor_id",
    "review_round", "branch_status", "adjudication_status", "status_rule_id", "context_json",
    "writeback_table", "writeback_key",
]
EVIDENCE_HEADERS = [
    "evidence_id", "report_id", "source_file_id", "source_sha256", "page_or_location",
    "table_figure_section", "evidence_span", "extraction_method", "search_scope", "reviewer_id", "timestamp",
]
QUESTION_HEADERS = [
    "question_id", "priority", "report_id", "entity_type", "entity_id", "field_name", "issue_type",
    "evidence_a", "evidence_b", "source_locator", "recommended_answer", "recommendation_basis",
    "options_json", "user_answer", "adjudication_rationale", "status", "writeback_table", "writeback_key",
    "writeback_field", "expected_type", "allowed_values", "created_at", "resolved_at",
]
SOURCE_HEADERS = [
    "source_file_id", "report_id", "source_sha256", "source_role", "access_status",
    "text_layer_status", "ocr_status", "page_count", "included_in_complete_search_01",
]
RULE_HEADERS = ["rule_id", "entity_type", "field_name", "condition_field", "condition_operator",
                "condition_value", "rule_version", "rationale", "active_01"]


def write_tsv(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t")
        writer.writeheader(); writer.writerows(rows)


class ExtractionV56Tests(unittest.TestCase):
    def evidence(self) -> dict[str, str]:
        return {"evidence_id": "EV1", "report_id": "R1", "source_file_id": "SRC1",
                "source_sha256": "abc", "page_or_location": "p.4", "table_figure_section": "Table 2",
                "evidence_span": "AUC 0.82", "extraction_method": "TEXT_TABLE",
                "search_scope": "main report and supplement", "reviewer_id": "A", "timestamp": "2026-07-22"}

    def fact(self, status: str = "OBSERVED") -> dict[str, str]:
        return {"fact_id": "F1", "report_id": "R1", "study_id": "S1", "entity_type": "performance",
                "entity_id": "P1", "field_name": "auc", "raw_value": "0.82" if status == "OBSERVED" else "",
                "normalized_value": "0.82" if status == "OBSERVED" else "", "value_status_code": status,
                "status_rationale": "" if status == "OBSERVED" else "targeted search unresolved",
                "evidence_id": "EV1", "extractor_id": "A", "review_round": "1", "branch_status": "FROZEN_A",
                "adjudication_status": "BRANCH", "status_rule_id": "",
                "context_json": json.dumps({"review_task_code": "NEW_MODEL_DEVELOPMENT"}),
                "writeback_table": "performance",
                "writeback_key": "P1"}

    def run_package(self, facts: list[dict[str, str]], questions: list[dict[str, str]] | None = None,
                    mode: str = "branch", evidence_rows: list[dict[str, str]] | None = None) -> dict:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); fp = root / "facts.tsv"; ep = root / "evidence.tsv"
            sp = root / "sources.tsv"; rp = root / "rules.tsv"
            write_tsv(fp, FACT_HEADERS, facts); write_tsv(ep, EVIDENCE_HEADERS, evidence_rows or [self.evidence()])
            write_tsv(sp, SOURCE_HEADERS, [{"source_file_id": "SRC1", "report_id": "R1", "source_sha256": "abc",
                                            "source_role": "MAIN_REPORT", "access_status": "ACCESSIBLE",
                                            "text_layer_status": "TEXT_AVAILABLE", "ocr_status": "NOT_NEEDED",
                                            "page_count": "10", "included_in_complete_search_01": "1"}])
            write_tsv(rp, RULE_HEADERS, [{"rule_id": "RULE-DEV", "entity_type": "model",
                                         "field_name": "development_sample_size",
                                         "condition_field": "review_task_code", "condition_operator": "EQ",
                                         "condition_value": "EXTERNAL_EVALUATION_ONLY", "rule_version": "v1",
                                         "rationale": "Development sample size is inapplicable to evaluation-only reports",
                                         "active_01": "1"}])
            qp = None
            if questions is not None:
                qp = root / "questions.tsv"; write_tsv(qp, QUESTION_HEADERS, questions)
            return validate(fp, ep, qp, sp, rp, mode)

    def test_observed_fact_passes(self):
        result = self.run_package([self.fact()])
        self.assertTrue(result["pass"], result)

    def test_legacy_missing_is_not_source_nr(self):
        self.assertEqual(migrate_legacy_value("NR"), ("NR", "NOT_CAPTURED"))
        self.assertEqual(migrate_legacy_value(""), ("", "NOT_CAPTURED"))

    def test_not_captured_blocks_freeze(self):
        row = self.fact("NOT_CAPTURED"); row["evidence_id"] = ""
        result = self.run_package([row], mode="freeze")
        self.assertFalse(result["pass"])
        self.assertTrue(any("blocks freeze" in e for e in result["errors"]))

    def test_pending_review_requires_question(self):
        result = self.run_package([self.fact("PENDING_REVIEW")])
        self.assertFalse(result["pass"])
        question = {"question_id": "Q1", "priority": "HIGH", "report_id": "R1", "entity_type": "performance",
                    "entity_id": "P1", "field_name": "auc", "issue_type": "PENDING_REVIEW",
                    "evidence_a": "0.82", "evidence_b": "", "source_locator": "p.4 Table 2",
                    "recommended_answer": "0.82", "options_json": json.dumps(["0.82", "0.79", "需补证据"]),
                    "recommendation_basis": "Table 2 is explicit", "user_answer": "",
                    "adjudication_rationale": "",
                    "status": "OPEN", "writeback_table": "performance", "writeback_key": "P1",
                    "writeback_field": "auc", "expected_type": "FLOAT", "allowed_values": "0-1",
                    "created_at": "2026-07-22", "resolved_at": ""}
        result = self.run_package([self.fact("PENDING_REVIEW")], [question])
        self.assertTrue(result["pass"], result)

    def test_review_queue_excludes_structural_and_source_nr(self):
        base = self.fact("PENDING_REVIEW")
        base.update({"options_json": json.dumps(["Yes", "No", "Unclear"]), "recommended_answer": "Yes",
                     "evidence_a": "reported yes", "evidence_b": "", "source_locator": "p.4",
                     "recommendation_basis": "explicit statement", "expected_type": "CATEGORY",
                     "allowed_values": "Yes|No|Unclear"})
        structural = dict(base); structural["fact_id"] = "F2"; structural["value_status_code"] = "NA_STRUCTURAL"
        source_nr = dict(base); source_nr["fact_id"] = "F3"; source_nr["value_status_code"] = "NR_SOURCE"
        queue = build([base, structural, source_nr])
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["issue_type"], "PENDING_REVIEW")

    def test_literal_nr_cannot_be_observed(self):
        row = self.fact(); row["raw_value"] = "NR"; row["normalized_value"] = ""
        result = self.run_package([row])
        self.assertFalse(result["pass"])

    def test_literal_na_in_normalized_value_cannot_be_observed(self):
        row = self.fact(); row["normalized_value"] = "NA"
        result = self.run_package([row])
        self.assertFalse(result["pass"])

    def test_freeze_requires_final_branch_and_adjudication(self):
        result = self.run_package([self.fact()], mode="freeze")
        self.assertFalse(result["pass"])
        self.assertTrue(any("FROZEN_FINAL" in e for e in result["errors"]))

    def test_structural_na_requires_matching_rule(self):
        row = self.fact("NA_STRUCTURAL")
        result = self.run_package([row])
        self.assertFalse(result["pass"])
        row.update({"entity_type": "model", "entity_id": "M1", "field_name": "development_sample_size",
                    "status_rule_id": "RULE-DEV", "context_json": json.dumps({"review_task_code": "EXTERNAL_EVALUATION_ONLY"}),
                    "writeback_table": "model", "writeback_key": "M1"})
        result = self.run_package([row])
        self.assertTrue(result["pass"], result)
        row["context_json"] = json.dumps({"review_task_code": "NEW_MODEL_DEVELOPMENT"})
        result = self.run_package([row])
        self.assertFalse(result["pass"])

    def test_negative_structural_operator_requires_present_context_field(self):
        self.assertFalse(evaluate_structural_rule(
            {"condition_field": "review_task_code", "condition_operator": "NE",
             "condition_value": "NEW_MODEL_DEVELOPMENT"}, {}
        ))
        self.assertFalse(evaluate_structural_rule(
            {"condition_field": "review_task_code", "condition_operator": "NOT_IN",
             "condition_value": "A|B"}, {}
        ))
        row = self.fact("NA_STRUCTURAL")
        row.update({"entity_type": "model", "entity_id": "M1", "field_name": "development_sample_size",
                    "status_rule_id": "RULE-DEV", "context_json": "{}", "writeback_table": "model",
                    "writeback_key": "M1"})
        result = self.run_package([row])
        self.assertFalse(result["pass"])

    def test_nr_source_requires_field_specific_complete_manifest_search(self):
        row = self.fact("NR_SOURCE")
        evidence = self.evidence(); evidence["search_scope"] = "all"
        result = self.run_package([row], evidence_rows=[evidence])
        self.assertFalse(result["pass"])
        evidence["search_scope"] = json.dumps({"complete_source_package_01": True, "study_id": "S1",
                                                "entity_type": "performance", "entity_id": "P1", "field_name": "auc",
                                                "source_file_ids": ["SRC1"],
                                                "locations_searched": ["Methods", "Results", "Supplement"]})
        result = self.run_package([row], evidence_rows=[evidence])
        self.assertTrue(result["pass"], result)

    def test_nr_search_evidence_cannot_be_reused_for_another_entity(self):
        first = self.fact("NR_SOURCE")
        second = dict(first); second["fact_id"] = "F2"; second["entity_id"] = "P2"; second["writeback_key"] = "P2"
        evidence = self.evidence()
        evidence["search_scope"] = json.dumps({"complete_source_package_01": True, "study_id": "S1",
                                                "entity_type": "performance", "entity_id": "P1", "field_name": "auc",
                                                "source_file_ids": ["SRC1"], "locations_searched": ["full report"]})
        result = self.run_package([first, second], evidence_rows=[evidence])
        self.assertFalse(result["pass"])
        self.assertTrue(any("entity_id does not match" in e for e in result["errors"]))

    def test_conflict_requires_two_evidence_records(self):
        row = self.fact("CONFLICT")
        result = self.run_package([row])
        self.assertFalse(result["pass"])
        self.assertTrue(any("at least two" in e for e in result["errors"]))

    def test_review_queue_requires_recommended_answer(self):
        row = self.fact("PENDING_REVIEW")
        row.update({"options_json": json.dumps(["Yes", "No"]), "recommended_answer": "",
                    "evidence_a": "Yes", "source_locator": "p.4", "recommendation_basis": "explicit",
                    "expected_type": "CATEGORY", "allowed_values": "Yes|No"})
        with self.assertRaises(ValueError):
            build([row])


if __name__ == "__main__":
    unittest.main()
