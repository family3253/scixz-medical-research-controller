from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "resolve-srrsh-report-template.py"
PROMPT_BUILDER = ROOT / "scripts" / "01_build_slide_prompt_v20260504.py"
TEMPLATE_ROOT = ROOT / "references" / "srrsh_report_templates"
DEFAULT_STYLE = ROOT / "references" / "001_通用医学汇报PPT风格提示词.json"
SRRSH_STYLE = TEMPLATE_ROOT / "style_prompt.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SrrshTemplateResolverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resolver = load_module("srrsh_template_resolver", SCRIPT)
        cls.manifest = cls.resolver.load_json(TEMPLATE_ROOT / "manifest.json")

    def test_all_campus_assets_are_present_and_widescreen(self):
        hashes = set()
        for item in self.manifest["campuses"].values():
            path = TEMPLATE_ROOT / item["cover"]
            self.assertTrue(path.exists(), path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (2560, 1440))
            import hashlib

            hashes.add(hashlib.sha256(path.read_bytes()).hexdigest())
        self.assertEqual(len(hashes), 5, "Each campus must have a distinct cover image")

        ending = TEMPLATE_ROOT / self.manifest["ending"]["image"]
        self.assertTrue(ending.exists())
        with Image.open(ending) as image:
            self.assertEqual(image.size, (2560, 1440))

    def test_alias_resolves_to_correct_campus(self):
        campus_id, campus = self.resolver.resolve_campus(self.manifest, "邵逸夫医院钱塘院区")
        self.assertEqual(campus_id, "qiantang")
        self.assertEqual(campus["canonical_zh"], "钱塘院区")

        campus_id, campus = self.resolver.resolve_campus(self.manifest, "新疆阿拉尔")
        self.assertEqual(campus_id, "alaer")
        self.assertEqual(campus["canonical_zh"], "阿拉尔院区")

    def test_missing_campus_never_defaults(self):
        with self.assertRaisesRegex(ValueError, "必须明确院区"):
            self.resolver.resolve_campus(self.manifest, None)

    def test_inject_plan_binds_first_and_last_slides(self):
        plan = {
            "deck": {"title": "工作汇报"},
            "slides": [
                {"slide_id": "slide01", "slide_number": 1, "role": "title"},
                {"slide_id": "slide02", "slide_number": 2, "role": "content"},
                {"slide_id": "slide03", "slide_number": 3, "role": "closing"},
            ],
        }
        campus_id, campus = self.resolver.resolve_campus(self.manifest, "绍兴院区")
        updated = self.resolver.inject_plan(plan, self.manifest, campus_id, campus, "both")

        self.assertEqual(updated["deck"]["campus"], "绍兴院区")
        self.assertTrue(updated["deck"]["organization_template"]["strict_campus_match"])
        cover = updated["slides"][0]["template_binding"]
        ending = updated["slides"][-1]["template_binding"]
        self.assertEqual(cover["campus_id"], "shaoxing")
        self.assertTrue(cover["reference_image"].endswith("covers\\shaoxing.png") or cover["reference_image"].endswith("covers/shaoxing.png"))
        self.assertTrue(cover["campus_locked"])
        self.assertEqual(ending["source_slide"], 8)
        self.assertFalse(ending["campus_specific"])

    def test_cli_style_plan_roundtrip(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan_path = directory / "plan.json"
            out_path = directory / "updated.json"
            plan_path.write_text(
                json.dumps(
                    {
                        "deck": {"title": "工作汇报"},
                        "slides": [
                            {"slide_id": "slide01", "slide_number": 1},
                            {"slide_id": "slide02", "slide_number": 2},
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            import subprocess
            import sys

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--campus",
                    "庆春",
                    "--role",
                    "both",
                    "--plan",
                    str(plan_path),
                    "--out-plan",
                    str(out_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["campus_id"], "qingchun")
            self.assertTrue(out_path.exists())

    def test_explicit_style_overrides_unlocked_page_binding(self):
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan_path = directory / "plan.json"
            out_path = directory / "prompt.md"
            plan_path.write_text(
                json.dumps(
                    {
                        "deck": {"title": "普通医学汇报"},
                        "slides": [
                            {
                                "slide_id": "slide01",
                                "slide_number": 1,
                                "template_binding": {
                                    "style_selector": str(SRRSH_STYLE),
                                    "reference_image": "ordinary-template.png",
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            subprocess.run(
                [
                    sys.executable,
                    str(PROMPT_BUILDER),
                    "--style-json",
                    str(DEFAULT_STYLE),
                    "--plan",
                    str(plan_path),
                    "--slide-id",
                    "slide01",
                    "--slide-number",
                    "1",
                    "--out",
                    str(out_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            prompt = out_path.read_text(encoding="utf-8")
            self.assertIn(str(DEFAULT_STYLE.resolve()), prompt)
            self.assertNotIn(str(SRRSH_STYLE.resolve()), prompt)

    def test_campus_locked_binding_overrides_explicit_generic_style(self):
        import subprocess
        import sys

        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan_path = directory / "plan.json"
            out_path = directory / "prompt.md"
            campus_id, campus = self.resolver.resolve_campus(self.manifest, "大运河院区")
            plan = self.resolver.inject_plan(
                {
                    "deck": {"title": "工作汇报"},
                    "slides": [
                        {"slide_id": "slide01", "slide_number": 1},
                        {"slide_id": "slide02", "slide_number": 2},
                    ],
                },
                self.manifest,
                campus_id,
                campus,
                "both",
            )
            plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(PROMPT_BUILDER),
                    "--style-json",
                    str(DEFAULT_STYLE),
                    "--plan",
                    str(plan_path),
                    "--slide-id",
                    "slide01",
                    "--slide-number",
                    "1",
                    "--out",
                    str(out_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            prompt = out_path.read_text(encoding="utf-8")
            self.assertIn(str(SRRSH_STYLE.resolve()), prompt)
            self.assertIn("大运河院区", prompt)
            self.assertIn("grand_canal.png", prompt)
            self.assertNotIn(str(DEFAULT_STYLE.resolve()), prompt)


if __name__ == "__main__":
    unittest.main()
