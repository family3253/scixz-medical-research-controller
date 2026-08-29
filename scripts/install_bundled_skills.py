#!/usr/bin/env python3
"""Install bundled SciXZ companion skills into a local Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def default_target() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        return Path(codex_home) / "skills"
    return Path.home() / ".codex" / "skills"


def copy_skill(source: Path, destination: Path, overwrite: bool) -> str:
    if not (source / "SKILL.md").exists():
        return "skipped: missing SKILL.md"
    if destination.exists():
        if not overwrite:
            return "skipped: already exists"
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return "installed"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install all or selected skills from bundled-skills/."
    )
    parser.add_argument(
        "skills",
        nargs="*",
        help="Optional bundled skill folder names to install. Defaults to all.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Path to the cloned scixz-medical-research-controller repository.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=default_target(),
        help="Destination skills directory. Defaults to CODEX_HOME/skills or ~/.codex/skills.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing destination skill folders.",
    )
    args = parser.parse_args()

    bundled_root = args.repo / "bundled-skills"
    if not bundled_root.exists():
        raise SystemExit(f"bundled-skills directory not found: {bundled_root}")

    args.target.mkdir(parents=True, exist_ok=True)
    requested = set(args.skills)
    sources = [
        path
        for path in sorted(bundled_root.iterdir())
        if path.is_dir() and (not requested or path.name in requested)
    ]
    missing = requested - {path.name for path in sources}
    if missing:
        raise SystemExit("Requested bundled skills not found: " + ", ".join(sorted(missing)))

    for source in sources:
        status = copy_skill(source, args.target / source.name, args.overwrite)
        print(f"{source.name}: {status}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
