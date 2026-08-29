from __future__ import annotations

import argparse
import csv
import importlib
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from urllib.response import addinfourl
from typing import Callable, Final, cast

write_candidate_rows: Final[Callable[[Path, list[dict[str, str]]], None]] = cast(
    Callable[[Path, list[dict[str, str]]], None],
    importlib.import_module(
        ".provider_adapter_common" if __package__ else "provider_adapter_common",
        package=__package__,
    ).write_candidate_rows,
)
schema_module = importlib.import_module(
    ".review_project_schema" if __package__ else "review_project_schema",
    package=__package__,
)
CANDIDATE_HEADERS: Final[list[str]] = cast(list[str], schema_module.CANDIDATE_HEADERS)
FULLTEXT_ACQUISITION_HEADERS: Final[list[str]] = cast(
    list[str], schema_module.FULLTEXT_ACQUISITION_HEADERS
)


TEXT_HINTS = (
    "全文",
    "正文",
    "方法",
    "结果",
    "abstract",
    "introduction",
    "method",
    "result",
)


def extract_text(html: str) -> str:
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def detect_provider(url: str) -> str:
    lowered = url.lower()
    if "cnki" in lowered:
        return "cnki"
    if "wanfang" in lowered:
        return "wanfang"
    if "pubmed" in lowered:
        return "pubmed"
    if "pmc" in lowered:
        return "pmc"
    return "unknown"


def fetch_url(url: str) -> tuple[str, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        typed_response = cast(addinfourl | urllib.response.addbase, response)
        final_url = str(typed_response.geturl())
        html = typed_response.read().decode("utf-8", errors="ignore")
    return final_url, html


def candidate_row(
    doi: str, final_url: str, html: str, search_batch: str
) -> dict[str, str]:
    provider = detect_provider(final_url)
    text = extract_text(html)
    has_fulltext_hint = any(token.lower() in html.lower() for token in TEXT_HINTS)
    row = {header: "" for header in CANDIDATE_HEADERS}
    row.update(
        {
            "citation_id": doi,
            "search_batch": search_batch,
            "database_source": f"{provider}-doi-resolver"
            if provider != "unknown"
            else "doi-resolver",
            "source_provider": provider,
            "access_mode": "doi-acquisition",
            "retrieval_date": datetime.now().strftime("%Y-%m-%d"),
            "doi_or_link": final_url,
            "document_type": "resolved-doi",
            "duplicate_status": "unique",
            "full_text_available": "yes"
            if has_fulltext_hint and len(text) > 500
            else "",
            "topic_tag": doi,
            "notes": f"final_url={final_url}; has_fulltext_hint={has_fulltext_hint}",
        }
    )
    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    if title_match:
        row["title"] = extract_text(title_match.group(1))[:500]
    if not row["title"]:
        row["title"] = f"DOI acquisition for {doi}"
    return row


def acquisition_row(
    doi: str, final_url: str, html: str, output_basename: str
) -> dict[str, str]:
    provider = detect_provider(final_url)
    text = extract_text(html)
    has_fulltext_hint = any(token.lower() in html.lower() for token in TEXT_HINTS)
    return {
        "citation_id": doi,
        "acquisition_status": "acquired" if text else "metadata-only",
        "acquisition_source": provider,
        "access_mode": "doi-acquisition",
        "authorized_session_used": "",
        "target_url": final_url,
        "acquired_at": datetime.now().isoformat(timespec="seconds"),
        "version_note": "html-landing-page",
        "copyright_or_license_note": "",
        "access_notes": f"has_fulltext_hint={has_fulltext_hint}",
        "pdf_status": "",
        "local_filename": f"{output_basename}.txt" if text else "",
        "readable": "yes" if text else "",
        "is_complete_full_text": "yes"
        if has_fulltext_hint and len(text) > 2000
        else "",
        "has_abstract": "yes" if "abstract" in html.lower() or "摘要" in html else "",
        "paywalled": "",
        "notes": f"final_url={final_url}",
    }


def write_acquisition_csv(path: Path, row: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FULLTEXT_ACQUISITION_HEADERS)
        _ = writer.writeheader()
        _ = writer.writerow(
            {header: row.get(header, "") for header in FULLTEXT_ACQUISITION_HEADERS}
        )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Resolve DOI to its landing provider and persist acquisition artifacts."
    )
    parser.add_argument("doi")
    parser.add_argument("--candidate-output", required=True)
    parser.add_argument("--acquisition-output", required=True)
    parser.add_argument("--text-output", required=True)
    parser.add_argument("--search-batch", default="")
    args = parser.parse_args()

    doi = cast(str, args.doi)
    candidate_output = cast(str, args.candidate_output)
    acquisition_output = cast(str, args.acquisition_output)
    text_output = cast(str, args.text_output)
    search_batch = cast(str, args.search_batch) or datetime.now().strftime(
        "doi-acquisition-%Y%m%d-%H%M%S"
    )
    start_url = f"https://doi.org/{doi}"
    try:
        final_url, html = fetch_url(start_url)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"HTTP error during DOI acquisition: {exc.code} {exc.reason}"
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error during DOI acquisition: {exc.reason}") from exc

    text = extract_text(html)
    candidate = candidate_row(doi, final_url, html, search_batch)
    acquisition = acquisition_row(doi, final_url, html, Path(text_output).stem)

    candidate_path = Path(candidate_output).expanduser().resolve()
    acquisition_path = Path(acquisition_output).expanduser().resolve()
    text_path = Path(text_output).expanduser().resolve()
    text_path.parent.mkdir(parents=True, exist_ok=True)

    write_candidate_rows(candidate_path, [candidate])
    write_acquisition_csv(acquisition_path, acquisition)
    written = text_path.write_text(text, encoding="utf-8")
    assert written >= 0
    print(f"[ok] candidate row -> {candidate_path}")
    print(f"[ok] acquisition row -> {acquisition_path}")
    print(f"[ok] extracted text -> {text_path}")


if __name__ == "__main__":
    main()
