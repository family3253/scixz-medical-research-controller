#!/usr/bin/env python3
"""Verify that every assessed corpus source has a concrete SciXZ integration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object: {path}")
    return payload


def _owner_path(root: Path, owner: str) -> Path:
    """Resolve an owner in either the public bundle or installed local layout."""
    bundled = Path(owner)
    direct = root / bundled
    if direct.is_file():
        return direct
    if len(bundled.parts) >= 3 and bundled.parts[0] == "bundled-skills":
        return root.parent / bundled.parts[1] / Path(*bundled.parts[2:])
    return direct


def verify(repo_root: Path | str) -> dict[str, int]:
    root = Path(repo_root).resolve()
    sources = _read_json(root / "registry" / "prompt_corpus_sources.json").get("sources", [])
    contract = _read_json(root / "registry" / "corpus_integration_contract.json").get("integrations", [])
    if not isinstance(sources, list) or not isinstance(contract, list):
        raise ValueError("Corpus source and integration lists are required")

    source_ids = {item.get("id") for item in sources if isinstance(item, dict) and item.get("id")}
    by_source = {}
    for item in contract:
        if not isinstance(item, dict) or not item.get("source"):
            raise ValueError("Every integration requires a source")
        source = item["source"]
        if source in by_source:
            raise ValueError(f"Duplicate integration: {source}")
        by_source[source] = item

    missing = sorted(source_ids - by_source.keys())
    unknown = sorted(set(by_source) - source_ids)
    if missing or unknown:
        raise ValueError(f"Source/integration mismatch: missing={missing}, unknown={unknown}")

    owner_count = 0
    for source, item in by_source.items():
        outcome = item.get("outcome")
        capabilities = item.get("capabilities")
        owners = item.get("owners")
        if outcome not in {"adopted", "new-skill", "adopted-and-constrained", "canonicalized", "rejected"}:
            raise ValueError(f"Invalid outcome for {source}: {outcome}")
        if not isinstance(capabilities, list) or not capabilities:
            raise ValueError(f"No concrete capability for {source}")
        if not isinstance(owners, list) or not owners:
            raise ValueError(f"No concrete owner for {source}")
        for owner in owners:
            target = _owner_path(root, owner)
            if not target.is_file():
                raise FileNotFoundError(f"Missing integration owner for {source}: {owner}")
            owner_count += 1

    return {"sources": len(source_ids), "integrations": len(by_source), "owners": owner_count}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify concrete SciXZ corpus integrations.")
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(verify(args.repo), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
