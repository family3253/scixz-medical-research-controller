#!/usr/bin/env python3
"""Download current public ShowJCR CSVs and build a local sci-select index.

The raw files stay in a user cache and are never written to the repository. The
resulting SQLite file uses sci-select's own schema and can be selected with
``SCI_SELECT_JOURNAL_INDEX_DB`` or the SciXZ lookup runner's local discovery.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Callable, Dict, Optional
from urllib import request


SHOWJCR_RAW_BASE = (
    "https://raw.githubusercontent.com/hitfyd/ShowJCR/master/"
    "%E4%B8%AD%E7%A7%91%E9%99%A2%E5%88%86%E5%8C%BA%E8%A1%A8%E5%8F%8AJCR%E5%8E%9F%E5%A7%8B%E6%95%B0%E6%8D%AE%E6%96%87%E4%BB%B6/"
)
SOURCE_FILES = {
    "jcr_2025": "JCR2025-UTF8.csv",
    "cas_2025": "FQBJCR2025-UTF8.csv",
    "xinrui_2026": "XR2026-UTF8.csv",
}


def default_data_dir() -> Path:
    configured = os.environ.get("SCIXZ_JOURNAL_DATA_DIR", "").strip()
    if configured:
        return Path(configured).expanduser()
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        return base / "scixz" / "journal-index"
    cache_home = os.environ.get("XDG_CACHE_HOME", "").strip()
    base = Path(cache_home) if cache_home else Path.home() / ".cache"
    return base / "scixz" / "journal-index"


def _download(url: str, destination: Path, timeout: int = 60) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".tmp")
    try:
        req = request.Request(url, headers={"User-Agent": "scixz-journal-index-refresh"})
        try:
            with request.urlopen(req, timeout=timeout) as response, temporary.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
        except Exception as urllib_error:
            # Some managed Windows environments inject a broken proxy into
            # urllib. Retry without inherited proxy settings when requests is
            # available; this remains opt-in to the fallback path only.
            try:
                import requests
            except ImportError:
                raise urllib_error
            session = requests.Session()
            session.trust_env = False
            response = session.get(
                url,
                headers={"User-Agent": "scixz-journal-index-refresh"},
                timeout=timeout,
                stream=True,
            )
            response.raise_for_status()
            with temporary.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
            response.close()
        temporary.replace(destination)
    finally:
        if temporary.exists():
            temporary.unlink()


def _load_builder():
    root = Path(__file__).resolve().parents[1]
    candidates = (
        root / "bundled-skills" / "sci-select" / "scripts" / "build_journal_index.py",
        root.parent / "sci-select" / "scripts" / "build_journal_index.py",
        Path.home() / ".codex" / "skills" / "sci-select" / "scripts" / "build_journal_index.py",
        Path.home() / ".agents" / "skills" / "sci-select" / "scripts" / "build_journal_index.py",
    )
    for builder_path in candidates:
        if not builder_path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("scixz_sci_select_index_builder", builder_path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    raise RuntimeError("Cannot load sci-select index builder from bundled or local Skill layouts")


def refresh_index(
    data_dir: Optional[os.PathLike[str] | str] = None,
    output_path: Optional[os.PathLike[str] | str] = None,
    base_url: str = SHOWJCR_RAW_BASE,
    downloader: Optional[Callable[[str, Path, int], None]] = None,
    force: bool = False,
) -> Dict:
    """Refresh public ShowJCR inputs and return a build summary.

    ``downloader`` is injectable for deterministic tests; production calls use
    the standard-library HTTPS client. Existing source files are reused unless
    ``force`` is true.
    """
    root = Path(data_dir).expanduser() if data_dir else default_data_dir()
    root.mkdir(parents=True, exist_ok=True)
    output = Path(output_path).expanduser() if output_path else root / "sci_select_journals.sqlite"
    fetch = downloader or _download
    source_paths: Dict[str, Path] = {}
    source_status: Dict[str, str] = {}
    source_urls: Dict[str, str] = {}

    for key, filename in SOURCE_FILES.items():
        path = root / filename
        url = base_url.rstrip("/") + "/" + filename
        source_paths[key] = path
        source_urls[key] = url
        if force or not path.is_file() or path.stat().st_size == 0:
            fetch(url, path, 60)
            source_status[key] = "downloaded"
        else:
            source_status[key] = "cached"

    builder = _load_builder()
    payload = builder.build_index(
        jcr_file=str(source_paths["jcr_2025"]),
        cas_2025_xlsx=str(source_paths["cas_2025"]),
        xinrui_2026_xlsx=str(source_paths["xinrui_2026"]),
    )
    payload.setdefault("meta", {})["source_urls"] = source_urls
    payload["meta"]["refresh_source"] = "ShowJCR public CSV snapshot"
    builder.write_sqlite_index(payload, str(output))
    return {
        "output_path": str(output),
        "data_dir": str(root),
        "journal_count": len(payload.get("journals", [])),
        "source_status": source_status,
        "source_urls": source_urls,
        "jcr_release_year": payload.get("meta", {}).get("jcr_release_year"),
        "jcr_data_year": payload.get("meta", {}).get("jcr_data_year"),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Refresh the local sci-select journal index from public ShowJCR CSVs."
    )
    parser.add_argument("--data-dir", default="", help="User cache directory for raw source CSVs.")
    parser.add_argument("--output", default="", help="Output sci-select SQLite path.")
    parser.add_argument("--base-url", default=SHOWJCR_RAW_BASE, help="ShowJCR raw CSV base URL.")
    parser.add_argument("--force", action="store_true", help="Redownload all source CSVs.")
    args = parser.parse_args(argv)
    try:
        result = refresh_index(
            data_dir=args.data_dir or None,
            output_path=args.output or None,
            base_url=args.base_url,
            force=args.force,
        )
    except Exception as exc:
        print(f"journal index refresh failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
