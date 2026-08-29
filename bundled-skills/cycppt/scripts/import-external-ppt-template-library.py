#!/usr/bin/env python3
"""Build a page-level catalog for an external folder of PowerPoint templates.

The source decks stay in place. The generated catalog contains one record and one
preview image per source slide so later PPT planning can select a different page
template for every generated slide.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from zipfile import BadZipFile, ZipFile


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = Path.home() / ".cache" / "yixueAIganhuo-PPT" / "external_ppt_page_library"
SUPPORTED_EXTENSIONS = {".ppt", ".pptx", ".pot", ".potx", ".pps", ".ppsx"}
OPENXML_EXTENSIONS = {".pptx", ".potx", ".ppsx"}
SLIDE_RE = re.compile(r"^ppt/slides/slide(?P<number>\d+)\.xml$")
TEXT_RE = re.compile(r"<a:t(?:\s[^>]*)?>(.*?)</a:t>", re.DOTALL)


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stable_id(relative_path: str) -> str:
    import hashlib

    value = relative_path.replace("\\", "/").casefold().encode("utf-8")
    return "ext-" + hashlib.sha256(value).hexdigest()[:12]


def page_id(template_id: str, number: int) -> str:
    return f"{template_id}-s{number:03d}"


def clean_xml_text(raw: bytes) -> str:
    from html import unescape

    decoded = raw.decode("utf-8", errors="ignore")
    values = [unescape(re.sub(r"\s+", " ", value)).strip() for value in TEXT_RE.findall(decoded)]
    return " | ".join(value for value in values if value)


def slide_number(name: str) -> int:
    match = SLIDE_RE.match(name)
    return int(match.group("number")) if match else 0


def aspect_from_presentation(raw: bytes) -> tuple[float | None, str]:
    decoded = raw.decode("utf-8", errors="ignore")
    match = re.search(r"<p:sldSz[^>]*\bcx=\"(?P<cx>\d+)\"[^>]*\bcy=\"(?P<cy>\d+)\"", decoded)
    if not match:
        return None, "unknown"
    cx, cy = int(match.group("cx")), int(match.group("cy"))
    if cy == 0:
        return None, "unknown"
    ratio = cx / cy
    if abs(ratio - 16 / 9) < 0.03:
        label = "16:9"
    elif abs(ratio - 4 / 3) < 0.03:
        label = "4:3"
    else:
        label = f"{ratio:.3f}:1"
    return round(ratio, 4), label


def classify_file(relative_path: str, text: str) -> dict[str, Any]:
    filename = Path(relative_path).name.casefold()
    value = f"{relative_path} {text}".casefold()
    if "开题" in filename:
        category = "开题答辩"
    elif "文献" in filename or "组会" in filename:
        category = "文献汇报"
    elif "毕业" in filename:
        category = "毕业答辩"
    elif "答辩" in filename or "学术答辩合集" in value:
        category = "学术答辩"
    elif "开题答辩ppt" in value:
        category = "开题答辩"
    elif "论文答辩汇报" in value:
        category = "学术答辩"
    else:
        category = "通用学术模板"
    colors = [("红", "红色"), ("蓝", "蓝色"), ("绿", "绿色"), ("紫", "紫色"), ("橙", "橙色"), ("灰", "灰色"), ("黑", "黑色"), ("粉", "粉色"), ("棕", "棕色"), ("米", "米色")]
    color_tags = [label for token, label in colors if token in value]
    universities = [name for name in ("北大", "清华", "浙大", "复旦", "同济", "中山", "华科") if name in value]
    nav_tags = []
    for token, label in (("上导航", "上导航栏"), ("横向导航", "横向导航栏"), ("竖向导航", "竖向导航栏"), ("左侧导航", "左侧导航栏"), ("右侧导航", "右侧导航栏"), ("导航栏", "导航栏")):
        if token in value and label not in nav_tags:
            nav_tags.append(label)
    tags = [category, *color_tags, *universities, *nav_tags]
    if any(token in value for token in ("医学", "医院", "医疗", "临床")):
        tags.append("医学")
    if "动态" in value:
        tags.append("动态")
    if "静态" in value:
        tags.append("静态")
    return {
        "category": category,
        "colors": list(dict.fromkeys(color_tags)),
        "organizations": list(dict.fromkeys(universities)),
        "navigation": nav_tags,
        "tags": list(dict.fromkeys(tags)),
    }


def extract_title(raw: bytes) -> str:
    decoded = raw.decode("utf-8", errors="ignore")
    candidates: list[tuple[int, int, str]] = []
    for block in re.findall(r"<p:sp(?:\s[^>]*)?>.*?</p:sp>", decoded, re.DOTALL):
        values = [html.unescape(re.sub(r"\s+", " ", value)).strip() for value in TEXT_RE.findall(block)]
        text = " ".join(value for value in values if value).strip()
        if not text:
            continue
        is_title = bool(re.search(r"<p:ph[^>]*type=\"(?:title|ctrTitle)\"", block))
        sizes = [int(value) for value in re.findall(r"\bsz=\"(\d+)\"", block)]
        max_size = max(sizes, default=0)
        candidates.append((1 if is_title else 0, max_size, text))
    if not candidates:
        return ""
    candidates.sort(key=lambda item: (-item[0], -item[1], len(item[2])))
    return candidates[0][2][:300]


def classify_page(number: int, total: int, text: str, counts: dict[str, int], file_meta: dict[str, Any], title: str = "") -> tuple[str, list[str]]:
    value = text.casefold()
    headline = (title or text.split(" | ", 1)[0]).casefold()
    if any(token in headline for token in ("致谢", "谢谢", "thank you", "thanks", "鸣谢")):
        role = "ending"
    elif any(token in headline for token in ("目录", "contents", "agenda", "outline")):
        role = "agenda"
    elif any(token in headline for token in ("参考文献", "references", "bibliography")):
        role = "references"
    elif any(token in headline for token in ("研究背景", "背景", "现状", "研究意义", "问题提出")):
        role = "background"
    elif any(token in headline for token in ("研究目的", "研究目标", "目标与假设", "aim", "objective")):
        role = "objectives"
    elif any(token in headline for token in ("研究方法", "方法学", "材料与方法", "研究设计", "技术路线", "workflow", "method")):
        role = "methods"
    elif any(token in headline for token in ("结果", "发现", "数据分析", "outcome", "result")):
        role = "results"
    elif any(token in headline for token in ("讨论", "解释", "局限", "discussion")):
        role = "discussion"
    elif any(token in headline for token in ("结论", "总结", "展望", "conclusion", "take home")):
        role = "conclusion"
    elif number == 1 and len(text) < 360:
        role = "cover"
    elif len(text) < 140 and number not in (1, total) and counts["text_shapes"] <= 5:
        role = "section_divider"
    elif counts["tables"] and any(token in value for token in ("进度", "计划", "阶段", "时间安排", "x月", "月—", "月-")):
        role = "timeline"
    elif counts["tables"]:
        role = "table"
    elif counts["charts"]:
        role = "chart"
    elif counts["diagrams"]:
        role = "process_diagram"
    elif counts["pictures"] >= 2 and len(text) < 420:
        role = "image_focus"
    elif len(text) > 900:
        role = "dense_text"
    else:
        role = "content"

    layout = []
    if role in {"cover", "ending", "section_divider"}:
        layout.append(role)
    if counts["tables"]:
        layout.append("table_focus")
    if role == "timeline":
        layout.extend(["timeline", "gantt", "schedule"])
    if counts["charts"]:
        layout.append("chart_focus")
    if counts["diagrams"]:
        layout.append("diagram_focus")
    if counts["pictures"]:
        layout.append("image_focus")
    if counts["text_shapes"] >= 4 and counts["pictures"] >= 1:
        layout.append("text_plus_visual")
    elif counts["text_shapes"] >= 5:
        layout.append("multi_panel_text")
    elif counts["text_shapes"] <= 2 and counts["pictures"] == 0:
        layout.append("minimal")
    else:
        layout.append("balanced")
    if file_meta.get("aspect"):
        layout.append(file_meta["aspect"])
    return role, list(dict.fromkeys(layout))


def semantic_page_tags(role: str, title: str, text: str, counts: dict[str, int]) -> list[str]:
    value = f"{title} {text}".casefold()
    tags = [role]
    mapping = {
        "cover": ["academic", "title_page"],
        "agenda": ["toc", "contents"],
        "methods": ["workflow", "technical_route", "process"],
        "results": ["data_analysis", "evidence"],
        "chart": ["data_analysis", "results", "chart"],
        "table": ["data_table"],
        "timeline": ["timeline", "gantt", "schedule", "research_plan"],
        "ending": ["acknowledgement", "conclusion"],
        "process_diagram": ["workflow", "process", "diagram"],
    }
    tags.extend(mapping.get(role, []))
    if "技术路线" in value:
        tags.extend(["technical_route", "workflow"])
    if "饼图" in value or "比例" in value or "占比" in value:
        tags.append("pie_chart_candidate")
    if counts.get("pictures", 0) >= 2:
        tags.append("multi_image")
    if counts.get("charts", 0) >= 2:
        tags.append("multi_chart")
    return list(dict.fromkeys(tags))


def placeholder_flags(title: str, text: str) -> list[str]:
    value = f"{title} {text}"
    checks = [
        (r"(?i)xxxx|20xx|xx月|xx日", "masked_placeholder"),
        (r"输入内容|点击添加|添加标题|请输入|示例文字", "instruction_placeholder"),
        (r"研究主题\s*\d+|step\s*\d+", "generic_structure_placeholder"),
        (r"(?i)lorem|ipsum", "lorem_placeholder"),
    ]
    flags = [label for pattern, label in checks if re.search(pattern, value)]
    lowered = value.casefold()
    if any(token in title for token in ("总结", "致谢")) and any(token in lowered for token in ("background", "significance", "研究背景")):
        flags.append("title_subtitle_semantic_mismatch")
    return list(dict.fromkeys(flags))


def xml_counts(raw: bytes) -> dict[str, int]:
    text = raw.decode("utf-8", errors="ignore")
    return {
        "text_shapes": text.count("<p:sp"),
        "pictures": text.count("<p:pic"),
        "graphic_frames": text.count("<p:graphicFrame"),
        "tables": text.count("<a:tbl"),
        "charts": text.count("/charts/chart"),
        "diagrams": text.count("/diagrams/"),
        "media": text.count("/media/"),
    }


def positions(raw: bytes) -> dict[str, float | int]:
    decoded = raw.decode("utf-8", errors="ignore")
    points = [(int(x), int(y), int(cx), int(cy)) for x, y, cx, cy in re.findall(r"<a:off[^>]*x=\"(\d+)\"[^>]*y=\"(\d+)\"[^>]*>.*?<a:ext[^>]*cx=\"(\d+)\"[^>]*cy=\"(\d+)\"", decoded, re.DOTALL)]
    if not points:
        return {"shape_count": 0, "left_fraction": None, "right_fraction": None}
    centers = [x + cx / 2 for x, _, cx, _ in points]
    return {
        "shape_count": len(points),
        "left_fraction": round(sum(center < 4500000 for center in centers) / len(centers), 3),
        "right_fraction": round(sum(center >= 4500000 for center in centers) / len(centers), 3),
    }


def inspect_openxml(path: Path, root: Path, template_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    with ZipFile(path) as archive:
        names = archive.namelist()
        slide_names = sorted((name for name in names if re.match(r"^ppt/slides/slide\d+\.xml$", name)), key=slide_number)
        presentation = archive.read("ppt/presentation.xml") if "ppt/presentation.xml" in names else b""
        ratio, aspect = aspect_from_presentation(presentation)
        texts = []
        pages = []
        file_meta = {"aspect": aspect, "aspect_ratio": ratio}
        for name in slide_names:
            number = slide_number(name)
            raw = archive.read(name)
            text = clean_xml_text(raw)
            title = extract_title(raw) or (text.split(" | ", 1)[0] if text else "")
            counts = xml_counts(raw)
            rel_name = f"ppt/slides/_rels/slide{number}.xml.rels"
            if rel_name in names:
                rel_text = archive.read(rel_name).decode("utf-8", errors="ignore")
                counts["charts"] = rel_text.count("../charts/")
                counts["diagrams"] = rel_text.count("../diagrams/")
                counts["media"] = rel_text.count("../media/")
            pos = positions(raw)
            role, layout_tags = classify_page(number, len(slide_names), text, counts, file_meta, title=title)
            semantic_tags = semantic_page_tags(role, title, text, counts)
            placeholders = placeholder_flags(title, text)
            pages.append({
                "page_id": page_id(template_id, number),
                "template_id": template_id,
                "source_slide": number,
                "title": title,
                "text": text[:4000],
                "role": role,
                "layout_tags": layout_tags,
                "semantic_tags": semantic_tags,
                "placeholder_flags": placeholders,
                "placeholder_risk": bool(placeholders),
                "shape_counts": counts,
                "positions": pos,
                "preview": None,
            })
            if text:
                texts.append(text)
        meta = {
            "slide_count": len(slide_names),
            "aspect_ratio": ratio,
            "aspect": aspect,
            "sample_text": " || ".join(texts[:5])[:4000],
        }
        return meta, pages


def inspect_legacy_with_com(path: Path, template_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import win32com.client  # type: ignore

    app = win32com.client.DispatchEx("PowerPoint.Application")
    presentation = None
    try:
        presentation = app.Presentations.Open(str(path), True, False, False)
        slide_count = int(presentation.Slides.Count)
        width, height = float(presentation.PageSetup.SlideWidth), float(presentation.PageSetup.SlideHeight)
        ratio = width / height if height else None
        aspect = "16:9" if ratio and abs(ratio - 16 / 9) < 0.03 else "4:3" if ratio and abs(ratio - 4 / 3) < 0.03 else "legacy-ppt"
        pages = []
        for index in range(1, slide_count + 1):
            texts = []
            slide = presentation.Slides(index)
            for shape_index in range(1, int(slide.Shapes.Count) + 1):
                shape = slide.Shapes(shape_index)
                try:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        texts.append(str(shape.TextFrame.TextRange.Text).strip())
                except Exception:
                    continue
            text = " | ".join(value for value in texts if value)
            counts = {"text_shapes": len(texts), "pictures": 0, "graphic_frames": 0, "tables": 0, "charts": 0, "diagrams": 0, "media": 0}
            role, layout_tags = classify_page(index, slide_count, text, counts, {"aspect": aspect})
            title = texts[0] if texts else ""
            pages.append({"page_id": page_id(template_id, index), "template_id": template_id, "source_slide": index, "title": title, "text": text[:4000], "role": role, "layout_tags": layout_tags, "semantic_tags": semantic_page_tags(role, title, text, counts), "placeholder_flags": placeholder_flags(title, text), "placeholder_risk": bool(placeholder_flags(title, text)), "shape_counts": counts, "positions": {}, "preview": None})
        return {"slide_count": slide_count, "aspect_ratio": round(ratio, 4) if ratio else None, "aspect": aspect, "sample_text": ""}, pages
    finally:
        if presentation is not None:
            presentation.Close()
        app.Quit()


def render_previews(source_files: list[Path], records: list[dict[str, Any]], preview_dir: Path, width: int, overwrite: bool) -> None:
    import pythoncom  # type: ignore
    import win32com.client  # type: ignore

    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_template[record["template_id"]].append(record)
    source_by_template = {stable_id(path.relative_to(source_files[0].parents[0]).as_posix()): path for path in []}
    del source_by_template
    pythoncom.CoInitialize()
    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        for deck_index, path in enumerate(source_files, 1):
            template_id = stable_id(path.relative_to(SOURCE_ROOT).as_posix())
            pages = sorted(by_template.get(template_id, []), key=lambda item: item["source_slide"])
            if not pages:
                continue
            presentation = None
            try:
                presentation = app.Presentations.Open(str(path), True, False, False)
                slide_width = float(presentation.PageSetup.SlideWidth)
                slide_height = float(presentation.PageSetup.SlideHeight)
                height = max(1, round(width * slide_height / slide_width)) if slide_width else round(width * 9 / 16)
                for record in pages:
                    output = preview_dir / f"{record['page_id']}.jpg"
                    if output.exists() and not overwrite:
                        record["preview"] = f"previews/{output.name}"
                        continue
                    presentation.Slides(record["source_slide"]).Export(str(output), "JPG", width, height)
                    record["preview"] = f"previews/{output.name}"
                print(f"rendered {deck_index}/{len(source_files)}: {path.name} ({len(pages)} pages)", flush=True)
            except Exception as exc:
                print(f"render failed: {path}: {exc}", file=sys.stderr, flush=True)
            finally:
                if presentation is not None:
                    presentation.Close()
    finally:
        app.Quit()
        pythoncom.CoUninitialize()


def dominant_color(path: Path) -> str | None:
    try:
        from PIL import Image

        with Image.open(path) as image:
            image = image.convert("RGB").resize((48, 27))
            colors = image.quantize(colors=8).getpalette()
            histogram = image.quantize(colors=8).getcolors()
            if not histogram:
                return None
            _, index = max(histogram)
            rgb = tuple(colors[index * 3:index * 3 + 3])
            return "#%02x%02x%02x" % rgb
    except Exception:
        return None


def write_catalog(manifest: dict[str, Any], output: Path) -> None:
    payload = [{
        "page_id": item["page_id"], "template_id": item["template_id"], "source_slide": item["source_slide"],
        "title": item.get("title", ""), "role": item["role"], "layout_tags": item.get("layout_tags", []),
        "text": item.get("text", ""), "preview": item.get("preview"), "template_name": item["template_name"],
        "source_template": item["source_template"], "tags": item.get("tags", []),
    } for item in manifest["pages"]]
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    page_count = len(payload)
    html_text = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>cycppt 页面模板库</title><style>
body{{margin:0;background:#f4f6f8;color:#17212b;font-family:"Microsoft YaHei",sans-serif}}header{{position:sticky;top:0;z-index:2;background:#8e1f32;color:#fff;padding:20px 4vw;box-shadow:0 2px 12px #0002}}h1{{margin:0 0 8px;font-size:26px}}header p{{margin:0 0 12px;opacity:.86}}input,select{{padding:10px 12px;border:0;border-radius:8px;font-size:15px;margin:4px 6px 4px 0}}main{{padding:24px 4vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}.card{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 3px 14px #25364a18}}.card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#e8edf2}}.body{{padding:13px}}h2{{font-size:16px;line-height:1.35;margin:6px 0}}code{{font-size:11px;color:#8e1f32}}p{{font-size:11px;color:#65717e;min-height:28px;word-break:break-all}}.tags{{color:#7f1c2e;font-size:11px;line-height:1.6}}small{{color:#65717e}}button{{display:block;width:100%;margin-top:9px;padding:8px;border:0;border-radius:7px;background:#8e1f32;color:#fff;cursor:pointer}}.empty{{grid-column:1/-1;padding:40px;text-align:center;color:#65717e}}
</style></head><body><header><h1>逐页模板选择器</h1><p>{page_count} 张页面模板；可按角色、布局、颜色、文件名和页面标题检索。复制 page_id 后绑定到 ppt_plan.json。</p><input id="q" placeholder="搜索：方法、图表、浙大蓝、开题"><select id="role"><option value="">全部页面角色</option></select><select id="layout"><option value="">全部布局标签</option></select></header><main id="grid"></main><script>const pages={data};const q=document.querySelector('#q'),role=document.querySelector('#role'),layout=document.querySelector('#layout'),grid=document.querySelector('#grid');const roles=[...new Set(pages.map(x=>x.role))].sort(),layouts=[...new Set(pages.flatMap(x=>x.layout_tags||[]))].sort();roles.forEach(x=>role.insertAdjacentHTML('beforeend',`<option>${{x}}</option>`));layouts.forEach(x=>layout.insertAdjacentHTML('beforeend',`<option>${{x}}</option>`));function render(){{const query=q.value.trim().toLowerCase();const rr=role.value,ll=layout.value;const found=pages.filter(x=>(!query||[x.page_id,x.title,x.text,x.template_name,...(x.tags||[]),...(x.layout_tags||[])].join(' ').toLowerCase().includes(query))&&(!rr||x.role===rr)&&(!ll||(x.layout_tags||[]).includes(ll))).slice(0,300);grid.innerHTML=found.length?found.map(x=>`<article class="card"><img loading="lazy" src="${{x.preview}}"><div class="body"><code>${{x.page_id}}</code><h2>${{x.title||x.template_name}}</h2><p>${{x.template_name}} · 原第 ${{x.source_slide}} 页</p><div class="tags">角色：${{x.role}}<br>布局：${{(x.layout_tags||[]).join(' / ')}}</div><small>${{(x.text||'').slice(0,180)}}</small><button data-id="${{x.page_id}}">复制 page_id</button></div></article>`).join(''):'<div class="empty">没有匹配页面，请放宽筛选条件。</div>';document.querySelectorAll('button').forEach(b=>b.onclick=async()=>{{await navigator.clipboard.writeText(b.dataset.id);const old=b.textContent;b.textContent='已复制';setTimeout(()=>b.textContent=old,1000)}})}}[q,role,layout].forEach(x=>x.addEventListener('input',render));render();</script></body></html>'''
    atomic_write_text(output / "catalog.html", html_text)


def build_manifest(source: Path, output: Path, with_hash: bool) -> dict[str, Any]:
    files = sorted((p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS), key=lambda p: p.relative_to(source).as_posix().casefold())
    if not files:
        raise ValueError(f"No PowerPoint templates found under: {source}")
    preview_dir = output / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)
    templates, pages = [], []
    for index, path in enumerate(files, 1):
        relative = path.relative_to(source).as_posix()
        template_id = stable_id(relative)
        try:
            if path.suffix.lower() in OPENXML_EXTENSIONS:
                meta, page_records = inspect_openxml(path, source, template_id)
            else:
                meta, page_records = inspect_legacy_with_com(path, template_id)
        except Exception as exc:
            meta, page_records = {"slide_count": None, "aspect_ratio": None, "aspect": "unknown", "sample_text": ""}, []
            print(f"parse failed: {path}: {exc}", file=sys.stderr, flush=True)
        file_class = classify_file(relative, meta.get("sample_text", ""))
        template = {
            "template_id": template_id, "name": path.stem, "relative_path": relative,
            "source_template": str(path.resolve()), "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size, "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
            "sha256": sha256_file(path) if with_hash else None, "source_mode": "external_link",
            **meta, **file_class,
        }
        templates.append(template)
        for page in page_records:
            page.update({"template_name": path.stem, "source_template": str(path.resolve()), "tags": file_class["tags"], "source_aspect": meta.get("aspect")})
            pages.append(page)
        print(f"indexed {index}/{len(files)}: {path.name} ({len(page_records)} pages)", flush=True)
    manifest = {
        "schema_version": 2, "library_id": "external-graduation-ppt-templates",
        "name": "毕业论文相关写作 PPT 模板逐页库", "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source.resolve()), "storage_mode": "external_link",
        "catalog_html": str((output / "catalog.html").resolve()),
        "summary": {
            "template_count": len(templates), "page_count": len(pages),
            "total_size_bytes": sum(x["size_bytes"] for x in templates),
            "total_slide_count": sum(x.get("slide_count") or 0 for x in templates),
            "category_counts": dict(sorted(Counter(x["category"] for x in templates).items())),
            "role_counts": dict(sorted(Counter(x["role"] for x in pages).items())) if pages and "role" in pages[0] else {},
            "aspect_counts": dict(sorted(Counter(x.get("source_aspect") for x in pages).items())),
        },
        "usage_contract": {
            "selection": "Each generated slide may select a different page_id. Prefer explicit page_id or a high-confidence role/layout search.",
            "storage": "Original PPT/PPTX files remain in the external folder; only page previews and metadata are cached.",
            "binding": "Record page_id, source_template, source_slide, reference_image, style_text, confidence, and reason in template_binding.",
            "placeholder_guard": "Replace names, schools, dates, topics, statistics, logos, and other template-specific metadata unless verified for the current report.",
        },
        "templates": templates, "pages": pages,
    }
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="External folder containing PPT/PPTX templates.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT), help="Shared page-library output directory.")
    parser.add_argument("--skip-hash", action="store_true")
    parser.add_argument("--render", action="store_true", help="Render every source slide to a JPEG preview using PowerPoint COM.")
    parser.add_argument("--render-width", type=int, default=640)
    parser.add_argument("--overwrite-previews", action="store_true")
    args = parser.parse_args()
    source = Path(args.source).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.exists() or not source.is_dir():
        raise SystemExit(f"Source folder not found: {source}")
    output.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(source, output, with_hash=not args.skip_hash)
    if args.render:
        source_files = sorted((p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS), key=lambda p: p.relative_to(source).as_posix().casefold())
        render_previews(source, source_files, output / "previews", args.render_width, args.overwrite_previews, manifest["pages"])
        for page in manifest["pages"]:
            preview = output / f"previews/{page['page_id']}.jpg"
            if preview.exists():
                page["preview"] = f"previews/{preview.name}"
                page["preview_source"] = "powerpoint_render"
                page["dominant_color"] = dominant_color(preview)
    atomic_write_text(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_catalog(manifest, output)
    print(json.dumps({"manifest": str((output / "manifest.json").resolve()), "catalog": str((output / "catalog.html").resolve()), **manifest["summary"]}, ensure_ascii=False, indent=2))
    return 0


def inspect_legacy_with_com(path: Path, template_id: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    import win32com.client  # type: ignore

    app = win32com.client.DispatchEx("PowerPoint.Application")
    presentation = None
    try:
        presentation = app.Presentations.Open(str(path), True, False, False)
        count = int(presentation.Slides.Count)
        width, height = float(presentation.PageSetup.SlideWidth), float(presentation.PageSetup.SlideHeight)
        ratio = width / height if height else None
        aspect = "16:9" if ratio and abs(ratio - 16 / 9) < 0.03 else "4:3" if ratio and abs(ratio - 4 / 3) < 0.03 else "legacy-ppt"
        pages = []
        for number in range(1, count + 1):
            slide = presentation.Slides(number)
            texts = []
            for shape_index in range(1, int(slide.Shapes.Count) + 1):
                shape = slide.Shapes(shape_index)
                try:
                    if shape.HasTextFrame and shape.TextFrame.HasText:
                        texts.append(str(shape.TextFrame.TextRange.Text).strip())
                except Exception:
                    continue
            text = " | ".join(x for x in texts if x)
            counts = {"text_shapes": len(texts), "pictures": 0, "graphic_frames": 0, "tables": 0, "charts": 0, "diagrams": 0, "media": 0}
            role, tags = classify_page(number, count, text, counts, {"aspect": aspect})
            title = texts[0] if texts else ""
            pages.append({"page_id": page_id(template_id, number), "template_id": template_id, "source_slide": number, "title": title, "text": text[:4000], "role": role, "layout_tags": tags, "semantic_tags": semantic_page_tags(role, title, text, counts), "placeholder_flags": placeholder_flags(title, text), "placeholder_risk": bool(placeholder_flags(title, text)), "shape_counts": counts, "positions": {}, "preview": None})
        return {"slide_count": count, "aspect_ratio": round(ratio, 4) if ratio else None, "aspect": aspect, "sample_text": ""}, pages
    finally:
        if presentation is not None:
            presentation.Close()
        app.Quit()


def render_previews(source: Path, source_files: list[Path], preview_dir: Path, width: int, overwrite: bool, pages: list[dict[str, Any]]) -> None:
    import pythoncom  # type: ignore
    import win32com.client  # type: ignore

    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for page in pages:
        by_template[page["template_id"]].append(page)
    pythoncom.CoInitialize()
    app = win32com.client.DispatchEx("PowerPoint.Application")
    try:
        for deck_index, path in enumerate(source_files, 1):
            template_id = stable_id(path.relative_to(source).as_posix())
            records = sorted(by_template.get(template_id, []), key=lambda x: x["source_slide"])
            if not records:
                continue
            presentation = None
            try:
                presentation = app.Presentations.Open(str(path), True, False, False)
                sw, sh = float(presentation.PageSetup.SlideWidth), float(presentation.PageSetup.SlideHeight)
                height = max(1, round(width * sh / sw)) if sw else round(width * 9 / 16)
                for record in records:
                    out = preview_dir / f"{record['page_id']}.jpg"
                    if not out.exists() or overwrite:
                        presentation.Slides(record["source_slide"]).Export(str(out), "JPG", width, height)
                    record["preview"] = f"previews/{out.name}"
                print(f"rendered {deck_index}/{len(source_files)}: {path.name} ({len(records)} pages)", flush=True)
            except Exception as exc:
                print(f"render failed: {path}: {exc}", file=sys.stderr, flush=True)
            finally:
                if presentation is not None:
                    presentation.Close()
    finally:
        app.Quit()
        pythoncom.CoUninitialize()


def dominant_color(path: Path) -> str | None:
    try:
        from PIL import Image

        with Image.open(path) as image:
            image = image.convert("RGB").resize((48, 27))
            palette_image = image.quantize(colors=8)
            palette = palette_image.getpalette()
            histogram = palette_image.getcolors()
            if not histogram:
                return None
            _, index = max(histogram)
            rgb = tuple(palette[index * 3:index * 3 + 3])
            return "#%02x%02x%02x" % rgb
    except Exception:
        return None


def write_catalog(manifest: dict[str, Any], output: Path) -> None:
    payload = [{"page_id": x["page_id"], "template_id": x["template_id"], "source_slide": x["source_slide"], "title": x.get("title", ""), "text": x.get("text", ""), "role": x["role"], "layout_tags": x.get("layout_tags", []), "semantic_tags": x.get("semantic_tags", []), "placeholder_flags": x.get("placeholder_flags", []), "preview": x.get("preview"), "template_name": x["template_name"], "tags": x.get("tags", [])} for x in manifest["pages"]]
    data = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html_text = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>逐页 PowerPoint 模板库</title><style>body{{margin:0;background:#f4f6f8;color:#17212b;font-family:"Microsoft YaHei",sans-serif}}header{{position:sticky;top:0;z-index:2;background:#8e1f32;color:white;padding:20px 4vw;box-shadow:0 2px 12px #0002}}h1{{margin:0 0 8px;font-size:26px}}header p{{margin:0 0 12px;opacity:.86}}input,select{{padding:10px 12px;border:0;border-radius:8px;font-size:15px;margin:4px 6px 4px 0}}main{{padding:24px 4vw;display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}}.card{{background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 3px 14px #25364a18}}.card img{{display:block;width:100%;aspect-ratio:16/9;object-fit:cover;background:#e8edf2}}.body{{padding:13px}}h2{{font-size:16px;line-height:1.35;margin:6px 0}}code{{font-size:11px;color:#8e1f32}}p{{font-size:11px;color:#65717e;min-height:28px;word-break:break-all}}.tags{{color:#7f1c2e;font-size:11px;line-height:1.6}}small{{color:#65717e}}button{{display:block;width:100%;margin-top:9px;padding:8px;border:0;border-radius:7px;background:#8e1f32;color:#fff;cursor:pointer}}.empty{{grid-column:1/-1;padding:40px;text-align:center;color:#65717e}}</style></head><body><header><h1>逐页模板选择器</h1><p>{len(payload)} 张页面模板；复制 page_id 后可在 ppt_plan.json 中逐页绑定。</p><input id="q" placeholder="搜索：方法、图表、浙大蓝、开题"><select id="role"><option value="">全部页面角色</option></select><select id="layout"><option value="">全部布局标签</option></select></header><main id="grid"></main><script>const pages={data};const q=document.querySelector('#q'),role=document.querySelector('#role'),layout=document.querySelector('#layout'),grid=document.querySelector('#grid');const roles=[...new Set(pages.map(x=>x.role))].sort(),layouts=[...new Set(pages.flatMap(x=>x.layout_tags||[]))].sort();roles.forEach(x=>role.insertAdjacentHTML('beforeend',`<option>${{x}}</option>`));layouts.forEach(x=>layout.insertAdjacentHTML('beforeend',`<option>${{x}}</option>`));function render(){{const query=q.value.trim().toLowerCase();const rr=role.value,ll=layout.value;const found=pages.filter(x=>(!query||[x.page_id,x.title,x.text,x.template_name,...(x.tags||[]),...(x.layout_tags||[])].join(' ').toLowerCase().includes(query))&&(!rr||x.role===rr)&&(!ll||(x.layout_tags||[]).includes(ll))).slice(0,300);grid.innerHTML=found.length?found.map(x=>`<article class="card"><img loading="lazy" src="${{x.preview}}"><div class="body"><code>${{x.page_id}}</code><h2>${{x.title||x.template_name}}</h2><p>${{x.template_name}} · 原第 ${{x.source_slide}} 页</p><div class="tags">角色：${{x.role}}<br>布局：${{(x.layout_tags||[]).join(' / ')}}</div><small>${{(x.text||'').slice(0,180)}}</small><button data-id="${{x.page_id}}">复制 page_id</button></div></article>`).join(''):'<div class="empty">没有匹配页面，请放宽筛选条件。</div>'}}[q,role,layout].forEach(x=>x.addEventListener('input',render));render();</script></body></html>'''
    atomic_write_text(output / "catalog.html", html_text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="External folder containing PPT/PPTX templates.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--skip-hash", action="store_true")
    parser.add_argument("--render", action="store_true", help="Render every page using installed PowerPoint COM.")
    parser.add_argument("--render-width", type=int, default=640)
    parser.add_argument("--overwrite-previews", action="store_true")
    args = parser.parse_args()
    source = Path(args.source).expanduser().resolve()
    output = Path(args.output).expanduser().resolve()
    if not source.is_dir():
        raise SystemExit(f"Source folder not found: {source}")
    output.mkdir(parents=True, exist_ok=True)
    files = sorted((p for p in source.rglob("*") if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS), key=lambda p: p.relative_to(source).as_posix().casefold())
    if not files:
        raise SystemExit(f"No PowerPoint templates found under: {source}")
    templates, pages = [], []
    for index, path in enumerate(files, 1):
        relative = path.relative_to(source).as_posix()
        template_id = stable_id(relative)
        if path.suffix.lower() in OPENXML_EXTENSIONS:
            try:
                meta, page_records = inspect_openxml(path, source, template_id)
            except Exception as exc:
                print(f"parse failed: {path}: {exc}", file=sys.stderr, flush=True)
                meta, page_records = {"slide_count": None, "aspect_ratio": None, "aspect": "unknown", "sample_text": ""}, []
        else:
            meta, page_records = inspect_legacy_with_com(path, template_id)
        file_meta = classify_file(relative, meta.get("sample_text", ""))
        template = {"template_id": template_id, "name": path.stem, "relative_path": relative, "source_template": str(path.resolve()), "extension": path.suffix.lower(), "size_bytes": path.stat().st_size, "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(), "sha256": None if args.skip_hash else sha256_file(path), "source_mode": "external_link", **meta, **file_meta}
        templates.append(template)
        for page in page_records:
            page.update({"template_name": path.stem, "source_template": str(path.resolve()), "tags": file_meta["tags"], "source_aspect": meta.get("aspect")})
            pages.append(page)
        print(f"indexed {index}/{len(files)}: {path.name} ({len(page_records)} pages)", flush=True)
    manifest = {"schema_version": 3, "library_id": "external-graduation-ppt-templates", "name": "毕业论文相关写作 PPT 模板逐页库", "generated_at": datetime.now(timezone.utc).isoformat(), "source_root": str(source), "storage_mode": "external_link", "catalog_html": str((output / "catalog.html").resolve()), "summary": {"template_count": len(templates), "page_count": len(pages), "total_size_bytes": sum(x["size_bytes"] for x in templates), "total_slide_count": sum(x.get("slide_count") or 0 for x in templates), "category_counts": dict(sorted(Counter(x["category"] for x in templates).items())), "role_counts": dict(sorted(Counter(x["role"] for x in pages).items())), "layout_counts": dict(sorted(Counter(tag for x in pages for tag in x.get("layout_tags", [])).items())), "placeholder_risk_count": sum(bool(x.get("placeholder_risk")) for x in pages)}, "usage_contract": {"selection": "Each generated slide may select a different page_id.", "storage": "Original PPT/PPTX files remain in the external folder; only metadata and cached previews are stored.", "binding": "Record page_id, source_template, source_slide, reference_image, style_text, confidence, and reason in template_binding.", "placeholder_guard": "Replace names, schools, dates, topics, statistics, logos, and claims unless verified for the current report."}, "templates": templates, "pages": pages}
    if args.render:
        (output / "previews").mkdir(parents=True, exist_ok=True)
        render_previews(source, files, output / "previews", args.render_width, args.overwrite_previews, pages)
        for page in pages:
            candidate = output / f"previews/{page['page_id']}.jpg"
            if candidate.exists():
                page["preview"] = f"previews/{candidate.name}"
                page["preview_source"] = "powerpoint_render"
                page["dominant_color"] = dominant_color(candidate)
    atomic_write_text(output / "manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    write_catalog(manifest, output)
    print(json.dumps({"manifest": str((output / "manifest.json").resolve()), "catalog": str((output / "catalog.html").resolve()), **manifest["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
