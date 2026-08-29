from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import fitz
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract-paper-evidence.py"


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("extract_paper_evidence", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PaperEvidenceExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extractor = load_module(SCRIPT)

    def test_crop_writes_original_evidence_metadata(self):
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            pdf_path = directory / "paper.pdf"
            document = fitz.open()
            page = document.new_page(width=400, height=300)
            page.draw_rect(fitz.Rect(100, 80, 300, 220), color=(0, 0, 0), fill=(0.8, 0.9, 1.0))
            page.insert_text((120, 150), "Table 4", fontsize=24)
            document.save(pdf_path)
            document.close()

            out_path = directory / "table4.png"
            payload = self.extractor.extract_evidence(
                pdf_path,
                1,
                fitz.Rect(90, 70, 310, 230),
                "table",
                "Table 4",
                out_path,
                dpi=144,
            )
            metadata = json.loads(Path(payload["metadata"]).read_text(encoding="utf-8"))
            self.assertEqual(metadata["evidence_mode"], "original")
            self.assertEqual(metadata["source_page"], 1)
            self.assertEqual(metadata["kind"], "table")
            self.assertEqual(metadata["render_policy"], "reconstruct_allowed")
            self.assertEqual(metadata["source_region"]["unit"], "pdf_points")
            self.assertIn("ai_redraw", metadata["forbidden_transformations"])
            with Image.open(out_path) as image:
                self.assertEqual(image.size, (440, 320))


if __name__ == "__main__":
    unittest.main()
