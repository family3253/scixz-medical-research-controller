#!/usr/bin/env python3
"""Create and validate privacy-preserving PaperReview.ai review records.

This adapter deliberately performs no browser action, upload, email collection, or provider API
call. It only makes the external-review boundary auditable.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


TOOL = "paperreview-ai"
MAX_PAGES = 15


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def prepare_upload(manuscript: Path, language: str, declared_pages: int, authorized_upload: bool) -> Dict[str, Any]:
    reasons: List[str] = []
    if not manuscript.is_file():
        reasons.append("manuscript file does not exist")
    elif manuscript.suffix.lower() != ".pdf":
        reasons.append("PaperReview.ai preparation requires a PDF")
    if language.strip().lower() != "english":
        reasons.append("provider advertises English-only review")
    if declared_pages < 1:
        reasons.append("declared page count must be positive")
    if not authorized_upload:
        reasons.append("explicit user authorization for this external upload is missing")
    if reasons:
        return {
            "tool": TOOL,
            "status": "BLOCKED",
            "blocking_reasons": reasons,
            "next_action": "Resolve the listed conditions; this adapter will never upload a file itself.",
        }
    reviewed_pages = min(declared_pages, MAX_PAGES)
    status = "READY_FOR_MANUAL_UPLOAD" if declared_pages <= MAX_PAGES else "READY_FOR_MANUAL_UPLOAD_WITH_PAGE_LIMIT"
    return {
        "tool": TOOL,
        "status": status,
        "input_fingerprint": fingerprint(manuscript),
        "input_file_name": manuscript.name,
        "language": "English",
        "declared_pages": declared_pages,
        "provider_reviewed_pages_maximum": MAX_PAGES,
        "expected_pages_reviewed": reviewed_pages,
        "authorization": "explicit-user-authorization-recorded",
        "privacy_boundary": "No browser upload, email address, provider URL, cookie, or manuscript copy is stored by this adapter.",
        "next_action": "User may manually upload the approved PDF, save the resulting review locally, then validate the saved-result artifact.",
    }


def validate_review_artifact(artifact: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(artifact, dict):
        return {"tool": TOOL, "status": "BLOCKED", "missing": ["artifact"]}
    required = ("input_fingerprint", "submitted_at", "result_artifact", "language", "pages_reviewed")
    missing = [key for key in required if artifact.get(key) in (None, "", [], {})]
    if artifact.get("tool") not in (None, TOOL):
        missing.append("matching tool")
    if str(artifact.get("status", "")).lower() != "completed":
        missing.append("status=completed")
    if str(artifact.get("language", "")).lower() != "english":
        missing.append("language=English")
    try:
        pages = int(artifact.get("pages_reviewed", 0))
    except (TypeError, ValueError):
        pages = 0
    if not 1 <= pages <= MAX_PAGES:
        missing.append("pages_reviewed within 1..15")
    if missing:
        return {"tool": TOOL, "status": "BLOCKED", "missing": missing}
    return {
        "tool": TOOL,
        "status": "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION",
        "input_fingerprint": artifact["input_fingerprint"],
        "submitted_at": artifact["submitted_at"],
        "result_artifact": artifact["result_artifact"],
        "pages_reviewed": pages,
        "limitations": [
            "External review is advisory only.",
            "Independently verify every issue against the frozen manuscript and domain review routes.",
            "Do not infer an editorial decision, medical validity, or reporting compliance from this signal alone.",
        ],
        "next_action": "Map verified findings into the SciXZ issue ledger with location, severity, evidence, and disposition.",
    }


def _load_json(path: str) -> Dict[str, Any]:
    payload = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("artifact must be a JSON object")
    return payload


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare or validate a non-automated PaperReview.ai external-review record.")
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--prepare", action="store_true")
    action.add_argument("--validate-artifact", default="")
    parser.add_argument("--manuscript", default="")
    parser.add_argument("--language", default="")
    parser.add_argument("--pages", type=int, default=0)
    parser.add_argument("--authorized-upload", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args(argv)
    if args.prepare:
        result = prepare_upload(Path(args.manuscript), args.language, args.pages, args.authorized_upload)
    else:
        result = validate_review_artifact(_load_json(args.validate_artifact))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["status"] in {"READY_FOR_MANUAL_UPLOAD", "READY_FOR_MANUAL_UPLOAD_WITH_PAGE_LIMIT", "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
