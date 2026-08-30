#!/usr/bin/env python3
"""Render a verified bilingual SciXZ final review JSON into Chinese and English DOCX files."""

from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor


LANGUAGES = {"zh": "中文", "en": "English"}
REQUIRED = ("metadata", "decision", "overall_assessment", "strengths", "major_concerns", "minor_concerns", "external_signal_integration", "limitations")


def _text(value: Any, language: str, path: str, errors: List[str]) -> str:
    if not isinstance(value, dict) or not isinstance(value.get(language), str) or not value[language].strip():
        errors.append(f"{path}.{language} is required")
        return ""
    return value[language].strip()


def validate(review: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for key in REQUIRED:
        if key not in review or review.get(key) is None:
            errors.append(f"{key} is required")
    if errors:
        return errors
    metadata = review.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("metadata must be an object")
    else:
        for key in ("manuscript_title", "review_scope"):
            if not isinstance(metadata.get(key), str) or not metadata[key].strip():
                errors.append(f"metadata.{key} is required")
    if not isinstance(review.get("external_signal_integration"), list):
        errors.append("external_signal_integration must be a list")
        return errors
    for language in LANGUAGES:
        _text(review["decision"], language, "decision", errors)
        _text(review["overall_assessment"], language, "overall_assessment", errors)
        for collection in ("strengths", "major_concerns", "minor_concerns", "limitations"):
            if not isinstance(review.get(collection), list):
                errors.append(f"{collection} must be a list")
                continue
            for index, item in enumerate(review[collection], 1):
                if collection in {"major_concerns", "minor_concerns"}:
                    if not isinstance(item, dict) or not str(item.get("id", "")).strip() or not str(item.get("location", "")).strip():
                        errors.append(f"{collection}[{index}] needs id and location")
                    else:
                        _text(item.get("concern"), language, f"{collection}[{index}].concern", errors)
                        _text(item.get("recommendation"), language, f"{collection}[{index}].recommendation", errors)
                else:
                    _text(item, language, f"{collection}[{index}]", errors)
        for index, item in enumerate(review.get("external_signal_integration", []), 1):
            if not isinstance(item, dict) or item.get("disposition") not in {"incorporated", "incorporated-with-revision", "rejected", "unresolved"}:
                errors.append(f"external_signal_integration[{index}] needs an allowed disposition")
            else:
                _text(item.get("external_issue"), language, f"external_signal_integration[{index}].external_issue", errors)
                _text(item.get("rationale"), language, f"external_signal_integration[{index}].rationale", errors)
    return errors


def _shade(cell: Any, fill: str) -> None:
    properties = cell._tc.get_or_add_tcPr()
    for child in list(properties):
        if child.tag == qn("w:shd"):
            properties.remove(child)
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def _set_cell_text(cell: Any, text: str, bold: bool = False) -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(9)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP


def _configure(document: Document) -> None:
    section = document.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.left_margin = Cm(2)
    section.right_margin = Cm(2)
    normal = document.styles["Normal"]
    normal.font.name = "Arial"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Microsoft YaHei")
    normal.font.size = Pt(10.5)


def _heading(document: Document, text: str, level: int = 1) -> None:
    paragraph = document.add_heading(text, level=level)
    paragraph.paragraph_format.space_before = Pt(10)
    paragraph.paragraph_format.space_after = Pt(5)


def _bullet(document: Document, text: str) -> None:
    document.add_paragraph(text, style="List Bullet")


def render(review: Dict[str, Any], language: str, output: Path) -> None:
    errors = validate(review)
    if errors:
        raise ValueError("; ".join(errors))
    label = LANGUAGES[language]
    document = Document()
    _configure(document)
    title = "SciXZ 最终同行评审意见" if language == "zh" else "SciXZ Final Peer-Review Report"
    subtitle = "已核验的外部 AI 审稿信号仅作辅助参考" if language == "zh" else "Verified external AI-review signals are advisory evidence only"
    title_p = document.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_p.add_run(title)
    title_run.bold = True
    title_run.font.size = Pt(18)
    title_run.font.color.rgb = RGBColor(31, 78, 121)
    sub_p = document.add_paragraph(subtitle)
    sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sub_p.runs[0].italic = True

    meta = review["metadata"]
    table = document.add_table(rows=0, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    labels = [("Manuscript" if language == "en" else "稿件", meta.get("manuscript_title", "")), ("Decision" if language == "en" else "总体建议", _text(review["decision"], language, "decision", [])), ("Review scope" if language == "en" else "审稿范围", meta.get("review_scope", "")), ("Language" if language == "en" else "报告语言", label)]
    for left, right in labels:
        cells = table.add_row().cells
        _set_cell_text(cells[0], str(left), bold=True)
        _set_cell_text(cells[1], str(right))
        _shade(cells[0], "D9EAF7")

    _heading(document, "Overall Assessment" if language == "en" else "总体评价")
    document.add_paragraph(_text(review["overall_assessment"], language, "overall_assessment", []))
    _heading(document, "Strengths" if language == "en" else "主要优点")
    for item in review["strengths"]:
        _bullet(document, _text(item, language, "strengths", []))

    for key, heading in (("major_concerns", "Major Concerns" if language == "en" else "主要问题"), ("minor_concerns", "Minor Concerns" if language == "en" else "次要问题")):
        _heading(document, heading)
        concerns = review[key]
        if not concerns:
            document.add_paragraph("None." if language == "en" else "无。")
            continue
        table = document.add_table(rows=1, cols=4)
        table.style = "Table Grid"
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        headers = ["ID", "Location" if language == "en" else "位置", "Concern" if language == "en" else "问题", "Recommendation" if language == "en" else "建议"]
        for cell, header in zip(table.rows[0].cells, headers):
            _set_cell_text(cell, header, bold=True)
            _shade(cell, "D9EAF7")
        for item in concerns:
            cells = table.add_row().cells
            values = [item["id"], item["location"], _text(item["concern"], language, "concern", []), _text(item["recommendation"], language, "recommendation", [])]
            for cell, value in zip(cells, values):
                _set_cell_text(cell, str(value))

    _heading(document, "External AI-Review Integration" if language == "en" else "外部 AI 审稿意见的处理")
    if not review["external_signal_integration"]:
        document.add_paragraph("No external AI-review signal was used." if language == "en" else "未使用外部 AI 审稿信号。")
    for item in review["external_signal_integration"]:
        issue = _text(item["external_issue"], language, "external_issue", [])
        rationale = _text(item["rationale"], language, "rationale", [])
        document.add_paragraph(f"[{item['disposition']}] {issue}", style="List Bullet")
        document.add_paragraph(rationale)
    _heading(document, "Limitations and Verification" if language == "en" else "限制与核验边界")
    for item in review["limitations"]:
        _bullet(document, _text(item, language, "limitations", []))

    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)
    with zipfile.ZipFile(output) as archive:
        if "word/document.xml" not in archive.namelist():
            raise RuntimeError("DOCX validation failed: missing word/document.xml")
    Document(output)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Render Chinese and English final-review DOCX files from a verified bilingual JSON review.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--stem", default="scixz_final_review")
    args = parser.parse_args(argv)
    review = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    if not isinstance(review, dict):
        parser.error("input must be a JSON object")
    errors = validate(review)
    if errors:
        parser.exit(2, "Final review DOCX rendering blocked: " + "; ".join(errors) + "\n")
    destination = Path(args.output_dir)
    outputs = {language: destination / f"{args.stem}_{language}.docx" for language in LANGUAGES}
    for language, path in outputs.items():
        render(review, language, path)
    print(json.dumps({"status": "COMPLETE", "outputs": {key: str(value) for key, value in outputs.items()}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
