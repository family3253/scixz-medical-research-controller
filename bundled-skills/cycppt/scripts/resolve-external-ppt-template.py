#!/usr/bin/env python3
"""Search and bind individual pages from the external PowerPoint page library."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST = Path.home() / ".cache" / "yixueAIganhuo-PPT" / "external_ppt_page_library" / "manifest.json"
ROLE_ALIASES = {
    "title": "cover", "cover": "cover", "封面": "cover",
    "agenda": "agenda", "目录": "agenda", "outline": "agenda",
    "section": "section_divider", "divider": "section_divider", "章节": "section_divider",
    "background": "background", "背景": "background",
    "objectives": "objectives", "objective": "objectives", "目的": "objectives",
    "methods": "methods", "method": "methods", "方法": "methods",
    "results": "results", "result": "results", "结果": "results",
    "discussion": "discussion", "讨论": "discussion",
    "conclusion": "conclusion", "summary": "conclusion", "总结": "conclusion", "结论": "conclusion",
    "references": "references", "参考文献": "references",
    "closing": "ending", "ending": "ending", "thanks": "ending", "致谢": "ending",
    "table": "table", "chart": "chart", "process": "process_diagram",
    "timeline": "timeline", "gantt": "timeline", "schedule": "timeline", "进度": "timeline",
}
NAVIGATION_MARKERS = {
    "horizontal": ("横排导航", "横向导航", "顶部导航", "horizontal navigation", "top navigation"),
    "vertical": ("竖排导航", "纵向导航", "左侧导航", "vertical navigation", "left navigation", "sidebar navigation"),
    "custom": ("导航栏", "导航条", "navigation bar", "navigation demo"),
}
ROLE_TITLE_MARKERS = {
    "agenda": ("content", "contents", "目录", "汇报框架", "outline"),
    "background": ("研究背景", "背景", "现状", "background"),
    "objectives": ("研究目标", "研究目的", "目标与内容", "objectives"),
    "methods": ("研究方法", "技术路线", "方法与思路", "methods"),
    "process_diagram": ("技术路线", "流程", "flow", "process", "route"),
    "results": ("研究成果", "主要结果", "结果", "results"),
    "mechanism": ("机制", "架构", "mechanism", "architecture"),
    "discussion": ("讨论", "局限", "创新点", "discussion", "limitations"),
    "conclusion": ("研究总结", "结论", "总结", "conclusion", "summary"),
    "ending": ("致谢", "谢谢", "thank", "ending"),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalize_role(value: Any) -> str:
    raw = str(value or "content").strip().casefold()
    return ROLE_ALIASES.get(raw, raw or "content")


def page_search_text(page: dict[str, Any]) -> str:
    return " ".join(str(value) for value in [
        page.get("page_id", ""), page.get("template_name", ""), page.get("title", ""),
        page.get("text", ""), page.get("role", ""), *(page.get("layout_tags") or []), *(page.get("semantic_tags") or []), *(page.get("tags") or []),
    ]).casefold()


def navigation_variant(page: dict[str, Any]) -> str:
    haystack = page_search_text(page)
    for variant, markers in NAVIGATION_MARKERS.items():
        if any(marker in haystack for marker in markers):
            return variant
    return "default"


def navigation_compatible(page: dict[str, Any], policy: str) -> bool:
    variant = navigation_variant(page)
    normalized = str(policy or "none").strip().casefold()
    if normalized in {"none", "family_default"}:
        return variant == "default"
    if normalized in {"horizontal", "vertical"}:
        return variant in {"default", normalized}
    return variant == "default"


def existing_external_template_ids(slides: list[dict[str, Any]]) -> set[str]:
    """Return already-bound external families, excluding organization-only bindings."""
    result: set[str] = set()
    for slide in slides:
        binding = slide.get("template_binding")
        if not isinstance(binding, dict) or not binding:
            continue
        template_id = str(binding.get("external_template_id") or "").strip()
        if template_id:
            result.add(template_id)
    return result


def match_score(
    page: dict[str, Any],
    *,
    query: str = "",
    role: str = "",
    layout: str = "",
    tags: list[str] | None = None,
    preferred_tags: list[str] | None = None,
) -> int:
    score = 0
    if role:
        wanted_role = normalize_role(role)
        actual_role = normalize_role(page.get("role"))
        if actual_role == wanted_role:
            score += 130
        elif wanted_role == "process_diagram" and actual_role == "methods":
            score += 85
        elif wanted_role == "mechanism" and actual_role in {"methods", "process_diagram"}:
            score += 60
        elif wanted_role in {"agenda", "background", "objectives", "methods", "process_diagram", "results", "mechanism", "discussion", "conclusion"} and actual_role in {"content", "image_focus", "table", "chart"}:
            score += 30
        else:
            score -= 40
    if layout:
        wanted_layout = layout.casefold()
        if wanted_layout in {str(value).casefold() for value in page.get("layout_tags", [])}:
            score += 70
        elif wanted_layout in page_search_text(page):
            score += 25
    haystack = page_search_text(page)
    if role:
        wanted_role = normalize_role(role)
        role_title_text = " ".join(
            str(value) for value in (page.get("title", ""), page.get("template_name", ""))
        ).casefold()
        if any(marker in role_title_text for marker in ROLE_TITLE_MARKERS.get(wanted_role, ())):
            score += 65
    for term in [value for value in query.casefold().replace("/", " ").replace("\\", " ").split() if value]:
        if term in haystack:
            score += 35
            if term in str(page.get("template_name", "")).casefold():
                score += 20
        else:
            score -= 15
    for tag in tags or []:
        if tag.casefold() in haystack:
            score += 30
        else:
            score -= 10
    actual_tags = {str(value).casefold() for value in page.get("tags", [])}
    score += sum(8 for value in preferred_tags or [] if value.casefold() in actual_tags)
    if page.get("source_aspect") == "16:9":
        score += 12
    if page.get("preview"):
        score += 8
    return score


def search_pages(
    manifest: dict[str, Any],
    *,
    query: str = "",
    role: str = "",
    layout: str = "",
    tags: list[str] | None = None,
    preferred_tags: list[str] | None = None,
    exclude_ids: set[str] | None = None,
    template_id: str = "",
    navigation_policy: str = "none",
    limit: int = 30,
) -> list[dict[str, Any]]:
    excluded = exclude_ids or set()
    ranked = []
    for page in manifest.get("pages", []):
        if page.get("page_id") in excluded:
            continue
        if template_id and page.get("template_id") != template_id:
            continue
        if not navigation_compatible(page, navigation_policy):
            continue
        score = match_score(page, query=query, role=role, layout=layout, tags=tags, preferred_tags=preferred_tags)
        if score > 0:
            ranked.append((score, page))
    ranked.sort(key=lambda pair: (-pair[0], pair[1].get("template_name", "").casefold(), int(pair[1].get("source_slide", 0))))
    return [dict(page, match_score=score) for score, page in ranked[:limit]]


def choose_master_template_id(
    slides: list[dict[str, Any]],
    manifest: dict[str, Any],
    *,
    query: str,
    tags: list[str],
    navigation_policy: str,
) -> str:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for page in manifest.get("pages", []):
        template_id = str(page.get("template_id") or "")
        if template_id and navigation_compatible(page, navigation_policy):
            grouped.setdefault(template_id, []).append(page)
    ranked: list[tuple[int, str]] = []
    for template_id, pages in grouped.items():
        total = 0
        covered = 0
        for slide in slides:
            role = normalize_role(slide.get("role"))
            layout = slide_layout(slide)
            title = str(slide.get("title") or slide.get("core_message") or "")
            scores = [
                match_score(page, query=" ".join(value for value in (query, title) if value), role=role, layout=layout, tags=tags)
                for page in pages
            ]
            best = max(scores, default=-100)
            total += best
            if best > 0:
                covered += 1
        total += covered * 40
        ranked.append((total, template_id))
    if not ranked:
        raise ValueError("No coherent template family is available")
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked[0][1]


def get_page(manifest: dict[str, Any], wanted: str) -> dict[str, Any]:
    matches = [page for page in manifest.get("pages", []) if page.get("page_id") == wanted]
    if len(matches) != 1:
        raise ValueError(f"Page template id not found: {wanted}")
    page = matches[0]
    if not Path(page["source_template"]).exists():
        raise ValueError(f"Source template is unavailable: {page['source_template']}")
    return page


def binding_payload(
    page: dict[str, Any],
    manifest_path: Path,
    style_selector: str,
    reason: str,
    confidence: float,
    *,
    master_template_id: str | None = None,
    navigation_policy: str = "none",
) -> dict[str, Any]:
    preview = manifest_path.parent / str(page["preview"])
    return {
        "mode": "page",
        "external_template_library": "external-graduation-ppt-templates",
        "external_template_id": page["template_id"],
        "external_page_id": page["page_id"],
        "source_template": page["source_template"],
        "source_slide": page["source_slide"],
        "reference_image": str(preview.resolve()),
        "style_selector": style_selector,
        "style_text": (
            f"本页采用页面模板 {page['page_id']}，来源“{page['template_name']}”第 {page['source_slide']} 页。"
            f"只继承该页主体内容区的构图、图文比例和留白；页面角色为 {page.get('role')}，"
            f"布局标签为 {'、'.join(page.get('layout_tags') or ['balanced'])}。"
            "整套 PPT 的页眉、页脚、导航条、Logo 区、标题起点、页码位置和品牌色由统一母版控制，"
            "不得因本页模板而移动、增删或更换导航形态。"
            "替换原模板中的姓名、学校、课题、日期、数据、徽标和示例文字，不得把这些占位内容带入新汇报。"
        ),
        "template_page_role": page.get("role"),
        "template_layout_tags": page.get("layout_tags") or [],
        "template_tags": page.get("tags") or [],
        "template_semantic_tags": page.get("semantic_tags") or [],
        "placeholder_flags": page.get("placeholder_flags") or [],
        "placeholder_cleanup_required": bool(page.get("placeholder_risk")),
        "confidence": round(float(confidence), 3),
        "reason": reason,
        "external_source_required": True,
        "master_template_id": master_template_id or page["template_id"],
        "content_layout_selected_independently": True,
        "navigation_policy": navigation_policy,
        "deck_chrome_locked": True,
    }


def slide_layout(slide: dict[str, Any]) -> str:
    layout = slide.get("layout")
    if isinstance(layout, dict):
        return str(layout.get("structure") or "")
    return str(layout or "")


def bind_exact(plan: dict[str, Any], slide_id: str, page: dict[str, Any], manifest_path: Path, style_selector: str) -> dict[str, Any]:
    updated = copy.deepcopy(plan)
    for slide in updated.get("slides", []):
        if slide.get("slide_id") == slide_id:
            binding = binding_payload(page, manifest_path, style_selector, "Explicit page_id selection", 1.0)
            binding["template_selection_mode"] = "explicit"
            binding["template_locked"] = True
            slide["template_binding"] = binding
            return updated
    raise ValueError(f"Slide not found in plan: {slide_id}")


def auto_bind(
    plan: dict[str, Any],
    manifest: dict[str, Any],
    manifest_path: Path,
    style_selector: str,
    query: str,
    tags: list[str],
    replace_existing: bool = False,
    *,
    master_template_id: str | None = None,
    navigation_policy: str | None = None,
    allow_cross_family: bool = False,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    updated = copy.deepcopy(plan)
    slides = updated.get("slides")
    if not isinstance(slides, list) or not slides:
        raise ValueError("ppt_plan.json must contain a non-empty slides array")
    deck = updated.setdefault("deck", {})
    if not isinstance(deck, dict):
        raise ValueError("ppt_plan.json deck must be an object")
    selected_navigation_policy = str(navigation_policy or deck.get("navigation_policy") or "none")
    selected_master = str(master_template_id or deck.get("master_template_id") or "") or None
    existing_families = existing_external_template_ids(slides)
    if not allow_cross_family and not replace_existing and len(existing_families) > 1:
        raise ValueError(
            "Existing template bindings span multiple external template families; "
            "normalize them to one family or explicitly use --allow-cross-family"
        )
    if selected_master is None and len(existing_families) == 1:
        selected_master = next(iter(existing_families))
    if selected_master and not allow_cross_family and not replace_existing:
        conflicting = existing_families - {selected_master}
        if conflicting:
            raise ValueError(
                f"Existing binding conflicts with master_template_id={selected_master}: "
                + ", ".join(sorted(conflicting))
            )
    if selected_master is None and not allow_cross_family:
        selected_master = choose_master_template_id(
            slides,
            manifest,
            query=query,
            tags=tags,
            navigation_policy=selected_navigation_policy,
        )
    used: set[str] = set()
    preferred_tags: list[str] = []
    selections = []
    for slide in sorted(slides, key=lambda item: int(item.get("slide_number", 0))):
        existing_binding = slide.get("template_binding")
        if isinstance(existing_binding, dict) and existing_binding and not replace_existing:
            existing_page_id = existing_binding.get("external_page_id")
            if existing_page_id:
                used.add(str(existing_page_id))
            locked_organization = existing_binding.get("campus_locked") is True
            selections.append({
                "slide_id": slide.get("slide_id"),
                "page_id": existing_page_id,
                "mode": "preserved_locked_binding" if locked_organization else "preserved_existing_binding",
                "reason": "Existing campus-locked organization template was preserved" if locked_organization else "Existing explicit or preplanned page template binding was preserved",
            })
            continue
        role = normalize_role(slide.get("role"))
        layout = slide_layout(slide)
        title = str(slide.get("title") or slide.get("core_message") or "")
        family_filter = "" if allow_cross_family else str(selected_master or "")
        candidates = search_pages(manifest, query=" ".join(value for value in (query, title) if value), role=role, layout=layout, tags=tags, preferred_tags=preferred_tags, exclude_ids=used, template_id=family_filter, navigation_policy=selected_navigation_policy, limit=10)
        if not candidates:
            candidates = search_pages(manifest, query=query, role=role, tags=tags, preferred_tags=preferred_tags, exclude_ids=used, template_id=family_filter, navigation_policy=selected_navigation_policy, limit=10)
        if not candidates:
            candidates = search_pages(manifest, query=query, tags=tags, preferred_tags=preferred_tags, exclude_ids=used, template_id=family_filter, navigation_policy=selected_navigation_policy, limit=10)
        if not candidates:
            raise ValueError(f"No page template candidate found for slide: {slide.get('slide_id')}")
        selected = candidates[0]
        used.add(selected["page_id"])
        if not preferred_tags:
            preferred_tags = list(selected.get("tags") or [])
        confidence = min(0.99, max(0.55, selected["match_score"] / 260))
        reason = f"Automatic page-level match: role={role}, layout={layout or 'unspecified'}, score={selected['match_score']}"
        binding = binding_payload(selected, manifest_path, style_selector, reason, confidence, master_template_id=selected_master, navigation_policy=selected_navigation_policy)
        binding["template_selection_mode"] = "automatic"
        binding["template_locked"] = False
        slide["template_binding"] = binding
        selections.append({"slide_id": slide.get("slide_id"), "page_id": selected["page_id"], "template_name": selected["template_name"], "source_slide": selected["source_slide"], "score": selected["match_score"], "role": role, "layout": layout})
    deck["template_mode"] = "per_page_within_master_family" if not allow_cross_family else "per_page_cross_family_explicit"
    deck["template_consistency_policy"] = "single_template_family" if not allow_cross_family else "cross_family_allowed"
    deck["master_template_id"] = selected_master
    deck["navigation_policy"] = selected_navigation_policy
    deck["deck_chrome_locked"] = True
    deck["external_template_library"] = {"library_id": manifest.get("library_id"), "manifest": str(manifest_path), "selection_count": len(selections)}
    return updated, selections


def brief(page: dict[str, Any]) -> dict[str, Any]:
    result = {key: page.get(key) for key in ("page_id", "template_id", "template_name", "source_slide", "title", "role", "layout_tags", "tags", "source_template", "preview")}
    if "match_score" in page:
        result["match_score"] = page["match_score"]
    return result


def main() -> int:
    # Windows PowerShell commonly starts with a GBK console encoding.  Search
    # results contain Chinese template titles, so force UTF-8 output when the
    # stream supports reconfiguration instead of failing before emitting JSON.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--query", default="")
    parser.add_argument("--role", default="")
    parser.add_argument("--layout", default="")
    parser.add_argument("--tag", action="append", default=[])
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--page-id", help="Exact page template id.")
    parser.add_argument("--plan", help="ppt_plan.json to update.")
    parser.add_argument("--slide-id", help="Target slide for --page-id binding.")
    parser.add_argument("--auto-bind", action="store_true", help="Choose a different page template for every plan slide.")
    parser.add_argument("--replace-existing", action="store_true", help="Allow automatic selection to replace existing non-empty template bindings.")
    parser.add_argument("--master-template-id", help="Lock automatic page selection to one external template family.")
    parser.add_argument("--navigation-policy", choices=["none", "family_default", "horizontal", "vertical"], help="Deck-wide navigation policy. Default: none.")
    parser.add_argument("--allow-cross-family", action="store_true", help="Explicitly allow automatic selection across unrelated template families.")
    parser.add_argument("--out-plan")
    parser.add_argument("--in-place", action="store_true")
    parser.add_argument("--style-selector", default="001")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).expanduser().resolve()
    manifest = load_json(manifest_path)
    if not args.plan:
        if args.page_id:
            print(json.dumps(brief(get_page(manifest, args.page_id)), ensure_ascii=False, indent=2))
        else:
            results = search_pages(manifest, query=args.query, role=args.role, layout=args.layout, tags=args.tag, limit=args.limit)
            print(json.dumps([brief(item) for item in results], ensure_ascii=False, indent=2))
        return 0

    plan_path = Path(args.plan).expanduser().resolve()
    plan = load_json(plan_path)
    try:
        if args.auto_bind:
            updated, selections = auto_bind(
                plan,
                manifest,
                manifest_path,
                args.style_selector,
                args.query,
                args.tag,
                replace_existing=args.replace_existing,
                master_template_id=args.master_template_id,
                navigation_policy=args.navigation_policy,
                allow_cross_family=args.allow_cross_family,
            )
        elif args.page_id and args.slide_id:
            page = get_page(manifest, args.page_id)
            updated = bind_exact(plan, args.slide_id, page, manifest_path, args.style_selector)
            selections = [{"slide_id": args.slide_id, "page_id": args.page_id, "mode": "explicit"}]
        else:
            raise ValueError("With --plan, use --auto-bind or provide both --page-id and --slide-id")
        if args.in_place:
            out_path = plan_path
        elif args.out_plan:
            out_path = Path(args.out_plan).expanduser().resolve()
        else:
            raise ValueError("--out-plan is required with --plan unless --in-place is used")
        write_json(out_path, updated)
        print(json.dumps({"updated_plan": str(out_path), "selections": selections}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"passed": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
