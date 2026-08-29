from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESOLVER = ROOT / "scripts" / "resolve-external-ppt-template.py"
SHARED_MANIFEST = Path.home() / ".cache" / "yixueAIganhuo-PPT" / "external_ppt_page_library" / "manifest.json"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("external_ppt_page_resolver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ExternalPageLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = load_module(RESOLVER)

    def test_shared_catalog_has_page_level_records_and_previews(self):
        self.assertTrue(SHARED_MANIFEST.exists(), SHARED_MANIFEST)
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["summary"]["template_count"], 172)
        self.assertEqual(manifest["summary"]["page_count"], 5006)
        self.assertEqual(len(manifest["pages"]), 5006)
        self.assertGreater(manifest["summary"]["role_counts"]["timeline"], 0)
        self.assertGreater(manifest["summary"]["placeholder_risk_count"], 0)
        sample = manifest["pages"][0]
        self.assertIn("page_id", sample)
        self.assertIn("source_slide", sample)
        self.assertTrue((SHARED_MANIFEST.parent / sample["preview"]).exists())

    def test_search_prefers_requested_role_and_layout(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        results = self.resolver.search_pages(manifest, role="methods", layout="text_plus_visual", limit=5)
        self.assertTrue(results)
        self.assertEqual(results[0]["role"], "methods")
        self.assertIn("text_plus_visual", results[0]["layout_tags"])

    def test_timeline_pages_are_searchable_as_gantt_layouts(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        results = self.resolver.search_pages(manifest, role="timeline", layout="gantt", limit=5)
        self.assertTrue(results)
        self.assertEqual(results[0]["role"], "timeline")
        self.assertIn("gantt", results[0]["layout_tags"])

    def test_exact_page_binding_records_source_page(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        page = manifest["pages"][0]
        plan = {"deck": {"title": "demo"}, "slides": [{"slide_id": "slide01", "slide_number": 1}]}
        updated = self.resolver.bind_exact(plan, "slide01", page, SHARED_MANIFEST, "001")
        binding = updated["slides"][0]["template_binding"]
        self.assertEqual(binding["external_page_id"], page["page_id"])
        self.assertEqual(binding["source_slide"], page["source_slide"])
        self.assertTrue(binding["reference_image"].endswith(page["preview"].replace("/", "\\")))
        self.assertEqual(binding["template_selection_mode"], "explicit")
        self.assertTrue(binding["template_locked"])

    def test_auto_bind_can_choose_different_pages_per_slide(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        plan = {
            "deck": {"title": "demo"},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "role": "title", "layout": {"structure": "cover"}},
                {"slide_id": "slide02", "slide_number": 2, "role": "methods", "layout": {"structure": "two_column"}},
                {"slide_id": "slide03", "slide_number": 3, "role": "closing", "layout": {"structure": "ending"}},
            ],
        }
        updated, selections = self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [])
        self.assertEqual(len(selections), 3)
        ids = [slide["template_binding"]["external_page_id"] for slide in updated["slides"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(ids))
        self.assertTrue(all(slide["template_binding"]["template_selection_mode"] == "automatic" for slide in updated["slides"]))
        families = {slide["template_binding"]["external_template_id"] for slide in updated["slides"]}
        self.assertEqual(len(families), 1)
        self.assertEqual(updated["deck"]["master_template_id"], next(iter(families)))
        self.assertEqual(updated["deck"]["template_consistency_policy"], "single_template_family")
        self.assertEqual(updated["deck"]["template_mode"], "per_page_within_master_family")
        self.assertTrue(updated["deck"]["deck_chrome_locked"])
        self.assertEqual(updated["deck"]["navigation_policy"], "none")

    def test_default_navigation_policy_excludes_navigation_demo_pages(self):
        manifest = {
            "library_id": "test",
            "pages": [
                {"page_id": "a-nav", "template_id": "family-a", "template_name": "A", "source_slide": 1, "title": "横排导航栏", "role": "methods", "layout_tags": ["two_column"], "source_aspect": "16:9", "preview": "a-nav.png"},
                {"page_id": "a-clean", "template_id": "family-a", "template_name": "A", "source_slide": 2, "title": "研究方法", "role": "methods", "layout_tags": ["two_column"], "source_aspect": "16:9", "preview": "a-clean.png"},
            ],
        }
        results = self.resolver.search_pages(manifest, role="methods", layout="two_column")
        self.assertEqual([item["page_id"] for item in results], ["a-clean"])

    def test_cross_family_selection_requires_explicit_opt_in(self):
        manifest = {
            "library_id": "test",
            "pages": [
                {"page_id": "a-cover", "template_id": "family-a", "template_name": "A", "source_template": "A.pptx", "source_slide": 1, "title": "封面", "role": "cover", "layout_tags": ["cover"], "source_aspect": "16:9", "preview": "a-cover.png"},
                {"page_id": "a-content", "template_id": "family-a", "template_name": "A", "source_template": "A.pptx", "source_slide": 2, "title": "正文", "role": "content", "layout_tags": ["two_column"], "source_aspect": "16:9", "preview": "a-content.png"},
                {"page_id": "b-methods", "template_id": "family-b", "template_name": "B", "source_template": "B.pptx", "source_slide": 1, "title": "研究方法", "role": "methods", "layout_tags": ["two_column"], "source_aspect": "16:9", "preview": "b-methods.png"},
            ],
        }
        plan = {
            "deck": {},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "role": "cover", "layout": {"structure": "cover"}},
                {"slide_id": "slide02", "slide_number": 2, "role": "methods", "layout": {"structure": "two_column"}},
            ],
        }
        coherent, _ = self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [])
        self.assertEqual(
            {slide["template_binding"]["external_template_id"] for slide in coherent["slides"]},
            {"family-a"},
        )
        cross_family, _ = self.resolver.auto_bind(
            plan, manifest, SHARED_MANIFEST, "001", "", [], allow_cross_family=True
        )
        self.assertEqual(
            {slide["template_binding"]["external_template_id"] for slide in cross_family["slides"]},
            {"family-a", "family-b"},
        )
        self.assertEqual(cross_family["deck"]["template_consistency_policy"], "cross_family_allowed")

    def test_conflicting_existing_families_fail_without_override(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        plan = {
            "deck": {},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "template_binding": {"external_template_id": "family-a"}},
                {"slide_id": "slide02", "slide_number": 2, "template_binding": {"external_template_id": "family-b"}},
            ],
        }
        with self.assertRaisesRegex(ValueError, "multiple external template families"):
            self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [])

    def test_auto_bind_preserves_campus_locked_hospital_pages(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        locked = {"campus_locked": True, "organization_template_id": "srrsh-report-2024-v9", "reference_image": "official-cover.png"}
        plan = {
            "deck": {"title": "hospital demo"},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "role": "title", "template_binding": locked},
                {"slide_id": "slide02", "slide_number": 2, "role": "methods"},
            ],
        }
        updated, selections = self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [])
        self.assertEqual(updated["slides"][0]["template_binding"], locked)
        self.assertEqual(selections[0]["mode"], "preserved_locked_binding")
        self.assertIn("external_page_id", updated["slides"][1]["template_binding"])

    def test_auto_bind_preserves_existing_explicit_template_binding(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        explicit = {
            "mode": "page",
            "reference_image": "user-selected-template.png",
            "style_selector": "003",
            "template_selection_mode": "explicit",
            "template_locked": True,
        }
        plan = {
            "deck": {"title": "demo"},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "role": "title", "template_binding": explicit},
                {"slide_id": "slide02", "slide_number": 2, "role": "results"},
            ],
        }
        updated, selections = self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [])
        self.assertEqual(updated["slides"][0]["template_binding"], explicit)
        self.assertEqual(selections[0]["mode"], "preserved_existing_binding")
        self.assertEqual(updated["slides"][1]["template_binding"]["template_selection_mode"], "automatic")

    def test_replace_existing_requires_explicit_override_flag(self):
        manifest = json.loads(SHARED_MANIFEST.read_text(encoding="utf-8"))
        original = {"mode": "page", "reference_image": "old-template.png"}
        plan = {"deck": {}, "slides": [{"slide_id": "slide01", "slide_number": 1, "role": "title", "template_binding": original}]}
        updated, _ = self.resolver.auto_bind(plan, manifest, SHARED_MANIFEST, "001", "", [], replace_existing=True)
        binding = updated["slides"][0]["template_binding"]
        self.assertNotEqual(binding, original)
        self.assertEqual(binding["template_selection_mode"], "automatic")


if __name__ == "__main__":
    unittest.main()
