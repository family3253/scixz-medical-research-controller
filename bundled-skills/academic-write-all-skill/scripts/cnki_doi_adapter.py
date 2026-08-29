from __future__ import annotations

import argparse
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from provider_adapter_common import write_candidate_rows
from review_project_schema import CANDIDATE_HEADERS


TEXT_HINTS = ("全文", "正文", "方法", "结果")


def extract_text(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def fetch_doi(doi: str) -> tuple[str, str, str]:
    url = f"https://doi.org/{doi}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        html = response.read().decode("utf-8", errors="ignore")
    return url, final_url, html


def build_row(
    doi: str, start_url: str, final_url: str, html: str, search_batch: str
) -> dict[str, str]:
    row = {header: "" for header in CANDIDATE_HEADERS}
    text = extract_text(html)
    looks_like_cnki = "cnki" in final_url.lower()
    has_fulltext_hint = any(token in html for token in TEXT_HINTS)
    row.update(
        {
            "citation_id": doi,
            "search_batch": search_batch,
            "database_source": "cnki-doi-resolver",
            "source_provider": "cnki",
            "access_mode": "doi-resolver",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d"),
            "doi_or_link": final_url or start_url,
            "document_type": "resolved-doi",
            "duplicate_status": "unique",
            "full_text_available": "yes"
            if looks_like_cnki and has_fulltext_hint and len(text) > 500
            else "",
            "topic_tag": doi,
            "notes": "; ".join(
                [
                    f"start_url={start_url}",
                    f"final_url={final_url}",
                    f"looks_like_cnki={looks_like_cnki}",
                    f"has_fulltext_hint={has_fulltext_hint}",
                ]
            ),
        }
    )
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if title_match:
        row["title"] = extract_text(title_match.group(1))[:500]
    if not row["title"]:
        row["title"] = f"CNKI DOI resolution for {doi}"
    return row


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve a DOI through doi.org and normalize CNKI-aware access metadata."
    )
    parser.add_argument("doi")
    parser.add_argument("--output", required=True)
    parser.add_argument("--search-batch", default="")
    args = parser.parse_args()

    search_batch = args.search_batch or datetime.now().strftime(
        "cnki-doi-%Y%m%d-%H%M%S"
    )
    try:
        start_url, final_url, html = fetch_doi(args.doi)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"HTTP error during DOI resolution: {exc.code} {exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error during DOI resolution: {exc.reason}") from exc

    row = build_row(args.doi, start_url, final_url, html, search_batch)
    output_path = Path(args.output).expanduser().resolve()
    write_candidate_rows(output_path, [row])
    print(f"[ok] wrote DOI resolution row to {output_path}")


if __name__ == "__main__":
    main()
