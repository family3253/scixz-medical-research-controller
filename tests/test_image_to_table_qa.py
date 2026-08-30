import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = next(
    path
    for path in (
        ROOT / "bundled-skills" / "image-to-table-qa" / "scripts" / "build_table.py",
        ROOT.parent / "image-to-table-qa" / "scripts" / "build_table.py",
    )
    if path.is_file()
)
SPEC = importlib.util.spec_from_file_location("scixz_image_table", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_build_table_preserves_source_flags_units_and_low_confidence_review():
    payload = {
        "records": [
            {
                "source": "report-001.jpg",
                "fields": {
                    "WBC": {"value": "5.55", "unit": "10^9/L", "flag": "high", "confidence": 0.96},
                    "HGB": {"value": "121", "unit": "g/L", "flag": "low", "confidence": 0.61},
                },
            },
            {
                "source": "report-002.jpg",
                "fields": {
                    "WBC": {"value": "4.80", "unit": "10^9/L", "confidence": 0.93},
                    "HGB": {"status": "unreadable", "raw": "blurred"},
                },
            },
        ]
    }

    result = MODULE.build_table(payload, confidence_threshold=0.8)

    assert result["columns"][:2] == ["_source_file", "_review_status"]
    assert result["rows"][0]["WBC"] == "5.55"
    assert result["rows"][0]["WBC__flag"] == "high"
    assert result["rows"][0]["HGB__unit"] == "g/L"
    assert result["rows"][0]["_review_status"] == "needs-review"
    assert result["rows"][1]["HGB"] == ""
    assert result["rows"][1]["_review_status"] == "needs-review"
    assert result["qa"]["low_confidence_cells"] == 1
    assert result["qa"]["unreadable_cells"] == 1


def test_build_table_rejects_duplicate_source_rows():
    payload = {
        "records": [
            {"source": "same.jpg", "fields": {"A": "1"}},
            {"source": "same.jpg", "fields": {"A": "2"}},
        ]
    }

    with pytest.raises(ValueError, match="duplicate source"):
        MODULE.build_table(payload)
