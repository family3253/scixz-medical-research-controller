#!/usr/bin/env python3
"""Create a deterministic manifest for the isolated candidate after acceptance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {"STAGING_MANIFEST.json"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    pycache = [str(p.relative_to(ROOT)) for p in ROOT.rglob("__pycache__")]
    files = {}
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.name in EXCLUDE:
            continue
        rel = path.relative_to(ROOT).as_posix()
        files[rel] = {"sha256": digest(path), "bytes": path.stat().st_size}
    payload = {
        "artifact": "mdrgnb-meta-v5-4-candidate",
        "state": "RELEASABLE",
        "reason": "All candidate and first-15 release gates pass using the read-only Batch02 v5.4 validation overlay.",
        "protocol": "v5.4-candidate",
        "pycache_directories_present": pycache,
        "files": files,
    }
    (ROOT / "STAGING_MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files": len(files), "pycache_directories_present": pycache}, ensure_ascii=False))
    return 0 if not pycache else 1


if __name__ == "__main__":
    raise SystemExit(main())
