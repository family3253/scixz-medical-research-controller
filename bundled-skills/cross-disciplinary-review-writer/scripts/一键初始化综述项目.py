#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="一键初始化、校验并生成闸门报告")
    parser.add_argument("输出目录", help="综述项目输出目录")
    parser.add_argument(
        "--topic", default="", help="真实综述主题；提供后会生成真实项目骨架"
    )
    parser.add_argument("--title-zh", default="", help="中文工作题目")
    parser.add_argument("--title-en", default="", help="英文工作题目")
    parser.add_argument("--domain", default="跨学科主题", help="学科类别")
    parser.add_argument(
        "--review-type", default="投稿级叙述/综合综述", help="主综述类型"
    )
    parser.add_argument(
        "--gate-profile", default="B", choices=["A", "B", "C", "D"], help="闸门档位"
    )
    parser.add_argument("--language", default="中文", help="输出语言")
    parser.add_argument("--purpose", default="投稿级综述项目骨架", help="写作用途")
    parser.add_argument("--time-boundary", default="近5年", help="时间边界")
    parser.add_argument("--keywords-zh", default="", help="中文关键词，逗号/分号分隔")
    parser.add_argument("--keywords-en", default="", help="英文关键词，逗号/分号分隔")
    parser.add_argument("--subthemes", default="", help="一级子主题，逗号/分号分隔")
    parser.add_argument("--force", action="store_true", help="覆盖已存在文件")
    parser.add_argument(
        "--skip-existing", action="store_true", help="保留已存在文件，仅补缺失项"
    )
    args = parser.parse_args()

    scripts_dir = Path(__file__).resolve().parent
    init_script = scripts_dir / "初始化综述项目.py"
    validate_script = scripts_dir / "校验综述项目.py"
    gate_script = scripts_dir / "生成闸门检查报告.py"

    output_dir = str(Path(args.输出目录).expanduser().resolve())

    init_command = [sys.executable, str(init_script), output_dir]
    if args.force:
        init_command.append("--force")
    if args.skip_existing:
        init_command.append("--skip-existing")
    for key in (
        "topic",
        "title_zh",
        "title_en",
        "domain",
        "review_type",
        "gate_profile",
        "language",
        "purpose",
        "time_boundary",
        "keywords_zh",
        "keywords_en",
        "subthemes",
    ):
        value = getattr(args, key)
        if value:
            init_command.extend([f"--{key.replace('_', '-')}", value])

    print("[STEP] 初始化项目")
    run_step(init_command)

    print("[STEP] 校验项目")
    run_step([sys.executable, str(validate_script), output_dir])

    print("[STEP] 生成闸门检查报告")
    run_step(
        [
            sys.executable,
            str(gate_script),
            output_dir,
            "--gate-profile",
            args.gate_profile,
        ]
    )

    print(f"[OK] 一键流程完成: {output_dir}")


if __name__ == "__main__":
    main()
