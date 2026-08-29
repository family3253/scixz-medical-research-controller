#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from review_project_schema import PROJECT_DEFAULT_PATHS, SCHEMA_VERSION


YES_TOKENS = {
    "1",
    "true",
    "yes",
    "y",
    "是",
    "纳入",
    "进入",
    "进入全文",
    "included",
    "include",
    "keep",
    "保留",
}

DUPLICATE_TOKENS = {
    "duplicate",
    "duplicated",
    "dup",
    "重复",
    "重复文献",
    "已重复",
    "排除重复",
    "remove_duplicate",
}

CORE_ROLE_TOKENS = {
    "核心",
    "主论点",
    "直接支撑",
    "core",
    "primary",
    "claim",
}

FIELD_ALIASES = {
    "year": ["年份", "year", "pubyear", "publicationyear"],
    "subtheme": ["子主题标签", "一级子主题", "subtheme", "subtheme_tag"],
    "dedupe_status": ["去重状态", "dedupe_status"],
    "doi": ["DOI/链接", "doi/链接", "doi", "link"],
    "title": ["题名", "title"],
    "pmid": ["pmid", "PMID"],
    "abstract_include": ["是否进入全文阶段", "是否进入全文", "enter_fulltext", "included"],
    "fulltext_include": ["是否纳入", "included", "纳入"],
    "grade": ["等级(A/B/C/D)", "等级", "grade"],
    "review_status": ["评阅状态", "review_status"],
    "core_read": ["是否核心精读", "core_reading", "is_core"],
    "quality": [
        "质量评价/偏倚风险",
        "质量评价",
        "偏倚风险",
        "risk_of_bias",
        "quality_assessment",
    ],
    "evidence_role": ["综述中的作用", "证据用途", "role"],
    "conflict": ["与其他研究的矛盾点", "矛盾点", "conflict"],
    "trace": ["可追溯引文页码/位置", "页码/位置", "trace", "page_locator"],
}

FIXED_GATES = {
    "A": {
        "候选文献总量": 150,
        "去重后进入初筛": 120,
        "初筛后保留": 80,
        "完成全文评阅": 50,
        "核心精读": 35,
        "深度证据提取": 30,
        "可直接支撑主论点的核心证据": 20,
    },
    "B": {
        "候选文献总量": 120,
        "去重后进入初筛": 90,
        "初筛后保留": 60,
        "完成全文评阅": 25,
        "核心精读": 15,
        "深度证据提取": 12,
        "可直接支撑主论点的核心证据": 0,
    },
    "D": {
        "候选文献总量": 80,
        "去重后进入初筛": 60,
        "初筛后保留": 40,
        "完成全文评阅": 30,
        "核心精读": 20,
        "深度证据提取": 15,
        "可直接支撑主论点的核心证据": 0,
    },
}


def normalize_text(value: str) -> str:
    normalized = value.strip().lower().replace("\ufeff", "")
    for token in (" ", "\t", "\r", "\n", "_", "-", "/", "\\"):
        normalized = normalized.replace(token, "")
    return normalized


def is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


def truthy(value: str | None) -> bool:
    if is_blank(value):
        return False
    normalized = normalize_text(value)
    return normalized in {normalize_text(item) for item in YES_TOKENS}


def looks_duplicate(value: str | None) -> bool:
    if is_blank(value):
        return False
    normalized = normalize_text(value)
    return any(normalize_text(token) in normalized for token in DUPLICATE_TOKENS)


def looks_core_role(value: str | None) -> bool:
    if is_blank(value):
        return False
    normalized = normalize_text(value)
    return any(normalize_text(token) in normalized for token in CORE_ROLE_TOKENS)


def load_rows(path: Path) -> tuple[list[dict[str, str]], str | None]:
    if not path.exists():
        return [], f"缺少文件: {path}"

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [{(key or "").strip(): (value or "").strip() for key, value in row.items()} for row in reader]
    return rows, None


def find_value(row: dict[str, str], aliases: list[str]) -> str:
    normalized_aliases = {normalize_text(alias) for alias in aliases}
    for key, value in row.items():
        if normalize_text(key) in normalized_aliases:
            return value.strip()
    return ""


def find_field(row: dict[str, str], field_name: str) -> str:
    return find_value(row, FIELD_ALIASES[field_name])


def canonical_candidate_key(row: dict[str, str]) -> str:
    for field_name in ("doi", "pmid", "title"):
        value = find_field(row, field_name)
        if not is_blank(value):
            return normalize_text(value)
    return ""


def parse_year(value: str) -> int | None:
    if is_blank(value):
        return None
    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) < 4:
        return None
    year = int(digits[:4])
    if 1900 <= year <= 2100:
        return year
    return None


def status_line(ok: bool, label: str, detail: str) -> str:
    marker = "PASS" if ok else "FAIL"
    return f"- [{marker}] {label}: {detail}"


def warn_line(label: str, detail: str) -> str:
    return f"- [WARN] {label}: {detail}"


def format_ratio(value: float | None) -> str:
    if value is None:
        return "无法计算"
    return f"{value * 100:.1f}%"


def count_recent(rows: list[dict[str, str]], current_year: int, within_years: int) -> tuple[int, int]:
    valid_years = []
    for row in rows:
        year = parse_year(find_field(row, "year"))
        if year is not None:
            valid_years.append(year)
    if not valid_years:
        return 0, 0

    floor_year = current_year - within_years + 1
    recent_count = sum(1 for year in valid_years if year >= floor_year)
    return recent_count, len(valid_years)


def count_by_subtheme(rows: list[dict[str, str]]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for row in rows:
        subtheme = find_field(row, "subtheme")
        if not is_blank(subtheme):
            counter[subtheme] += 1
    return counter


def is_nonempty_row(row: dict[str, str]) -> bool:
    return any(not is_blank(value) for value in row.values())


def main() -> None:
    parser = argparse.ArgumentParser(description="生成综述项目的闸门检查报告")
    parser.add_argument("项目目录", help="按 skill 初始化后的综述项目目录")
    parser.add_argument("--gate-profile", choices=["A", "B", "C", "D"], default="A", help="闸门档位")
    parser.add_argument("--current-year", type=int, default=datetime.now().year, help="用于时效性检查的当前年份")
    parser.add_argument("--candidate-csv", help="候选文献表路径，默认读取项目目录内模板位置")
    parser.add_argument("--abstract-screen-csv", help="摘要筛选记录表路径，默认读取项目目录内模板位置")
    parser.add_argument("--fulltext-screen-csv", help="全文筛选记录表路径，默认读取项目目录内模板位置")
    parser.add_argument("--fulltext-review-csv", help="全文评阅登记表路径，默认读取项目目录内模板位置")
    parser.add_argument("--evidence-csv", help="证据提取表路径，默认读取项目目录内模板位置")
    parser.add_argument("--output", help="输出 Markdown 报告路径，默认写入 08_修改与终检/闸门检查报告.md")
    parser.add_argument("--strict", action="store_true", help="若存在未达线项目则返回非零退出码")
    args = parser.parse_args()

    project_dir = Path(args.项目目录).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve() if args.output else project_dir / PROJECT_DEFAULT_PATHS["gate_report_md"]

    candidate_path = Path(args.candidate_csv).expanduser().resolve() if args.candidate_csv else project_dir / PROJECT_DEFAULT_PATHS["candidate_csv"]
    abstract_path = Path(args.abstract_screen_csv).expanduser().resolve() if args.abstract_screen_csv else project_dir / PROJECT_DEFAULT_PATHS["abstract_screen_csv"]
    fulltext_screen_path = Path(args.fulltext_screen_csv).expanduser().resolve() if args.fulltext_screen_csv else project_dir / PROJECT_DEFAULT_PATHS["fulltext_screen_csv"]
    fulltext_review_path = Path(args.fulltext_review_csv).expanduser().resolve() if args.fulltext_review_csv else project_dir / PROJECT_DEFAULT_PATHS["fulltext_review_csv"]
    evidence_path = Path(args.evidence_csv).expanduser().resolve() if args.evidence_csv else project_dir / PROJECT_DEFAULT_PATHS["evidence_csv"]

    candidate_rows, candidate_error = load_rows(candidate_path)
    abstract_rows, abstract_error = load_rows(abstract_path)
    fulltext_screen_rows, fulltext_screen_error = load_rows(fulltext_screen_path)
    fulltext_review_rows, fulltext_review_error = load_rows(fulltext_review_path)
    evidence_rows, evidence_error = load_rows(evidence_path)

    errors = [
        error
        for error in (
            candidate_error,
            abstract_error,
            fulltext_screen_error,
            fulltext_review_error,
            evidence_error,
        )
        if error
    ]

    deduped_candidates = 0
    if candidate_rows:
        if any(not is_blank(find_field(row, "dedupe_status")) for row in candidate_rows):
            deduped_candidates = sum(1 for row in candidate_rows if not looks_duplicate(find_field(row, "dedupe_status")))
        else:
            unique_keys = {canonical_candidate_key(row) for row in candidate_rows if canonical_candidate_key(row)}
            deduped_candidates = len(unique_keys) if unique_keys else len(candidate_rows)

    abstract_included_rows = [row for row in abstract_rows if truthy(find_field(row, "abstract_include"))]
    fulltext_included_rows = [row for row in fulltext_screen_rows if truthy(find_field(row, "fulltext_include"))]
    reviewed_rows = [row for row in fulltext_review_rows if is_nonempty_row(row)]
    core_review_rows = [row for row in fulltext_review_rows if truthy(find_field(row, "core_read"))]
    evidence_rows_nonempty = [row for row in evidence_rows if any(not is_blank(value) for value in row.values())]
    direct_core_evidence = [row for row in evidence_rows_nonempty if looks_core_role(find_field(row, "evidence_role"))]
    if not direct_core_evidence:
        direct_core_evidence = [row for row in fulltext_screen_rows if normalize_text(find_field(row, "grade")) == "a" and truthy(find_field(row, "fulltext_include"))]

    quality_rows = [
        row
        for row in fulltext_review_rows + evidence_rows_nonempty
        if not is_blank(find_field(row, "quality"))
    ]
    conflict_rows = [row for row in evidence_rows_nonempty if not is_blank(find_field(row, "conflict"))]
    trace_rows = [row for row in evidence_rows_nonempty if not is_blank(find_field(row, "trace"))]

    retained_rows_for_year = fulltext_included_rows or abstract_included_rows
    core_rows_for_year = evidence_rows_nonempty or core_review_rows
    recent_five_count, recent_five_total = count_recent(retained_rows_for_year, args.current_year, 5)
    recent_three_count, recent_three_total = count_recent(core_rows_for_year, args.current_year, 3)

    recent_five_ratio = (recent_five_count / recent_five_total) if recent_five_total else None
    recent_three_ratio = (recent_three_count / recent_three_total) if recent_three_total else None

    subtheme_candidate = count_by_subtheme(candidate_rows)
    subtheme_retained = count_by_subtheme(fulltext_included_rows or abstract_included_rows)
    subtheme_reviewed = count_by_subtheme(reviewed_rows)
    subtheme_core = count_by_subtheme(evidence_rows_nonempty or core_review_rows)
    all_subthemes = sorted(set(subtheme_candidate) | set(subtheme_retained) | set(subtheme_reviewed) | set(subtheme_core))

    report_lines = [
        "# 闸门检查报告",
        "",
        f"- 项目目录：{project_dir}",
        f"- schema：{SCHEMA_VERSION}",
        f"- 闸门档位：{args.gate_profile}",
        f"- 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 文件情况",
        f"- 候选文献表：{candidate_path}（{len(candidate_rows)} 行）",
        f"- 摘要筛选记录表：{abstract_path}（{len(abstract_rows)} 行）",
        f"- 全文筛选记录表：{fulltext_screen_path}（{len(fulltext_screen_rows)} 行）",
        f"- 全文评阅登记表：{fulltext_review_path}（{len(fulltext_review_rows)} 行）",
        f"- 证据提取表：{evidence_path}（{len(evidence_rows)} 行）",
        "",
    ]

    if errors:
        report_lines.append("## 缺失或异常")
        for error in errors:
            report_lines.append(warn_line("文件读取", error))
        report_lines.append("")

    report_lines.extend(
        [
            "## 核心统计",
            "| 指标 | 数值 |",
            "|---|---:|",
            f"| 候选文献总量 | {len(candidate_rows)} |",
            f"| 去重后进入初筛 | {deduped_candidates} |",
            f"| 初筛后保留 | {len(abstract_included_rows)} |",
            f"| 完成全文评阅 | {len(reviewed_rows)} |",
            f"| 核心精读 | {len(core_review_rows)} |",
            f"| 深度证据提取 | {len(evidence_rows_nonempty)} |",
            f"| 可直接支撑主论点的核心证据 | {len(direct_core_evidence)} |",
            f"| 已填写质量评价/偏倚风险 | {len(quality_rows)} |",
            f"| 已记录证据矛盾点 | {len(conflict_rows)} |",
            f"| 已记录可追溯页码/位置 | {len(trace_rows)} |",
            "",
        ]
    )

    hard_failures = 0
    if args.gate_profile in FIXED_GATES:
        report_lines.append("## 固定闸门检查")
        metrics = {
            "候选文献总量": len(candidate_rows),
            "去重后进入初筛": deduped_candidates,
            "初筛后保留": len(abstract_included_rows),
            "完成全文评阅": len(reviewed_rows),
            "核心精读": len(core_review_rows),
            "深度证据提取": len(evidence_rows_nonempty),
            "可直接支撑主论点的核心证据": len(direct_core_evidence),
        }
        for label, threshold in FIXED_GATES[args.gate_profile].items():
            actual = metrics[label]
            if threshold == 0:
                report_lines.append(warn_line(label, f"当前档位不强制设定数量线，当前统计值为 {actual}"))
                continue
            passed = actual >= threshold
            if not passed:
                hard_failures += 1
            report_lines.append(status_line(passed, label, f"{actual} / {threshold}"))
        report_lines.append("")
    else:
        c_failures = 0
        checks = [
            (bool(candidate_rows), "候选池记录", len(candidate_rows)),
            (bool(abstract_rows), "摘要筛选记录", len(abstract_rows)),
            (bool(fulltext_screen_rows), "全文筛选记录", len(fulltext_screen_rows)),
            (bool(fulltext_review_rows), "全文评阅记录", len(fulltext_review_rows)),
            (bool(evidence_rows_nonempty), "证据提取记录", len(evidence_rows_nonempty)),
            (bool(quality_rows), "质量评价/偏倚评价记录", len(quality_rows)),
        ]
        report_lines.extend(
            [
                "## C 档过程完整性检查",
            ]
        )
        for passed, label, count in checks:
            if not passed:
                c_failures += 1
            report_lines.append(status_line(passed, label, f"{count} 行"))
        report_lines.append("")
        hard_failures += c_failures

    report_lines.extend(
        [
            "## 时效性检查",
            warn_line("近五年占比", f"{format_ratio(recent_five_ratio)}（基于保留文献，可计算样本 {recent_five_total}）"),
            warn_line("近三年占比", f"{format_ratio(recent_three_ratio)}（基于核心阅读/证据提取，可计算样本 {recent_three_total}）"),
            "",
        ]
    )

    if all_subthemes:
        report_lines.extend(
            [
                "## 子主题覆盖",
                "| 子主题 | 候选池 | 保留 | 评阅 | 核心/证据 |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for subtheme in all_subthemes:
            report_lines.append(
                f"| {subtheme} | {subtheme_candidate.get(subtheme, 0)} | {subtheme_retained.get(subtheme, 0)} | {subtheme_reviewed.get(subtheme, 0)} | {subtheme_core.get(subtheme, 0)} |"
            )
        report_lines.append("")
    else:
        report_lines.extend(
            [
                "## 子主题覆盖",
                warn_line("子主题标签", "当前表格中未发现可统计的子主题标签"),
                "",
            ]
        )

    report_lines.extend(
        [
            "## 记录完整性提示",
            warn_line("质量评价/偏倚风险", "若当前任务是系统化证据综述或 umbrella review，应确保质量评价记录完整"),
            warn_line("证据矛盾点", "若矛盾点记录过少，通常意味着综述的比较与批判部分还不够"),
            warn_line("可追溯引文位置", "若页码/位置为空过多，后续反向核查会变得困难"),
            "",
        ]
    )

    blocker_count = hard_failures + len(errors)
    overall_ok = blocker_count == 0
    report_lines.append("## 结论")
    if overall_ok:
        report_lines.append("- 当前统计结果未发现硬性闸门失败项。")
    else:
        report_lines.append(f"- 当前统计结果存在 {blocker_count} 项未达线或关键文件缺失，暂不建议标记为当前档位完成稿。")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    print(f"[OK] 已生成闸门检查报告: {output_path}")

    if args.strict and not overall_ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
