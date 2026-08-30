import importlib.util
import zipfile
from pathlib import Path

from docx import Document


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "render_editorial_review_docx.py"
SPEC = importlib.util.spec_from_file_location("scixz_editorial_review_renderer", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def bilingual(zh, en):
    return {"zh": zh, "en": en}


def review():
    return {
        "metadata": {"manuscript_title": "Fictional Manuscript", "review_scope": "Full review", "manuscript_fingerprint": "sha256:test"},
        "decision": bilingual("大修", "Major revision"),
        "overall_assessment": bilingual("核心分析需要重做。", "The core analysis requires revision."),
        "strengths": [bilingual("问题重要。", "The question is important.")],
        "major_concerns": [{"id": "M1", "location": "Methods", "concern": bilingual("时间顺序不清。", "Temporality is unclear."), "recommendation": bilingual("报告事件时间。", "Report event times.")}],
        "minor_concerns": [{"id": "N1", "location": "Tables", "concern": bilingual("单位不清。", "Units are unclear."), "recommendation": bilingual("定义单位。", "Define units.")}],
        "external_signal_integration": [{"source_issue_id": "PR-01", "manuscript_location": "Methods", "disposition": "incorporated-with-revision", "external_issue": bilingual("外部信号。", "External signal."), "rationale": bilingual("经核验。", "Verified.")}],
        "synthesis_trace": {"external_issue_ids_expected": ["PR-01"], "agreement_disagreement_matrix": [{"id": "X1", "classification": "agreement", "local_issue_ids": ["M1"], "external_issue_ids": ["PR-01"], "resolution": bilingual("已核验。", "Verified.")}], "dissenting_sources": []},
        "limitations": [bilingual("无原始数据。", "No source data.")],
    }


def profile():
    return {
        "review_metadata": {"review_type": bilingual("完整同行评审", "Full peer review"), "review_date": "2026-08-30", "main_manuscript": bilingual("虚构稿件", "Fictional Manuscript"), "companion_files": []},
        "editorial_decision_note": bilingual("须重做核心分析。", "Core analyses must be revised."),
        "reviewer_panel": [{"id": "EIC", "perspective": bilingual("编辑", "Editorial"), "recommendation": bilingual("大修", "Major revision"), "confidence": "4/5"}],
        "major_issue_profiles": [{"concern_id": "M1", "title": bilingual("时间框架", "Temporal framework"), "source": bilingual("方法学审稿人；方法部分", "Methods reviewer; Methods"), "acceptance_criteria": bilingual("报告完整事件时间线。", "A complete event timeline is reported.")}],
        "minor_issue_profiles": [{"concern_id": "N1", "title": bilingual("单位", "Units")}],
        "recommended_revisions": [bilingual("统一术语。", "Harmonize terminology.")],
        "adversarial_stress_test": bilingual("替代解释是监测偏倚。", "The alternative explanation is surveillance bias."),
        "author_questions": [bilingual("事件何时发生？", "When did events occur?")],
        "dimension_scores": [{"dimension": bilingual("方法学", "Methods"), "score": 50, "assessment": bilingual("较弱", "Weak")}],
        "reporting_completeness": bilingual("报告不充分。", "Reporting is incomplete."),
        "revision_roadmap": [{"priority": bilingual("优先级1", "Priority 1"), "items": [bilingual("重做分析。", "Re-run the analysis.")]}],
        "recommended_revision_period": bilingual("6-8周", "6-8 weeks"),
    }


def test_full_editorial_renderer_restores_expected_sections(tmp_path):
    output = tmp_path / "review.docx"

    assert MODULE.validate_profile(profile(), review()) == []
    MODULE.render(review(), profile(), "zh", output)

    assert output.exists() and output.stat().st_size > 1000
    document = Document(output)
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    for expected in ("审阅稿件", "编辑决定", "审稿人配置", "必须修改的问题（P0", "反方论证压力测试", "作者必须回答的问题", "维度评分", "修订路线图", "附录A", "附录B"):
        assert expected in text
    with zipfile.ZipFile(output) as archive:
        assert "word/document.xml" in archive.namelist()


def test_full_editorial_profile_requires_exact_concern_mapping():
    invalid = profile()
    invalid["major_issue_profiles"] = []

    assert any("major_issue_profiles" in error for error in MODULE.validate_profile(invalid, review()))
