import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "paperreview_adapter.py"
SPEC = importlib.util.spec_from_file_location("scixz_paperreview_adapter", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_prepare_requires_explicit_authorization_and_never_needs_an_email(tmp_path):
    manuscript = tmp_path / "fictional.pdf"
    manuscript.write_bytes(b"%PDF-1.4\nfictional")

    blocked = MODULE.prepare_upload(manuscript, "English", 3, authorized_upload=False)
    ready = MODULE.prepare_upload(manuscript, "English", 20, authorized_upload=True)

    assert blocked["status"] == "BLOCKED"
    assert ready["status"] == "READY_FOR_MANUAL_UPLOAD_WITH_PAGE_LIMIT"
    assert ready["expected_pages_reviewed"] == 15
    assert all("email" not in key.lower() for key in ready)


def test_result_artifact_requires_english_completed_and_page_boundary():
    valid = {
        "tool": "paperreview-ai", "status": "completed", "input_fingerprint": "sha256:test",
        "submitted_at": "2026-08-30T12:00:00+08:00", "result_artifact": "saved-review.md",
        "language": "English", "pages_reviewed": 15,
    }
    result = MODULE.validate_review_artifact(valid)
    invalid = MODULE.validate_review_artifact({**valid, "pages_reviewed": 16})

    assert result["status"] == "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION"
    assert invalid["status"] == "BLOCKED"
    assert "pages_reviewed within 1..15" in invalid["missing"]


def test_registry_records_optional_manual_upload_boundary():
    registry = json.loads((ROOT / "registry" / "external_review_adapters.json").read_text(encoding="utf-8"))
    tool = registry["tools"][0]

    assert tool["id"] == "paperreview-ai"
    assert tool["mandatory"] is False
    assert tool["mode"] == "manual-browser-upload"
    assert tool["provider_constraints"]["reviewed_pages_maximum"] == 15
