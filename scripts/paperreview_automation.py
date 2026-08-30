#!/usr/bin/env python3
"""Authorized PaperReview.ai submission and retrieval automation.

The provider's public browser code uses a three-step flow: obtain a presigned
upload URL, POST the PDF to that URL, then confirm with the provider. This
script follows that public flow only after an explicit authorization flag. It
never prints an email address or review token, and refuses to write sensitive
state into a Git worktree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from pypdf import PdfReader


BASE_URL = "https://paperreview.ai"
MAX_BYTES = 10 * 1024 * 1024
MAX_REVIEWED_PAGES = 15
SCHEMA = "scixz-paperreview-automation-v1"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def token_fingerprint(token: str) -> str:
    return "sha256:" + hashlib.sha256(token.encode("utf-8")).hexdigest()


def review_content_fingerprint(payload: Dict[str, Any]) -> str:
    content = payload.get("sections")
    if not isinstance(content, dict) or not content:
        content = payload.get("content") or payload
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def in_git_worktree(path: Path) -> bool:
    """Return whether a private artifact would enter this SciXZ checkout.

    Some Windows installations expose a broad Git worktree at the drive root.
    Treating every descendant as a repository would prevent a genuinely private
    path from being used. The protected boundary is the SciXZ checkout that can
    be committed or pushed by this workflow.
    """
    try:
        path.resolve().relative_to(Path(__file__).resolve().parents[1])
    except ValueError:
        return False
    return True


def write_private_json(path: Path, payload: Dict[str, Any]) -> None:
    if in_git_worktree(path):
        raise ValueError("Refusing to write PaperReview state or results inside a Git worktree")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def read_private_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError("State must be a JSON object")
    return payload


def validate_submission(manuscript: Path, language: str, authorized_upload: bool) -> Tuple[List[str], int]:
    errors: List[str] = []
    pages = 0
    if not manuscript.is_file() or manuscript.suffix.lower() != ".pdf":
        errors.append("manuscript must be an existing PDF")
    else:
        if manuscript.stat().st_size > MAX_BYTES:
            errors.append("provider limit is 10 MB")
        try:
            pages = len(PdfReader(str(manuscript)).pages)
        except Exception as exc:
            errors.append(f"PDF page count could not be read: {exc}")
    if language.strip().lower() != "english":
        errors.append("provider advertises English-only review")
    if not authorized_upload:
        errors.append("explicit user authorization for this exact external upload is required")
    return errors, pages


def _json_response(response: Any, operation: str) -> Dict[str, Any]:
    try:
        payload = response.json()
    except Exception as exc:
        raise RuntimeError(f"{operation} returned non-JSON data") from exc
    if not isinstance(payload, dict):
        raise RuntimeError(f"{operation} returned an invalid JSON object")
    return payload


def _error_message(response: Any, operation: str) -> str:
    try:
        detail = _json_response(response, operation).get("detail")
    except RuntimeError:
        detail = None
    return str(detail or f"{operation} failed with HTTP {getattr(response, 'status_code', 'unknown')}")


def redacted_state_summary(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": SCHEMA,
        "tool": "paperreview-ai",
        "status": state.get("status"),
        "input_fingerprint": state.get("input_fingerprint"),
        "token_fingerprint": state.get("token_fingerprint"),
        "submitted_at": state.get("submitted_at"),
        "pages": state.get("pages"),
        "provider_reviewed_pages_maximum": MAX_REVIEWED_PAGES,
    }


def submit(
    manuscript: Path,
    email: str,
    venue: str,
    state_path: Path,
    authorized_upload: bool,
    language: str = "English",
    session: Optional[Any] = None,
) -> Dict[str, Any]:
    errors, pages = validate_submission(manuscript, language, authorized_upload)
    if not email.strip():
        errors.append("configured email is empty")
    if errors:
        return {"tool": "paperreview-ai", "status": "BLOCKED", "blocking_reasons": errors}

    client = session or requests.Session()
    try:
        upload_url_response = client.post(
            f"{BASE_URL}/api/get-upload-url",
            json={"filename": manuscript.name, "venue": venue or ""},
            timeout=60,
        )
        if not getattr(upload_url_response, "ok", False):
            raise RuntimeError(_error_message(upload_url_response, "upload URL request"))
        upload_data = _json_response(upload_url_response, "upload URL request")
        required = ("success", "presigned_url", "presigned_fields", "s3_key")
        if not upload_data.get("success") or any(upload_data.get(key) in (None, "", {}) for key in required[1:]):
            raise RuntimeError("upload URL response omitted a required presigned-upload field")
        with manuscript.open("rb") as handle:
            upload_response = client.post(
                upload_data["presigned_url"],
                data=upload_data["presigned_fields"],
                files={"file": (manuscript.name, handle, "application/pdf")},
                timeout=180,
            )
        if not getattr(upload_response, "ok", False):
            raise RuntimeError(f"presigned PDF upload failed with HTTP {getattr(upload_response, 'status_code', 'unknown')}")
        confirm_response = client.post(
            f"{BASE_URL}/api/confirm-upload",
            data={"s3_key": upload_data["s3_key"], "venue": venue or "", "email": email},
            timeout=60,
        )
        if not getattr(confirm_response, "ok", False):
            raise RuntimeError(_error_message(confirm_response, "upload confirmation"))
        confirmation = _json_response(confirm_response, "upload confirmation")
        token = str(confirmation.get("token") or "")
        if not confirmation.get("success") or not token:
            raise RuntimeError("upload confirmation did not return a review token")
    except requests.RequestException as exc:
        return {"tool": "paperreview-ai", "status": "FAILED", "reason": f"network error: {exc}"}
    except RuntimeError as exc:
        return {"tool": "paperreview-ai", "status": "FAILED", "reason": str(exc)}

    state = {
        "schema": SCHEMA,
        "tool": "paperreview-ai",
        "status": "SUBMITTED",
        "input_fingerprint": fingerprint(manuscript),
        "input_file_name": manuscript.name,
        "submitted_at": now(),
        "venue": venue or None,
        "language": "English",
        "pages": pages,
        "provider_reviewed_pages_maximum": MAX_REVIEWED_PAGES,
        "review_token": token,
        "token_fingerprint": token_fingerprint(token),
    }
    write_private_json(state_path, state)
    return {**redacted_state_summary(state), "state_path": str(state_path), "next_action": "Poll or fetch the provider review using the saved private state file."}


def fetch_review(state_path: Path, result_path: Path, artifact_path: Path, session: Optional[Any] = None) -> Dict[str, Any]:
    state = read_private_json(state_path)
    token = str(state.get("review_token") or "")
    if state.get("tool") != "paperreview-ai" or not token:
        return {"tool": "paperreview-ai", "status": "BLOCKED", "blocking_reasons": ["state lacks a PaperReview review token"]}
    client = session or requests.Session()
    try:
        response = client.get(f"{BASE_URL}/api/review/{token}", timeout=60)
        payload = _json_response(response, "review retrieval")
    except requests.RequestException as exc:
        return {"tool": "paperreview-ai", "status": "FAILED", "reason": f"network error: {exc}"}
    except RuntimeError as exc:
        return {"tool": "paperreview-ai", "status": "FAILED", "reason": str(exc)}
    state["last_checked_at"] = now()
    if getattr(response, "status_code", 0) == 202:
        state["status"] = "PENDING"
        write_private_json(state_path, state)
        return {**redacted_state_summary(state), "next_action": "The provider has not completed the review; poll again later."}
    if not getattr(response, "ok", False):
        return {"tool": "paperreview-ai", "status": "FAILED", "reason": str(payload.get("detail") or f"review retrieval failed with HTTP {getattr(response, 'status_code', 'unknown')}")}

    write_private_json(result_path, payload)
    artifact = {
        "tool": "paperreview-ai",
        "status": "completed",
        "input_fingerprint": state["input_fingerprint"],
        "submitted_at": state["submitted_at"],
        "result_artifact": str(result_path),
        "language": state["language"],
        "pages_reviewed": min(int(state["pages"]), MAX_REVIEWED_PAGES),
        "review_title": payload.get("title") or None,
        "review_sections": sorted((payload.get("sections") or {}).keys()),
        "token_fingerprint": state["token_fingerprint"],
        "review_content_fingerprint": review_content_fingerprint(payload),
    }
    write_private_json(artifact_path, artifact)
    state["status"] = "COMPLETED"
    state["result_artifact"] = str(result_path)
    state["artifact_path"] = str(artifact_path)
    write_private_json(state_path, state)
    return {
        **redacted_state_summary(state),
        "status": "COMPLETED",
        "result_path": str(result_path),
        "artifact_path": str(artifact_path),
        "next_action": "Build a synthesis bundle, then let the SciXZ reviewer independently assess and absorb verified external findings.",
    }


def poll_review(state_path: Path, result_path: Path, artifact_path: Path, attempts: int, interval_seconds: int, session: Optional[Any] = None) -> Dict[str, Any]:
    if attempts < 1 or interval_seconds < 1:
        return {"tool": "paperreview-ai", "status": "BLOCKED", "blocking_reasons": ["attempts and interval must be positive"]}
    for attempt in range(1, attempts + 1):
        result = fetch_review(state_path, result_path, artifact_path, session=session)
        result["attempt"] = attempt
        if result.get("status") != "PENDING" or attempt == attempts:
            return result
        time.sleep(interval_seconds)
    raise AssertionError("unreachable")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Submit, fetch, or poll an explicitly authorized PaperReview.ai run.")
    commands = parser.add_subparsers(dest="command", required=True)
    submit_parser = commands.add_parser("submit")
    submit_parser.add_argument("--manuscript", required=True)
    submit_parser.add_argument("--venue", default="")
    submit_parser.add_argument("--language", default="English")
    submit_parser.add_argument("--state", required=True)
    submit_parser.add_argument("--email-env", default="PAPERREVIEW_EMAIL")
    submit_parser.add_argument("--authorized-upload", action="store_true")
    for name in ("fetch", "poll"):
        child = commands.add_parser(name)
        child.add_argument("--state", required=True)
        child.add_argument("--result", required=True)
        child.add_argument("--artifact", required=True)
        if name == "poll":
            child.add_argument("--attempts", type=int, default=24)
            child.add_argument("--interval-seconds", type=int, default=900)
    args = parser.parse_args(argv)
    if args.command == "submit":
        result = submit(Path(args.manuscript), os.environ.get(args.email_env, ""), args.venue, Path(args.state), args.authorized_upload, args.language)
    elif args.command == "fetch":
        result = fetch_review(Path(args.state), Path(args.result), Path(args.artifact))
    else:
        result = poll_review(Path(args.state), Path(args.result), Path(args.artifact), args.attempts, args.interval_seconds)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("status") in {"SUBMITTED", "PENDING", "COMPLETED"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
