"""Verify SciXZ Word artifacts use the required author metadata."""
from __future__ import annotations
import argparse
from pathlib import Path
from docx_metadata import assert_docx_author


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--author", default="chenyechao")
    args = parser.parse_args()
    for path in args.paths:
        assert_docx_author(path, args.author)
        print(f"PASS {path}: author={args.author}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
