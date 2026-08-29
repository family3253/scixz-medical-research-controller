#!/usr/bin/env python3
"""Validate a claim-driven journal-club PPT plan against paper logic and evidence."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


RESULT_ROLES = {"result", "results", "evidence", "mechanism", "key_result"}
GENERIC_RESULT_TITLE = re.compile(
    r"^(?:研究)?(?:主要)?结果(?:[一二三四五六七八九十\d]*)?$|^(?:figure|fig\.?|table|图|表)\s*\d+[a-z]?$",
    re.IGNORECASE,
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def inventory_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("usable_assets", "assets", "items", "figures"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return []


def required_assets(slide: dict[str, Any]) -> list[dict[str, Any]]:
    assets = slide.get("assets")
    if isinstance(assets, dict):
        assets = assets.get("required")
    if not isinstance(assets, list):
        return []
    return [item for item in assets if isinstance(item, dict)]


def validate(plan_path: Path, paper_logic_path: Path, figure_inventory_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    try:
        plan = load_json(plan_path)
        logic = load_json(paper_logic_path)
        inventory = load_json(figure_inventory_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"passed": False, "errors": [f"cannot read validation input: {exc}"]}
    if not all(isinstance(value, dict) for value in (plan, logic, inventory)):
        return {"passed": False, "errors": ["plan, paper_logic, and figure_inventory must be JSON objects"]}

    deck = plan.get("deck")
    slides = plan.get("slides")
    if not isinstance(deck, dict):
        errors.append("plan.deck must be an object")
        deck = {}
    if not isinstance(slides, list) or not slides:
        errors.append("plan.slides must be a non-empty list")
        slides = []
    if deck.get("authoring_mode") not in {"JOURNAL_CLUB", "journal_club"}:
        errors.append("deck.authoring_mode must be JOURNAL_CLUB")

    numbers = [slide.get("slide_number") for slide in slides if isinstance(slide, dict)]
    if numbers != list(range(1, len(slides) + 1)):
        errors.append("slide_number values must be continuous and ordered from 1")
    total = deck.get("total_slides")
    if total != len(slides):
        errors.append("deck.total_slides must equal the number of slides")

    fit = logic.get("content_fit_audit") if isinstance(logic, dict) else None
    if isinstance(fit, dict) and fit.get("target_slide_count") != len(slides):
        errors.append("confirmed content_fit_audit.target_slide_count must equal plan slide count")

    chain = logic.get("evidence_chain") if isinstance(logic, dict) else None
    claims = {
        item.get("claim_id"): item
        for item in chain or []
        if isinstance(item, dict) and nonempty_text(item.get("claim_id"))
    }
    included = {
        item.get("asset_id"): item
        for item in inventory_items(inventory)
        if item.get("include_decision") == "include" and nonempty_text(item.get("asset_id"))
    }

    roles = {str(slide.get("role") or "").casefold() for slide in slides if isinstance(slide, dict)}
    for required_role in ("title", "author_team", "background", "methods", "discussion"):
        if required_role not in roles:
            errors.append(f"journal-club plan must include role={required_role}")

    author_slides = [slide for slide in slides if isinstance(slide, dict) and str(slide.get("role")).casefold() == "author_team"]
    if author_slides:
        author_slide = author_slides[0]
        if not nonempty_list(author_slide.get("references")):
            errors.append("author_team slide must cite source anchors")

    used_assets: set[str] = set()
    result_count = 0
    for slide in slides:
        if not isinstance(slide, dict):
            errors.append("every slide must be an object")
            continue
        role = str(slide.get("role") or "").casefold()
        if role not in RESULT_ROLES:
            continue
        result_count += 1
        slide_id = slide.get("slide_id") or f"slide{slide.get('slide_number')}"
        title = str(slide.get("title") or "").strip()
        if not title or GENERIC_RESULT_TITLE.fullmatch(title):
            errors.append(f"{slide_id} must use a claim-driven result title")
        claim_id = slide.get("claim_id")
        if claim_id not in claims:
            errors.append(f"{slide_id} claim_id does not map to paper_logic.evidence_chain: {claim_id!r}")
            allowed_refs: set[str] = set()
        else:
            allowed_refs = set(claims[claim_id].get("evidence_refs") or [])

        bound = {item.get("asset_id") for item in required_assets(slide) if nonempty_text(item.get("asset_id"))}
        valid_bound = bound & set(included) & allowed_refs
        if not valid_bound:
            errors.append(f"{slide_id} must bind included evidence referenced by its claim")
        used_assets.update(valid_bound)

        interpretation = slide.get("interpretation")
        if not isinstance(interpretation, dict):
            errors.append(f"{slide_id} must define interpretation")
        else:
            for field in ("how_to_read", "what_it_proves", "caveat"):
                if not nonempty_text(interpretation.get(field)):
                    errors.append(f"{slide_id} interpretation.{field} must be non-empty")
        if not nonempty_text(slide.get("speaker_notes_zh")):
            errors.append(f"{slide_id} must define speaker_notes_zh")

    if result_count == 0:
        errors.append("journal-club plan must include at least one result/evidence slide")

    orphaned = sorted(set(included) - used_assets)
    if orphaned:
        errors.append("included evidence is not used by any claim-driven result slide: " + ", ".join(orphaned))

    appraisal = plan.get("journal_club")
    if not isinstance(appraisal, dict):
        errors.append("plan.journal_club must be an object")
    else:
        for field in ("strengths", "limitations", "follow_up_experiments"):
            if not nonempty_list(appraisal.get(field)):
                errors.append(f"plan.journal_club.{field} must be a non-empty list")
        if not nonempty_text(appraisal.get("scope_boundary")):
            errors.append("plan.journal_club.scope_boundary must be non-empty")
        questions = appraisal.get("discussion_questions")
        if not isinstance(questions, list) or not 2 <= len(questions) <= 4 or not all(nonempty_text(q) for q in questions):
            errors.append("plan.journal_club.discussion_questions must contain 2-4 non-empty questions")

    return {
        "passed": not errors,
        "plan": str(plan_path),
        "metrics": {
            "slide_count": len(slides),
            "result_slide_count": result_count,
            "claim_count": len(claims),
            "included_evidence_count": len(included),
            "used_evidence_count": len(used_assets),
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--paper-logic", required=True)
    parser.add_argument("--figure-inventory", required=True)
    args = parser.parse_args()
    payload = validate(Path(args.plan), Path(args.paper_logic), Path(args.figure_inventory))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
