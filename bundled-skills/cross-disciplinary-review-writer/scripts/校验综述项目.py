#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from review_project_schema import (
    ABSTRACT_SCREEN_HEADERS,
    CANDIDATE_HEADERS,
    EVIDENCE_HEADERS,
    FULLTEXT_ACQUISITION_HEADERS,
    FULLTEXT_REVIEW_HEADERS,
    FULLTEXT_SCREEN_HEADERS,
    PROJECT_DEFAULT_PATHS,
    SCHEMA_VERSION,
)


HEADER_RULES = {
    "candidate_csv": CANDIDATE_HEADERS,
    "abstract_screen_csv": ABSTRACT_SCREEN_HEADERS,
    "fulltext_acquisition_csv": FULLTEXT_ACQUISITION_HEADERS,
    "fulltext_screen_csv": FULLTEXT_SCREEN_HEADERS,
    "fulltext_review_csv": FULLTEXT_REVIEW_HEADERS,
    "evidence_csv": EVIDENCE_HEADERS,
}

REQUIRED_PATH_KEYS = (
    "candidate_csv",
    "abstract_screen_csv",
    "fulltext_acquisition_csv",
    "fulltext_screen_csv",
    "fulltext_review_csv",
    "evidence_csv",
    "visual_summary_md",
)


def read_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        try:
            return next(reader)
        except StopIteration:
            return []


def main() -> None:
    parser = argparse.ArgumentParser(description="校验综述项目目录及 CSV schema 完整性")
    parser.add_argument("项目目录", help="按 skill 初始化后的综述项目目录")
    parser.add_argument(
        "--strict", action="store_true", help="发现问题时返回非零退出码"
    )
    args = parser.parse_args()

    project_dir = Path(args.项目目录).expanduser().resolve()
    if not project_dir.exists():
        raise FileNotFoundError(f"项目目录不存在: {project_dir}")

    problems: list[str] = []
    print(f"[INFO] project={project_dir}")
    print(f"[INFO] schema={SCHEMA_VERSION}")

    for key in REQUIRED_PATH_KEYS:
        relative_path = PROJECT_DEFAULT_PATHS[key]
        path = project_dir / relative_path
        if not path.exists():
            problems.append(f"缺少文件: {path}")
            print(f"[FAIL] missing={path}")
            continue

        print(f"[PASS] exists={path}")
        expected_headers = HEADER_RULES.get(key)
        if expected_headers is None:
            continue

        actual_headers = read_headers(path)
        if actual_headers == expected_headers:
            print(f"[PASS] header={path.name}")
            continue

        missing = [item for item in expected_headers if item not in actual_headers]
        extra = [item for item in actual_headers if item not in expected_headers]
        problems.append(f"表头不匹配: {path}")
        print(f"[FAIL] header={path.name}")
        if missing:
            print(f"  missing={missing}")
        if extra:
            print(f"  extra={extra}")

    if problems:
        print(f"[WARN] 共发现 {len(problems)} 个问题")
        if args.strict:
            sys.exit(1)
        return

    print("[OK] 项目结构与 schema 校验通过")


if __name__ == "__main__":
    main()
