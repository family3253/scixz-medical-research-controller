from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from common import package_sha256, require_file


def add_file(source: Path, destination: Path, root: Path, manifest: list[dict]):
    source = require_file(source, "Submission file")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    manifest.append({"path": str(destination.relative_to(root)), "source": str(source), "sha256": package_sha256(destination), "size": destination.stat().st_size})


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a submission package from explicit files only")
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--manuscript", type=Path, required=True)
    parser.add_argument("--requirements", type=Path, required=True)
    parser.add_argument("--change-log", type=Path, required=True)
    parser.add_argument("--title-page", type=Path)
    parser.add_argument("--figures-dir", type=Path)
    parser.add_argument("--supplements-dir", type=Path)
    args = parser.parse_args()
    args.destination.mkdir(parents=True, exist_ok=True)
    manifest = []
    add_file(args.manuscript, args.destination / args.manuscript.name, args.destination, manifest)
    add_file(args.requirements, args.destination / args.requirements.name, args.destination, manifest)
    add_file(args.change_log, args.destination / args.change_log.name, args.destination, manifest)
    if args.title_page:
        add_file(args.title_page, args.destination / args.title_page.name, args.destination, manifest)
    for label, directory in (("figures", args.figures_dir), ("supplements", args.supplements_dir)):
        if not directory:
            continue
        for source in sorted(p for p in directory.rglob("*") if p.is_file()):
            add_file(source, args.destination / label / source.name, args.destination, manifest)
    result = {"status": "packaged", "destination": str(args.destination), "files": manifest}
    (args.destination / "PACKAGE_MANIFEST.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
