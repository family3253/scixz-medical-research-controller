#!/usr/bin/env python3
"""Prepare a bounded, auditable input for SciXZ final-review synthesis."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]


def _load_adapter():
    path = ROOT / "scripts" / "paperreview_adapter.py"
    spec = importlib.util.spec_from_file_location("scixz_paperreview_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("PaperReview adapter is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _fingerprint(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def build_bundle(manuscript: Path, artifact: Dict[str, Any], provider_review: Dict[str, Any]) -> Dict[str, Any]:
    if not manuscript.is_file():
        raise ValueError("manuscript does not exist")
    validation = _load_adapter().validate_review_artifact(artifact)
    if validation["status"] != "EXTERNAL_SIGNAL_READY_FOR_VERIFICATION":
        raise ValueError(f"PaperReview artifact is not valid: {validation.get('missing', [])}")
    current_fingerprint = _fingerprint(manuscript)
    if current_fingerprint != artifact["input_fingerprint"]:
        raise ValueError("frozen manuscript fingerprint does not match the PaperReview submission artifact")
    sections = provider_review.get("sections") or {}
    if not isinstance(sections, dict):
        raise ValueError("provider review sections must be an object")
    return {
        "schema": "scixz-paperreview-synthesis-bundle-v1",
        "status": "READY_FOR_SCIXZ_FINAL_REVIEW",
        "manuscript": {"file_name": manuscript.name, "fingerprint": current_fingerprint},
        "external_signal": {
            "tool": "paperreview-ai",
            "artifact": validation,
            "provider_review": {
                "title": provider_review.get("title") or None,
                "venue": provider_review.get("venue") or None,
                "submission_date": provider_review.get("submission_date") or None,
                "sections": sections,
                "numerical_score": provider_review.get("numerical_score"),
            },
        },
        "required_synthesis_steps": [
            "Read the frozen manuscript independently before treating any external statement as a finding.",
            "Decompose every external statement into an atomic issue; locate it in the manuscript or mark it unresolved.",
            "Verify methodology, statistics, reporting, ethics, and claim scope through the primary SciXZ review routes.",
            "For each external issue record one disposition: incorporated, incorporated-with-revision, rejected, or unresolved, with a reason.",
            "Do not copy the provider's editorial score or wording into the final recommendation without independent justification.",
            "Produce the bilingual final-review JSON required by render_final_review_docx.py.",
        ],
        "final_review_contract": {
            "required": ["metadata", "decision", "overall_assessment", "strengths", "major_concerns", "minor_concerns", "external_signal_integration", "limitations"],
            "language_fields": ["zh", "en"],
            "external_dispositions": ["incorporated", "incorporated-with-revision", "rejected", "unresolved"],
        },
        "boundary": "This bundle imports an external signal. It is not itself a peer-review decision or a final manuscript review.",
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build the bounded PaperReview-to-SciXZ synthesis input.")
    parser.add_argument("--manuscript", required=True)
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--provider-review", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        bundle = build_bundle(Path(args.manuscript), _load_json(Path(args.artifact)), _load_json(Path(args.provider_review)))
    except (OSError, ValueError) as exc:
        parser.exit(2, f"PaperReview synthesis bundle blocked: {exc}\n")
    Path(args.output).write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": bundle["status"], "output": args.output}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
