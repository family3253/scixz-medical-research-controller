#!/usr/bin/env python3
"""Optional EasyScholar journal-rank adapter for SciXZ/find-journal.

The secret is read only from EASY_SCHOLAR_SECRET_KEY. It is never accepted as a
command-line argument, printed, or written to a result file. The adapter keeps
EasyScholar as a third-party evidence source; it does not claim that the
service's ``officialRank`` is an official Clarivate or CAS record.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any, Dict, Iterable, List
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ENDPOINT = "https://www.easyscholar.cc/open/getPublicationRank"
MIN_DELAY_SECONDS = 0.5  # API documentation: no more than two requests/second.


def _rank_text(rank_info: Dict[str, Any], rank_number: int) -> str | None:
    keys = ("oneRankText", "twoRankText", "threeRankText", "fourRankText", "fiveRankText")
    if not 1 <= rank_number <= len(keys):
        return None
    value = rank_info.get(keys[rank_number - 1])
    return str(value).strip() if value not in (None, "") else None


def _parse_custom_rank(custom: Dict[str, Any]) -> List[Dict[str, Any]]:
    rank_info = custom.get("rankInfo") or []
    by_uuid = {str(item.get("uuid")): item for item in rank_info if isinstance(item, dict) and item.get("uuid")}
    parsed: List[Dict[str, Any]] = []
    for raw in custom.get("rank") or []:
        parts = str(raw).split("&&&", 1)
        if len(parts) != 2:
            parsed.append({"raw": raw, "status": "unparsed"})
            continue
        uuid, rank_text = parts
        try:
            rank_number = int(rank_text)
        except ValueError:
            parsed.append({"raw": raw, "uuid": uuid, "status": "unparsed"})
            continue
        info = by_uuid.get(uuid, {})
        parsed.append(
            {
                "raw": raw,
                "uuid": uuid,
                "dataset": info.get("abbName"),
                "rank_number": rank_number,
                "rank_text": _rank_text(info, rank_number),
                "status": "parsed" if uuid in by_uuid else "missing_rank_info",
            }
        )
    return parsed


def normalize_payload(journal_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    data = payload.get("data") if isinstance(payload, dict) else None
    data = data if isinstance(data, dict) else {}
    official = data.get("officialRank") if isinstance(data.get("officialRank"), dict) else {}
    custom = data.get("customRank") if isinstance(data.get("customRank"), dict) else {}
    all_ranks = official.get("all") if isinstance(official.get("all"), dict) else {}
    selected_ranks = official.get("select") if isinstance(official.get("select"), dict) else {}

    # Keep the provider's abbreviations intact; they are the documented API keys.
    fields = {
        "sciif": all_ranks.get("sciif"),
        "jcr_quartile": all_ranks.get("sci"),
        "ssci_quartile": all_ranks.get("ssci"),
        "jci": all_ranks.get("jci"),
        "cas_warning": all_ranks.get("sciwarn"),
        "cas_base_quartile": all_ranks.get("sciBase"),
        "cas_upgraded_major_quartile": all_ranks.get("sciUp"),
        "cas_upgraded_minor_quartile": all_ranks.get("sciUpSmall"),
        "cas_upgraded_top": all_ranks.get("sciUpTop"),
        "xinrui_quartile": all_ranks.get("xr"),
        "xinrui_warning": all_ranks.get("xrWarn"),
        "xinrui_top": all_ranks.get("xrTop"),
        "xinrui_minor_quartile": all_ranks.get("xrSmall"),
    }
    fields = {key: value for key, value in fields.items() if value not in (None, "")}
    return {
        "journal_name": journal_name,
        "provider": "EasyScholar",
        "source_type": "third-party-api",
        "source_status": "succeeded" if payload.get("code") == 200 else "partial",
        "source_url": ENDPOINT,
        "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "fields": fields,
        "official_rank_all": all_ranks,
        "official_rank_selected": selected_ranks,
        "custom_rank": _parse_custom_rank(custom),
        "api_code": payload.get("code"),
        "api_message": payload.get("msg"),
    }


def fetch_rank(journal_name: str, secret_key: str, timeout: float = 20.0) -> Dict[str, Any]:
    query = urlencode({"secretKey": secret_key, "publicationName": journal_name})
    request = Request(
        f"{ENDPOINT}?{query}",
        headers={"User-Agent": "SciXZ-EasyScholar-adapter/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
        payload = json.loads(body)
    except HTTPError as exc:
        return {"journal_name": journal_name, "provider": "EasyScholar", "source_status": "attempted", "error": f"HTTP {exc.code}"}
    except (URLError, TimeoutError) as exc:
        return {"journal_name": journal_name, "provider": "EasyScholar", "source_status": "attempted", "error": str(exc)}
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"journal_name": journal_name, "provider": "EasyScholar", "source_status": "attempted", "error": f"invalid response: {exc}"}
    return normalize_payload(journal_name, payload)


def lookup(journal_names: Iterable[str], secret_key: str, timeout: float = 20.0) -> List[Dict[str, Any]]:
    names = [name.strip() for name in journal_names if name and name.strip()]
    results: List[Dict[str, Any]] = []
    for index, name in enumerate(names):
        if index:
            time.sleep(MIN_DELAY_SECONDS)
        results.append(fetch_rank(name, secret_key, timeout=timeout))
    return results


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Query EasyScholar journal-rank fields without exposing the API key.")
    parser.add_argument("journal", nargs="+", help="One or more journal names.")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    secret_key = os.environ.get("EASY_SCHOLAR_SECRET_KEY", "").strip()
    if not secret_key:
        print("EASY_SCHOLAR_SECRET_KEY is not set; no request was sent.", file=sys.stderr)
        return 2
    output = lookup(args.journal, secret_key, timeout=args.timeout)
    print(json.dumps(output, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
