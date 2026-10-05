from __future__ import annotations

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

from common import require_file


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def files_under(path: Path | None):
    if not path or not path.exists():
        return []
    return sorted(p for p in path.rglob("*") if p.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory DOCX figures, tables, and explicit supplementary files")
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--supplements-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manuscript = require_file(args.manuscript, "Manuscript")
    with zipfile.ZipFile(manuscript) as archive:
        names = archive.namelist()
        embedded_images = sorted(n for n in names if n.startswith("word/media/") and not n.endswith("/"))
        document_xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    def describe(path: Path):
        return {"name": str(path), "size": path.stat().st_size, "sha256": sha256(path)}
    result = {
        "manuscript": str(manuscript),
        "embedded_images": embedded_images,
        "figure_references": sorted(set(re.findall(r"\bFigure\s+\d+", document_xml, flags=re.I))),
        "table_references": sorted(set(re.findall(r"\bTable\s+\d+", document_xml, flags=re.I))),
        "separate_figures": [describe(p) for p in files_under(args.figures_dir)],
        "supplements": [describe(p) for p in files_under(args.supplements_dir)],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
