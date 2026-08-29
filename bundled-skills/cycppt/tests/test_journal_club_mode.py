from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_LOGIC_VALIDATOR = ROOT / "scripts" / "validate-paper-logic.py"
PLAN_VALIDATOR = ROOT / "scripts" / "validate-journal-club-plan.py"
ROUTE_CLASSIFIER = ROOT / "scripts" / "classify-task-route.py"
AUDIT_EXPORTER = ROOT / "scripts" / "export-journal-club-audit.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_json(directory: Path, name: str, payload: dict) -> Path:
    path = directory / name
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def good_inventory() -> dict:
    return {
        "schema_version": 2,
        "usable_assets": [
            {
                "asset_id": "figure2_panel_b",
                "figure_id": "Figure 2",
                "panel_id": "B",
                "source_section": "main_text",
                "source_pdf": "paper.pdf",
                "source_page": 5,
                "source_region": {"x0": 10, "y0": 20, "x1": 100, "y1": 160, "unit": "pdf_points"},
                "caption_summary": "Treatment reduced the primary endpoint.",
                "supported_claim": "claim_primary",
                "visual_type": "figure",
                "kind": "figure",
                "include_decision": "include",
                "reason": "Directly tests the central hypothesis and remains readable.",
                "selection_score": {
                    "centrality_to_claim": 3,
                    "closes_key_gap": 3,
                    "method_explanatory_value": 1,
                    "visual_readability": 2,
                    "redundancy": 0,
                    "excessive_detail": 0,
                    "include_score": 9,
                },
                "evidence_mode": "original",
                "render_policy": "original_preferred",
                "output_path": "figures/figure2_panel_b.png",
                "citation": "Example et al., Figure 2B, p.5",
            }
        ],
    }


def good_logic() -> dict:
    return {
        "schema_version": 1,
        "mode": "journal_club",
        "bibliographic_identity": {
            "title": "Example Trial",
            "journal": "Example Journal",
            "year": "2026",
            "citation": "Example et al. Example Journal. 2026.",
            "stable_identifier": "doi:10.0000/example",
        },
        "author_team": {
            "first_authors": ["A. Example"],
            "corresponding_authors": ["B. Example"],
            "affiliations": ["Example Hospital"],
            "collaboration_structure": "Clinical and statistical collaboration.",
            "why_team_matters": "The team links recruitment with endpoint analysis.",
            "source_anchors": ["paper byline", "author contributions"],
        },
        "central_problem": "The optimal intervention is uncertain.",
        "knowledge_gap": "Prior evidence did not resolve the primary endpoint.",
        "hypothesis_or_claim": "The intervention improves the endpoint.",
        "system_and_data": "A prospective clinical cohort.",
        "study_design": "A controlled comparative study.",
        "evidence_chain": [
            {
                "claim_id": "claim_primary",
                "claim": "The intervention reduced the primary endpoint.",
                "experiment_or_analysis": "Adjusted between-group comparison.",
                "evidence_refs": ["figure2_panel_b"],
                "interpretation": "The adjusted difference favored intervention.",
                "caveat": "The study was performed at one center.",
            }
        ],
        "final_conclusion": "The intervention is associated with a better endpoint.",
        "scope_boundary": "The study does not establish multicenter generalizability.",
        "content_fit_audit": {
            "target_slide_count": 6,
            "recommended_min": 6,
            "recommended_max": 8,
            "status": "fit",
            "rationale": "One central claim fits one result slide without panel compression.",
        },
    }


def base_slide(number: int, role: str, title: str) -> dict:
    return {
        "slide_id": f"slide{number:02d}",
        "slide_number": number,
        "role": role,
        "title": title,
        "core_message": title,
        "assets": {"required": []},
        "references": ["Example et al. 2026"],
        "speaker_notes_zh": "说明本页内容与证据边界。",
    }


def good_plan() -> dict:
    slides = [
        base_slide(1, "title", "该研究检验一项关键干预"),
        base_slide(2, "author_team", "临床与统计协作支撑研究设计"),
        base_slide(3, "background", "现有证据仍未解决主要终点"),
        base_slide(4, "methods", "对照设计直接检验核心假设"),
        base_slide(5, "results", "干预降低了主要终点"),
        base_slide(6, "discussion", "结果支持疗效信号但外推仍有限"),
    ]
    slides[4].update(
        {
            "claim_id": "claim_primary",
            "assets": {"required": [{"asset_id": "figure2_panel_b", "evidence_mode": "original"}]},
            "interpretation": {
                "how_to_read": "先比较两组点估计，再查看置信区间。",
                "what_it_proves": "组间差异支持核心疗效主张。",
                "caveat": "单中心设计限制外推。",
            },
        }
    )
    return {
        "deck": {"authoring_mode": "JOURNAL_CLUB", "total_slides": 6},
        "journal_club": {
            "strengths": ["设计直接对应研究问题"],
            "limitations": ["单中心"],
            "scope_boundary": "不能证明多中心普适性。",
            "follow_up_experiments": ["开展多中心外部验证"],
            "discussion_questions": ["该效应能否外推？", "下一步应优先验证哪个亚组？"],
        },
        "slides": slides,
    }


class PaperLogicValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module("validate_paper_logic", PAPER_LOGIC_VALIDATOR)

    def test_complete_logic_and_panel_ledger_pass(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            logic = write_json(directory, "paper_logic.json", good_logic())
            inventory = write_json(directory, "figure_inventory.json", good_inventory())
            payload = self.validator.validate(logic, inventory)
            self.assertTrue(payload["passed"], payload["errors"])

    def test_missing_scope_boundary_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            data = good_logic()
            data["scope_boundary"] = ""
            logic = write_json(directory, "paper_logic.json", data)
            inventory = write_json(directory, "figure_inventory.json", good_inventory())
            payload = self.validator.validate(logic, inventory)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("scope_boundary" in error for error in payload["errors"]))

    def test_supplemental_evidence_requires_justification(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            data = good_inventory()
            data["usable_assets"][0]["source_section"] = "supplement"
            logic = write_json(directory, "paper_logic.json", good_logic())
            inventory = write_json(directory, "figure_inventory.json", data)
            payload = self.validator.validate(logic, inventory)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("exception_justification" in error for error in payload["errors"]))


class JournalClubPlanValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.validator = load_module("validate_journal_club_plan", PLAN_VALIDATOR)

    def validate_payload(self, directory: Path, plan: dict):
        return self.validator.validate(
            write_json(directory, "ppt_plan.json", plan),
            write_json(directory, "paper_logic.json", good_logic()),
            write_json(directory, "figure_inventory.json", good_inventory()),
        )

    def test_claim_driven_plan_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            payload = self.validate_payload(Path(raw), good_plan())
            self.assertTrue(payload["passed"], payload["errors"])

    def test_generic_result_title_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            plan = good_plan()
            plan["slides"][4]["title"] = "主要结果"
            payload = self.validate_payload(Path(raw), plan)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("claim-driven result title" in error for error in payload["errors"]))

    def test_result_must_explain_how_to_read_and_what_it_proves(self):
        with tempfile.TemporaryDirectory() as raw:
            plan = good_plan()
            plan["slides"][4]["interpretation"]["how_to_read"] = ""
            plan["slides"][4]["interpretation"]["what_it_proves"] = ""
            payload = self.validate_payload(Path(raw), plan)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("how_to_read" in error for error in payload["errors"]))
            self.assertTrue(any("what_it_proves" in error for error in payload["errors"]))

    def test_discussion_requires_two_to_four_questions(self):
        with tempfile.TemporaryDirectory() as raw:
            plan = good_plan()
            plan["journal_club"]["discussion_questions"] = ["只有一个问题？"]
            payload = self.validate_payload(Path(raw), plan)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("2-4" in error for error in payload["errors"]))


class JournalClubRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.classifier = load_module("classify_task_route", ROUTE_CLASSIFIER)

    def test_literature_presentation_activates_journal_club(self):
        payload = self.classifier.classify(
            "请根据这篇论文制作文献汇报 PPT",
            "title authors abstract methods results references",
            ["paper.pdf"],
        )
        self.assertEqual(payload["task_route"], "FULL_AUTHORING_FROM_SOURCE")
        self.assertEqual(payload["authoring_mode"], "JOURNAL_CLUB")

    def test_guideline_summary_remains_general_medical(self):
        payload = self.classifier.classify(
            "根据指南制作临床培训 PPT",
            "clinical guideline references",
            ["guideline.pdf"],
        )
        self.assertEqual(payload["task_route"], "FULL_AUTHORING_FROM_SOURCE")
        self.assertEqual(payload["authoring_mode"], "GENERAL_MEDICAL")


class JournalClubAuditExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exporter = load_module("export_journal_club_audit", AUDIT_EXPORTER)

    def test_exports_outline_and_panel_ledger(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            outline = directory / "reports" / "deck_outline.md"
            ledger = directory / "reports" / "figure_ledger.csv"
            payload = self.exporter.export(
                write_json(directory, "ppt_plan.json", good_plan()),
                write_json(directory, "figure_inventory.json", good_inventory()),
                outline,
                ledger,
            )
            self.assertEqual(payload["slide_count"], 6)
            self.assertIn("干预降低了主要终点", outline.read_text(encoding="utf-8"))
            self.assertIn("What it proves", outline.read_text(encoding="utf-8"))
            self.assertIn("figure2_panel_b", ledger.read_text(encoding="utf-8-sig"))


if __name__ == "__main__":
    unittest.main()
