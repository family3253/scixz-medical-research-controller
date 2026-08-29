#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def copy_tree(src: Path, dst: Path) -> None:
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="安装当前综述 skill 到本机个人 skills 目录"
    )
    parser.add_argument(
        "--target-root",
        default=str(Path.home() / ".config" / "opencode" / "skills"),
        help="skills 根目录，默认安装到 ~/.config/opencode/skills",
    )
    parser.add_argument(
        "--name",
        default="cross-disciplinary-review-writer",
        help="安装后的 skill 目录名",
    )
    parser.add_argument(
        "--force", action="store_true", help="若目标目录已存在则先删除再安装"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="只打印目标路径，不实际复制"
    )
    args = parser.parse_args()

    source_dir = Path(__file__).resolve().parents[1]
    skill_md = source_dir / "SKILL.md"
    if not skill_md.exists():
        raise FileNotFoundError(f"缺少 SKILL.md: {skill_md}")

    target_root = Path(args.target_root).expanduser().resolve()
    target_dir = target_root / args.name

    if args.dry_run:
        print(f"[DRY-RUN] source={source_dir}")
        print(f"[DRY-RUN] target={target_dir}")
        return

    target_root.mkdir(parents=True, exist_ok=True)
    if target_dir.exists():
        if not args.force:
            raise FileExistsError(
                f"目标目录已存在: {target_dir}. 使用 --force 覆盖安装。"
            )
        shutil.rmtree(target_dir)

    copy_tree(source_dir, target_dir)
    print(f"[OK] 已安装 skill: {target_dir}")


if __name__ == "__main__":
    main()
