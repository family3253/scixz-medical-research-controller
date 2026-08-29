from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "reference_audit.py"
SPEC = importlib.util.spec_from_file_location("reference_audit", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


MATCHED = {
    "ok": True,
    "title": "Redox control of antitumor immunity",
    "first_author": "Smith",
    "year": "2025",
    "container_title": "Cancer Research",
    "type": "journal-article",
    "publisher": "Example Publisher",
}


def bib_entry(
    title: str = "Redox control of antitumor immunity",
    author: str = "Smith, Jane and Doe, John",
    year: str = "2025",
    journal: str = "Cancer Research",
) -> str:
    return f"""@article{{smith2025,
  title = {{{title}}},
  author = {{{author}}},
  year = {{{year}}},
  journal = {{{journal}}},
  doi = {{10.1234/example.2025.1}}
}}"""


class ReferenceAuditTests(unittest.TestCase):
    def test_clean_doi_removes_trailing_punctuation(self) -> None:
        self.assertEqual(
            audit.extract_dois("doi:10.1234/example.2025.1)."),
            ["10.1234/example.2025.1"],
        )

    def test_matching_bib_metadata_is_reported(self) -> None:
        rows = audit.audit_text(bib_entry(), lookup=lambda _doi: MATCHED)
        self.assertEqual(rows[0]["status"], "metadata_match")
        self.assertEqual(
            rows[0]["compared_fields"], "title,first_author,year,journal"
        )

    def test_year_and_title_mismatch_are_reported(self) -> None:
        rows = audit.audit_text(
            bib_entry(title="Unrelated title", year="2023"),
            lookup=lambda _doi: MATCHED,
        )
        self.assertEqual(rows[0]["status"], "metadata_mismatch")
        self.assertIn("title", rows[0]["mismatch_fields"])
        self.assertIn("year", rows[0]["mismatch_fields"])

    def test_resolved_doi_without_parseable_metadata_is_not_full_match(self) -> None:
        rows = audit.audit_text(
            "Reference with DOI 10.1234/example.2025.1.",
            lookup=lambda _doi: MATCHED,
        )
        self.assertEqual(rows[0]["status"], "doi_resolves")

    def test_duplicate_doi_is_explicit(self) -> None:
        text = bib_entry() + "\n" + bib_entry()
        rows = audit.audit_text(text, lookup=lambda _doi: MATCHED)
        self.assertEqual(rows[0]["duplicate"], "no")
        self.assertEqual(rows[1]["duplicate"], "yes")

    def test_unresolved_doi_is_not_verified(self) -> None:
        rows = audit.audit_text(
            bib_entry(), lookup=lambda _doi: {"ok": False, "error": "HTTP 404"}
        )
        self.assertEqual(rows[0]["status"], "unresolved")


if __name__ == "__main__":
    unittest.main()
