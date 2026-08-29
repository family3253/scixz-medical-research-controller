#!/usr/bin/env python3
"""Run the SciXZ known-journal lookup smoke workflow.

The runner composes the installed sci-select Skill, an optional EasyScholar
adapter, and the live LetPub path already implemented by sci-select. It emits
one JSON record per journal with field-level source/status information.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


def _candidate_sci_select_roots(explicit: str = "") -> Iterable[Path]:
    if explicit:
        yield Path(explicit).expanduser()
    configured = os.environ.get("SCIXZ_SCI_SELECT_PATH", "").strip()
    if configured:
        yield Path(configured).expanduser()
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    yield codex_home / "skills" / "sci-select"
    yield Path.home() / ".agents" / "skills" / "sci-select"


def _load_sci_select(explicit: str = ""):
    for root in _candidate_sci_select_roots(explicit):
        module_path = root / "scripts" / "journal_metrics.py"
        if not module_path.is_file():
            continue
        sys.path.insert(0, str(root))
        try:
            # This runner itself lives in a `scripts` package. Remove that
            # package from the import cache before loading sci-select, whose
            # modules also use the package name `scripts`.
            for loaded in list(sys.modules):
                if loaded == "scripts" or loaded.startswith("scripts."):
                    del sys.modules[loaded]
            from scripts.journal_metrics import get_journal_metrics  # type: ignore

            return get_journal_metrics, root
        except Exception:
            sys.path.pop(0)
    return None, None


def _load_easy_adapter(explicit: str = ""):
    candidates = []
    if explicit:
        candidates.append(Path(explicit).expanduser())
    configured = os.environ.get("SCIXZ_EASY_SCHOLAR_ADAPTER", "").strip()
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.append(Path(__file__).resolve().parents[1] / "bundled-skills" / "find-journal" / "scripts" / "easyscholar_lookup.py")
    for module_path in candidates:
        if not module_path.is_file():
            continue
        spec = importlib.util.spec_from_file_location("scixz_easyscholar_lookup", module_path)
        if spec is None or spec.loader is None:
            continue
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def _source_status(metrics: Dict[str, Any], source: str, fallback: str = "not verified") -> Dict[str, str]:
    status = (metrics.get("_source_status") or {}).get(source)
    if isinstance(status, dict):
        return {"status": str(status.get("status", "unknown")), "reason": str(status.get("reason", ""))}
    return {"status": "unknown", "reason": fallback}


def _field(value: Any, source: str, status: str, reason: str = "") -> Dict[str, Any]:
    return {"value": value if value not in (None, "", [], {}) else None, "source": source, "status": status, "reason": reason}


def _easy_field(easy: Dict[str, Any], key: str) -> Any:
    return (easy.get("fields") or {}).get(key)


def build_card(metrics: Dict[str, Any], easy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    index_status = _source_status(metrics, "journal-index", "no local/static match")
    letpub_status = _source_status(metrics, "letpub", "LetPub was not queried")
    easy_status = (
        {"status": str(easy.get("source_status", "unknown")), "reason": str(easy.get("api_message", ""))}
        if easy
        else {"status": "skipped", "reason": "EASY_SCHOLAR_SECRET_KEY not configured or adapter not found"}
    )

    jcr = metrics.get("jcr_quartile") or (_easy_field(easy or {}, "jcr_quartile"))
    cas_major = metrics.get("cas_partition_2025") or (_easy_field(easy or {}, "cas_upgraded_major_quartile"))
    cas_minor = metrics.get("cas_minor_categories")
    cas_minor_source = "sci-select/ShowJCR"
    cas_minor_status = "profile_snapshot"
    if not cas_minor:
        cas_minor = _easy_field(easy or {}, "cas_upgraded_minor_quartile")
        cas_minor_source = "EasyScholar"
        cas_minor_status = "third-party-api"
    if not cas_minor:
        detail = metrics.get("partition_detail")
        if isinstance(detail, dict):
            cas_minor = detail.get("小类学科")
            cas_minor_source = "LetPub detail"
            cas_minor_status = "partial"
    xinrui = metrics.get("xinrui_partition_2026") or (_easy_field(easy or {}, "xinrui_quartile"))
    warning = metrics.get("warning")
    if warning is None:
        warning = _easy_field(easy or {}, "cas_warning") or _easy_field(easy or {}, "xinrui_warning")

    card = {
        "journal_name": metrics.get("name", ""),
        "issn": metrics.get("issn", ""),
        "impact_factor": _field(metrics.get("impact_factor") or _easy_field(easy or {}, "sciif"), "sci-select/ShowJCR or EasyScholar", "profile_snapshot" if metrics.get("impact_factor") else "third-party-api"),
        "jcr_quartile": _field(jcr, "sci-select/ShowJCR or EasyScholar", "profile_snapshot" if metrics.get("jcr_quartile") else "third-party-api"),
        "cas_major_quartile_2025": _field(cas_major, "sci-select/ShowJCR or EasyScholar", "profile_snapshot" if metrics.get("cas_partition_2025") else "third-party-api"),
        "cas_minor_quartile_2025": _field(cas_minor, cas_minor_source, cas_minor_status),
        "xinrui_quartile_2026": _field(xinrui, "sci-select/ShowJCR or EasyScholar", "profile_snapshot" if metrics.get("xinrui_partition_2026") else "third-party-api"),
        "letpub_review_speed": _field(metrics.get("speed"), "LetPub", "succeeded" if letpub_status["status"] in {"succeeded", "partial"} else letpub_status["status"], letpub_status["reason"]),
        "indexing": _field(metrics.get("sci_type"), "LetPub/journal-index", "partial" if metrics.get("sci_type") else "not verified"),
        "warning": _field(warning, "sci-select/ShowJCR or EasyScholar", "partial" if warning is not None else "not verified"),
        "_source_status": {
            "journal-index": index_status,
            "letpub": letpub_status,
            "easyscholar": easy_status,
            "openalex": _source_status(metrics, "openalex", "not configured"),
        },
        "notes": [
            "JCR/CAS/XinRui values from local indexes or EasyScholar are third-party/auxiliary evidence and should be rechecked for formal use.",
            "LetPub review speed is page-displayed text, not an acceptance probability or guarantee.",
        ],
    }
    if metrics.get("if_year"):
        card["impact_factor"]["year"] = metrics["if_year"]
    if metrics.get("jcr_categories"):
        card["jcr_quartile"]["categories"] = metrics["jcr_categories"]
    if easy:
        card["easyscholar_raw_fields"] = easy.get("fields", {})
        card["easyscholar_custom_rank"] = easy.get("custom_rank", [])
    return card


def run(journals: List[str], sci_select_path: str = "", easy_adapter_path: str = "") -> List[Dict[str, Any]]:
    get_metrics, _ = _load_sci_select(sci_select_path)
    if get_metrics is None:
        raise RuntimeError("sci-select is not installed or could not be loaded; install it or set SCIXZ_SCI_SELECT_PATH")
    easy_module = _load_easy_adapter(easy_adapter_path)
    secret = os.environ.get("EASY_SCHOLAR_SECRET_KEY", "").strip()
    output = []
    for journal in journals:
        metrics = get_metrics(journal, use_cache=False, source_mode="full")
        easy = None
        if easy_module is not None and secret:
            easy = easy_module.lookup([journal], secret_key=secret)[0]
        output.append(build_card(metrics, easy))
    return output


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SciXZ known-journal lookup smoke workflow.")
    parser.add_argument("journal", nargs="+", help="One or more journal names.")
    parser.add_argument("--sci-select-path", default="")
    parser.add_argument("--easy-adapter-path", default="")
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run(args.journal, args.sci_select_path, args.easy_adapter_path)
    except Exception as exc:
        print(f"journal lookup failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
