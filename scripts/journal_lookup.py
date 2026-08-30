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
    repo_bundled = Path(__file__).resolve().parents[1] / "bundled-skills" / "sci-select"
    yield repo_bundled
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")).expanduser()
    yield codex_home / "skills" / "sci-select"
    yield Path.home() / ".agents" / "skills" / "sci-select"


def configure_local_index() -> Optional[Path]:
    """Point sci-select at the index produced by refresh_journal_index.py.

    An explicit ``SCI_SELECT_JOURNAL_INDEX_DB`` remains authoritative. For a
    zero-configuration lookup, discover the refresh script's per-user cache or
    an explicit ``SCIXZ_JOURNAL_INDEX_DB`` path and set sci-select's native
    environment variable for this process.
    """
    configured = os.environ.get("SCI_SELECT_JOURNAL_INDEX_DB", "").strip()
    if configured:
        return Path(configured).expanduser()

    candidates: List[Path] = []
    explicit = os.environ.get("SCIXZ_JOURNAL_INDEX_DB", "").strip()
    if explicit:
        candidates.append(Path(explicit).expanduser())

    data_dir = os.environ.get("SCIXZ_JOURNAL_DATA_DIR", "").strip()
    if data_dir:
        candidates.append(Path(data_dir).expanduser() / "sci_select_journals.sqlite")

    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA", "").strip()
        base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
        candidates.append(base / "scixz" / "journal-index" / "sci_select_journals.sqlite")
    else:
        cache_home = os.environ.get("XDG_CACHE_HOME", "").strip()
        base = Path(cache_home) if cache_home else Path.home() / ".cache"
        candidates.append(base / "scixz" / "journal-index" / "sci_select_journals.sqlite")

    for candidate in candidates:
        candidate = candidate.expanduser()
        if candidate.is_file() and candidate.stat().st_size > 0:
            os.environ["SCI_SELECT_JOURNAL_INDEX_DB"] = str(candidate)
            return candidate
    return None


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


def _showjcr_index_field(metrics: Dict[str, Any], *fields: str) -> bool:
    provenance = metrics.get("journal_index_provenance")
    if not isinstance(provenance, dict):
        return False
    return any(
        provenance.get(field) in {"jcr_2025", "cas_2025", "xinrui_2026", "showjcr_db"}
        for field in fields
    )


def build_card(metrics: Dict[str, Any], easy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    index_status = _source_status(metrics, "journal-index", "no local/static match")
    letpub_status = _source_status(metrics, "letpub", "LetPub was not queried")
    easy_status = (
        {"status": str(easy.get("source_status", "unknown")), "reason": str(easy.get("api_message", ""))}
        if easy
        else {"status": "skipped", "reason": "EASY_SCHOLAR_SECRET_KEY not configured or adapter not found"}
    )

    impact_factor = (
        metrics.get("impact_factor")
        or metrics.get("real_time_if")
        or metrics.get("jif")
        or _easy_field(easy or {}, "sciif")
    )
    impact_factor_source = "sci-select/LetPub or EasyScholar"
    if metrics.get("impact_factor") or metrics.get("real_time_if") or metrics.get("jif"):
        impact_factor_status = "profile_snapshot"
        if _showjcr_index_field(metrics, "jif_2025", "impact_factor"):
            impact_factor_source = "sci-select/ShowJCR"
    elif _easy_field(easy or {}, "sciif"):
        impact_factor_status = "third-party-api"
        impact_factor_source = "EasyScholar"
    else:
        impact_factor_status = "not verified"

    jcr = (
        metrics.get("jcr_quartile")
        or metrics.get("jcr_partition")
        or metrics.get("jcr_q")
        or _easy_field(easy or {}, "jcr_quartile")
    )
    if any(metrics.get(k) for k in ("jcr_quartile", "jcr_partition", "jcr_q")):
        jcr_status = "profile_snapshot"
    elif _easy_field(easy or {}, "jcr_quartile"):
        jcr_status = "third-party-api"
    else:
        jcr_status = "not verified"
    cas_major = metrics.get("cas_partition_2025") or (_easy_field(easy or {}, "cas_upgraded_major_quartile"))
    if metrics.get("cas_partition_2025"):
        cas_major_status = "profile_snapshot"
    elif _easy_field(easy or {}, "cas_upgraded_major_quartile"):
        cas_major_status = "third-party-api"
    else:
        cas_major_status = "not verified"
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
    if not cas_minor:
        cas_minor_source = "sci-select/ShowJCR or EasyScholar"
        cas_minor_status = "not verified"
    xinrui = metrics.get("xinrui_partition_2026") or (_easy_field(easy or {}, "xinrui_quartile"))
    if metrics.get("xinrui_partition_2026"):
        xinrui_status = "profile_snapshot"
    elif _easy_field(easy or {}, "xinrui_quartile"):
        xinrui_status = "third-party-api"
    else:
        xinrui_status = "not verified"
    warning = metrics.get("warning")
    if warning is None:
        warning = _easy_field(easy or {}, "cas_warning") or _easy_field(easy or {}, "xinrui_warning")
    if "warning" in metrics and metrics.get("warning") is not None:
        warning_status = "profile_snapshot"
    elif _easy_field(easy or {}, "cas_warning") or _easy_field(easy or {}, "xinrui_warning"):
        warning_status = "third-party-api"
    else:
        warning_status = "not verified"

    metric_source = "sci-select/ShowJCR" if _showjcr_index_field(metrics, "jcr_quartile", "jcr_quartile_2025") else "sci-select/ShowJCR or EasyScholar"
    cas_source = "sci-select/ShowJCR" if _showjcr_index_field(metrics, "cas_2025", "cas_partition_2025") else "sci-select/ShowJCR or EasyScholar"
    xinrui_source = "sci-select/ShowJCR" if _showjcr_index_field(metrics, "xuankan_2026", "xinrui_partition_2026") else "sci-select/ShowJCR or EasyScholar"

    card = {
        "journal_name": metrics.get("name", ""),
        "issn": metrics.get("issn", ""),
        "impact_factor": _field(impact_factor, impact_factor_source, impact_factor_status),
        "jcr_quartile": _field(jcr, metric_source, jcr_status),
        "cas_major_quartile_2025": _field(cas_major, cas_source, cas_major_status),
        "cas_minor_quartile_2025": _field(cas_minor, cas_minor_source, cas_minor_status),
        "xinrui_quartile_2026": _field(xinrui, xinrui_source, xinrui_status),
        "letpub_review_speed": _field(metrics.get("speed"), "LetPub", "succeeded" if letpub_status["status"] in {"succeeded", "partial"} else letpub_status["status"], letpub_status["reason"]),
        "indexing": _field(metrics.get("sci_type"), "LetPub/journal-index", "partial" if metrics.get("sci_type") else "not verified"),
        "warning": _field(warning, "sci-select/ShowJCR or EasyScholar", warning_status),
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
    if metrics.get("jcr_release_year"):
        card["jcr_quartile"]["release_year"] = metrics["jcr_release_year"]
        card["impact_factor"]["jcr_release_year"] = metrics["jcr_release_year"]
    if metrics.get("jcr_data_year"):
        card["jcr_quartile"]["data_year"] = metrics["jcr_data_year"]
        card["impact_factor"]["data_year"] = metrics["jcr_data_year"]
    if metrics.get("jcr_categories"):
        card["jcr_quartile"]["categories"] = metrics["jcr_categories"]
    elif metrics.get("field"):
        card["jcr_quartile"]["categories"] = metrics["field"]
    if easy:
        card["easyscholar_raw_fields"] = easy.get("fields", {})
        card["easyscholar_custom_rank"] = easy.get("custom_rank", [])
    return card


def run(journals: List[str], sci_select_path: str = "", easy_adapter_path: str = "") -> List[Dict[str, Any]]:
    configure_local_index()
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
