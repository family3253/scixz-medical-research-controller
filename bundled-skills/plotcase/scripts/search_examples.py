from __future__ import annotations

import argparse
import json
from pathlib import Path


ALIASES: dict[str, list[str]] = {
    "论文风": ["临床", "森林图", "生存分析", "热图", "火山图"],
    "医学风": ["临床", "生存分析", "森林图", "游泳图"],
    "临床图": ["临床", "生存分析", "森林图", "游泳图"],
    "组学图": ["组学", "热图", "火山图", "网络图"],
    "发表图": ["论文", "临床", "组学"],
}


def load_examples(index_path: Path) -> list[dict]:
    if not index_path.exists():
        raise FileNotFoundError(f"Examples index not found: {index_path}")
    return json.loads(index_path.read_text(encoding="utf-8"))


def expand_terms(query: str) -> list[str]:
    normalized = query.strip().lower()
    terms = [term for term in normalized.split() if term] or [normalized]
    expanded = list(terms)
    for term in terms:
        expanded.extend(ALIASES.get(term, []))
    return list(dict.fromkeys(expanded))


def search_examples(
    examples: list[dict],
    query: str,
    top: int,
    category: str | None,
    ext: str | None,
) -> list[dict]:
    normalized = query.strip().lower()
    if not normalized:
        raise ValueError("Query must not be empty.")

    terms = expand_terms(query)
    scored: list[dict] = []

    for example in examples:
        example_path = str(example.get("example_path", ""))
        example_category = str(example.get("category", ""))

        if category and example_category.lower() != category.lower():
            continue

        if ext and Path(example_path).suffix.lower() != ext.lower():
            continue

        haystack = " ".join(
            [
                str(example.get("title", "")),
                str(example.get("summary", "")),
                " ".join(example.get("keywords", [])),
                " ".join(example.get("tags", [])),
                str(example.get("category", "")),
                str(example.get("id", "")),
            ]
        ).lower()

        score = sum(1 for term in terms if term in haystack)
        if score > 0:
            scored.append(
                {
                    "score": score,
                    "title": example.get("title", ""),
                    "category": example.get("category", ""),
                    "summary": example.get("summary", ""),
                    "tags": example.get("tags", []),
                    "example_path": example_path,
                }
            )

    scored.sort(key=lambda item: (-item["score"], item["title"]))
    return scored[:top]


def render_text(matches: list[dict], query: str) -> str:
    if not matches:
        return f"No PlotCase examples found for query: {query}"

    lines = [f"Found {len(matches)} PlotCase example(s) for query: {query}"]
    for match in matches:
        lines.extend(
            [
                "---",
                f"Title: {match['title']}",
                f"Category: {match['category']}",
                f"Summary: {match['summary']}",
                f"Tags: {', '.join(match['tags'])}",
                f"Path: {match['example_path']}",
            ]
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--output-format", choices=["Text", "Json"], default="Text")
    parser.add_argument("--category")
    parser.add_argument("--ext")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    root = script_dir.parent
    index_path = root / "assets" / "examples" / "examples.json"

    try:
        examples = load_examples(index_path)
        matches = search_examples(
            examples, args.query, args.top, args.category, args.ext
        )
    except Exception as exc:  # noqa: BLE001
        print(str(exc))
        return 1

    if args.output_format == "Json":
        print(
            json.dumps(
                {
                    "query": args.query,
                    "category": args.category,
                    "ext": args.ext,
                    "count": len(matches),
                    "matches": matches,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(render_text(matches, args.query))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
