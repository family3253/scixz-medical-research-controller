from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path


def fetch_crossref(doi: str, mailto: str | None, timeout: int):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="")
    headers = {"User-Agent": "formatting-journal-submissions/1.0"}
    if mailto:
        headers["User-Agent"] += f" (mailto:{mailto})"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))["message"]
    except Exception as exc:
        return {"_error": str(exc)}


def journal(data: dict) -> str:
    values = data.get("short-container-title") or data.get("container-title") or []
    return values[0] if values else ""


def year(data: dict) -> str:
    parts = data.get("issued", {}).get("date-parts", [[]])
    return str(parts[0][0]) if parts and parts[0] else ""


def authors(data: dict, style: str) -> str:
    people = data.get("author") or []
    rendered = []
    for person in people[:6]:
        family = person.get("family", "")
        given = person.get("given", "")
        initials = "".join(part[0] for part in re.findall(r"[A-Za-z]+", given))
        if style == "apa":
            rendered.append(f"{family}, {(' '.join(ch + '.' for ch in initials))}".rstrip(", "))
        else:
            rendered.append(f"{family} {initials}".strip())
    result = ", ".join(rendered)
    if len(people) > 6:
        result += ", et al."
    return result


def format_reference(data: dict, style: str) -> str:
    title = (data.get("title") or [""])[0].rstrip(".")
    journal_name = journal(data)
    pub_year = year(data)
    volume = data.get("volume", "")
    issue = data.get("issue", "")
    pages = data.get("page", "")
    doi = data.get("DOI", "")
    author_text = authors(data, style)
    if style == "apa":
        result = f"{author_text} ({pub_year}). {title}."
        if journal_name:
            result += f" {journal_name}"
        if volume:
            result += f", {volume}"
        if issue:
            result += f"({issue})"
        if pages:
            result += f", {pages}"
        if doi:
            result += f". https://doi.org/{doi}"
        return result
    if style == "nature":
        result = f"{author_text} {title}."
        if journal_name:
            result += f" {journal_name}"
        if volume:
            result += f" {volume}"
        if pages:
            result += f", {pages}"
        if pub_year:
            result += f" ({pub_year})"
        return result + "."
    result = f"{author_text}. {title}." if author_text else f"{title}."
    if journal_name:
        result += f" {journal_name}."
    if pub_year:
        result += f" {pub_year}"
    if volume:
        result += f";{volume}"
        if issue:
            result += f"({issue})"
    if pages:
        result += f":{pages}"
    result += "."
    if doi:
        result += f" doi:{doi}"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch DOI metadata conservatively from Crossref")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--style", choices=["vancouver", "nature", "apa"], default="vancouver")
    parser.add_argument("--mailto")
    parser.add_argument("--delay", type=float, default=0.3)
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    results = []
    for record in records:
        doi = record.get("doi")
        fallback = record.get("fallback", f"Reference {record.get('id')}")
        data = fetch_crossref(doi, args.mailto, args.timeout) if doi else None
        if data and "_error" not in data:
            formatted = format_reference(data, args.style)
            source = "crossref"
            error = None
        else:
            formatted = fallback
            source = "fallback"
            error = data.get("_error") if isinstance(data, dict) else None
        results.append({"id": record["id"], "doi": doi, "formatted": formatted, "source": source, "error": error})
        if doi:
            time.sleep(args.delay)
    args.output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"output": str(args.output), "count": len(results), "crossref": sum(r["source"] == "crossref" for r in results)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
