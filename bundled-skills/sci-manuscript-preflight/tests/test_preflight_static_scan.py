from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "preflight_static_scan.py"
SPEC = importlib.util.spec_from_file_location("preflight_static_scan", MODULE_PATH)
assert SPEC and SPEC.loader
scanner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scanner)


class StaticScanTests(unittest.TestCase):
    def run_cli(self, target: Path, out: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(MODULE_PATH), str(target), "--out", str(out)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_missing_target_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "scan.tsv"
            result = self.run_cli(root / "missing", out)
            report = out.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("input_not_found", report)

    def test_empty_directory_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            out = root / "scan.tsv"
            result = self.run_cli(root, out)
            report = out.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertIn("no_supported_files", report)

    def test_markdown_headings_are_not_artifacts_in_markdown_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manuscript = root / "manuscript.md"
            manuscript.write_text("# Title\n\n## Methods\n\nA normal paragraph.\n", encoding="utf-8")
            out = root / "scan.tsv"
            result = self.run_cli(manuscript, out)
            report = out.read_text(encoding="utf-8")
        self.assertEqual(result.returncode, 0)
        self.assertNotIn("markdown_artifact", report)

    def test_generic_prompt_term_is_not_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.md"
            path.write_text("The survey evaluated prompt design.", encoding="utf-8")
            findings = list(scanner.scan_file(path))
        self.assertFalse(any(item["severity"] == "BLOCKER" for item in findings))

    def test_explicit_ai_residue_is_a_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.md"
            path.write_text("As an AI language model, I cannot comply.", encoding="utf-8")
            findings = list(scanner.scan_file(path))
        self.assertTrue(any(item["rule"] == "explicit_ai_residue" for item in findings))


if __name__ == "__main__":
    unittest.main()
