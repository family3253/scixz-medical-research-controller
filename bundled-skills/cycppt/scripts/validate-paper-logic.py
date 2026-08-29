#!/usr/bin/env python3
"""Validate journal-club paper logic and its panel-level evidence ledger."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_TEXT_FIELDS = (
    "central_problem",
    "knowledge_gap",
    "hypothesis_or_claim",
    "system_and_data",
    "study_design",
    "final_conclusion",
    "scope_boundary",
)
SCORE_FIELDS = (
    "centrality_to_claim",
    "closes_key_gap",
    "method_explanatory_value",
    "visual_readability",
    "redundancy",
    "excessive_detail",
)
VALID_SOURCE_SECTIONS = {"main_text", "supplement", "extended_data", "user_provided"}
VALID_DECISIONS = {"include", "maybe", "exclude"}
FIGURE_KINDS = {"figure", "chart", "medical_image", "flow_diagram"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def nonempty_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def nonempty_list(value: Any) -> bool:
    return isinstance(value, list) and bool(value)


def inventory_items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("usable_assets", "assets", "items", "figures"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def validate_inventory(items: list[dict[str, Any]], errors: list[str]) -> set[str]:
    included_ids: set[str] = set()
    seen: set[str] = set()
    for index, item in enumerate(items, 1):
        prefix = f"figure_inventory item {index}"
        asset_id = item.get("asset_id")
        if not nonempty_text(asset_id):
            errors.append(f"{prefix} must define asset_id")
            continue
        if asset_id in seen:
            errors.append(f"duplicate figure_inventory asset_id: {asset_id}")
        seen.add(asset_id)

        for field in ("figure_id", "caption_summary", "supported_claim", "visual_type", "reason"):
            if not nonempty_text(item.get(field)):
                errors.append(f"{prefix} ({asset_id}) must define {field}")

        section = item.get("source_section")
        if section not in VALID_SOURCE_SECTIONS:
            errors.append(f"{prefix} ({asset_id}) has invalid source_section: {section!r}")
        decision = item.get("include_decision")
        if decision not in VALID_DECISIONS:
            errors.append(f"{prefix} ({asset_id}) has invalid include_decision: {decision!r}")

        score = item.get("selection_score")
        if not isinstance(score, dict):
            errors.append(f"{prefix} ({asset_id}) must define selection_score")
        else:
            missing_scores = [field for field in SCORE_FIELDS if not isinstance(score.get(field), (int, float))]
            if missing_scores:
                errors.append(f"{prefix} ({asset_id}) selection_score missing numeric: {', '.join(missing_scores)}")
            elif not isinstance(score.get("include_score"), (int, float)):
                errors.append(f"{prefix} ({asset_id}) selection_score must define include_score")
            else:
                expected = sum(float(score[field]) for field in SCORE_FIELDS[:4]) - sum(
                    float(score[field]) for field in SCORE_FIELDS[4:]
                )
                if abs(float(score["include_score"]) - expected) > 1e-6:
                    errors.append(f"{prefix} ({asset_id}) include_score does not match the scoring formula")

        if decision == "include":
            included_ids.add(asset_id)
            if not nonempty_text(item.get("output_path") or item.get("crop_path")):
                errors.append(f"{prefix} ({asset_id}) included evidence must define output_path or crop_path")
            if section in {"supplement", "extended_data"} and not nonempty_text(item.get("exception_justification")):
                errors.append(f"{prefix} ({asset_id}) supplemental evidence requires exception_justification")

        kind = str(item.get("kind") or item.get("visual_type") or "").casefold()
        if kind in FIGURE_KINDS and item.get("render_policy") != "original_preferred":
            errors.append(f"{prefix} ({asset_id}) source figures/images must use render_policy=original_preferred")
        if kind == "table" and item.get("render_policy") not in {"original_preferred", "reconstruct_allowed"}:
            errors.append(f"{prefix} ({asset_id}) table render_policy must allow original or reconstruction")
    return included_ids


def validate(paper_logic_path: Path, figure_inventory_path: Path | None = None) -> dict[str, Any]:
    errors: list[str] = []
    try:
        logic = load_json(paper_logic_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {"passed": False, "errors": [f"cannot read paper_logic JSON: {exc}"]}
    if not isinstance(logic, dict):
        return {"passed": False, "errors": ["paper_logic must be a JSON object"]}

    if logic.get("mode") != "journal_club":
        errors.append("paper_logic.mode must be journal_club")
    for field in REQUIRED_TEXT_FIELDS:
        if not nonempty_text(logic.get(field)):
            errors.append(f"paper_logic must define non-empty {field}")

    identity = logic.get("bibliographic_identity")
    if not isinstance(identity, dict):
        errors.append("bibliographic_identity must be an object")
    else:
        for field in ("title", "journal", "year", "citation", "stable_identifier"):
            if not nonempty_text(str(identity.get(field) or "")):
                errors.append(f"bibliographic_identity must define {field}")

    team = logic.get("author_team")
    if not isinstance(team, dict):
        errors.append("author_team must be an object")
    else:
        for field in ("first_authors", "corresponding_authors", "affiliations", "source_anchors"):
            if not nonempty_list(team.get(field)):
                errors.append(f"author_team must define non-empty {field}")
        for field in ("collaboration_structure", "why_team_matters"):
            if not nonempty_text(team.get(field)):
                errors.append(f"author_team must define {field}")

    fit = logic.get("content_fit_audit")
    if not isinstance(fit, dict):
        errors.append("content_fit_audit must be an object")
    else:
        for field in ("target_slide_count", "recommended_min", "recommended_max"):
            if not isinstance(fit.get(field), int) or fit[field] <= 0:
                errors.append(f"content_fit_audit.{field} must be a positive integer")
        if fit.get("status") not in {"fit", "underfilled", "overfull", "user_override"}:
            errors.append("content_fit_audit.status is invalid")
        if not nonempty_text(fit.get("rationale")):
            errors.append("content_fit_audit.rationale must be non-empty")

    inventory_ids: set[str] | None = None
    inventory_count = 0
    if figure_inventory_path is not None:
        try:
            inventory = load_json(figure_inventory_path)
            items = inventory_items(inventory)
            inventory_count = len(items)
            if not items:
                errors.append("figure_inventory contains no evidence items")
            inventory_ids = validate_inventory(items, errors)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"cannot read figure_inventory JSON: {exc}")

    chain = logic.get("evidence_chain")
    seen_claims: set[str] = set()
    evidence_refs: set[str] = set()
    if not nonempty_list(chain):
        errors.append("evidence_chain must be a non-empty list")
    else:
        for index, item in enumerate(chain, 1):
            prefix = f"evidence_chain item {index}"
            if not isinstance(item, dict):
                errors.append(f"{prefix} must be an object")
                continue
            claim_id = item.get("claim_id")
            if not nonempty_text(claim_id):
                errors.append(f"{prefix} must define claim_id")
            elif claim_id in seen_claims:
                errors.append(f"duplicate claim_id: {claim_id}")
            else:
                seen_claims.add(claim_id)
            for field in ("claim", "experiment_or_analysis", "interpretation", "caveat"):
                if not nonempty_text(item.get(field)):
                    errors.append(f"{prefix} ({claim_id}) must define {field}")
            refs = item.get("evidence_refs")
            if not nonempty_list(refs) or not all(nonempty_text(ref) for ref in refs):
                errors.append(f"{prefix} ({claim_id}) must define non-empty evidence_refs")
            else:
                evidence_refs.update(refs)
                if inventory_ids is not None:
                    missing = sorted(set(refs) - inventory_ids)
                    if missing:
                        errors.append(f"{prefix} ({claim_id}) references evidence not marked include: {', '.join(missing)}")

    return {
        "passed": not errors,
        "paper_logic": str(paper_logic_path),
        "figure_inventory": str(figure_inventory_path) if figure_inventory_path else None,
        "metrics": {
            "claim_count": len(seen_claims),
            "referenced_evidence_count": len(evidence_refs),
            "inventory_item_count": inventory_count,
        },
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper-logic", required=True)
    parser.add_argument("--figure-inventory")
    args = parser.parse_args()
    payload = validate(
        Path(args.paper_logic),
        Path(args.figure_inventory) if args.figure_inventory else None,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
