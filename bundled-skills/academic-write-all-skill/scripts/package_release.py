from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


EXCLUDED_DIR_NAMES = {".git", ".venv", "__pycache__", "dist", "smoke-project"}
EXCLUDED_SUFFIXES = {".pyc"}
DEFAULT_ROOT_FILES = {
    "SKILL.md",
    "README.md",
    "CHANGELOG.md",
    "RELEASE_NOTES.md",
    ".gitignore",
    "requirements-cycwrite.txt",
    "academic-write-all-skill.bat",
    "bootstrap_academic_write_all_skill_runtime.bat",
}
DEFAULT_TOP_LEVEL_DIRS = {"assets", "evals", "references", "scripts"}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    if parts & EXCLUDED_DIR_NAMES:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def iter_files(root: Path):
    for file_name in sorted(DEFAULT_ROOT_FILES):
        path = root / file_name
        if path.exists() and path.is_file():
            yield path
    for dir_name in sorted(DEFAULT_TOP_LEVEL_DIRS):
        base = root / dir_name
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file() and not should_skip(path.relative_to(root)):
                yield path


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Package academic-write-all-skill into dist/ zip")
    parser.add_argument("--version", default="20260318", help="version tag used in artifact filename")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    dist = root / "dist"
    dist.mkdir(exist_ok=True)

    zip_name = f"academic-write-all-skill-{args.version}.zip"
    zip_path = dist / zip_name
    sha_path = dist / f"{zip_name}.sha256"

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as zf:
        for path in iter_files(root):
            arcname = Path("academic-write-all-skill") / path.relative_to(root)
            zf.write(path, arcname.as_posix())

    sha_value = sha256_of(zip_path)
    sha_path.write_text(f"{sha_value}  {zip_name}\n", encoding="utf-8")

    print(f"[ok] package: {zip_path}")
    print(f"[ok] sha256: {sha_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
