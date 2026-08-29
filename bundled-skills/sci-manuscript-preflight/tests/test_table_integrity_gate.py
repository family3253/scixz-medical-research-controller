from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "table_integrity_gate.py"
SPEC = importlib.util.spec_from_file_location("table_integrity_gate", MODULE_PATH)
assert SPEC and SPEC.loader
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def base_scan() -> dict:
    return {
        "tool": "paperconan",
        "tool_version": "0.8.0",
        "profile": "review",
        "n_files": 2,
        "scan_errors": [],
        "scan_stats": {
            "files": [{"file": "a.csv"}, {"file": "b.csv"}],
            "sheets": [
                {"file": "a.csv", "sheet": "a"},
                {"file": "b.csv", "sheet": "b"},
            ],
        },
        "relations_blocks": [],
        "cross_sheet_findings": [],
        "digit_distribution": [],
    }


class TableIntegrityGateTests(unittest.TestCase):
    def test_scan_error_is_blocker(self) -> None:
        scan = base_scan()
        scan["scan_errors"] = [{"file": "legacy.xls", "error": "could not parse"}]
        self.assertEqual(gate.summarize_scan(scan)["decision"], "BLOCKER")

    def test_unsupported_schema_version_fails_closed(self) -> None:
        scan = base_scan()
        scan["tool_version"] = "0.9.0"
        with self.assertRaises(gate.ScanContractError):
            gate.summarize_scan(scan)

    def test_missing_schema_key_fails_closed(self) -> None:
        scan = base_scan()
        del scan["scan_stats"]
        with self.assertRaises(gate.ScanContractError):
            gate.summarize_scan(scan)

    def test_manifest_file_mismatch_is_blocker(self) -> None:
        summary = gate.summarize_scan(base_scan(), ["a.csv", "missing.xlsx"])
        self.assertEqual(summary["decision"], "BLOCKER")
        self.assertEqual(summary["coverage"]["missing_manifest_files"], ["missing.xlsx"])

    def test_sheet_parse_failure_is_blocker(self) -> None:
        scan = base_scan()
        scan["scan_stats"]["sheets"][0]["oversized"] = True
        self.assertEqual(gate.summarize_scan(scan)["decision"], "BLOCKER")

    def test_file_without_parsed_sheets_is_blocker(self) -> None:
        scan = base_scan()
        scan["scan_stats"]["files"][0]["n_sheets"] = 0
        self.assertEqual(gate.summarize_scan(scan)["decision"], "BLOCKER")

    def test_kept_high_cross_sheet_signal_requires_review(self) -> None:
        scan = base_scan()
        scan["cross_sheet_findings"] = [{
            "kind": "constant_offset",
            "severity": "high",
            "profile_action": "kept",
            "file_a": "fig2.xlsx",
            "file_b": "fig5.xlsx",
            "sheet_a": "Fig2B",
            "sheet_b": "Fig5D",
            "rule": "B = A + 2.13 across 12 rows",
            "n": 12,
            "examples": [{"a": 1.2, "b": 3.33}],
        }]
        summary = gate.summarize_scan(scan)
        self.assertEqual(summary["decision"], "REVIEW_REQUIRED")
        finding = summary["findings"][0]
        self.assertEqual(finding["file"], "fig2.xlsx <-> fig5.xlsx")
        self.assertEqual(finding["sheet"], "Fig2B <-> Fig5D")
        self.assertIn("2.13", finding["rule"])

    def test_demoted_unit_conversion_needs_manual_confirmation(self) -> None:
        scan = base_scan()
        scan["relations_blocks"] = [{
            "file": "source.xlsx",
            "sheet": "Table1",
            "block": {"rows": "2-11", "cols": "B-C"},
            "relations": [{
                "kind": "constant_ratio",
                "severity": "low",
                "profile_action": "demoted",
                "rule": "ng = ug * 1000",
                "n": 10,
                "likely_benign": "unit conversion",
                "false_positive_context": ["derived_or_unit_conversion"],
            }],
        }]
        summary = gate.summarize_scan(scan)
        self.assertEqual(summary["decision"], "MANUAL_REVIEW")
        self.assertEqual(summary["profile_action_counts"], {"demoted": 1})

    def test_no_signal_is_only_pass_candidate(self) -> None:
        summary = gate.summarize_scan(base_scan())
        self.assertEqual(summary["decision"], "PASS_CANDIDATE")
        self.assertIn("named author sign-off", summary["final_pass_requires"])

    def test_source_manifest_uses_sha256(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "table.csv").write_text("sample,value\na,1\n", encoding="utf-8")
            (root / "notes.txt").write_text("ignored", encoding="utf-8")
            manifest = gate.build_source_manifest(root)
        self.assertEqual(len(manifest), 1)
        self.assertEqual(manifest[0]["path"], "table.csv")
        self.assertEqual(len(manifest[0]["sha256"]), 64)

    def test_cli_interprets_existing_scan_and_writes_gate_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            scan_json = root / "scan.json"
            out = root / "gate"
            scan_json.write_text(json.dumps(base_scan()), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--scan-json",
                    str(scan_json),
                    "--out",
                    str(out),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS_CANDIDATE", result.stdout)
            self.assertTrue((out / "gate.json").exists())
            self.assertTrue((out / "findings.tsv").exists())
            self.assertTrue((out / "gate_report.md").exists())


if __name__ == "__main__":
    unittest.main()
