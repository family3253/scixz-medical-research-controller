#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path


def copy_template(src: Path, dst: Path, *, force: bool, skip_existing: bool) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        if skip_existing:
            return
        if not force:
            raise FileExistsError(
                f"目标文件已存在: {dst}. 使用 --force 覆盖，或使用 --skip-existing 跳过已有文件。"
            )
    shutil.copy2(src, dst)


def write_text_file(
    path: Path, content: str, *, force: bool, skip_existing: bool
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if skip_existing:
            return
        if not force:
            raise FileExistsError(
                f"目标文件已存在: {path}. 使用 --force 覆盖，或使用 --skip-existing 跳过已有文件。"
            )
    path.write_text(content, encoding="utf-8")


def parse_keywords(value: str) -> list[str]:
    normalized = value.replace("；", ",").replace(";", ",").replace("，", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def infer_subthemes(topic: str) -> list[str]:
    return [
        "概念界定与研究范围",
        "主要技术/机制/方法路线",
        "典型应用场景与代表性证据",
        "局限、争议与未来方向",
    ]


def render_topic_brief(
    *,
    topic: str,
    title_zh: str,
    title_en: str,
    domain: str,
    review_type: str,
    gate_profile: str,
    language: str,
    purpose: str,
    time_boundary: str,
    zh_keywords: list[str],
    en_keywords: list[str],
    subthemes: list[str],
) -> str:
    return f"""# 选题说明

- 当前模式：完整投稿级综述模式
- 主综述类型：{review_type}
- 闸门档位：{gate_profile}
- 综述类型/闸门选择理由：当前项目以真实综述骨架开题为目标，先采用可执行且相对稳妥的默认路线，后续可根据证据量再升级或降级。
- 研究主题：{topic}
- 标准化中文题目：{title_zh}
- 英文工作题目：{title_en}
- 学科类别：{domain}
- 写作用途：{purpose}
- 目标期刊/学位类型/基金场景：未指定
- 输出语言：{language}
- 研究对象：围绕“{topic}”形成的研究对象、方法路线、应用场景与证据体系
- 核心问题：当前领域的主要研究路线、关键证据、共识、争议和可投稿切口分别是什么
- 预期贡献或新意：形成可直接进入检索、筛选、证据提取与提纲写作的真实项目骨架
- 时间边界：{time_boundary}
- 中文关键词：{"；".join(zh_keywords)}
- 英文关键词：{"; ".join(en_keywords)}
- 同义词/近义词：待补充
- 一级子主题：{"；".join(subthemes)}
- 排除方向：纯新闻报道、非学术评论、与主题仅边缘相关的泛化讨论
- 纳入范围说明：优先纳入与主题直接相关的原创研究、高质量综述、指南或标准文本
- 排除范围说明：排除缺少方法与结果支撑的意见性文本、无法追溯来源的材料
- 是否需要质量评价/偏倚评价：是
- 预期输出级别：投稿级综述项目骨架
- 备注：该骨架已完成真实主题落盘，但检索式、子主题覆盖和闸门档位仍需结合实际题录进一步修订。
"""


def render_search_strategy(
    *,
    topic: str,
    review_type: str,
    domain: str,
    gate_profile: str,
    time_boundary: str,
    zh_keywords: list[str],
    en_keywords: list[str],
    subthemes: list[str],
) -> str:
    zh_query = " OR ".join(zh_keywords[:4]) if zh_keywords else topic
    en_query = " OR ".join(en_keywords[:4]) if en_keywords else topic
    concept_b = subthemes[1] if len(subthemes) > 1 else "核心机制/方法"
    concept_c = subthemes[2] if len(subthemes) > 2 else "应用场景"
    return f"""# 检索策略

## 1. 检索目标
- 主题：{topic}
- 主综述类型：{review_type}
- 学科路线：{domain}
- 闸门档位：{gate_profile}
- 目标数量门槛：先按 {gate_profile} 档准备候选池，后续根据真实证据覆盖调整
- 核心研究问题：围绕 {topic} 的研究对象、方法路线、代表性证据、争议点与未来方向展开梳理

## 2. 关键词组
### 中文关键词
{chr(10).join(f"- {item}" for item in zh_keywords)}

### 英文关键词
{chr(10).join(f"- {item}" for item in en_keywords)}

### 同义词扩展
- 待结合数据库试检结果补充近义词、缩写与上下位概念

## 3. 概念组拆分
- 概念组 A：{topic}
- 概念组 B：{concept_b}
- 概念组 C：{concept_c}

## 4. 布尔检索式
- 通用表达：({zh_query}) AND ({concept_b} OR {concept_c})
- 数据库适配表达：({en_query}) AND ({concept_b} OR {concept_c})

## 5. 数据库与检索执行
| 数据库/平台 | 检索式版本 | 检索日期 | 时间范围 | 语言限制 | 文献类型限制 | 备注 |
|---|---|---|---|---|---|---|
| Web of Science / Scopus / PubMed / Google Scholar | v1 | {datetime.now().strftime("%Y-%m-%d")} | {time_boundary} | zh/en | review/original/guideline | 初始骨架，待实检后修订 |

## 6. 纳入与排除标准
### 纳入标准
- 与 {topic} 直接相关
- 能支撑至少一个一级子主题
- 可追溯来源且具备基本方法与结果信息

### 排除标准
- 与主题弱相关的泛化描述
- 重复记录
- 缺少可用摘要或全文线索

## 7. 文献类型优先级
- 高质量综述
- 原创研究
- 指南/标准/政策文本

## 8. 版本与更新记录
- 当前版本：v1
- 上次更新日期：{datetime.now().strftime("%Y-%m-%d")}
- 扩检触发条件：候选池数量不足、一级子主题覆盖不足、近年文献占比偏低
"""


def render_framework(*, topic: str, review_type: str, subthemes: list[str]) -> str:
    framework_type = "主题模块型 + 争议问题型"
    return f"""# 写作框架说明

- 主题：{topic}
- 主综述类型：{review_type}
- 选择的框架类型：{framework_type}
- 选择理由：该主题适合先按研究模块建立主线，再把争议与局限单列，以避免堆砌文献。
- 一级章节主线：引言 → 基础概念 → {subthemes[1] if len(subthemes) > 1 else subthemes[0]} → {subthemes[2] if len(subthemes) > 2 else subthemes[0]} → 争议与局限 → 未来方向
- 二级章节逻辑：先定义概念与范围，再比较代表性研究路线，最后归纳证据强弱与空白
- 各章节证据来源：高质量综述、原创研究、指南/标准文本
- 需要配套的图表：研究路线图、代表性证据比较表、证据矩阵表
- 各章节预期回答的问题：每章分别回答“研究了什么、证据如何、哪里仍不确定”
- 哪些章节不能形成强结论：证据不足、结论分歧大、研究设计异质性高的章节
"""


def render_outline(*, review_type: str, topic: str, subthemes: list[str]) -> str:
    section_31 = subthemes[0] if len(subthemes) > 0 else topic
    section_32 = subthemes[1] if len(subthemes) > 1 else topic
    section_33 = subthemes[2] if len(subthemes) > 2 else topic
    return f"""# 综述提纲

- 主综述类型：{review_type}
- 选用写作框架：主题模块型 + 争议问题型
- 核心研究问题：{topic} 的关键研究路线、代表性证据、主要争议与未来方向是什么

## 1. 引言
- 本节目的：界定主题、说明写作必要性与综述边界
- 关键证据：待检索后补充

## 2. 核心概念/理论/技术基础
- 本节目的：统一术语、研究对象和评价口径
- 关键证据：待检索后补充

## 3. 主要研究方向或主题模块
### 3.1 {section_31}
- 本节目的：梳理该模块的核心问题和代表性研究
- 关键证据：待检索后补充

### 3.2 {section_32}
- 本节目的：比较不同研究路线或方法框架
- 关键证据：待检索后补充

### 3.3 {section_33}
- 本节目的：总结应用证据、成效指标与局限
- 关键证据：待检索后补充

## 4. 代表性证据比较
- 比较维度：研究对象、方法、样本/数据规模、结论强度、局限性
- 对应文献：待筛选后补充

## 5. 核心争议、局限与空白
- 主要争议：待筛选后补充
- 证据缺口：待筛选后补充

## 6. 未来方向
- 应建立在以下缺口上：证据覆盖不足、评价口径不统一、外部有效性有限等

## 7. 结论
- 可形成的结论边界：仅基于后续纳入与评阅后达到门槛的证据作结论
"""


def render_draft(*, title_zh: str, review_type: str, topic: str) -> str:
    return f"""# 初稿

## 标题
{title_zh}

## 综述类型与范围说明
本文按“{review_type}”的要求组织内容，围绕“{topic}”梳理研究范围、代表性证据、争议和未来方向。

## 摘要
待在完成检索、筛选和证据提取后撰写。

## 1. 引言

## 2. 核心概念/理论/技术基础

## 3. 主要研究方向或主题模块

## 4. 代表性证据比较

## 5. 核心争议、局限与空白

## 6. 未来方向

## 7. 结论

## 附：主要论点与证据回溯
"""


def populate_real_project_skeleton(
    output_dir: Path,
    *,
    force: bool,
    skip_existing: bool,
    topic: str,
    title_zh: str,
    title_en: str,
    domain: str,
    review_type: str,
    gate_profile: str,
    language: str,
    purpose: str,
    time_boundary: str,
    zh_keywords: list[str],
    en_keywords: list[str],
    subthemes: list[str],
) -> None:
    write_text_file(
        output_dir / "00_选题说明" / "选题说明.md",
        render_topic_brief(
            topic=topic,
            title_zh=title_zh,
            title_en=title_en,
            domain=domain,
            review_type=review_type,
            gate_profile=gate_profile,
            language=language,
            purpose=purpose,
            time_boundary=time_boundary,
            zh_keywords=zh_keywords,
            en_keywords=en_keywords,
            subthemes=subthemes,
        ),
        force=force,
        skip_existing=skip_existing,
    )
    write_text_file(
        output_dir / "01_检索策略" / "检索策略.md",
        render_search_strategy(
            topic=topic,
            review_type=review_type,
            domain=domain,
            gate_profile=gate_profile,
            time_boundary=time_boundary,
            zh_keywords=zh_keywords,
            en_keywords=en_keywords,
            subthemes=subthemes,
        ),
        force=force,
        skip_existing=skip_existing,
    )
    write_text_file(
        output_dir / "05_写作框架与图表规划" / "写作框架说明.md",
        render_framework(topic=topic, review_type=review_type, subthemes=subthemes),
        force=force,
        skip_existing=skip_existing,
    )
    write_text_file(
        output_dir / "06_论点映射与提纲" / "综述提纲.md",
        render_outline(review_type=review_type, topic=topic, subthemes=subthemes),
        force=force,
        skip_existing=skip_existing,
    )
    write_text_file(
        output_dir / "07_正文草稿" / "初稿_v1.md",
        render_draft(title_zh=title_zh, review_type=review_type, topic=topic),
        force=force,
        skip_existing=skip_existing,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="初始化投稿级综述项目目录与模板")
    parser.add_argument("输出目录", help="综述项目输出目录")
    overwrite_group = parser.add_mutually_exclusive_group()
    overwrite_group.add_argument(
        "--force", action="store_true", help="覆盖已存在的模板文件"
    )
    overwrite_group.add_argument(
        "--skip-existing",
        action="store_true",
        help="保留已存在的模板文件，仅创建缺失文件",
    )
    parser.add_argument(
        "--topic", default="", help="真实综述主题；提供后会预填项目骨架"
    )
    parser.add_argument("--title-zh", default="", help="中文工作题目")
    parser.add_argument("--title-en", default="", help="英文工作题目")
    parser.add_argument("--domain", default="跨学科主题", help="学科类别")
    parser.add_argument(
        "--review-type", default="投稿级叙述/综合综述", help="主综述类型"
    )
    parser.add_argument("--gate-profile", default="B", help="默认闸门档位")
    parser.add_argument("--language", default="中文", help="输出语言")
    parser.add_argument("--purpose", default="投稿级综述项目骨架", help="写作用途")
    parser.add_argument("--time-boundary", default="近5年", help="时间边界")
    parser.add_argument("--keywords-zh", default="", help="中文关键词，逗号/分号分隔")
    parser.add_argument("--keywords-en", default="", help="英文关键词，逗号/分号分隔")
    parser.add_argument("--subthemes", default="", help="一级子主题，逗号/分号分隔")
    args = parser.parse_args()

    output_dir = Path(args.输出目录).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    stage_dirs = [
        "00_选题说明",
        "01_检索策略",
        "02_候选池与筛选",
        "03_全文获取与评阅",
        "04_证据提取与阅读笔记",
        "05_写作框架与图表规划",
        "06_论点映射与提纲",
        "07_正文草稿",
        "08_修改与终检",
    ]
    for dirname in stage_dirs:
        (output_dir / dirname).mkdir(parents=True, exist_ok=True)

    assets_dir = Path(__file__).resolve().parents[1] / "assets" / "模板资源"

    mapping = {
        "选题说明模板.md": output_dir / "00_选题说明" / "选题说明.md",
        "检索策略模板.md": output_dir / "01_检索策略" / "检索策略.md",
        "候选文献表模板.csv": output_dir / "02_候选池与筛选" / "候选文献表.csv",
        "摘要筛选记录表模板.csv": output_dir / "02_候选池与筛选" / "摘要筛选记录表.csv",
        "全文获取登记表模板.csv": output_dir
        / "03_全文获取与评阅"
        / "全文获取登记表.csv",
        "全文筛选记录表模板.csv": output_dir
        / "03_全文获取与评阅"
        / "全文筛选记录表.csv",
        "全文评阅登记表模板.csv": output_dir
        / "03_全文获取与评阅"
        / "全文评阅登记表.csv",
        "证据提取表模板.csv": output_dir / "04_证据提取与阅读笔记" / "证据提取表.csv",
        "阅读笔记模板.md": output_dir / "04_证据提取与阅读笔记" / "阅读笔记模板.md",
        "写作框架模板.md": output_dir / "05_写作框架与图表规划" / "写作框架说明.md",
        "图表规划模板.md": output_dir / "05_写作框架与图表规划" / "图表规划.md",
        "统计图表草案模板.md": output_dir / "05_写作框架与图表规划" / "统计图表草案.md",
        "论点映射模板.md": output_dir / "06_论点映射与提纲" / "论点映射.md",
        "综述提纲模板.md": output_dir / "06_论点映射与提纲" / "综述提纲.md",
        "初稿模板.md": output_dir / "07_正文草稿" / "初稿_v1.md",
        "二轮修改清单模板.md": output_dir / "08_修改与终检" / "二轮修改清单.md",
        "最终核查模板.md": output_dir / "08_修改与终检" / "最终核查清单.md",
    }

    for src_name, dst_path in mapping.items():
        copy_template(
            assets_dir / src_name,
            dst_path,
            force=args.force,
            skip_existing=args.skip_existing,
        )

    topic = args.topic.strip()
    if topic:
        zh_keywords = parse_keywords(args.keywords_zh) or [
            topic,
            "研究进展",
            "证据比较",
            "未来方向",
        ]
        en_keywords = parse_keywords(args.keywords_en) or [
            topic,
            "research progress",
            "evidence synthesis",
            "future directions",
        ]
        subthemes = parse_keywords(args.subthemes) or infer_subthemes(topic)
        title_zh = args.title_zh.strip() or f"{topic}：研究进展、关键问题与未来方向"
        title_en = args.title_en.strip() or topic
        populate_real_project_skeleton(
            output_dir,
            force=args.force,
            skip_existing=args.skip_existing,
            topic=topic,
            title_zh=title_zh,
            title_en=title_en,
            domain=args.domain.strip(),
            review_type=args.review_type.strip(),
            gate_profile=args.gate_profile.strip(),
            language=args.language.strip(),
            purpose=args.purpose.strip(),
            time_boundary=args.time_boundary.strip(),
            zh_keywords=zh_keywords,
            en_keywords=en_keywords,
            subthemes=subthemes,
        )

    print(f"[OK] 已初始化综述项目目录: {output_dir}")


if __name__ == "__main__":
    main()
