from __future__ import annotations

import argparse
import hashlib
import re
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

import yaml


class VisibleTextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1
        if tag.lower() in {"p", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_depth and data.strip():
            self.parts.append(data)


def visible_text(raw: str) -> str:
    parser = VisibleTextParser()
    parser.feed(raw)
    lines = []
    for line in re.split(r"\n+", "".join(parser.parts)):
        clean = re.sub(r"\s+", " ", line).strip()
        if clean:
            lines.append(clean)
    return "\n".join(lines)


def classify(line: str) -> str | None:
    checks = [
        ("abstract", "abstract"),
        ("references", "reference"),
        ("figures", "figure"),
        ("tables", "table"),
        ("supplements", "supplement"),
        ("review_model", "anonymous|blinded|blind review|open review"),
        ("word_limit", "word limit|words|word count"),
        ("line_numbering", "line number"),
        ("title_page", "title page|author information"),
        ("cover_letter", "cover letter"),
        ("ethics", "ethic|consent|registration"),
        ("declarations", "funding|competing interest|conflict of interest|data availability|code availability"),
    ]
    for category, pattern in checks:
        if re.search(pattern, line, flags=re.I):
            return category
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture official journal instructions as reviewable evidence")
    parser.add_argument("--url", help="Official source URL to record and/or fetch")
    parser.add_argument("--html-file", type=Path, help="Local HTML snapshot used instead of fetching the URL")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--journal", required=True)
    parser.add_argument("--article-type", default="")
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    if not args.url and not args.html_file:
        parser.error("one of --url or --html-file is required")

    if args.html_file:
        raw = args.html_file.read_text(encoding="utf-8")
    else:
        request = urllib.request.Request(args.url, headers={"User-Agent": "journal-submission-skill/1.0"})
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw = response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")

    text = visible_text(raw)
    snapshot = args.output.with_suffix(".source.txt")
    snapshot.write_text(text, encoding="utf-8")
    snapshot_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    requirements = []
    seen = set()
    for line in text.splitlines():
        category = classify(line)
        if not category or line.casefold() in seen:
            continue
        seen.add(line.casefold())
        requirements.append({
            "id": f"R{len(requirements) + 1:03d}",
            "category": category,
            "rule": line,
            "evidence": line,
            "applies_to": args.article_type,
            "source_url": args.url or "",
            "source_type": "official-journal",
            "accessed_at": date.today().isoformat(),
            "verification": "unverified",
            "planned_change": "Review and map to an explicit action before editing",
            "change_class": "formatting",
            "status": "needs_review",
        })

    unverified_items = [item["id"] for item in requirements]
    source_status = "captured" if text.strip() else "source_text_empty_or_js_rendered"
    if not requirements and text.strip():
        unverified_items.append("NO_RULE_CANDIDATES")
    if not text.strip():
        unverified_items.append("SOURCE_TEXT_EMPTY")

    payload = {
        "schema_version": 1,
        "journal": args.journal,
        "article_type": args.article_type,
        "retrieved_at": date.today().isoformat(),
        "review_model": "unverified",
        "source_records": [{
            "url": args.url or "",
            "source_type": "official-journal",
            "accessed_at": date.today().isoformat(),
            "snapshot_file": snapshot.name,
            "snapshot_sha256": snapshot_hash,
            "status": source_status,
        }],
        "requirements": requirements,
        "actions": {
            "page_size": None,
            "margins_pt": {"top": None, "right": None, "bottom": None, "left": None},
            "default_font_name": None,
            "default_font_size_pt": None,
            "line_spacing": None,
            "paragraph_spacing_after_pt": None,
            "line_numbers": None,
            "page_numbers": None,
            "reference_style": None,
            "preserve_dynamic_fields": True,
            "anonymization_required": None,
        },
        "conflicts": [],
        "unverified_items": unverified_items,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {len(requirements)} candidate requirements to {args.output}")
    print(f"Evidence snapshot: {snapshot}")
    if source_status != "captured":
        print("WARNING: source text was empty; use a browser-rendered snapshot or official PDF.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
