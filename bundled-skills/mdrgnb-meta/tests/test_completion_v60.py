from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "qa_completion_release_v60.py"
def write_tsv(path: Path, rows: list[dict[str, str]]) -> None:
    headers = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


class CompletionReleaseV60Tests(unittest.TestCase):
    def run_qa(
        self,
        fact: dict[str, str] | list[dict[str, str]],
        evidence: list[dict[str, str]] | None = None,
        manifest: list[dict[str, str]] | None = None,
        structural_rules: list[dict[str, str]] | None = None,
        extra_source_files: list[str] | None = None,
    ) -> tuple[int, dict]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source_root = root / "source_package"
            source_root.mkdir()
            for filename in extra_source_files or []:
                (source_root / filename).write_text(f"unregistered content for {filename}", encoding="utf-8")
            facts_path = root / "facts.tsv"
            entities_path = root / "entities.tsv"
            fact_rows = fact if isinstance(fact, list) else [fact]
            write_tsv(facts_path, fact_rows)
            entity_rows = []
            seen_entities = set()
            for fact_row in fact_rows:
                entity_key = (
                    fact_row.get("report_id", ""),
                    fact_row.get("study_id", ""),
                    fact_row.get("entity_type", ""),
                    fact_row.get("entity_id", ""),
                )
                if entity_key in seen_entities:
                    continue
                seen_entities.add(entity_key)
                entity_rows.append({
                    "report_id": entity_key[0],
                    "study_id": entity_key[1],
                    "entity_type": entity_key[2],
                    "entity_id": entity_key[3],
                    "parent_entity_id": "",
                })
            write_tsv(
                entities_path,
                entity_rows,
            )
            cmd = [
                sys.executable,
                str(SCRIPT),
                "--facts",
                str(facts_path),
                "--entities",
                str(entities_path),
            ]
            if evidence is not None:
                evidence = [dict(row) for row in evidence]
            if manifest is not None:
                manifest = [dict(row) for row in manifest]
                for source in manifest:
                    source_id = source["source_file_id"]
                    source_path = source_root / f"{source_id}.txt"
                    source_path.write_text(f"content for {source_id}", encoding="utf-8")
                    actual_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
                    source.setdefault("source_path", str(source_path))
                    source.setdefault("source_package_root", str(source_root))
                    source.setdefault("inventory_complete_01", "1")
                    source.setdefault("inventory_review_round", "V6.0_INVENTORY_1")
                    source.setdefault("inventory_reviewer", "C_FINAL")
                    if source.get("source_sha256") == "AUTO":
                        source["source_sha256"] = actual_hash
                    for ev in evidence or []:
                        if ev.get("source_file_id") == source_id and ev.get("source_sha256") == "AUTO":
                            ev["source_sha256"] = actual_hash
            if evidence is not None:
                evidence_path = root / "evidence.tsv"
                write_tsv(evidence_path, evidence)
                cmd.extend(["--evidence", str(evidence_path)])
            if manifest is not None:
                manifest_path = root / "source_manifest.tsv"
                write_tsv(manifest_path, manifest)
                cmd.extend(["--source-manifest", str(manifest_path)])
            if structural_rules is not None:
                rules_path = root / "structural_rules.tsv"
                write_tsv(rules_path, structural_rules)
                cmd.extend(["--structural-rules", str(rules_path)])
            env = dict(os.environ)
            env["PYTHONIOENCODING"] = "utf-8"
            cp = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
            return cp.returncode, json.loads(cp.stdout)

    @staticmethod
    def fact(status: str = "NR_SOURCE") -> dict[str, str]:
        return {
            "report_id": "R1",
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "raw_value": "",
            "normalized_value": "",
            "value_type": "number",
            "value_status": status,
            "evidence_id": "E1",
            "derivation_rule": "legacy migration says source not reported",
            "reviewer": "OLD",
            "review_round": "V5_9_2",
            "status_rule_id": "",
        }

    def test_legacy_nr_source_is_rejected(self) -> None:
        code, payload = self.run_qa(self.fact())
        self.assertEqual(code, 1)
        error_codes = {row["code"] for row in payload["errors"]}
        self.assertIn("NR_SOURCE_EVIDENCE_TABLE_REQUIRED", error_codes)

    def test_renewed_search_must_cover_supplement(self) -> None:
        fact = self.fact()
        fact.update({
            "derivation_rule": "Renewed targeted v6.0 review found no reportable value.",
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        })
        scope = {
            "complete_source_package_01": True,
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "searched_source_files": ["SRC_MAIN"],
            "locations_searched": ["Methods", "Tables"],
            "review_round": "V6.0_REVIEW_1",
            "rationale": "Renewed targeted review of the complete source package.",
        }
        evidence = [{
            "evidence_id": "E1",
            "report_id": "R1",
            "source_file_id": "SRC_MAIN",
            "source_sha256": "AUTO",
            "locator": "pp. 1-12",
            "table_figure_section": "Methods, Results, Tables",
            "evidence_span": "No candidate count reported after targeted review.",
            "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
            "search_scope": json.dumps(scope),
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        }]
        manifest = [
            {
                "source_file_id": "SRC_MAIN",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "MAIN_ARTICLE",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
            {
                "source_file_id": "SRC_SUPP",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "SUPPLEMENT",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
        ]
        code, payload = self.run_qa(fact, evidence, manifest)
        self.assertEqual(code, 1)
        self.assertTrue(any(
            row["code"] == "NR_SOURCE_SCOPE_INVALID" and "SRC_SUPP" in row.get("message", "")
            for row in payload["errors"]
        ))

    def test_renewed_complete_source_search_passes(self) -> None:
        fact = self.fact()
        fact.update({
            "evidence_id": "E1|E2",
            "derivation_rule": "Renewed targeted v6.0 review found no reportable value.",
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        })
        scope = {
            "complete_source_package_01": True,
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "searched_source_files": ["SRC_MAIN", "SRC_SUPP"],
            "locations_searched": ["Main: Methods/Results/Tables", "Supplement: all tables"],
            "review_round": "V6.0_REVIEW_1",
            "rationale": "Renewed targeted review of main text and accessible supplement.",
        }
        evidence = [
            {
                "evidence_id": "E1",
                "report_id": "R1",
                "source_file_id": "SRC_MAIN",
                "source_sha256": "AUTO",
                "locator": "main pp. 1-12",
                "table_figure_section": "Methods, Results, all tables",
                "evidence_span": "No candidate count reported after targeted review.",
                "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
                "search_scope": json.dumps(scope),
                "reviewer": "C_FINAL",
                "review_round": "V6.0_REVIEW_1",
            },
            {
                "evidence_id": "E2",
                "report_id": "R1",
                "source_file_id": "SRC_SUPP",
                "source_sha256": "AUTO",
                "locator": "supplement pp. 1-8",
                "table_figure_section": "All supplementary methods and tables",
                "evidence_span": "No candidate count reported after targeted review.",
                "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
                "search_scope": json.dumps(scope),
                "reviewer": "C_FINAL",
                "review_round": "V6.0_REVIEW_1",
            },
        ]
        manifest = [
            {
                "source_file_id": "SRC_MAIN",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "MAIN_ARTICLE",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
            {
                "source_file_id": "SRC_SUPP",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "SUPPLEMENT",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
        ]
        code, payload = self.run_qa(fact, evidence, manifest)
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["pass"])

    def test_canonical_v56_columns_cannot_bypass_nr_gate(self) -> None:
        compact = self.fact()
        canonical = {
            "report_id": compact["report_id"],
            "study_id": compact["study_id"],
            "entity_type": compact["entity_type"],
            "entity_id": compact["entity_id"],
            "field_name": compact["field_code"],
            "raw_value": "",
            "normalized_value": "",
            "value_status_code": "NR_SOURCE",
            "evidence_id": "",
            "status_rationale": "",
            "extractor_id": "OLD",
            "review_round": "V5_9_2",
        }
        code, payload = self.run_qa(canonical)
        self.assertEqual(code, 1)
        self.assertEqual(payload["nr_source_rows"], 1)
        self.assertIn("NR_SOURCE_EVIDENCE_MISSING", {x["code"] for x in payload["errors"]})

    def test_nr_source_requires_fact_rationale(self) -> None:
        fact = self.fact()
        fact["derivation_rule"] = ""
        fact["reviewer"] = "C_FINAL"
        fact["review_round"] = "V6.0_REVIEW_1"
        code, payload = self.run_qa(fact)
        self.assertEqual(code, 1)
        self.assertIn("NR_SOURCE_RATIONALE_MISSING", {x["code"] for x in payload["errors"]})

    def test_canonical_status_rationale_cannot_be_replaced_by_derivation_rule(self) -> None:
        compact = self.fact()
        canonical = {
            "report_id": compact["report_id"],
            "study_id": compact["study_id"],
            "entity_type": compact["entity_type"],
            "entity_id": compact["entity_id"],
            "field_name": compact["field_code"],
            "raw_value": "",
            "normalized_value": "",
            "value_status_code": "NR_SOURCE",
            "evidence_id": "",
            "status_rationale": "",
            "derivation_rule": "Renewed targeted review.",
            "extractor_id": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        }
        code, payload = self.run_qa(canonical)
        self.assertEqual(code, 1)
        self.assertIn(
            "NR_SOURCE_CANONICAL_STATUS_RATIONALE_MISSING",
            {x["code"] for x in payload["errors"]},
        )

    def test_manifest_hash_must_match_real_file(self) -> None:
        fact = self.fact()
        fact.update({
            "derivation_rule": "Renewed targeted v6.0 review found no reportable value.",
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        })
        scope = {
            "complete_source_package_01": True,
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "searched_source_files": ["SRC_MAIN"],
            "locations_searched": ["Main: all methods/results/tables"],
            "review_round": "V6.0_REVIEW_1",
            "rationale": "Renewed targeted review of the complete source package.",
        }
        evidence = [{
            "evidence_id": "E1",
            "report_id": "R1",
            "source_file_id": "SRC_MAIN",
            "source_sha256": "a" * 64,
            "locator": "pp. 1-12",
            "table_figure_section": "All methods/results/tables",
            "evidence_span": "No candidate count reported.",
            "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
            "search_scope": json.dumps(scope),
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        }]
        manifest = [{
            "source_file_id": "SRC_MAIN",
            "report_id": "R1",
            "source_sha256": "a" * 64,
            "source_role": "MAIN_ARTICLE",
            "access_status": "ACCESSIBLE",
            "included_in_complete_search_01": "1",
        }]
        code, payload = self.run_qa(fact, evidence, manifest)
        self.assertEqual(code, 1)
        self.assertIn("NR_SOURCE_SOURCE_FILE_HASH_MISMATCH", {x["code"] for x in payload["errors"]})

    def test_manifest_cannot_omit_unregistered_supplement(self) -> None:
        fact = self.fact()
        fact.update({
            "derivation_rule": "Renewed targeted v6.0 review found no reportable value.",
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        })
        scope = {
            "complete_source_package_01": True,
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "searched_source_files": ["SRC_MAIN"],
            "locations_searched": ["Main: all methods/results/tables"],
            "review_round": "V6.0_REVIEW_1",
            "rationale": "Renewed targeted review of the complete source package.",
        }
        evidence = [{
            "evidence_id": "E1",
            "report_id": "R1",
            "source_file_id": "SRC_MAIN",
            "source_sha256": "AUTO",
            "locator": "pp. 1-12",
            "table_figure_section": "All methods/results/tables",
            "evidence_span": "No candidate count reported.",
            "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
            "search_scope": json.dumps(scope),
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        }]
        manifest = [{
            "source_file_id": "SRC_MAIN",
            "report_id": "R1",
            "source_sha256": "AUTO",
            "source_role": "MAIN_ARTICLE",
            "access_status": "ACCESSIBLE",
            "included_in_complete_search_01": "1",
        }]
        code, payload = self.run_qa(
            fact,
            evidence,
            manifest,
            extra_source_files=["supplement.pdf"],
        )
        self.assertEqual(code, 1)
        self.assertIn("SOURCE_PACKAGE_FILE_UNREGISTERED", {x["code"] for x in payload["errors"]})

    def test_evidence_report_must_match_fact(self) -> None:
        fact = self.fact()
        fact.update({
            "derivation_rule": "Renewed targeted v6.0 review found no reportable value.",
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        })
        scope = {
            "complete_source_package_01": True,
            "study_id": "S1",
            "entity_type": "MODEL",
            "entity_id": "M1",
            "field_code": "candidate_predictor_n",
            "searched_source_files": ["SRC_MAIN"],
            "locations_searched": ["Main all sections"],
            "review_round": "V6.0_REVIEW_1",
            "rationale": "Renewed targeted review.",
        }
        evidence = [{
            "evidence_id": "E1",
            "report_id": "R_WRONG",
            "source_file_id": "SRC_MAIN",
            "source_sha256": "AUTO",
            "locator": "pp. 1-12",
            "table_figure_section": "All sections",
            "evidence_span": "No value reported.",
            "extraction_method": "RENEWED_TARGETED_SOURCE_REVIEW",
            "search_scope": json.dumps(scope),
            "reviewer": "C_FINAL",
            "review_round": "V6.0_REVIEW_1",
        }]
        manifest = [{
            "source_file_id": "SRC_MAIN",
            "report_id": "R1",
            "source_sha256": "AUTO",
            "source_role": "MAIN_ARTICLE",
            "access_status": "ACCESSIBLE",
            "included_in_complete_search_01": "1",
        }]
        code, payload = self.run_qa(fact, evidence, manifest)
        self.assertEqual(code, 1)
        self.assertIn("NR_SOURCE_EVIDENCE_REPORT_MISMATCH", {x["code"] for x in payload["errors"]})

    def test_na_structural_rule_condition_is_evaluated(self) -> None:
        fact = self.fact("NA_STRUCTURAL")
        fact.update({
            "evidence_id": "",
            "derivation_rule": "Deterministic rule.",
            "status_rule_id": "RULE1",
            "context_json": json.dumps({"algorithm_superclass": "MACHINE_LEARNING"}),
        })
        rules = [{
            "rule_id": "RULE1",
            "entity_type": "MODEL",
            "field_code": "candidate_predictor_n",
            "condition_field": "algorithm_superclass",
            "condition_operator": "EQ",
            "condition_value": "TRADITIONAL_STATISTICAL",
            "active_01": "1",
        }]
        code, payload = self.run_qa(fact, structural_rules=rules)
        self.assertEqual(code, 1)
        self.assertIn("NA_STRUCTURAL_RULE_CONDITION_FAILED", {x["code"] for x in payload["errors"]})
        self.assertIn("STRUCTURAL_RULE_TABLE_NOT_CANONICAL", {x["code"] for x in payload["errors"]})

    def test_approved_bundled_structural_rule_passes(self) -> None:
        fact = self.fact("NA_STRUCTURAL")
        fact.update({
            "field_code": "hyperparameter_tuning",
            "evidence_id": "",
            "derivation_rule": "Approved deterministic v6.0 structural rule.",
            "status_rule_id": "RULE_V60_EXPERT_FIXED_HYPERPARAMETER",
            "context_json": json.dumps({"algorithm_superclass": "EXPERT_OR_HEURISTIC_RULE"}),
        })
        code, payload = self.run_qa(fact)
        self.assertEqual(code, 0, payload)
        self.assertTrue(payload["pass"])

    def test_duplicate_source_file_id_is_rejected(self) -> None:
        fact = self.fact()
        manifest = [
            {
                "source_file_id": "DUP",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "MAIN_ARTICLE",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
            {
                "source_file_id": "DUP",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "SUPPLEMENT",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
        ]
        code, payload = self.run_qa(fact, manifest=manifest)
        self.assertEqual(code, 1)
        self.assertIn("SOURCE_FILE_ID_DUPLICATE", {x["code"] for x in payload["errors"]})

    def test_accessible_supplement_cannot_be_excluded(self) -> None:
        fact = self.fact()
        manifest = [
            {
                "source_file_id": "SRC_MAIN",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "MAIN_ARTICLE",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
            {
                "source_file_id": "SRC_SUPP",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "SUPPLEMENT",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "0",
            },
        ]
        code, payload = self.run_qa(fact, manifest=manifest)
        self.assertEqual(code, 1)
        self.assertIn("ACCESSIBLE_SOURCE_EXCLUDED", {x["code"] for x in payload["errors"]})

    def test_cross_report_facts_do_not_collapse(self) -> None:
        first = self.fact("OBSERVED")
        first.update({
            "raw_value": "1",
            "normalized_value": "1",
            "evidence_id": "",
            "derivation_rule": "Observed test value.",
        })
        second = dict(first)
        second["report_id"] = "R2"
        second["raw_value"] = "2"
        second["normalized_value"] = "2"
        code, payload = self.run_qa([first, second])
        self.assertEqual(code, 0, payload)
        self.assertEqual(payload["effective_field_facts"], 2)

    def test_duplicate_full_fact_key_requires_unique_current_marker(self) -> None:
        first = self.fact("OBSERVED")
        first.update({
            "raw_value": "1",
            "normalized_value": "1",
            "evidence_id": "",
            "derivation_rule": "Observed test value.",
        })
        second = dict(first)
        second["raw_value"] = "2"
        second["normalized_value"] = "2"
        code, payload = self.run_qa([first, second])
        self.assertEqual(code, 1)
        self.assertIn("DUPLICATE_FACT_NO_UNIQUE_CURRENT", {x["code"] for x in payload["errors"]})

    def test_source_role_other_cannot_exclude_supplement(self) -> None:
        fact = self.fact()
        manifest = [
            {
                "source_file_id": "SRC_MAIN",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "MAIN_ARTICLE",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "1",
            },
            {
                "source_file_id": "SUPPLEMENT_FILE",
                "report_id": "R1",
                "source_sha256": "AUTO",
                "source_role": "OTHER",
                "access_status": "ACCESSIBLE",
                "included_in_complete_search_01": "0",
                "exclusion_rule_id": "FREE_TEXT",
                "exclusion_rationale": "caller says irrelevant",
                "exclusion_reviewer": "CALLER",
                "exclusion_review_round": "V6.0",
            },
        ]
        code, payload = self.run_qa(fact, manifest=manifest)
        self.assertEqual(code, 1)
        codes = {x["code"] for x in payload["errors"]}
        self.assertIn("ACCESSIBLE_SOURCE_EXCLUDED", codes)
        self.assertIn("SOURCE_ROLE_FILENAME_MISMATCH", codes)

    def test_invalid_and_open_statuses_block_release(self) -> None:
        for status, expected in (
            ("NR", "INVALID_VALUE_STATUS"),
            ("NOT_CAPTURED", "RELEASE_BLOCKING_VALUE_STATUS"),
            ("PENDING_REVIEW", "RELEASE_BLOCKING_VALUE_STATUS"),
            ("CONFLICT", "RELEASE_BLOCKING_VALUE_STATUS"),
        ):
            with self.subTest(status=status):
                fact = self.fact(status)
                fact["evidence_id"] = ""
                code, payload = self.run_qa(fact)
                self.assertEqual(code, 1)
                self.assertIn(expected, {x["code"] for x in payload["errors"]})

    def test_na_structural_requires_rule(self) -> None:
        fact = self.fact("NA_STRUCTURAL")
        fact["evidence_id"] = ""
        fact["derivation_rule"] = "not applicable"
        code, payload = self.run_qa(fact)
        self.assertEqual(code, 1)
        self.assertIn("NA_STRUCTURAL_RULE_MISSING", {x["code"] for x in payload["errors"]})


if __name__ == "__main__":
    unittest.main()
