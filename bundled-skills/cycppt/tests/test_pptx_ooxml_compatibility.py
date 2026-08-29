import importlib.util
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET


RUNTIME = Path(__file__).resolve().parents[1] / "cli" / "editppt" / "runtime"
MODULE_PATH = RUNTIME / "build_pptx_from_manifest.py"
SPEC = importlib.util.spec_from_file_location("build_pptx_from_manifest", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

P_NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}
A_NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


class PptxOoxmlCompatibilityTests(unittest.TestCase):
    def test_widescreen_uses_valid_ooxml_slide_size_token(self):
        xml = MODULE.presentation_xml(1, MODULE.emu(13.333), MODULE.emu(7.5))
        root = ET.fromstring(xml)
        slide_size = root.find("p:sldSz", P_NS)

        self.assertIsNotNone(slide_size)
        self.assertEqual(slide_size.attrib["type"], "screen16x9")

    def test_theme_format_style_lists_have_required_three_entries(self):
        root = ET.fromstring(MODULE.theme_xml())
        format_scheme = root.find("a:themeElements/a:fmtScheme", A_NS)

        self.assertIsNotNone(format_scheme)
        self.assertEqual(len(list(format_scheme.find("a:fillStyleLst", A_NS))), 3)
        self.assertEqual(len(list(format_scheme.find("a:lnStyleLst", A_NS))), 3)
        self.assertEqual(len(list(format_scheme.find("a:effectStyleLst", A_NS))), 3)
        self.assertEqual(len(list(format_scheme.find("a:bgFillStyleLst", A_NS))), 3)
