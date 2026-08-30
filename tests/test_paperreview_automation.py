import importlib.util
import json
import zipfile
from xml.etree import ElementTree
from pathlib import Path

import pytest
from pypdf import PdfWriter


ROOT = Path(__file__).resolve().parents[1]


def _module(name):
    path = ROOT / "scripts" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUTOMATION = _module("paperreview_automation.py")
SYNTHESIS = _module("build_paperreview_synthesis_bundle.py")
RENDERER = _module("render_final_review_docx.py")
REPEAT_AUDIT = _module("audit_paperreview_repeats.py")


def _pdf(path):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    with path.open("wb") as handle:
        writer.write(handle)


class Response:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.payload = payload
        self.ok = 200 <= status_code < 300

    def json(self):
        return self.payload


class Session:
    def __init__(self, review_status=200):
        self.calls = []
        self.review_status = review_status

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        if url.endswith("/api/get-upload-url"):
            return Response(200, {"success": True, "presigned_url": "https://upload.example", "presigned_fields": {"key": "value"}, "s3_key": "private/object.pdf"})
        if url == "https://upload.example":
            return Response(204, {})
        if url.endswith("/api/confirm-upload"):
            return Response(200, {"success": True, "token": "provider-secret-token"})
        raise AssertionError(url)

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        if self.review_status == 202:
            return Response(202, {"detail": "Still processing"})
        return Response(200, {"title": "Fictional Paper", "venue": "Other", "submission_date": "2026-08-30", "sections": {"summary": "Provider summary", "weaknesses": "Provider concern"}, "numerical_score": 4})


def test_automated_submission_uses_public_three_step_flow_and_redacts_email_token(tmp_path):
    manuscript = tmp_path / "paper.pdf"
    _pdf(manuscript)
    state = tmp_path / "paperreview-state.json"
    session = Session()

    result = AUTOMATION.submit(manuscript, "author@example.edu", "Other", state, authorized_upload=True, session=session)
    saved_state = AUTOMATION.read_private_json(state)

    assert result["status"] == "SUBMITTED"
    assert len(session.calls) == 3
    assert "author@example.edu" not in json.dumps(result)
    assert "provider-secret-token" not in json.dumps(result)
    assert saved_state["review_token"] == "provider-secret-token"
    assert "email" not in saved_state


def test_submission_blocks_without_explicit_upload_authorization(tmp_path):
    manuscript = tmp_path / "paper.pdf"
    _pdf(manuscript)

    result = AUTOMATION.submit(manuscript, "author@example.edu", "", tmp_path / "state.json", authorized_upload=False, session=Session())

    assert result["status"] == "BLOCKED"
    assert "authorization" in " ".join(result["blocking_reasons"])


def test_private_artifacts_are_rejected_inside_the_scixz_worktree():
    with pytest.raises(ValueError, match="Git worktree"):
        AUTOMATION.write_private_json(ROOT / "paperreview-state-test.json", {"status": "test"})


def test_fetch_persists_result_and_redacted_artifact_then_synthesis_requires_matching_fingerprint(tmp_path):
    manuscript = tmp_path / "paper.pdf"
    _pdf(manuscript)
    state_path = tmp_path / "paperreview-state.json"
    submit_result = AUTOMATION.submit(manuscript, "author@example.edu", "", state_path, authorized_upload=True, session=Session())
    assert submit_result["status"] == "SUBMITTED"
    raw_result = tmp_path / "provider-review.json"
    artifact_path = tmp_path / "paperreview-artifact.json"
    fetch_result = AUTOMATION.fetch_review(state_path, raw_result, artifact_path, session=Session())
    artifact = AUTOMATION.read_private_json(artifact_path)

    assert fetch_result["status"] == "COMPLETED"
    assert artifact["status"] == "completed"
    assert artifact["token_fingerprint"] == AUTOMATION.token_fingerprint("provider-secret-token")
    assert artifact["review_content_fingerprint"].startswith("sha256:")
    assert "provider-secret-token" not in artifact_path.read_text(encoding="utf-8")
    bundle = SYNTHESIS.build_bundle(manuscript, artifact, AUTOMATION.read_private_json(raw_result))
    assert bundle["status"] == "READY_FOR_SCIXZ_FINAL_REVIEW"
    assert bundle["external_signal"]["issue_ledger"]["issue_count"] == 1
    assert bundle["external_signal"]["issue_ledger"]["issues"][0]["id"] == "PR-01"
    manuscript.write_bytes(manuscript.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="fingerprint"):
        SYNTHESIS.build_bundle(manuscript, artifact, AUTOMATION.read_private_json(raw_result))


def test_pending_result_is_not_misrepresented_as_completed(tmp_path):
    state = tmp_path / "state.json"
    AUTOMATION.write_private_json(state, {"tool": "paperreview-ai", "review_token": "provider-secret-token", "input_fingerprint": "sha256:test", "submitted_at": "2026-08-30T00:00:00Z", "pages": 1})

    result = AUTOMATION.fetch_review(state, tmp_path / "result.json", tmp_path / "artifact.json", session=Session(review_status=202))

    assert result["status"] == "PENDING"


def test_repeat_audit_treats_identical_provider_content_as_one_external_signal(tmp_path):
    run_dirs = []
    provider = {"success": True, "sections": {"summary": "Same review", "questions": "1. Same issue?"}}
    content_hash = REPEAT_AUDIT.content_fingerprint(provider)
    for index in (1, 2):
        run_dir = tmp_path / f"run-{index:02d}"
        run_dirs.append(run_dir)
        token = f"private-token-{index}"
        AUTOMATION.write_private_json(run_dir / "paperreview-state.json", {"status": "COMPLETED", "input_fingerprint": "sha256:paper", "review_token": token})
        AUTOMATION.write_private_json(run_dir / "paperreview-artifact.json", {"status": "completed", "input_fingerprint": "sha256:paper", "token_fingerprint": AUTOMATION.token_fingerprint(token), "review_content_fingerprint": content_hash})
        AUTOMATION.write_private_json(run_dir / "provider-review.json", provider)

    audit = REPEAT_AUDIT.build_audit(run_dirs)

    assert audit["status"] == "PASS_WITH_DUPLICATE_CONTENT"
    assert audit["transport_success_rate"] == 1
    assert audit["distinct_token_count"] == 2
    assert audit["distinct_review_content_count"] == 1
    assert audit["independent_external_signal_count"] == 1


def _final_review():
    bilingual = lambda zh, en: {"zh": zh, "en": en}
    return {
        "metadata": {"manuscript_title": "Fictional Manuscript", "review_scope": "Independent methodological and reporting review", "manuscript_fingerprint": "sha256:test"},
        "decision": bilingual("大修", "Major revision"),
        "overall_assessment": bilingual("研究问题具有潜在价值，但关键报告信息尚不充分。", "The question is potentially valuable, but key reporting information remains incomplete."),
        "strengths": [bilingual("问题具有临床相关性。", "The question has clinical relevance.")],
        "major_concerns": [{"id": "M1", "location": "Methods, outcome definition", "concern": bilingual("结局定义不够可复现。", "The outcome definition is not reproducible enough."), "recommendation": bilingual("提供完整定义和判定流程。", "Provide the full definition and adjudication workflow.")}],
        "minor_concerns": [{"id": "m1", "location": "Introduction paragraph 2", "concern": bilingual("缩略语首次出现未定义。", "An abbreviation is not defined at first use."), "recommendation": bilingual("首次出现时定义缩略语。", "Define the abbreviation at first use.")}],
        "external_signal_integration": [{"source_issue_id": "PR-01", "manuscript_location": "Methods, outcome definition", "disposition": "incorporated-with-revision", "external_issue": bilingual("外部工具提示结局定义不清。", "The external tool flagged an unclear outcome definition."), "rationale": bilingual("经方法部分核验后纳入主要问题。", "It was independently verified in Methods and incorporated as a major concern.")}],
        "synthesis_trace": {"external_issue_ids_expected": ["PR-01"], "agreement_disagreement_matrix": [{"id": "X1", "classification": "agreement", "local_issue_ids": ["M1"], "external_issue_ids": ["PR-01"], "resolution": bilingual("两条路径均提出该问题，并经稿件核验。", "Both branches raised the issue and it was verified against the manuscript.")}], "dissenting_sources": []},
        "limitations": [bilingual("外部 AI 审稿仅作为辅助信号。", "External AI review was treated as an advisory signal only.")],
    }


def test_bilingual_final_review_renderer_creates_valid_word_documents(tmp_path):
    outputs = {language: tmp_path / f"review_{language}.docx" for language in ("zh", "en")}
    review = _final_review()

    assert RENDERER.validate(review) == []
    for language, path in outputs.items():
        RENDERER.render(review, language, path)
        assert path.exists() and path.stat().st_size > 1000


def test_bilingual_renderer_emits_schema_ordered_shading_and_complete_zoom(tmp_path):
    output = tmp_path / "review.docx"
    RENDERER.render(_final_review(), "en", output)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(output) as archive:
        document = ElementTree.fromstring(archive.read("word/document.xml"))
        settings = ElementTree.fromstring(archive.read("word/settings.xml"))
    shaded_cell_properties = document.find(".//w:tcPr[w:shd]", namespace)
    tags = [child.tag.rsplit("}", 1)[-1] for child in shaded_cell_properties]
    assert tags.index("shd") < tags.index("vAlign")
    shading = shaded_cell_properties.find("w:shd", namespace)
    assert shading.get(f"{{{namespace['w']}}}val") == "clear"
    zoom = settings.find("w:zoom", namespace)
    assert zoom.get(f"{{{namespace['w']}}}percent") == "100"


def test_final_review_renderer_blocks_missing_bilingual_content():
    review = _final_review()
    review["decision"].pop("en")

    assert any("decision.en" in error for error in RENDERER.validate(review))


def test_final_review_renderer_blocks_incomplete_metadata():
    review = _final_review()
    review["metadata"].pop("review_scope")

    assert any("metadata.review_scope" in error for error in RENDERER.validate(review))


def test_final_review_renderer_allows_an_empty_minor_concern_list():
    review = _final_review()
    review["minor_concerns"] = []

    assert RENDERER.validate(review) == []


def test_parallel_renderer_requires_exact_external_issue_coverage_and_trace():
    review = _final_review()

    assert RENDERER.validate(review, ["PR-01"], "sha256:test", ["M1"]) == []
    review["external_signal_integration"][0]["source_issue_id"] = "PR-02"
    errors = RENDERER.validate(review, ["PR-01"], "sha256:test")
    assert any("missing: PR-01" in error for error in errors)
    assert any("unknown ids: PR-02" in error for error in errors)

    review = _final_review()
    review["synthesis_trace"]["agreement_disagreement_matrix"][0]["local_issue_ids"] = []
    errors = RENDERER.validate(review, ["PR-01"], "sha256:test", ["M1"])
    assert any("missing local issue ids: M1" in error for error in errors)


def test_parallel_renderer_requires_companion_evidence_scope_disclosure():
    review = _final_review()
    manifest = {"companion_evidence": [{"fingerprint": "sha256:companion"}]}
    errors = RENDERER.validate(review, ["PR-01"], "sha256:test", ["M1"], manifest)
    assert any("evidence_scope is required" in error for error in errors)

    review["synthesis_trace"]["evidence_scope"] = {
        "shared_uploaded_pdf_fingerprint": "sha256:test",
        "branch_scopes_identical": False,
        "companion_evidence_fingerprints": ["sha256:companion"],
        "external_branch_limitations": {"zh": "外部分支未读取伴随证据。", "en": "The external branch did not receive the companion evidence."},
    }
    assert RENDERER.validate(review, ["PR-01"], "sha256:test", ["M1"], manifest) == []
