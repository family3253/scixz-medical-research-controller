#!/usr/bin/env python3
"""Audit repeated PaperReview runs without exposing private tokens or review text."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA = "scixz-paperreview-repeat-audit-v1"


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest()


def content_fingerprint(provider_review: Dict[str, Any]) -> str:
    content = provider_review.get("sections")
    if not isinstance(content, dict) or not content:
        content = provider_review.get("content") or provider_review
    canonical = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_text(canonical)


def audit_run(run_dir: Path, index: int) -> Dict[str, Any]:
    state_path = run_dir / "paperreview-state.json"
    artifact_path = run_dir / "paperreview-artifact.json"
    provider_path = run_dir / "provider-review.json"
    state = load_json(state_path)
    artifact = load_json(artifact_path)
    provider = load_json(provider_path)
    token = str(state.get("review_token") or "")
    expected_token_fingerprint = sha256_text(token) if token else None
    observed_content_fingerprint = content_fingerprint(provider)
    artifact_text = artifact_path.read_text(encoding="utf-8-sig")
    provider_text = provider_path.read_text(encoding="utf-8-sig")
    checks = {
        "state_completed": state.get("status") == "COMPLETED",
        "artifact_completed": str(artifact.get("status", "")).lower() == "completed",
        "provider_success": provider.get("success") is True,
        "input_fingerprint_match": bool(state.get("input_fingerprint")) and state.get("input_fingerprint") == artifact.get("input_fingerprint"),
        "token_present_only_in_private_state": bool(token) and token not in artifact_text and token not in provider_text,
        "artifact_token_fingerprint_match": artifact.get("token_fingerprint") in (None, expected_token_fingerprint),
        "artifact_content_fingerprint_match": artifact.get("review_content_fingerprint") in (None, observed_content_fingerprint),
    }
    return {
        "run": index,
        "run_dir": str(run_dir.resolve()),
        "input_fingerprint": state.get("input_fingerprint"),
        "token_fingerprint": expected_token_fingerprint,
        "review_content_fingerprint": observed_content_fingerprint,
        "checks": checks,
        "passed": all(checks.values()),
    }


def build_audit(run_dirs: List[Path]) -> Dict[str, Any]:
    if len(run_dirs) < 2:
        raise ValueError("repeat audit requires at least two run directories")
    runs = [audit_run(path, index) for index, path in enumerate(run_dirs, 1)]
    input_fingerprints = {item["input_fingerprint"] for item in runs}
    token_fingerprints = {item["token_fingerprint"] for item in runs}
    content_groups: Dict[str, List[int]] = defaultdict(list)
    for item in runs:
        content_groups[item["review_content_fingerprint"]].append(item["run"])
    duplicate_groups = [
        {"review_content_fingerprint": fingerprint, "runs": indexes}
        for fingerprint, indexes in content_groups.items()
        if len(indexes) > 1
    ]
    completed = sum(1 for item in runs if item["passed"])
    repeated_content = len(content_groups) < len(runs)
    status = "PASS_WITH_DUPLICATE_CONTENT" if completed == len(runs) and repeated_content else "PASS" if completed == len(runs) else "FAILED"
    return {
        "schema": SCHEMA,
        "status": status,
        "transport_runs": len(runs),
        "completed_runs": completed,
        "transport_success_rate": completed / len(runs),
        "same_input_fingerprint": len(input_fingerprints) == 1,
        "distinct_token_count": len(token_fingerprints),
        "distinct_review_content_count": len(content_groups),
        "independent_external_signal_count": len(content_groups),
        "duplicate_content_groups": duplicate_groups,
        "runs": runs,
        "interpretation": "Repeated runs test transport reliability. Identical review-content fingerprints are one external signal and must not be counted as independent reviewers or votes.",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Audit repeated private PaperReview run directories.")
    parser.add_argument("--run-dir", action="append", required=True)
    parser.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        audit = build_audit([Path(value) for value in args.run_dir])
    except (OSError, ValueError) as exc:
        parser.exit(2, f"PaperReview repeat audit blocked: {exc}\n")
    rendered = json.dumps(audit, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if audit["status"].startswith("PASS") else 2


if __name__ == "__main__":
    raise SystemExit(main())
