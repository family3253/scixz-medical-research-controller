from __future__ import annotations

import csv
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from qa_schema_recovery_v57 import validate
from recover_schema_drift_v57 import apply_field_overlay, observed, read_tsv, recover


def write_tsv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


class SchemaRecoveryV57Tests(unittest.TestCase):
    def test_missing_token_is_whole_cell_only(self):
        self.assertFalse(observed("NR"))
        self.assertTrue(observed("DCA_range=NR; net_benefit=graph only"))
        self.assertTrue(observed("coefficient=NR_FROZEN_PRIOR_MODEL"))

    def test_narrow_final_does_not_erase_a_b_consensus(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; b = root / "B"; out = root / "out"
            canonical.mkdir(); a.mkdir(); b.mkdir()
            write_tsv(canonical / "study.tsv", ["entity_id", "report_id", "study_id", "project", "source_evidence_id"],
                      [{"entity_id": "S18", "report_id": "R18", "study_id": "S18", "project": "narrow final", "source_evidence_id": "EF"}])
            fields = ["study_id", "report_id", "first_author_raw", "publication_year", "title_raw", "doi", "patient_n_total", "source_evidence_id"]
            row = {"study_id": "S18", "report_id": "R18", "first_author_raw": "Hao", "publication_year": "2025",
                   "title_raw": "ESBL model", "doi": "10.test/18", "patient_n_total": "119", "source_evidence_id": "EAB"}
            write_tsv(a / "study.tsv", fields, [row]); write_tsv(b / "study.tsv", fields, [row])
            manifest = recover(canonical, [("A", a), ("B", b)], out)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            by_field = {r["field_name"]: r for r in facts if r["entity_type"] == "study" and r["entity_id"] == "S18"}
            self.assertEqual(by_field["title"]["normalized_value"], "ESBL model")
            self.assertEqual(by_field["patient_n_total"]["normalized_value"], "119")
            self.assertEqual(by_field["title"]["resolution_code"], "RECOVERED_A_B_CONSENSUS")
            self.assertEqual(manifest["counts"]["unmapped_or_unlinked_source_fields"], 0)
            self.assertTrue(validate(out, "migration")["pass"])

    def test_companion_performance_value_is_materialized(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; out = root / "out"; canonical.mkdir()
            write_tsv(canonical / "performance.tsv",
                      ["entity_id", "study_id", "report_id", "model", "outcome", "dataset", "metric", "source_evidence_id"],
                      [{"entity_id": "P18", "study_id": "S18", "report_id": "R18", "model": "M18", "outcome": "O18",
                        "dataset": "D18", "metric": "AUC", "source_evidence_id": "E1"}])
            write_tsv(canonical / "performance_values.tsv",
                      ["performance_id", "stu", "model_id", "outcome_id", "dataset_id", "analysis_population_id", "metric_code", "estimate", "ci", "performance_context_code"],
                      [{"performance_id": "P18", "stu": "S18", "model_id": "M18", "outcome_id": "O18", "dataset_id": "D18",
                        "analysis_population_id": "ALL", "metric_code": "AUC", "estimate": "0.792", "ci": "0.615-0.869",
                        "performance_context_code": "APPARENT"}])
            manifest = recover(canonical, [], out)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            by_field = {r["field_name"]: r for r in facts if r["entity_id"] == "P18"}
            self.assertEqual(by_field["estimate"]["normalized_value"], "0.792")
            self.assertEqual(by_field["ci"]["normalized_value"], "0.615-0.869")
            self.assertEqual(by_field["estimate"]["resolution_code"], "RECOVERED_FINAL_OR_COMPANION")
            self.assertIn("performance_values.tsv", manifest["companion_tables_consumed"])

    def test_conflicting_a_b_values_remain_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; b = root / "B"; out = root / "out"
            canonical.mkdir(); a.mkdir(); b.mkdir()
            fields = ["study_id", "report_id", "title_raw", "source_evidence_id"]
            write_tsv(a / "study.tsv", fields, [{"study_id": "S1", "report_id": "R1", "title_raw": "Title A", "source_evidence_id": "EA"}])
            write_tsv(b / "study.tsv", fields, [{"study_id": "S1", "report_id": "R1", "title_raw": "Title B", "source_evidence_id": "EB"}])
            recover(canonical, [("A", a), ("B", b)], out)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            title = next(r for r in facts if r["entity_id"] == "S1" and r["field_name"] == "title")
            self.assertEqual(title["value_status_code"], "CONFLICT")
            self.assertEqual(title["raw_value"], "")
            self.assertFalse(validate(out, "freeze")["pass"])

    def test_unapproved_final_override_is_not_misreported_as_unmapped(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; b = root / "B"; out = root / "out"
            canonical.mkdir(); a.mkdir(); b.mkdir()
            fields = ["study_id", "report_id", "title_raw", "source_evidence_id"]
            write_tsv(canonical / "study.tsv", fields, [{"study_id": "S1", "report_id": "R1", "title_raw": "Final conflict", "source_evidence_id": "EF"}])
            branch_row = {"study_id": "S1", "report_id": "R1", "title_raw": "A/B consensus", "source_evidence_id": "EAB"}
            write_tsv(a / "study.tsv", fields, [branch_row]); write_tsv(b / "study.tsv", fields, [branch_row])
            manifest = recover(canonical, [("A", a), ("B", b)], out)
            self.assertEqual(manifest["counts"]["blocking_audit_issues"], 1)
            self.assertEqual(manifest["counts"]["unmapped_or_unlinked_source_fields"], 0)
            self.assertEqual(manifest["counts"]["blocking_audit_issues_by_code"], {"UNAPPROVED_FINAL_OVERRIDE": 1})
            result = validate(out, "migration")
            self.assertEqual(result["counts"]["unmapped"], 0)
            self.assertFalse(result["pass"])

    def test_unscoped_final_branch_cannot_override_a_b_consensus(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; b = root / "B"; final = root / "FINAL"; out = root / "out"
            canonical.mkdir(); a.mkdir(); b.mkdir(); final.mkdir()
            fields = ["study_id", "report_id", "title_raw", "source_evidence_id"]
            write_tsv(canonical / "study.tsv", fields, [{"study_id": "S1", "report_id": "R1", "title_raw": "A/B consensus", "source_evidence_id": "EC"}])
            consensus = {"study_id": "S1", "report_id": "R1", "title_raw": "A/B consensus", "source_evidence_id": "EAB"}
            write_tsv(a / "study.tsv", fields, [consensus]); write_tsv(b / "study.tsv", fields, [consensus])
            write_tsv(final / "study.tsv", fields, [{"study_id": "S1", "report_id": "R1", "title_raw": "Unscoped override", "source_evidence_id": "EF"}])
            manifest = recover(canonical, [("A", a), ("B", b), ("FINAL", final)], out)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            title = next(r for r in facts if r["entity_id"] == "S1" and r["field_name"] == "title")
            self.assertEqual(title["value_status_code"], "CONFLICT")
            self.assertEqual(title["resolution_code"], "UNAPPROVED_FINAL_OVERRIDE")
            self.assertGreater(manifest["counts"]["blocking_audit_issues"], 0)
            self.assertFalse(validate(out, "migration")["pass"])

    def test_qa_detects_deleted_expected_fact_and_status_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; out = root / "out"; canonical.mkdir()
            write_tsv(canonical / "study.tsv", ["study_id", "report_id", "title_raw"],
                      [{"study_id": "S1", "report_id": "R1", "title_raw": "Title"}])
            recover(canonical, [], out)
            headers, facts = read_tsv(out / "recovered_field_facts.tsv")
            removed = next(r for r in facts if r["field_name"] == "journal")
            write_tsv(out / "recovered_field_facts.tsv", headers, [r for r in facts if r is not removed])
            result = validate(out, "migration")
            self.assertFalse(result["pass"])
            self.assertTrue(any("expected field facts are missing" in e for e in result["errors"]))

            write_tsv(out / "recovered_field_facts.tsv", headers, facts)
            target = next(r for r in facts if r["field_name"] == "journal")
            target["value_status_code"] = "NR_SOURCE"
            write_tsv(out / "recovered_field_facts.tsv", headers, facts)
            result = validate(out, "migration")
            self.assertFalse(result["pass"])
            self.assertTrue(any("cannot assert NR_SOURCE" in e for e in result["errors"]))

    def test_duplicate_companion_key_across_final_sources_is_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; final = root / "FINAL"; out = root / "out"
            canonical.mkdir(); final.mkdir()
            write_tsv(canonical / "performance.tsv", ["performance_id", "study_id", "report_id", "metric_code"],
                      [{"performance_id": "P1", "study_id": "S1", "report_id": "R1", "metric_code": "AUC"}])
            fields = ["performance_id", "stu", "metric_code", "estimate"]
            row = {"performance_id": "P1", "stu": "S1", "metric_code": "AUC", "estimate": "0.81"}
            write_tsv(canonical / "performance_values.tsv", fields, [row])
            write_tsv(final / "performance_values.tsv", fields, [row])
            recover(canonical, [("FINAL", final)], out)
            _, audit = read_tsv(out / "recovery_audit.tsv")
            self.assertIn("DUPLICATE_COMPANION_KEY", {r["resolution"] for r in audit})
            self.assertFalse(validate(out, "migration")["pass"])

    def test_tripod_and_probast_scoring_companions_materialize(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; out = root / "out"; canonical.mkdir()
            write_tsv(canonical / "tripod_ai_long.tsv",
                      ["assessment_id", "report_id", "study_id", "component_id", "item_code", "status"],
                      [{"assessment_id": "T1", "report_id": "R1", "study_id": "S1", "component_id": "TC1", "item_code": "1", "status": "NR"}])
            write_tsv(canonical / "tripod_scoring_adjudication.tsv",
                      ["adjudication_id", "report_id", "study_id", "component_id", "item_code", "final_response", "final_evidence_id", "adjudication_rationale", "adjudication_status"],
                      [{"adjudication_id": "TA1", "report_id": "R1", "study_id": "S1", "component_id": "TC1", "item_code": "1", "final_response": "PRESENT", "final_evidence_id": "ET1", "adjudication_rationale": "source replay", "adjudication_status": "FROZEN_FINAL_ADJUDICATED"}])
            write_tsv(canonical / "probast_ai_long.tsv",
                      ["probast_assessment_id", "report_id", "study_id", "assessment_type", "scope_id", "model_id", "outcome_id", "dataset_id", "item_code", "record_type", "response"],
                      [{"probast_assessment_id": "P1", "report_id": "R1", "study_id": "S1", "assessment_type": "DEVELOPMENT", "scope_id": "PS1", "model_id": "M1", "outcome_id": "O1", "dataset_id": "NA", "item_code": "DEV-D1-SQ1.1", "record_type": "NR", "response": "NR"}])
            write_tsv(canonical / "probast_record_type.tsv",
                      ["probast_assessment_id", "report_id", "study_id", "assessment_type", "scope_id", "item_code", "record_type", "response"],
                      [{"probast_assessment_id": "P1", "report_id": "R1", "study_id": "S1", "assessment_type": "DEVELOPMENT", "scope_id": "PS1", "item_code": "DEV-D1-SQ1.1", "record_type": "SIGNALLING_QUESTION", "response": "PY"}])
            write_tsv(canonical / "probast_scoring_adjudication.tsv",
                      ["adjudication_id", "report_id", "study_id", "assessment_type", "final_scope_id", "model_id", "outcome_id", "dataset_id", "item_code", "final_response", "final_evidence_id", "record_type_guard", "final_rationale", "adjudication_status"],
                      [{"adjudication_id": "PA1", "report_id": "R1", "study_id": "S1", "assessment_type": "DEVELOPMENT", "final_scope_id": "PS1", "model_id": "M1", "outcome_id": "O1", "dataset_id": "NA", "item_code": "DEV-D1-SQ1.1", "final_response": "NI", "final_evidence_id": "EP1", "record_type_guard": "SIGNALLING_QUESTION", "final_rationale": "source replay", "adjudication_status": "FROZEN_FINAL_ADJUDICATED"}])
            manifest = recover(canonical, [], out, selected_tables={"tripod", "probast"},
                               required_companions={"tripod_scoring_adjudication.tsv", "probast_record_type.tsv", "probast_scoring_adjudication.tsv"})
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            lookup = {(r["entity_type"], r["entity_id"], r["field_name"]): r["normalized_value"] for r in facts}
            self.assertEqual(lookup[("tripod", "T1", "status")], "PRESENT")
            self.assertEqual(lookup[("probast", "P1", "record_type")], "SIGNALLING_QUESTION")
            self.assertEqual(lookup[("probast", "P1", "response")], "NI")
            self.assertNotEqual(lookup[("probast", "P1", "response")], "PY")
            self.assertEqual(set(manifest["companion_tables_consumed"]), {
                "tripod_scoring_adjudication.tsv", "probast_record_type.tsv", "probast_scoring_adjudication.tsv"
            })
            self.assertTrue(validate(out, "migration")["pass"])

    def test_fake_nr_alias_is_detected_and_recovered(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; out = root / "out"; canonical.mkdir()
            write_tsv(canonical / "performance.tsv", ["performance_id", "study_id", "report_id", "estimate", "auc"],
                      [{"performance_id": "P1", "study_id": "S1", "report_id": "R1", "estimate": "NR", "auc": "0.82"}])
            manifest = recover(canonical, [], out)
            self.assertEqual(manifest["counts"]["fake_nr_aliases"], 1)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            estimate = next(r for r in facts if r["entity_id"] == "P1" and r["field_name"] == "estimate")
            self.assertEqual(estimate["normalized_value"], "0.82")
            self.assertNotEqual(estimate["value_status_code"], "NR_SOURCE")

    def test_field_overlay_preserves_observed_base_against_narrow_missing_final(self):
        key = {"report_id": "R1", "study_id": "S1", "entity_type": "study", "entity_id": "S1", "field_name": "title"}
        base = key | {"raw_value": "Rich title", "normalized_value": "Rich title", "value_status_code": "OBSERVED"}
        final = key | {"raw_value": "", "normalized_value": "", "value_status_code": "NOT_CAPTURED"}
        merged, audit = apply_field_overlay([base], [final], {tuple(key[k] for k in ("report_id", "study_id", "entity_type", "entity_id", "field_name"))})
        self.assertEqual(merged[0]["normalized_value"], "Rich title")
        self.assertEqual(audit[0]["action"], "PRESERVE_BASE_OBSERVED")

    def test_field_overlay_rejects_unscoped_mutation(self):
        key = {"report_id": "R1", "study_id": "S1", "entity_type": "study", "entity_id": "S1", "field_name": "title"}
        base = key | {"raw_value": "A", "normalized_value": "A", "value_status_code": "OBSERVED"}
        final = key | {"raw_value": "B", "normalized_value": "B", "value_status_code": "OBSERVED"}
        with self.assertRaises(ValueError):
            apply_field_overlay([base], [final], set())

    def test_unmapped_nonmissing_source_field_blocks_qa(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; out = root / "out"; canonical.mkdir()
            write_tsv(canonical / "study.tsv", ["study_id", "report_id", "title_raw", "important_unmapped"],
                      [{"study_id": "S1", "report_id": "R1", "title_raw": "Title", "important_unmapped": "must not disappear"}])
            manifest = recover(canonical, [], out)
            self.assertEqual(manifest["counts"]["unmapped_or_unlinked_source_fields"], 1)
            result = validate(out, "migration")
            self.assertFalse(result["pass"])
            self.assertTrue(any("lack semantic mappings" in e for e in result["errors"]))

    def test_orphan_and_duplicate_companions_are_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; canonical.mkdir()
            write_tsv(canonical / "performance.tsv",
                      ["performance_id", "study_id", "report_id", "metric_code"],
                      [{"performance_id": "P1", "study_id": "S1", "report_id": "R1", "metric_code": "AUC"}])
            fields = ["performance_id", "stu", "metric_code", "estimate"]
            write_tsv(canonical / "performance_values.tsv", fields, [
                {"performance_id": "P1", "stu": "S1", "metric_code": "AUC", "estimate": "0.81"},
                {"performance_id": "P1", "stu": "S1", "metric_code": "AUC", "estimate": "0.81"},
                {"performance_id": "P2", "stu": "S1", "metric_code": "AUC", "estimate": "0.75"},
            ])
            out = root / "out"; manifest = recover(canonical, [], out)
            self.assertEqual(manifest["counts"]["entities"]["performance"], 1)
            _, audit = read_tsv(out / "recovery_audit.tsv")
            codes = {r["resolution"] for r in audit}
            self.assertIn("DUPLICATE_COMPANION_KEY", codes)
            self.assertIn("ORPHAN_COMPANION_KEY", codes)
            self.assertFalse(validate(out, "migration")["pass"])

    def test_required_missing_companion_is_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; canonical.mkdir()
            write_tsv(canonical / "performance.tsv",
                      ["performance_id", "study_id", "report_id", "metric_code"],
                      [{"performance_id": "P1", "study_id": "S1", "report_id": "R1", "metric_code": "AUC"}])
            out = root / "out"
            recover(canonical, [], out, required_companions={"performance_values.tsv"})
            _, audit = read_tsv(out / "recovery_audit.tsv")
            self.assertIn("MISSING_COMPANION_TABLE", {r["resolution"] for r in audit})
            self.assertFalse(validate(out, "migration")["pass"])

    def test_branch_companion_without_report_uses_unique_crosswalk(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; b = root / "B"
            canonical.mkdir(); a.mkdir(); b.mkdir()
            write_tsv(canonical / "performance.tsv",
                      ["performance_id", "study_id", "report_id", "metric_code"],
                      [{"performance_id": "PF", "study_id": "S1", "report_id": "R1", "metric_code": "AUC"}])
            xfields = ["report_id", "study_id", "entity_type", "a_entity_id", "b_entity_id",
                       "third_entity_id", "final_entity_id", "mapping_decision"]
            write_tsv(canonical / "semantic_key_crosswalk.tsv", xfields, [{
                "report_id": "R1", "study_id": "S1", "entity_type": "performance",
                "a_entity_id": "PA", "b_entity_id": "PB", "third_entity_id": "NA",
                "final_entity_id": "PF", "mapping_decision": "ONE_TO_ONE"}])
            fields = ["performance_id", "stu", "metric_code", "estimate"]
            write_tsv(a / "performance_values.tsv", fields,
                      [{"performance_id": "PA", "stu": "S1", "metric_code": "AUC", "estimate": "0.88"}])
            write_tsv(b / "performance_values.tsv", fields,
                      [{"performance_id": "PB", "stu": "S1", "metric_code": "AUC", "estimate": "0.88"}])
            out = root / "out"; manifest = recover(canonical, [("A", a), ("B", b)], out)
            self.assertEqual(manifest["counts"]["entities"]["performance"], 1)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            estimate = next(r for r in facts if r["entity_id"] == "PF" and r["field_name"] == "estimate")
            self.assertEqual(estimate["normalized_value"], "0.88")
            self.assertEqual(estimate["resolution_code"], "RECOVERED_A_B_CONSENSUS")

    def test_crosswalk_split_is_not_broadcast(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; a = root / "A"; canonical.mkdir(); a.mkdir()
            write_tsv(canonical / "predictor.tsv",
                      ["predictor_id", "study_id", "report_id", "predictor_raw"], [
                          {"predictor_id": "F1", "study_id": "S1", "report_id": "R1", "predictor_raw": "age 1"},
                          {"predictor_id": "F2", "study_id": "S1", "report_id": "R1", "predictor_raw": "age 2"},
                      ])
            xfields = ["report_id", "study_id", "entity_type", "a_entity_id", "b_entity_id",
                       "third_entity_id", "final_entity_id", "mapping_decision"]
            write_tsv(canonical / "semantic_key_crosswalk.tsv", xfields, [
                {"report_id": "R1", "study_id": "S1", "entity_type": "predictor", "a_entity_id": "A0",
                 "b_entity_id": "NA", "third_entity_id": "NA", "final_entity_id": "F1", "mapping_decision": "SPLIT_TO_FINAL"},
                {"report_id": "R1", "study_id": "S1", "entity_type": "predictor", "a_entity_id": "A0",
                 "b_entity_id": "NA", "third_entity_id": "NA", "final_entity_id": "F2", "mapping_decision": "SPLIT_TO_FINAL"},
            ])
            write_tsv(a / "predictor.tsv", ["predictor_id", "study_id", "report_id", "predictor_name_raw"],
                      [{"predictor_id": "A0", "study_id": "S1", "report_id": "R1", "predictor_name_raw": "age coarse"}])
            out = root / "out"; recover(canonical, [("A", a)], out)
            _, audit = read_tsv(out / "recovery_audit.tsv")
            self.assertIn("CROSSWALK_SPLIT_REQUIRES_ADJUDICATION", {r["resolution"] for r in audit})
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            values = {r["normalized_value"] for r in facts if r["field_name"] == "predictor"}
            self.assertNotIn("age coarse", values)

    def test_recovery_is_deterministic_across_fresh_outputs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; canonical.mkdir()
            write_tsv(canonical / "performance.tsv",
                      ["performance_id", "study_id", "report_id", "metric_code"],
                      [{"performance_id": "P1", "study_id": "S1", "report_id": "R1", "metric_code": "AUC"}])
            write_tsv(canonical / "performance_values.tsv",
                      ["performance_id", "stu", "metric_code", "estimate"],
                      [{"performance_id": "P1", "stu": "S1", "metric_code": "AUC", "estimate": "0.91"}])
            out1 = root / "out1"; out2 = root / "out2"
            recover(canonical, [], out1); recover(canonical, [], out2)
            def digest_tree(path: Path) -> str:
                digest = hashlib.sha256()
                for item in sorted(p for p in path.rglob("*") if p.is_file()):
                    digest.update(str(item.relative_to(path)).encode()); digest.update(item.read_bytes())
                return digest.hexdigest()
            self.assertEqual(digest_tree(out1), digest_tree(out2))

    def test_calibration_metric_companion_projects_to_typed_field(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; canonical.mkdir()
            write_tsv(canonical / "calibration.tsv",
                      ["calibration_id", "study_id", "report_id", "performance_id"],
                      [{"calibration_id": "C1", "study_id": "S1", "report_id": "R1", "performance_id": "P1"}])
            write_tsv(canonical / "calibration_values.tsv",
                      ["calibration_id", "performance_id", "metric_code", "value_raw"],
                      [{"calibration_id": "C1", "performance_id": "P1",
                        "metric_code": "HOSMER_LEMESHOW_P", "value_raw": "0.723; curve close to ideal"}])
            out = root / "out"; recover(canonical, [], out)
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            hl = next(r for r in facts if r["entity_id"] == "C1" and r["field_name"] == "hl_p")
            self.assertEqual(hl["raw_value"], "0.723; curve close to ideal")
            self.assertEqual(hl["normalized_value"], "0.723")
            self.assertEqual(hl["value_status_code"], "OBSERVED")
            self.assertTrue(validate(out, "migration")["pass"])

    def test_staged_table_recovery_inherits_report_from_study_index(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); canonical = root / "canonical"; canonical.mkdir()
            write_tsv(canonical / "study.tsv", ["study_id", "report_id", "title_raw"],
                      [{"study_id": "S1", "report_id": "R1", "title_raw": "Study"}])
            write_tsv(canonical / "threshold.tsv",
                      ["threshold_id", "study_id", "report_id", "sensitivity"],
                      [{"threshold_id": "T1", "study_id": "S1", "report_id": "NR", "sensitivity": "0.8"}])
            out = root / "out"; recover(canonical, [], out, selected_tables={"threshold"})
            _, facts = read_tsv(out / "recovered_field_facts.tsv")
            self.assertTrue(all(r["report_id"] == "R1" and r["study_id"] == "S1" for r in facts))
            self.assertTrue(validate(out, "migration")["pass"])


if __name__ == "__main__":
    unittest.main()
