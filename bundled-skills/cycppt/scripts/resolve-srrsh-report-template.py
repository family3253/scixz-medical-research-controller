#!/usr/bin/env python3
"""Resolve or inject Sir Run Run Shaw Hospital cover/ending template bindings."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "references" / "srrsh_report_templates"
MANIFEST_PATH = TEMPLATE_ROOT / "manifest.json"
STYLE_PROMPT_PATH = TEMPLATE_ROOT / "style_prompt.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_campus(value: str) -> str:
    text = str(value or "").strip().casefold()
    for prefix in (
        "浙江大学医学院附属邵逸夫医院",
        "浙大医学院附属邵逸夫医院",
        "邵逸夫医院",
        "sirrurrunshawhospital",
    ):
        text = text.replace(prefix.casefold(), "")
    text = re.sub(r"[\s\-—_()（）·]+", "", text)
    if text.endswith("院区"):
        text = text[: -len("院区")]
    return text


def resolve_campus(manifest: dict[str, Any], raw_campus: str | None) -> tuple[str, dict[str, Any]]:
    if not raw_campus:
        choices = "、".join(item["canonical_zh"] for item in manifest["campuses"].values())
        raise ValueError(f"邵逸夫医院汇报必须明确院区，可选：{choices}")

    wanted = normalize_campus(raw_campus)
    matches: list[tuple[str, dict[str, Any]]] = []
    for campus_id, item in manifest["campuses"].items():
        candidates = [campus_id, item.get("canonical_zh", ""), *(item.get("aliases") or [])]
        if wanted in {normalize_campus(candidate) for candidate in candidates}:
            matches.append((campus_id, item))
    if len(matches) == 1:
        return matches[0]
    if not matches:
        choices = "、".join(item["canonical_zh"] for item in manifest["campuses"].values())
        raise ValueError(f"无法识别院区：{raw_campus}。可选：{choices}")
    raise ValueError(f"院区名称存在歧义：{raw_campus}")


def absolute_resource(relative_path: str) -> str:
    return str((TEMPLATE_ROOT / relative_path).resolve())


def binding_payload(
    manifest: dict[str, Any],
    campus_id: str,
    campus: dict[str, Any],
    role: str,
) -> dict[str, Any]:
    if role == "cover":
        return {
            "mode": "page",
            "organization_template_id": manifest["template_id"],
            "organization": manifest["organization"]["zh"],
            "campus_id": campus_id,
            "campus": campus["canonical_zh"],
            "reference_image": absolute_resource(campus["cover"]),
            "source_template": absolute_resource(manifest["source_template"]),
            "source_slide": campus["source_slide"],
            "style_selector": str(STYLE_PROMPT_PATH.resolve()),
            "style_text": (
                f"邵逸夫医院{campus['canonical_zh']}工作汇报封面。严格保留该院区建筑照片、"
                "医院及合作机构标识、红色底栏和版式，仅替换议题、日期、姓名等字段。"
            ),
            "campus_locked": True,
        }
    ending = manifest["ending"]
    return {
        "mode": "page",
        "organization_template_id": manifest["template_id"],
        "organization": manifest["organization"]["zh"],
        "campus_id": campus_id,
        "campus": campus["canonical_zh"],
        "reference_image": absolute_resource(ending["image"]),
        "source_template": absolute_resource(manifest["source_template"]),
        "source_slide": ending["source_slide"],
        "style_selector": str(STYLE_PROMPT_PATH.resolve()),
        "style_text": "邵逸夫医院工作汇报通用结尾页。保留 THANK YOU、谢谢、医院及合作机构标识和红白构图。",
        "campus_locked": True,
        "campus_specific": False,
    }


def sorted_slides(plan: dict[str, Any]) -> list[dict[str, Any]]:
    slides = plan.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("ppt_plan.json must contain a non-empty slides array")
    return sorted(slides, key=lambda item: int(item.get("slide_number", 0)))


def inject_plan(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    campus_id: str,
    campus: dict[str, Any],
    role: str,
) -> dict[str, Any]:
    updated = copy.deepcopy(plan)
    slides = sorted_slides(updated)
    if role == "both" and len(slides) < 2:
        raise ValueError("cover and ending bindings require at least two slides")

    deck = updated.setdefault("deck", {})
    if not isinstance(deck, dict):
        raise ValueError("ppt_plan.json deck must be an object")
    deck["organization"] = manifest["organization"]["zh"]
    deck["campus"] = campus["canonical_zh"]
    deck["organization_template"] = {
        "template_id": manifest["template_id"],
        "campus_id": campus_id,
        "campus": campus["canonical_zh"],
        "strict_campus_match": True,
    }

    if role in {"cover", "both"}:
        slides[0]["template_binding"] = binding_payload(manifest, campus_id, campus, "cover")
    if role in {"ending", "both"}:
        slides[-1]["template_binding"] = binding_payload(manifest, campus_id, campus, "ending")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campus", help="院区名称：庆春、钱塘、阿拉尔、大运河或绍兴。")
    parser.add_argument("--role", choices=["cover", "ending", "both"], default="both")
    parser.add_argument("--plan", help="Optional ppt_plan.json to update with template bindings.")
    parser.add_argument("--out-plan", help="Output path for the updated plan. Required with --plan unless --in-place is used.")
    parser.add_argument("--in-place", action="store_true", help="Overwrite --plan after successful validation.")
    parser.add_argument("--list-campuses", action="store_true")
    args = parser.parse_args()

    manifest = load_json(MANIFEST_PATH)
    if args.list_campuses:
        print(json.dumps({key: value["canonical_zh"] for key, value in manifest["campuses"].items()}, ensure_ascii=False, indent=2))
        return 0

    try:
        campus_id, campus = resolve_campus(manifest, args.campus)
        result: dict[str, Any] = {
            "template_id": manifest["template_id"],
            "campus_id": campus_id,
            "campus": campus["canonical_zh"],
            "cover": binding_payload(manifest, campus_id, campus, "cover"),
            "ending": binding_payload(manifest, campus_id, campus, "ending"),
        }
        if args.plan:
            plan_path = Path(args.plan).expanduser().resolve()
            updated = inject_plan(load_json(plan_path), manifest, campus_id, campus, args.role)
            if args.in_place:
                out_path = plan_path
            elif args.out_plan:
                out_path = Path(args.out_plan).expanduser().resolve()
            else:
                raise ValueError("--out-plan is required with --plan unless --in-place is used")
            write_json(out_path, updated)
            result["updated_plan"] = str(out_path)
            result["role"] = args.role
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
