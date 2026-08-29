#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[1]
STYLE_DIR = SKILL_ROOT / 'references'
DEFAULT_STYLE_JSON = STYLE_DIR / '001_通用医学汇报PPT风格提示词.json'
STYLE_FILE_RE = re.compile(r'^(?P<index>\d{3})_(?P<name>.+)\.json$')

DEFAULT_GLOBAL_KEYS = ['medical_academic_slide', 'layout_geometry', 'typography_and_evidence', 'avoid_style']


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.expanduser().read_text(encoding='utf-8'))


def available_style_files() -> list[Path]:
    return sorted(STYLE_DIR.glob('[0-9][0-9][0-9]_*.json'))


def style_display(path: Path) -> str:
    match = STYLE_FILE_RE.match(path.name)
    if not match:
        return path.stem
    return f"{match.group('index')} {match.group('name')}"


def format_style_options(paths: list[Path]) -> str:
    if not paths:
        return f'No numbered style JSON files found in {STYLE_DIR}'
    return '\n'.join(f'- {style_display(path)} ({path})' for path in paths)


def resolve_style_json(selector: str | None) -> Path:
    if not selector:
        return DEFAULT_STYLE_JSON

    raw = str(selector).strip()
    if not raw:
        return DEFAULT_STYLE_JSON

    path_like = Path(raw).expanduser()
    path_candidates = [path_like]
    if not path_like.is_absolute():
        path_candidates.append(STYLE_DIR / raw)
    for candidate in path_candidates:
        if candidate.exists() and candidate.is_file():
            return candidate.resolve()
    if path_like.name == '通用医学汇报PPT风格提示词.json':
        return DEFAULT_STYLE_JSON.resolve()

    styles = available_style_files()
    if raw.isdigit():
        wanted = raw.zfill(3)
        matches = [path for path in styles if path.name.startswith(f'{wanted}_')]
    else:
        wanted = raw.casefold()
        exact = [
            path for path in styles
            if path.name.casefold() == wanted or path.stem.casefold() == wanted
        ]
        matches = exact or [
            path for path in styles
            if wanted in path.name.casefold() or wanted in path.stem.casefold()
        ]

    if len(matches) == 1:
        return matches[0].resolve()
    if len(matches) > 1:
        raise SystemExit(
            f'Ambiguous style selector: {selector}\n'
            f'Matches:\n{format_style_options(matches)}'
        )
    raise SystemExit(
        f'Style selector not found: {selector}\n'
        f'Available styles:\n{format_style_options(styles)}'
    )


def find_slide(plan: dict[str, Any], slide_id: str) -> dict[str, Any]:
    for slide in plan.get('slides', []):
        if slide.get('slide_id') == slide_id:
            return slide
    raise SystemExit(f'Slide not found in plan: {slide_id}')


def normalize_generation_keys(raw: Any, slide_number: int, slide: dict[str, Any]) -> dict[str, list[str]]:
    if isinstance(raw, dict):
        keys = {str(k): list(v or []) for k, v in raw.items()}
    else:
        keys = {'global': DEFAULT_GLOBAL_KEYS, 'continuity': [], 'illustration': [], 'asset_embedding': [], 'closing': [], 'negative_constraints': []}
        if slide_number == 1:
            keys['asset_embedding'].append('cover_no_asset')
        elif slide_number == 2:
            keys['continuity'].append('slide2_inherit_slide1')
        else:
            keys['continuity'].append('slide3_plus_inherit_slide1_slide2')
        if slide.get('asset_binding') or slide.get('assets', {}).get('required'):
            keys['asset_embedding'].append('preserve_original_asset')
        if slide.get('scientific_illustration_needed') or slide.get('content', {}).get('scientific_illustration_needed'):
            keys['illustration'].append('embedded_scientific_illustration')
        keys['negative_constraints'].append('avoid_fake_metadata')
    keys.setdefault('global', DEFAULT_GLOBAL_KEYS)
    keys.setdefault('continuity', [])
    keys.setdefault('illustration', [])
    keys.setdefault('asset_embedding', [])
    keys.setdefault('closing', [])
    keys.setdefault('negative_constraints', [])
    return keys


def style_text(style: dict[str, Any], group: str, keys: list[str]) -> list[str]:
    section = style.get(group, {})
    blocks = []
    for key in keys:
        if key not in section:
            raise SystemExit(f'Style key not found: {group}.{key}')
        blocks.append(f'[{group}.{key}]\n{section[key]}')
    return blocks


def compact_slide_json(slide: dict[str, Any]) -> str:
    return json.dumps(slide, ensure_ascii=False, indent=2)


def template_binding_for(slide: dict[str, Any]) -> dict[str, Any]:
    binding = slide.get('template_binding')
    return binding if isinstance(binding, dict) else {}


def required_assets_for(slide: dict[str, Any]) -> list[dict[str, Any]]:
    assets = slide.get('assets')
    required: Any = []
    if isinstance(assets, dict):
        required = assets.get('required') or []
    elif isinstance(assets, list):
        required = assets
    if not isinstance(required, list):
        return []
    normalized: list[dict[str, Any]] = []
    for item in required:
        if isinstance(item, dict):
            normalized.append(item)
        elif isinstance(item, str) and item.strip():
            normalized.append({'output_path': item, 'evidence_mode': 'original'})
    return normalized


def asset_input_path(asset: dict[str, Any]) -> str:
    for key in ('output_path', 'path', 'file', 'reference_image', 'source_path'):
        value = str(asset.get(key) or '').strip()
        if value:
            return value
    return ''


def build_prompt(
    plan: dict[str, Any],
    style: dict[str, Any],
    slide: dict[str, Any],
    slide_number: int,
    style_json: Path | None = None,
) -> str:
    keys = normalize_generation_keys(slide.get('generation_keys'), slide_number, slide)
    template_binding = template_binding_for(slide)
    deck = plan.get('deck') or {k: v for k, v in plan.items() if k not in {'slides', 'figures'}}
    required_assets = required_assets_for(slide)
    original_assets = [item for item in required_assets if str(item.get('evidence_mode') or '').casefold() == 'original']
    derived_assets = [item for item in required_assets if str(item.get('evidence_mode') or '').casefold() in {'derived', 'reconstructed'}]
    blocks: list[str] = []
    blocks.append('你正在为 GPT Image 2 生成一张医学学术 PowerPoint 页面。请严格按照以下风格键、页面计划和证据约束生成单页 16:9 PPT 图像。')
    blocks.append('不要生成网页、海报、信息流长图、UI mockup 或带浏览器/软件边框的图。输出必须是一张完整 PPT 页面。')
    blocks.append('')
    blocks.append('## 1. 已选风格提示词（必须逐条遵守）')
    if style_json is not None:
        blocks.append(f'本页解析后的风格来源：{style_json}')
    for group in ['global', 'continuity', 'illustration', 'asset_embedding', 'closing', 'negative_constraints']:
        selected = keys.get(group, [])
        if selected:
            blocks.extend(style_text(style, group, selected))
    blocks.append('')
    blocks.append('## 2. 整套母版契约（优先级高于任何单页模板）')
    blocks.append(f"- master_template_id：{deck.get('master_template_id') or template_binding.get('master_template_id') or '未显式记录，但仍须沿用 slide01/slide02 建立的同一母版'}")
    blocks.append(f"- navigation_policy：{deck.get('navigation_policy') or template_binding.get('navigation_policy') or 'none'}")
    blocks.append('- 单页 template_binding 只允许决定主体内容区的布局、图文比例、证据摆放与留白，不得替换整页母版。')
    blocks.append('- 页眉、页脚、导航条、Logo 区、标题起点、页码位置、字体体系和品牌色是 deck-wide chrome，所有正文页必须固定。')
    blocks.append('- 若 navigation_policy=none，即使参考模板图带有导航条、侧栏导航或章节导航，也必须删除；不得从参考页复制导航组件。')
    blocks.append('- 封面和结尾可采用同一模板家族中的角色专用版式；正文页不得出现位置变化的导航条或临时新增的页眉页脚。')
    blocks.append('')
    blocks.append('## 3. 本页模板绑定（仅约束主体内容区）')
    if template_binding:
        blocks.append(json.dumps(template_binding, ensure_ascii=False, indent=2))
        reference_image = template_binding.get('reference_image')
        if reference_image:
            blocks.append(f'- 页面生成 worker 必须把此模板图作为参考图传入：{reference_image}')
            blocks.append('- 只继承模板主体内容区的版式骨架、留白、图文区域和视觉节奏；标题起点及母版 chrome 服从上面的整套母版契约。')
        source_template = template_binding.get('source_template')
        source_slide = template_binding.get('source_slide')
        external_page_id = template_binding.get('external_page_id')
        if source_template:
            page_hint = f'第 {source_slide} 页' if source_slide else '对应页面'
            page_id_hint = f'（page_id={external_page_id}）' if external_page_id else ''
            blocks.append(f'- 外部 PowerPoint 来源：{source_template}；应参考其中{page_hint}{page_id_hint}的实际页面结构。')
            blocks.append('- 外部模板只提供本页视觉与版式参考；不要把源 PPT 中的姓名、学校、日期、课题、数据、徽标或示例文字原样带入。')
        style_text_override = template_binding.get('style_text')
        if style_text_override:
            blocks.append(f'- 本页模板补充描述：{style_text_override}')
        blocks.append('- 页面级模板只覆盖主体内容区，不得破坏整套汇报的字体体系、品牌色、页眉页脚、导航、Logo、页码和证据表达一致性。')
    else:
        blocks.append('本页未绑定独立模板，沿用整套 PPT 的统一母版和连续性规则。')
    blocks.append('')
    blocks.append('## 4. 本页 PPT 计划（必须按此执行）')
    blocks.append(compact_slide_json(slide))
    if deck:
        blocks.append('')
        blocks.append('## 5. 整套汇报上下文')
        blocks.append(json.dumps(deck, ensure_ascii=False, indent=2))
    blocks.append('')
    blocks.append('## 6. 原始证据与重构证据契约')
    if original_assets:
        blocks.append('- 下列 evidence_mode=original 的资产必须作为真实输入图传给 `editppt image edit/batch`，并在页面中直接嵌入；不得凭文字描述重新绘制、AI 仿制或改写图内数据：')
        for asset in original_assets:
            path = asset_input_path(asset) or '[缺少 output_path，必须在生成前补齐]'
            label = asset.get('label') or asset.get('asset_id') or asset.get('kind') or 'original evidence'
            citation = asset.get('citation') or ''
            blocks.append(f"  - {label}: {path}" + (f"；引用：{citation}" if citation else ''))
        blocks.append('- 原始 Figure、图表和医学影像仅允许等比例缩放、必要的白边裁剪和不遮挡数据的外部中文解读；不得修改像素中的曲线、数字、分组、图例或统计标记。原始 Table 也可直接嵌入，但若计划指定重构，则按下一条执行。')
    else:
        blocks.append('- 本页未声明 evidence_mode=original 的必需资产；不得因此虚构论文原图或数据。')
    if derived_assets:
        blocks.append('- 下列资产为 derived/reconstructed。Figure、图表和医学影像的重构只能用于解释、翻译或信息重构，并必须标注“重构示意 / Derived from source”；Table 允许为提高可读性或可编辑性而重构，但必须逐项忠实、保留单位/分母/脚注，并标注“表格重构 / Reconstructed from Table X”。所有重构资产都必须保留原始来源引用：')
        for asset in derived_assets:
            path = asset_input_path(asset) or '[按计划生成]'
            label = asset.get('label') or asset.get('asset_id') or asset.get('kind') or 'derived evidence'
            blocks.append(f"  - {label}: {path}")
    blocks.append('- 原始证据优先：Figure、图表和医学影像尽量直接使用原图；Table 可在不损失数据准确性的前提下重构为可编辑表格；不要为了视觉统一而默认全部重绘。')
    blocks.append('')
    blocks.append('## 7. 页面生成硬性要求')
    blocks.append('- 画布为 16:9 横版 PowerPoint 页面；所有元素位于安全边距内。')
    blocks.append('- 标题、模块标题、证据图、流程图、注释和底部引用必须网格对齐。')
    blocks.append('- 中文为主要汇报语言；英文只用于必要术语、图中短标签或文献。')
    blocks.append('- 不要虚构作者、医院、大学、日期、样本量、P 值、统计结果或参考文献。')
    blocks.append('- 严禁保留任何模板占位或泛化品牌文字：包括“单位占位文字区域”、LOGO、单位名称占位、姓名/学校/课题/日期占位符；若真实机构或 Logo 未提供，则留白或使用不带文字的中性装饰。')
    blocks.append('- 如果本页提供原始 Figure/医学影像/论文表格，请把它作为真实证据输入并嵌入，不要重画，不要改变医学内容，不要改变宽高比。')
    blocks.append('- 如果没有原始 Figure，可生成科研示意图或机制图，但必须科学准确、克制、像医学学术汇报页面。')
    blocks.append('- 底部引用区低调显示真实来源；不要让引用栏占据主体证据区。')
    blocks.append('')
    blocks.append('## 8. 连续性规则')
    if slide_number == 1:
        blocks.append('本页是整套 PPT 的视觉母版：请建立清晰、正式、可连续复用的医学学术模板。')
    elif slide_number == 2:
        blocks.append('本页必须参考随 prompt 提供的 slide01 图片，继承母版结构，仅替换内容。')
    else:
        blocks.append('本页必须同时参考随 prompt 提供的 slide01 和 slide02 图片，不得发明新模板。')
    return '\n\n'.join(blocks).strip() + '\n'


def main() -> None:
    parser = argparse.ArgumentParser(description='Build a detailed GPT Image 2 slide prompt from ppt_plan.json and selected style JSON keys.')
    parser.add_argument('style_selector', nargs='?', help='Optional style selector: 001, 1, filename, name fragment, or JSON path. Defaults to 001.')
    parser.add_argument('--style', dest='style_option', help='Optional style selector. Takes precedence over positional style_selector.')
    parser.add_argument('--style-json', help='Backward-compatible style JSON path or selector. Takes precedence over --style and positional style_selector.')
    parser.add_argument('--list-styles', action='store_true', help='List available numbered style JSON files and exit.')
    parser.add_argument('--plan', help='Path to ppt_plan.json')
    parser.add_argument('--slide-id')
    parser.add_argument('--slide-number', type=int)
    parser.add_argument('--out')
    args = parser.parse_args()

    if args.list_styles:
        print(format_style_options(available_style_files()))
        return

    missing = [
        name for name in ['plan', 'slide_id', 'slide_number', 'out']
        if getattr(args, name) in (None, '')
    ]
    if missing:
        parser.error('missing required arguments: ' + ', '.join(f'--{name.replace("_", "-")}' for name in missing))

    plan = load_json(Path(args.plan))
    slide = find_slide(plan, args.slide_id)
    deck = plan.get('deck') if isinstance(plan.get('deck'), dict) else {}
    template_binding = template_binding_for(slide)
    explicit_style_selector = args.style_json or args.style_option or args.style_selector
    locked_binding_style = None
    if template_binding.get('campus_locked') is True and template_binding.get('organization_template_id'):
        locked_binding_style = template_binding.get('style_selector')
    style_selector = (
        locked_binding_style
        or explicit_style_selector
        or template_binding.get('style_selector')
        or slide.get('style_selector')
        or deck.get('style_selector')
    )
    style_json = resolve_style_json(style_selector)
    style = load_json(style_json)
    prompt = build_prompt(plan, style, slide, args.slide_number, style_json=style_json)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(prompt, encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
