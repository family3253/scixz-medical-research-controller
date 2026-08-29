from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
PROMPT_SCRIPT = ROOT / "scripts" / "01_build_slide_prompt_v20260504.py"
READY_SCRIPT = ROOT / "scripts" / "validate-slide-ready.py"
RUNTIME_DIR = ROOT / "cli" / "editppt" / "runtime"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PromptTemplateBindingTests(unittest.TestCase):
    def _write_plan(self, directory: Path) -> Path:
        plan = {
            "deck": {"title": "Demo", "style_selector": "001"},
            "slides": [
                {
                    "slide_id": "slide01",
                    "slide_number": 1,
                    "role": "title",
                    "title": "测试页",
                    "core_message": "验证逐页模板绑定",
                    "layout": {"structure": "cover", "regions": [{"name": "title"}]},
                    "content": {"scientific_illustration_needed": False},
                    "assets": {"required": []},
                    "references": ["Example 2026"],
                    "speaker_notes_zh": "测试",
                    "template_binding": {
                        "style_selector": "003",
                        "reference_image": "C:/templates/page01.png",
                        "style_text": "标题置顶，左右双栏。",
                        "confidence": 0.9,
                        "reason": "角色与版式匹配。",
                    },
                }
            ],
        }
        path = directory / "plan.json"
        path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
        return path

    def test_page_binding_selects_style_and_enters_prompt(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan = self._write_plan(directory)
            out = directory / "prompt.txt"
            subprocess.run(
                [
                    sys.executable,
                    str(PROMPT_SCRIPT),
                    "--plan",
                    str(plan),
                    "--slide-id",
                    "slide01",
                    "--slide-number",
                    "1",
                    "--out",
                    str(out),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            prompt = out.read_text(encoding="utf-8")
            self.assertIn("003_深蓝灰医学研究汇报PPT风格提示词.json", prompt)
            self.assertIn("C:/templates/page01.png", prompt)
            self.assertIn("标题置顶，左右双栏。", prompt)

    def test_explicit_cli_style_overrides_page_binding(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan = self._write_plan(directory)
            out = directory / "prompt.txt"
            subprocess.run(
                [
                    sys.executable,
                    str(PROMPT_SCRIPT),
                    "--style",
                    "001",
                    "--plan",
                    str(plan),
                    "--slide-id",
                    "slide01",
                    "--slide-number",
                    "1",
                    "--out",
                    str(out),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            prompt = out.read_text(encoding="utf-8")
            self.assertIn("001_通用医学汇报PPT风格提示词.json", prompt)

    def test_prompt_locks_deck_chrome_and_preserves_original_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            plan_path = directory / "plan.json"
            out = directory / "prompt.txt"
            plan = {
                "deck": {
                    "title": "Evidence demo",
                    "style_selector": "001",
                    "master_template_id": "ext-master",
                    "navigation_policy": "none",
                    "deck_chrome_locked": True,
                },
                "slides": [
                    {
                        "slide_id": "slide03",
                        "slide_number": 3,
                        "role": "results",
                        "title": "主要结果",
                        "core_message": "展示原始回归表",
                        "layout": {"structure": "evidence_plus_interpretation", "regions": [{"name": "evidence"}]},
                        "assets": {
                            "required": [
                                {
                                    "asset_id": "table4",
                                    "label": "Table 4",
                                    "kind": "table",
                                    "evidence_mode": "original",
                                    "output_path": "C:/evidence/table4.png",
                                    "citation": "Source PDF p.7",
                                },
                                {
                                    "asset_id": "derived1",
                                    "label": "中文机制图",
                                    "kind": "figure",
                                    "evidence_mode": "derived",
                                    "output_path": "C:/evidence/derived1.png",
                                },
                            ]
                        },
                        "references": ["Example 2026"],
                        "speaker_notes_zh": "测试",
                        "template_binding": {
                            "external_template_id": "ext-master",
                            "master_template_id": "ext-master",
                            "reference_image": "C:/templates/content-layout.png",
                        },
                    }
                ],
            }
            plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            subprocess.run(
                [
                    sys.executable,
                    str(PROMPT_SCRIPT),
                    "--plan",
                    str(plan_path),
                    "--slide-id",
                    "slide03",
                    "--slide-number",
                    "3",
                    "--out",
                    str(out),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            prompt = out.read_text(encoding="utf-8")
            self.assertIn("单页 template_binding 只允许决定主体内容区", prompt)
            self.assertIn("页眉、页脚、导航条、Logo 区、标题起点、页码位置", prompt)
            self.assertIn("navigation_policy：none", prompt)
            self.assertIn("C:/evidence/table4.png", prompt)
            self.assertIn("不得凭文字描述重新绘制", prompt)
            self.assertIn("重构示意 / Derived from source", prompt)
            self.assertIn("严禁保留任何模板占位或泛化品牌文字", prompt)


class SlideQualityReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ready = load_module("validate_slide_ready", READY_SCRIPT)

    def _slide_and_result(self, directory: Path, include_review: bool = True):
        slide = directory / "slide01.png"
        image = Image.new("RGB", (1280, 720), "white")
        draw = ImageDraw.Draw(image)
        draw.rectangle((80, 80, 1200, 220), fill="#123A63")
        draw.rectangle((100, 280, 580, 650), fill="#76A5AF")
        draw.rectangle((650, 280, 1180, 650), fill="#D9EAF2")
        image.save(slide)
        result = {
            "status": "IMAGE_READY",
            "passed": True,
            "output": str(slide),
            "image_backend": {"tool_call": "editppt image generate"},
        }
        if include_review:
            result["quality_review"] = {
                "passed": True,
                "attempt": 1,
                "checks": {key: True for key in self.ready.REQUIRED_QUALITY_CHECKS},
                "issues": [],
            }
        result_path = directory / "slide01.json"
        result_path.write_text(json.dumps(result), encoding="utf-8")
        return slide, result_path

    def test_required_quality_review_passes(self):
        with tempfile.TemporaryDirectory() as raw:
            slide, result = self._slide_and_result(Path(raw))
            payload = self.ready.validate(slide, result, require_quality_review=True)
            self.assertTrue(payload["passed"], payload["errors"])

    def test_missing_required_quality_review_fails(self):
        with tempfile.TemporaryDirectory() as raw:
            slide, result = self._slide_and_result(Path(raw), include_review=False)
            payload = self.ready.validate(slide, result, require_quality_review=True)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("quality_review" in error for error in payload["errors"]))

    def test_failed_quality_check_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            slide, result_path = self._slide_and_result(directory)
            result = json.loads(result_path.read_text(encoding="utf-8"))
            result["quality_review"]["checks"]["no_garbled_text"] = False
            result_path.write_text(json.dumps(result), encoding="utf-8")
            payload = self.ready.validate(slide, result_path, require_quality_review=True)
            self.assertFalse(payload["passed"])
            self.assertTrue(any("no_garbled_text" in error for error in payload["errors"]))


class AtomicStateWriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(RUNTIME_DIR))
        cls.state = load_module("deck_run_state_atomic", RUNTIME_DIR / "deck_run_state.py")

    def test_write_json_replaces_atomically_without_temp_residue(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            target = directory / "run_state.json"
            self.state.write_json(target, {"status": "created"})
            self.state.write_json(target, {"status": "complete", "pages": 3})
            self.assertEqual(
                json.loads(target.read_text(encoding="utf-8")),
                {"status": "complete", "pages": 3},
            )
            self.assertEqual(list(directory.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
