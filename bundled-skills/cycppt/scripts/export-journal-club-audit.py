#!/usr/bin/env python3
"""Export human-auditable journal-club outline and panel ledger artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


LEDGER_FIELDS = (
    "asset_id",
    "figure_id",
    "panel_id",
    "source_section",
    "source_page",
    "caption_summary",
    "supported_claim",
    "visual_type",
    "include_decision",
    "include_score",
    "reason",
    "evidence_mode",
    "render_policy",
    "output_path",
    "citation",
    "exception_justification",
)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def inventory_items(payload: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("usable_assets", "assets", "items", "figures"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def asset_ids(slide: dict[str, Any]) -> list[str]:
    assets = slide.get("assets")
    if isinstance(assets, dict):
        assets = assets.get("required")
    if not isinstance(assets, list):
        return []
    return [str(item["asset_id"]) for item in assets if isinstance(item, dict) and item.get("asset_id")]


def export(plan_path: Path, inventory_path: Path, outline_path: Path, ledger_path: Path) -> dict[str, Any]:
    plan = load_json(plan_path)
    inventory = load_json(inventory_path)
    slides = [item for item in plan.get("slides", []) if isinstance(item, dict)]
    evidence = inventory_items(inventory)

    lines = ["# Deck outline", ""]
    for slide in slides:
        number = slide.get("slide_number", "?")
        role = slide.get("role", "unknown")
        title = slide.get("title", "")
        lines.extend([f"## {number}. {title}", "", f"- Role: `{role}`"])
        if slide.get("core_message"):
            lines.append(f"- Core message: {slide['core_message']}")
        if slide.get("claim_id"):
            lines.append(f"- Claim: `{slide['claim_id']}`")
        bound = asset_ids(slide)
        if bound:
            lines.append("- Evidence: " + ", ".join(f"`{item}`" for item in bound))
        interpretation = slide.get("interpretation")
        if isinstance(interpretation, dict):
            for label, field in (
                ("How to read", "how_to_read"),
                ("What it proves", "what_it_proves"),
                ("Caveat", "caveat"),
            ):
                if interpretation.get(field):
                    lines.append(f"- {label}: {interpretation[field]}")
        lines.append("")
    outline_path.parent.mkdir(parents=True, exist_ok=True)
    outline_path.write_text("\n".join(lines), encoding="utf-8")

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        writer.writeheader()
        for item in evidence:
            score = item.get("selection_score")
            row = {field: item.get(field, "") for field in LEDGER_FIELDS}
            row["include_score"] = score.get("include_score", "") if isinstance(score, dict) else ""
            writer.writerow(row)

    return {
        "outline": str(outline_path),
        "figure_ledger": str(ledger_path),
        "slide_count": len(slides),
        "evidence_count": len(evidence),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", required=True)
    parser.add_argument("--figure-inventory", required=True)
    parser.add_argument("--outline", required=True)
    parser.add_argument("--ledger", required=True)
    args = parser.parse_args()
    payload = export(
        Path(args.plan),
        Path(args.figure_inventory),
        Path(args.outline),
        Path(args.ledger),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
