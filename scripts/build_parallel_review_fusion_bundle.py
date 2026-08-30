#!/usr/bin/env python3
"""Build the evidence package for a fresh agent that fuses two review branches."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA = "scixz-parallel-review-fusion-bundle-v2"
PRIMARY_STATUSES = {"COMPLETED", "READY_FOR_FUSION"}


def load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return payload


def _fingerprint(payload: Dict[str, Any], branch: str) -> str:
    manuscript = payload.get("manuscript")
    if not isinstance(manuscript, dict):
        raise ValueError(f"{branch} branch lacks a manuscript object")
    fingerprint = manuscript.get("fingerprint")
    if not isinstance(fingerprint, str) or not fingerprint.startswith("sha256:"):
        raise ValueError(f"{branch} branch lacks a SHA-256 manuscript fingerprint")
    return fingerprint


def _external_issue_ids(paperreview_bundle: Dict[str, Any]) -> List[str]:
    external_signal = paperreview_bundle.get("external_signal")
    if not isinstance(external_signal, dict):
        raise ValueError("PaperReview branch lacks an external_signal object")
    ledger = external_signal.get("issue_ledger")
    if not isinstance(ledger, dict) or not isinstance(ledger.get("issues"), list) or not ledger["issues"]:
        raise ValueError("PaperReview branch lacks a canonical external issue ledger")
    identifiers: List[str] = []
    for issue in ledger["issues"]:
        if not isinstance(issue, dict) or not isinstance(issue.get("id"), str) or not issue["id"].strip():
            raise ValueError("PaperReview issue ledger contains an invalid issue id")
        identifiers.append(issue["id"].strip())
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("PaperReview issue ledger contains duplicate issue ids")
    if ledger.get("issue_count") != len(identifiers):
        raise ValueError("PaperReview issue ledger count does not match its issues")
    return identifiers


def _local_issue_ids(primary_review: Dict[str, Any]) -> List[str]:
    review = primary_review.get("review")
    if not isinstance(review, dict):
        raise ValueError("primary review branch lacks a substantive review object")
    identifiers: List[str] = []
    for collection in ("major_concerns", "minor_concerns"):
        items = review.get(collection, [])
        if not isinstance(items, list):
            raise ValueError(f"primary review {collection} must be a list")
        for issue in items:
            if not isinstance(issue, dict) or not isinstance(issue.get("id"), str) or not issue["id"].strip():
                raise ValueError(f"primary review {collection} contains an invalid issue id")
            identifiers.append(issue["id"].strip())
    if not identifiers:
        raise ValueError("primary review branch lacks canonical concern ids")
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("primary review branch contains duplicate concern ids")
    return identifiers


def _file_fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def companion_evidence_record(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"companion evidence does not exist: {path}")
    return {
        "file_name": path.name,
        "path": str(path.resolve()),
        "fingerprint": _file_fingerprint(path),
        "available_to": ["local-primary-review", "fresh-synthesis-agent"],
        "not_available_to": ["paperreview-ai"],
    }


def build_bundle(primary_review: Dict[str, Any], paperreview_bundle: Dict[str, Any], companion_evidence: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    if primary_review.get("status") not in PRIMARY_STATUSES:
        raise ValueError("primary review branch is not completed")
    if primary_review.get("branch_id") != "local-primary-review":
        raise ValueError("primary review branch_id must be local-primary-review")
    if not isinstance(primary_review.get("review"), dict) or not primary_review["review"]:
        raise ValueError("primary review branch lacks a substantive review object")
    if paperreview_bundle.get("status") != "READY_FOR_SCIXZ_FINAL_REVIEW":
        raise ValueError("PaperReview branch is not ready for final review")

    primary_fingerprint = _fingerprint(primary_review, "primary review")
    external_fingerprint = _fingerprint(paperreview_bundle, "PaperReview")
    if primary_fingerprint != external_fingerprint:
        raise ValueError("parallel review branches do not reference the same frozen manuscript")
    local_issue_ids = _local_issue_ids(primary_review)
    external_issue_ids = _external_issue_ids(paperreview_bundle)
    companion_evidence = companion_evidence or []
    companion_fingerprints: List[str] = []
    for item in companion_evidence:
        if not isinstance(item, dict) or not isinstance(item.get("fingerprint"), str) or not item["fingerprint"].startswith("sha256:"):
            raise ValueError("companion evidence contains an invalid fingerprint")
        if not isinstance(item.get("path"), str) or not item["path"].strip():
            raise ValueError("companion evidence contains an invalid path")
        companion_fingerprints.append(item["fingerprint"])
    if len(companion_fingerprints) != len(set(companion_fingerprints)):
        raise ValueError("companion evidence contains duplicate fingerprints")

    return {
        "schema": SCHEMA,
        "status": "READY_FOR_FRESH_SYNTHESIS_AGENT",
        "manuscript": {
            "fingerprint": primary_fingerprint,
            "file_name": primary_review["manuscript"].get("file_name")
            or paperreview_bundle["manuscript"].get("file_name"),
        },
        "evidence_manifest": {
            "shared_uploaded_pdf": {
                "file_name": primary_review["manuscript"].get("file_name") or paperreview_bundle["manuscript"].get("file_name"),
                "fingerprint": primary_fingerprint,
                "available_to": ["local-primary-review", "paperreview-ai", "fresh-synthesis-agent"],
            },
            "companion_evidence": companion_evidence,
            "branch_scopes_identical": not bool(companion_evidence),
        },
        "barrier": {
            "primary_review": "COMPLETED",
            "paperreview_external_signal": "COMPLETED",
            "synthesis_may_start": True,
            "local_issue_ids_requiring_matrix_mapping": local_issue_ids,
            "external_issue_ids_requiring_disposition": external_issue_ids,
        },
        "branches": {
            "local_primary_review": primary_review,
            "paperreview_external_signal": paperreview_bundle,
        },
        "fresh_synthesis_agent_contract": {
            "separation": "Use a new synthesis agent that did not author or revise either branch report.",
            "evidence_boundary": [
                "the same frozen manuscript",
                "the completed local primary-review artifact",
                "the completed PaperReview synthesis bundle",
            ],
            "required_steps": [
                "Read the frozen manuscript independently before comparing branch conclusions.",
                "Read every companion-evidence file in the manifest and preserve the fact that PaperReview did not receive it.",
                "Normalize both reports into atomic issues with source branch, manuscript location, severity, and requested action.",
                "Create an agreement/disagreement matrix; agreement increases priority but is not proof.",
                "Independently verify every retained issue against manuscript evidence and the applicable methodology/reporting standard.",
                "For each external issue record incorporated, incorporated-with-revision, rejected, or unresolved with a reason.",
                "Map every canonical external issue id exactly once; omission or duplication fails verification.",
                "Preserve material disagreements and uncertainty rather than forcing a majority decision.",
                "Produce the validated bilingual final-review JSON required by render_final_review_docx.py.",
            ],
            "prohibited": [
                "Do not expose hidden reasoning, credentials, email, or provider access tokens.",
                "Do not copy either branch recommendation without independent justification.",
                "Do not use a majority vote or treat correlated reviewers or agreement between two branches as independent validation.",
                "Do not start final synthesis before both branch artifacts pass the barrier.",
            ],
        },
        "final_review_contract": {
            "required": [
                "metadata",
                "decision",
                "overall_assessment",
                "strengths",
                "major_concerns",
                "minor_concerns",
                "external_signal_integration",
                "limitations",
                "synthesis_trace",
            ],
            "languages": ["zh", "en"],
            "outputs": ["Chinese DOCX", "English DOCX"],
            "external_issue_ids": external_issue_ids,
            "local_issue_ids": local_issue_ids,
            "companion_evidence_fingerprints": companion_fingerprints,
            "requires_evidence_scope_disclosure": bool(companion_evidence),
            "required_matrix_classes": ["agreement", "complementary", "disagreement", "local-only", "external-only"],
        },
        "boundary": "This package authorizes evidence synthesis, not automatic acceptance of either branch's conclusions.",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a strict two-branch review fusion package.")
    parser.add_argument("--primary-review", required=True)
    parser.add_argument("--paperreview-bundle", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--companion-evidence", action="append", default=[], help="Additional frozen evidence visible to the local and synthesis branches but not PaperReview")
    args = parser.parse_args(argv)
    try:
        companions = [companion_evidence_record(Path(value)) for value in args.companion_evidence]
        bundle = build_bundle(load_json(Path(args.primary_review)), load_json(Path(args.paperreview_bundle)), companions)
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Parallel review fusion blocked: {exc}\n")
    Path(args.output).write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": bundle["status"], "output": args.output}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
