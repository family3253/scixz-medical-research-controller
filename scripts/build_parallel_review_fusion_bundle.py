#!/usr/bin/env python3
"""Build the evidence package for a fresh agent that fuses two review branches."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA = "scixz-parallel-review-fusion-bundle-v1"
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


def build_bundle(primary_review: Dict[str, Any], paperreview_bundle: Dict[str, Any]) -> Dict[str, Any]:
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

    return {
        "schema": SCHEMA,
        "status": "READY_FOR_FRESH_SYNTHESIS_AGENT",
        "manuscript": {
            "fingerprint": primary_fingerprint,
            "file_name": primary_review["manuscript"].get("file_name")
            or paperreview_bundle["manuscript"].get("file_name"),
        },
        "barrier": {
            "primary_review": "COMPLETED",
            "paperreview_external_signal": "COMPLETED",
            "synthesis_may_start": True,
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
                "Normalize both reports into atomic issues with source branch, manuscript location, severity, and requested action.",
                "Create an agreement/disagreement matrix; agreement increases priority but is not proof.",
                "Independently verify every retained issue against manuscript evidence and the applicable methodology/reporting standard.",
                "For each external issue record incorporated, incorporated-with-revision, rejected, or unresolved with a reason.",
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
            ],
            "languages": ["zh", "en"],
            "outputs": ["Chinese DOCX", "English DOCX"],
        },
        "boundary": "This package authorizes evidence synthesis, not automatic acceptance of either branch's conclusions.",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a strict two-branch review fusion package.")
    parser.add_argument("--primary-review", required=True)
    parser.add_argument("--paperreview-bundle", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        bundle = build_bundle(load_json(Path(args.primary_review)), load_json(Path(args.paperreview_bundle)))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"Parallel review fusion blocked: {exc}\n")
    Path(args.output).write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": bundle["status"], "output": args.output}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
